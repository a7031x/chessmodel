import requests
import urllib
import sqlite3
import asyncio

cache = {}

def board_to_fen(board, red):
    rows = []
    for row in range(10):
        line = ''
        gap = 0
        for x in board[row*9:(row+1)*9]:
            if x != ' ':
                if gap != 0:
                    line += str(gap)
                    gap = 0
                line += x
            else:
                gap += 1
        if gap != 0:
            line += str(gap)
        rows.append(line)
    return '/'.join(rows) + ' ' + ('w' if red else 'b')


def fen_to_board(fen):
    rows, red = fen.split(' ')
    red = (red == 'w')
    rows = rows.split('/')
    board = ''
    for row in rows:
        for c in row:
            if '1' <= c <= '9':
                board += ' ' * int(c)
            else:
                board += c
    return board, red


def queryscore(board, red):
    fen = board_to_fen(board, red)
    return queryscore_fen(fen)


def queryscore_fen(fen):
    if fen in cache:
        return cache[fen]
    score = queryscore_fen_imply(fen)
    cache[fen] = score
    return score



def queryscore_fen_imply(fen):
    query = urllib.parse.quote(fen)
    while True:
        try:
            r = requests.get('http://api.chessdb.cn:81/chessdb.php?action=queryscore&board=' + query, timeout=1).text
            if 'unknown' in r:
                return None
            if 'eval' not in r:
                print('INVALID RESPONSE:', fen, r)
                return None
            score = int(r.strip('\x00').split(':')[1])
            return score
        except:
            print('retrying...')


def read_database():
    conn = sqlite3.connect('chess.db')
    cursor = conn.cursor()
    cursor.execute('SELECT board, score FROM board_score')
    rows = cursor.fetchall()
    for row in rows:
        board, red = fen_to_board(row[0])
        score = row[1]
        yield board, red, score


def download_database():
    conn = sqlite3.connect('chess.db')
    fen = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w'
    try:
        c = conn.cursor()
        c.execute('CREATE TABLE board_score (board text primary key, score integer, score2 integer, expand integer default 0)')
        c.execute('''INSERT INTO board_score (board, score) VALUES ('{}', {})'''.format(fen, 15))
        conn.commit()
    except:
        print('table already created')
    evaluating = set()
    queue = []
    c.execute('SELECT board, expand FROM board_score')
    for row in c.fetchall():
        evaluating.add(row[0])
        if row[1] == 0:
            queue.append(row[0])
    update_database(conn, queue, evaluating)


def update_database(conn, queue, evaluating):
    cursor = conn.cursor()
    while len(queue) != 0:
        fen = queue[0]
        queue.pop(0)
        next_boards, scores, scores2 = queryboards_fen_imply(fen, evaluating)
        values = list(zip(next_boards, scores, scores2))
        cursor.executemany('INSERT INTO board_score (board, score, score2) VALUES(?,?,?)', values)
        cursor.execute('UPDATE board_score SET expand=1 WHERE board=?', (fen,))
        for f, s1, s2 in values:
            queue.append(f)
            evaluating.add(f)
        conn.commit()
        print('records', len(evaluating))


def move_to_fen(board, red, move):
    move, _, _, _ = move.split(',')
    move = move.split(':')[1]
    movefrom = ord(move[0]) - ord('a') + (9 - int(move[1])) * 9
    moveto = ord(move[2]) - ord('a') + (9 - int(move[3])) * 9
    next_board = [c for c in board]
    next_board[moveto] = next_board[movefrom]
    next_board[movefrom] = ' '
    next_fen = board_to_fen(next_board, not red)
    return next_fen


@asyncio.coroutine
def process_move(board, red, move):
    move, score, _, _ = move.split(',')
    move = move.split(':')[1]
    score = score.split(':')[1]
    movefrom = ord(move[0]) - ord('a') + (9 - int(move[1])) * 9
    moveto = ord(move[2]) - ord('a') + (9 - int(move[3])) * 9
    next_board = [c for c in board]
    next_board[moveto] = next_board[movefrom]
    next_board[movefrom] = ' '
    next_fen = board_to_fen(next_board, not red)
    if '??' == score:
        score2 = None
    else:
        score2 = int(score)
        score2 = score2 if red else -score2
    score = queryscore_fen(next_fen)
    if score is not None and red:
        score = -score
    return next_fen, score, score2


def queryboards_fen_imply(fen, evaluating=None):
    query = urllib.parse.quote(fen)
    while True:
        try:
            r = requests.get('http://api.chessdb.cn:81/chessdb.php?action=queryall&board=' + query, timeout=1).text.strip('\x00')
            break
        except:
            print('retrying...')
            continue

    if r in ['unknown', 'checkmate']:
        return [], []
    if ':' not in r:
        print(r)
    movelist = r.split('|')
    board, red = fen_to_board(fen)
    boards = []
    scores = []
    tasks = []
    #loop = asyncio.get_event_loop()
    for move in movelist:
        if evaluating is not None and move_to_fen(board, red, move) in evaluating:
            continue
        task = process_move(board, red, move)
        tasks.append(task)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*tasks))
    scores2 = []
    for next_fen, score, score2 in results:
        if score is None:
            continue
        boards.append(next_fen)
        scores.append(score)
        scores2.append(score2)
    return boards, scores, scores2


if __name__ == '__main__':
    download_database()
    r = queryscore_fen('rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w')
    print(r)