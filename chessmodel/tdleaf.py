import rule
from trainer import *

def tdleaf(sess, model, initial_board, red, lamb=0.7, depth=12):
    initial_score = evaluate(sess, model, initial_board, red)
    series = []
    k = 0
    while pv_position(initial_board, red) or k < depth:
        boards = next_boards(initial_board, red)
        scores = batch_evaluate(sess, model, boards, not red)
        initial_board, score = optimal_board(boards, scores, red)
        red = not red
        series.append((initial_board, red, score))
        if abs(score) >= rule.GAMEOVER_THRESHOLD:
            break
        k += 1

    series = series[-depth:]
    weight = 1
    total_score = 0
    for _, _, score in series:
        total_score += score * weight
        weight *= lamb
    return total_score, [(board, red) for board, red, _ in series]
    

def next_boards(board, red):
    moves = rule.next_steps(board, red)
    return [rule.next_board(board, move) for move in moves]


def evaluate(sess, model, board, red):
    return batch_evaluate(sess, model, [board], red)


def batch_evaluate(sess, model, boards, red):
    for board in boards:
        score = rule.basic_score(board)
        if abs(score) > rule.GAMEOVER_THRESHOLD:
            return score if red else -score
    batch_board_red = [(board, red) for board in boards]
    scores = predict(sess, model, batch_board_red)
    return scores


def optimal_board(boards, scores, red):
    combined = list(zip(scores, boards))
    score, board = sorted(combined, reverse=not red)[0]
    return board, score


def pv_position(initial_board, red):
    return False