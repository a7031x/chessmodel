import rule
from square_rule import *

c2t = {
    'R': 0,
    'N': 1,
    'B': 2,
    'A': 3,
    'K': 4,
    'C': 5,
    'P': 6,
    'r': 7,
    'n': 8,
    'b': 9,
    'a': 10,
    'k': 11,
    'c': 12,
    'p': 13
}


def normalize_board(board, red):
    if red is False:
        board = [rule.flip_side(c) for c in board]
    pos = rule.find_chess(board, 'K')[0]
    if pos < 45:
        board = rule.rotate_board(board)
    return board


def normalized_square_map(board, red):
    board = normalize_board(board, red)
    return square_map(board)


def normalized_map_and_score(board, red):
    board = normalize_board(board, red)
    return square_map(board), rule.basic_score(board)


def create_feed_row(row, mlen):
    feed_row = []
    for chess, state in row:
        type = c2t[chess]
        feed_row.append((type, state))
    feed_row += [(14, 0)] * (mlen - len(row))
    return feed_row


def create_feed_from_map(maps):
    feed_lens = [[len(row) for row in m] for m in maps]
    mlen = max([max(x) for x in feed_lens])
    feed_maps = []
    for m in maps:
        feed_map = []
        for row in m:
            feed_row = create_feed_row(row, mlen)
            feed_map.append(feed_row)
        feed_maps.append(feed_map)
    feed = {
        'square': feed_maps,
        'length': feed_lens
    }
    return feed


def create_feed(batch_board_red):
    maps = []
    scores = []
    for board, red in batch_board_red:
        map, score = normalized_map_and_score(board, red)
        maps.append(map)
        scores.append(score)
    feed = create_feed_from_map(maps)
    feed['basic_score'] = scores
    return feed


def create_train_feed(batch_board_red_score):
    feed = create_feed([(board, red)
                        for board, red, _ in batch_board_red_score])
    feed['target'] = [score if red else -
                      score for _, red, score in batch_board_red_score]
    return feed


def unfeed(batch_score, batch_red):
    return [score if red else -score for score, red in zip(batch_score, batch_red)]
