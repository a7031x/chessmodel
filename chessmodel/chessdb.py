import requests
import urllib
import sqlite3

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
    while True:
        try:
            score = queryscore_fen_imply(fen)
            cache[fen] = score
            return score
        except:
            print('retrying...')
            continue


def queryscore_fen_imply(fen):
    query = urllib.parse.quote(fen)
    r = requests.get('http://api.chessdb.cn:81/chessdb.php?action=queryscore&board=' + query, timeout=1).text
    if 'unknown' in r:
        return None
    if 'eval' not in r:
        print('INVALID RESPONSE:', fen, r)
        return None
    score = int(r.strip('\x00').split(':')[1])
    return score


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
        c.execute('''CREATE TABLE board_score (board text primary key, score integer, conclude integer default 0)''')
        c.execute('''INSERT INTO board_score (board, score) VALUES ('{}', {})'''.format(fen, 15))
        conn.commit()
    except:
        print('table already created')
    update_database(conn, [(fen, 15)], set())


def update_database(conn, queue, evaluating):
    cursor = conn.cursor()
    while len(queue) != 0:
        fen, score = queue[-1]
        queue.pop()
        if score is None:
            cursor.execute('''UPDATE board_score SET conclude=1 WHERE board='{}' '''.format(fen))
            conn.commit()
            evaluating.remove(fen)
            print('conclude:', fen, 'depth:', len(evaluating), 'queue:', len(queue))
            continue
        queue.append((fen, None))
        evaluating.add(fen)
        next_boards, scores = queryboards_fen_imply(fen)
        for next_board, score in zip(next_boards, scores):
            if next_board in evaluating or is_conclude(conn, next_board):
                continue
            cursor.execute('''INSERT OR IGNORE INTO board_score (board, score) VALUES ('{}', {})'''.format(next_board, score))
            queue.append((next_board, score))
        conn.commit()


def is_conclude(conn, fen):
    cursor = conn.cursor()
    cursor.execute('''SELECT conclude FROM board_score WHERE board='{}' '''.format(fen))
    rows = cursor.fetchall()
    if len(rows) is 0:
        return False
    else:
        return rows[0][0] == 1


def queryboards_fen_imply(fen):
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
    for move in movelist:
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
            score = queryscore_fen(next_fen)
            if score is None:
                continue
        else:
            score = int(score)
        boards.append(next_fen)
        scores.append(score)
    return boards, scores


if __name__ == '__main__':
    download_database()
    r = queryscore_fen('rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w')
    print(r)