import rule

c2i = {
    'R': 1,
    'r': -1,
    'H': 2,
    'h': -2,
    'E': 3,
    'e': -3,
    'B': 4,
    'b': -4,
    'K': 5,
    'k': -5,
    'C': 6,
    'c': -6,
    'P': 7,
    'p': -7,
    ' ': 0
}


def create_feed(model, board_with_side, label):
    input = []
    rotate = []
    for board, red in board_with_side:
        if red is False:
            board = [rule.flip_side(c) for c in board]
        pos = rule.find_chess(board, 'K')[0]
        if pos < 45:
            board = rule.rotate_board(board)
            rotate.append(True)
        else:
            rotate.append(False)
        board = [c2i[c] for c in board]
        input.append(board)

    feed = {
        model.input: input
    }
    if label is not None:
        label = [(x if not r else 89 - x, y if not r else 89 - y) for (x, y), r in zip(label, rotate)]
        label = [x+y*90 for x, y in label]
        feed[model.label] = label
    return feed


def unfeed(moves, red):
    moves = [(x if red else 89 - x, y if red else 89 - 9) for x, y in moves]
    return moves

