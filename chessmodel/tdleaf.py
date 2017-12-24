import rule

def tdleaf(sess, initial_board, red, lamb=0.7, depth=12):
    initial_score = evaluate(sess, initial_board, red)
    #series = [(initial_board, red, initial_score)]
    series = []
    k = 0
    while pv_position(initial_board, red) or k < depth:
        boards = next_boards(initial_board, red)
        scores = batch_evaluate(sess, boards, not red)
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
    

def pv_position(initial_board, red):
    return False