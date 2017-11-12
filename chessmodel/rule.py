
def next_steps(board, red):
    steps = []
    for i in range(len(board)):
        chess = board[i]
        if side(chess) == 0 or is_red(chess) != red:
            continue
        moves = next_chess_steps[chess](board, i)
        steps += [(i, m) for m in moves]
    return steps


def is_red(chess):
    return 'A' <= chess and 'Z' >= chess


def position_1(x, y):
    return x + y * 9


def position_2(pos):
    return pos % 9, pos // 9


def flip_side(chess):
    if is_red(chess):
        return chess.lower()
    elif ' ' == chess:
        return chess
    else:
        return chess.upper()


def rotate_board(board):
    return [board[89 - i] for i in range(90)]


def valid_position2(x, y):
    return x >= 0 and x < 9 and y >= 0 and y < 10


def side(chess):
    if is_red(chess): return 1
    elif ' ' == chess: return 0
    else: return -1


def next_rider_steps(board, pos):
    steps = []
    px, py = position_2(pos)
    for r in [range(px+1, 9), range(px-1, -1, -1)]:
        for x in r:
            p = position_1(x, py)
            if side(board[p]) * side(board[pos]) <= 0:
                steps.append(p)
            if ' ' != board[p]:
                break
    for r in [range(py+1, 10), range(py-1, -1, -1)]:
        for y in r:
            p = position_1(px, y)
            if side(board[p]) * side(board[pos]) <= 0:
                steps.append(p)
            if ' ' != board[p]:
                break
    return steps


def next_horse_steps(board, pos):
    steps = []
    px, py = position_2(pos)
    for dx, dy in [(-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(-1,2),(1,-2),(1,2)]:
        if valid_position2(px+dx, py+dy) is False:
            continue
        bx = int(dx / 2)
        by = int(dy / 2)
        if board[position_1(px+bx, py+by)] != ' ':
            continue
        p = position_1(px+dx,py+dy)
        if side(board[p]) * side(board[pos]) <= 0:
            steps.append(p)
    return steps


def next_elephant_steps(board, pos):
    steps = []
    px, py = position_2(pos)
    for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
        if valid_position2(px+dx, py+dy) is False:
            continue
        bx = dx // 2
        by = dy // 2
        if board[position_1(px+bx, py+by)] != ' ':
            continue
        if py+dy not in [0, 2, 4, 5, 7, 9]:
            continue
        p = position_1(px+dx,py+dy)
        if side(board[p]) * side(board[pos]) <= 0:
            steps.append(p)
    return steps


def next_bishop_steps(board, pos):
    steps = []
    px, py = position_2(pos)
    for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        if valid_position2(px+dx,py+dy) is False:
            continue
        if px+dx not in [3,4,5] or py+dy not in [0,1,2,7,8,9]:
            continue
        p = position_1(px+dx,py+dy)
        if side(board[p]) * side(board[pos]) <= 0:
            steps.append(p)
    return steps


def next_king_steps(board, pos):
    steps = []
    px, py = position_2(pos)
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        if valid_position2(px+dx,py+dy) is False:
            continue
        if px+dx not in [3,4,5] or py+dy not in [0,1,2,7,8,9]:
            continue
        p = position_1(px+dx,py+dy)
        if side(board[p]) * side(board[pos]) <= 0:
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
    return steps


def next_cannon_steps(board, pos):
    steps = []
    px, py = position_2(pos)
    for r in [range(px+1, 9), range(px-1, -1, -1)]:
        counter = 0
        for x in r:
            p = position_1(x, py)
            if counter == 0:
                if ' ' == board[p]:
                    steps.append(p)
                else:
                    counter = 1
            elif counter == 1:
                if side(board[p]) * side(board[pos]) < 0:
                    steps.append(p)
                    counter = 2
                    break
    for r in [range(py+1, 10), range(py-1, -1, -1)]:
        counter = 0
        for y in r:
            p = position_1(px, y)
            if counter == 0:
                if ' ' == board[p]:
                    steps.append(p)
                else:
                    counter = 1
            elif counter == 1:
                if side(board[p]) * side(board[pos]) < 0:
                    steps.append(p)
                    counter = 2
                    break
    return steps


def next_pawn_steps(board, pos):
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
        if side(board[p]) * side(board[pos]) <= 0:
            steps.append(p)
    return steps


def find_chess(board, chess):
    return [i for i in range(90) if board[i] == chess]


def basic_score(board):
    return sum([score_map[c] for c in board])


def initial_board():
    return 'rhebkbehr##########c#####c#p#p#p#p#p##################P#P#P#P#P#C#####C##########RHEBKBEHR'.replace('#', ' ')


def next_board(board, move):
    r = [b for b in board]
    f, t = move
    r[t] = r[f]
    r[f] = ' '
    return ''.join(r)


score_map = {
    'R': 1000,
    'r': -1000,
    'H': 400,
    'h': -400,
    'E': 100,
    'e': -100,
    'B': 100,
    'b': -100,
    'K': 100000,
    'k': -100000,
    'C': 400,
    'c': -400,
    'P': 60,
    'p': -60,
    ' ': 0
}

next_chess_steps = {
    'R': next_rider_steps,
    'r': next_rider_steps,
    'H': next_horse_steps,
    'h': next_horse_steps,
    'E': next_elephant_steps,
    'e': next_elephant_steps,
    'B': next_bishop_steps,
    'b': next_bishop_steps,
    'K': next_king_steps,
    'k': next_king_steps,
    'C': next_cannon_steps,
    'c': next_cannon_steps,
    'P': next_pawn_steps,
    'p': next_pawn_steps
}
