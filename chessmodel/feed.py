import rule
from square_rule import *

c2t = {
    'R': 0,
    'H': 1,
    'E': 2,
    'B': 3,
    'K': 4,
    'C': 5,
    'P': 6,
    'r': 7,
    'h': 8,
    'e': 9,
    'b': 10,
    'k': 11,
    'c': 12,
    'p': 13
}


def normalized_square_map(board, red):
    if red is False:
        board = [rule.flip_side(c) for c in board]
    pos = rule.find_chess(board, 'K')[0]
    if pos < 45:
        board = rule.rotate_board(board)
    return square_map(board)


def create_feed_row(row, mlen):
    feed_row = []
    for chess, state in row:
        type = c2t[chess]
        feed_row.append((type, state))
    feed_row += [(14, 0)] * (mlen - len(row))
    return feed_row


def create_feed_from_map(model, maps):
    feed_lens = [[len(row) for row in map] for map in maps]
    mlen = max([max(x) for x in lens])
    feed_maps = []
    for map in maps:
        feed_map = []
        for row in map:
            feed_row = create_feed_row(row, mlen)
            feed_map.append(feed_row)
        feed_maps.append(feed_map)
    feed = {
        model.input_square: feed_maps,
        model.input_length: feed_lens
    }
    return feed


def create_feed(model, batch_board_red):
    maps = []
    for board, red in batch_board_red:
        map = normalized_square_map(board, red)
        maps.append(map)
    feed = create_feed_from_map(model, maps)
    return feed


def create_train_feed(model, batch_board_red_score):
    feed = create_feed(model, [(board, red) for board, red, _ in batch_board_red_score])
    feed[model.input_score] = [score for _, _, score in batch_board_red_score]
    return feed


def unfeed(batch_score, batch_red):
    return [score if red else -score for score in batch_score]

'''
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
        board = [rule.score_map[c] for c in board]
        input.append(board)

    feed = {
        model.input: input
    }
    if scores is not None:
        label = [score if red else -score for (_, red), score in zip(board_with_side, scores)]
        feed[model.label] = label
    return feed


def unfeed(scores, red):
    return [score if red else -score for score in scores]
'''