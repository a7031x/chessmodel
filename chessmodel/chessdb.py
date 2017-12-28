import requests
import urllib

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
    r = requests.get('http://api.chessdb.cn:81/chessdb.php?action=queryscore&board=' + query).text
    if 'unknown' in r:
        return None
    if 'eval' not in r:
        print('INVALID RESPONSE:', fen, r)
        return None
    score = int(r.strip('\x00').split(':')[1])
    return score


if __name__ == '__main__':
    r = queryscore_fen('rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w')
    print(r)