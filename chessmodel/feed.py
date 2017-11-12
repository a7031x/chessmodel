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


def create_feed(model, board_with_side, scores):
    input = []

    for board, red in board_with_side:
        if red is False:
            board = [rule.flip_side(c) for c in board]
        pos = rule.find_chess(board, 'K')[0]
        if pos < 45:
            board = rule.rotate_board(board)
        board = [c2i[c] for c in board]
        input.append(board)
        #input.append([model.embeddings[c] if c >= 0 else model.negative_embeddings[-c] for c in board])

    feed = {
        model.input: input
    }
    if scores is not None:
        label = [score if red else -score for (_, red), score in zip(board_with_side, scores)]
        feed[model.label] = label
    return feed


def unfeed(scores, red):
    return [score if red else -score for score in scores]

