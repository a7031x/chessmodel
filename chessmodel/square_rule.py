from rule import *

OCCUPY = 0

def square_map(board):
    map = [[] for _ in range(90)]
    for i in range(90):
        chess = board[i]
        if side(chess) == 0:
            continue
        map[i].append((chess, OCCUPY))
        states = next_covers[board[i]](board, i)
        state = 1
        for s in list(states):
            for pos in s:
                map[pos].append((chess, state))
            state += 1

    return map


def next_rider_covers(board, pos):
    covers = []
    next = []
    px, py = position_2(pos)
    for r in [range(px+1, 9), range(px-1, -1, -1)]:
        state = 0
        for x in r:
            p = position_1(x, py)
            if state is 0:
                covers.append(p)
            elif state is 1:
                next.append(p)
            if ' ' != board[p]:
                state += 1
                if state is 2:
                    break

    for r in [range(py+1, 10), range(py-1, -1, -1)]:
        for y in r:
            p = position_1(px, y)
            if state is 0:
                covers.append(p)
            elif state is 1:
                next.append(p)
            if ' ' != board[p]:
                state += 1
                if state is 2:
                    break
    return covers, next


def next_horse_covers(board, pos):
    steps = []
    blocks = []
    next = []
    px, py = position_2(pos)
    for dx, dy in [(-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(-1,2),(1,-2),(1,2)]:
        if valid_position2(px+dx, py+dy) is False:
            continue
        bx = int(dx / 2)
        by = int(dy / 2)
        block_position = position_1(px+bx, py+by)
        block = (board[block_position] != ' ')
        p = position_1(px+dx, py+dy)
        if block:
            blocks.append(block_position)
            next.append(p)
        else:
            steps.append(p)
    return steps, blocks, next


def next_elephant_covers(board, pos):
    steps = []
    blocks = []
    next = []
    px, py = position_2(pos)
    for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
        if valid_position2(px+dx, py+dy) is False:
            continue
        if py+dy not in [0, 2, 4, 5, 7, 9]:
            continue
        bx = dx // 2
        by = dy // 2
        block_position = position_1(px+bx, py+by)
        block = (board[block_position] != ' ')
        p = position_1(px+dx,py+dy)
        if block:
            blocks.append(block_position)
            next.append(p)
        else:
            steps.append(p)
    return steps, blocks, next


def next_bishop_covers(board, pos):
    steps = []
    px, py = position_2(pos)
    for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        if valid_position2(px+dx,py+dy) is False:
            continue
        if px+dx not in [3,4,5] or py+dy not in [0,1,2,7,8,9]:
            continue
        p = position_1(px+dx,py+dy)
        steps.append(p)
    return (steps,)


def next_king_covers(board, pos):
    steps = []
    check = []
    px, py = position_2(pos)
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        if valid_position2(px+dx,py+dy) is False:
            continue
        if px+dx not in [3,4,5] or py+dy not in [0,1,2,7,8,9]:
            continue
        p = position_1(px+dx,py+dy)
        steps.append(p)
    if py <= 2:
        rng = range(py+1, 10)
    else:
        rng = range(py-1, -1, -1)
    for y in rng:
        p = position_1(px, y)
        if board[p] != ' ':
            if board[p] in ['k', 'K']:
                steps.append(p)
            break
        else:
            if (py <= 2 and y >= 7) or (py >= 7 and y <= 2):
                check.append(p)
    return steps, check


def next_cannon_covers(board, pos):
    steps = []
    next = []
    px, py = position_2(pos)
    for r in [range(px+1, 9), range(px-1, -1, -1)]:
        counter = 0
        for x in r:
            p = position_1(x, py)
            if counter == 1:
                steps.append(p)
            elif counter == 2:
                next.append(p)
            if ' ' != board[p]:
                counter += 1
                if counter == 3:
                    break

    for r in [range(py+1, 10), range(py-1, -1, -1)]:
        counter = 0
        for y in r:
            p = position_1(px, y)
            if counter == 1:
                steps.append(p)
            elif counter == 2:
                next.append(p)
            if ' ' != board[p]:
                counter += 1
                if counter == 3:
                    break
    return steps, next


def next_pawn_covers(board, pos):
    steps = []
    px, py = position_2(pos)
    red_king_pos = find_chess(board, 'K')[0]
    if is_red(board[pos]) == (red_king_pos >= 45):
        if py <= 4:
            possible = [(0,-1),(-1,0),(1,0)]
        else:
            possible = [(0,-1)]
    else:
        if py >= 5:
            possible = [(0,1),(-1,0),(1,0)]
        else:
            possible = [(0,1)]
    for dx, dy in possible:
        if valid_position2(px+dx,py+dy) is False:
            continue
        p = position_1(px+dx, py+dy)
        steps.append(p)
    return (steps,)


next_covers = {
    'R': next_rider_covers,
    'r': next_rider_covers,
    'N': next_horse_covers,
    'n': next_horse_covers,
    'B': next_elephant_covers,
    'b': next_elephant_covers,
    'A': next_bishop_covers,
    'a': next_bishop_covers,
    'K': next_king_covers,
    'k': next_king_covers,
    'C': next_cannon_covers,
    'c': next_cannon_covers,
    'P': next_pawn_covers,
    'p': next_pawn_covers
}