
OCCUPY = 0
COVER = 1
NEXT_COVER = 2

def square_map(board):
    map = [[]] * 90
    for i in range(90):
        chess = board[i]
        if side(chess) == 0:
            continue
        map[i].append((chess, OCCUPY))
        covers, next_covers = next_covers(board, i)
        for pos in covers:
            map[pos].append((chess, COVER))

        for pos in next_covers:
            map[pos].append((chess, NEXT_COVER))
    return map


def next_covers(board, pos):
    pass