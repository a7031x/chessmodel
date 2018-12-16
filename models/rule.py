BASE = 100
GAMEOVER_THRESHOLD = 150 * BASE

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


def gameover_position(board):
    score = basic_score(board)
    return abs(score) >= GAMEOVER_THRESHOLD


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
                    counter += 1
            elif counter == 1:
                if side(board[p]) * side(board[pos]) < 0:
                    steps.append(p)
                if ' ' != board[p]:
                    counter = 2
                    break
            else:
                break
    for r in [range(py+1, 10), range(py-1, -1, -1)]:
        counter = 0
        for y in r:
            p = position_1(px, y)
            if counter == 0:
                if ' ' == board[p]:
                    steps.append(p)
                else:
                    counter += 1
            elif counter == 1:
                if side(board[p]) * side(board[pos]) < 0:
                    steps.append(p)
                if ' ' != board[p]:
                    counter = 2
                    break
            else:
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
    return 'rnbakabnr##########c#####c#p#p#p#p#p##################P#P#P#P#P#C#####C##########RNBAKABNR'.replace('#', ' ')


def next_board(board, move):
    r = [b for b in board]
    f, t = move
    r[t] = r[f]
    r[f] = ' '
    return ''.join(r)

'rnbakabnr'
score_map = {
    'R': 10 * BASE,
    'r': -10 * BASE,
    'N': 4 * BASE,
    'n': -4 * BASE,
    'B': 1 * BASE,
    'b': -1 * BASE,
    'A': 1 * BASE,
    'a': -1 * BASE,
    'K': 300 * BASE,
    'k': -300 * BASE,
    'C': 4 * BASE,
    'c': -4 * BASE,
    'P': 1 * BASE,
    'p': -1 * BASE,
    ' ': 0
}

next_chess_steps = {
    'R': next_rider_steps,
    'r': next_rider_steps,
    'N': next_horse_steps,
    'n': next_horse_steps,
    'B': next_elephant_steps,
    'b': next_elephant_steps,
    'A': next_bishop_steps,
    'a': next_bishop_steps,
    'K': next_king_steps,
    'k': next_king_steps,
    'C': next_cannon_steps,
    'c': next_cannon_steps,
    'P': next_pawn_steps,
    'p': next_pawn_steps
}
