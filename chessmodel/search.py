import rule
import random
import os
import pickle
#import engine as ec
from feed import create_feed, unfeed
import ast

class PerformanceCounter:
    def __init__(self):
        self.hash_hit = 0


class SearchEngine:
    def __init__(self, sess, model, folder=None):
        self.folder = folder
        self.load()
        self.sess = sess
        self.model = model


    def save(self):
        if self.folder is not None:
            path = os.path.join(self.folder, 'hash.sav')
            with open(path, 'wb') as file:
                pickle.dump(self.hash, file)
                pickle.dump(self.hash_table, file)
                pickle.dump(self.performance_counter, file)


    def load(self):
        if self.folder is not None:
            path = os.path.join(self.folder, 'hash.sav')
            if os.path.isfile(path):
                with open(path, 'rb') as file:
                    self.hash = pickle.load(file)
                    self.hash_table = pickle.load(file)
                    self.performance_counter = pickle.load(file)
                    return

        self.hash = {}
        self.hash_table = [self.generate_hash_board() for _ in range(90)]
        self.performance_counter = PerformanceCounter()


    def predict(self, batch_board_red):
        feed = create_feed(self.model, batch_board_red)
        scores = self.sess.run(self.model.score, feed)
        scores = unfeed(scores, [red for _, red in batch_board_red])
        return scores


    def generate_hash_board(self):
        board = {}
        for k in rule.score_map:
            board[k] = random.randint(0, 0x7FFFFFFFFFFFFFFF) if ' ' != k else 0
        return board


    def compute_hash(self, board, red):
        hash = 0 if red else 0xFFFFFFFFFFFFFFFF
        for i in range(90):
            table = self.hash_table[i]
            hash ^= table[board[i]]
        return hash


    def find_hash(self, key):
        return None, None, None


    def save_hash(self, key, depth, score, move):
        self.hash[key] = depth, score, move
        self.performance_counter.hash_size = len(self.hash)


    def search(self, board, red, depth):
        self.depth = depth
        self.moves = []
        self.scores = []
        self.boards = []
        self.deep_search(board, depth, red, (-rule.GAMEOVER_THRESHOLD*3, rule.GAMEOVER_THRESHOLD*3))
        idx = [i for _, i in sorted(zip(self.scores, range(len(self.scores))), key=lambda x: -x[0] if red else x[0])]
        assert(len(self.scores) > 0)
        return [self.moves[i] for i in idx], [self.scores[i] for i in idx], [self.boards[i] for i in idx]


    def fill_moves(self, board, m, s, red):
        if len(self.moves) > 0:
            return
        assert(m is not None)
        moves = rule.next_steps(board, red)
        assert(len(moves) > 0)
        moves.remove(m)
        self.moves = [m] + moves
        self.boards = [rule.next_board(board, move) for move in self.moves]
        self.scores = [s] + [rule.basic_score(b) for b in self.boards[1:]]
        assert(len(self.scores) > 0)


    def deep_search(self, board, depth, red, window):
        key = self.compute_hash(board, red)
        d, s, m = self.find_hash(key)
        if d is not None and d >= depth:
            if depth == self.depth:
                self.fill_moves(board, m, s, red)
            self.performance_counter.hash_hit += 1
            return s

        moves = rule.next_steps(board, red)
        next_boards = [rule.next_board(board, move) for move in moves]
        next_scores = [rule.basic_score(b) for b in next_boards]
        gameover_state = any([abs(x) >= rule.GAMEOVER_THRESHOLD for x in next_scores])
        if not gameover_state and depth == 1:
            next_scores = self.predict([(b, not red) for b in next_boards])
        if depth == 1 or gameover_state:
            best_move, best_score = max(zip(moves, next_scores), key=lambda ms: (ms[1] if red else -ms[1]))
            if depth == self.depth:
                self.fill_moves(board, best_move, best_score, red)
            self.save_hash(key, depth, best_score, best_move)
            return best_score
        idx = range(len(moves))
        idx = sorted(idx, key=lambda i: -next_scores[i] if red else next_scores[i])
        best_score = -rule.GAMEOVER_THRESHOLD*3 if red else rule.GAMEOVER_THRESHOLD*3
        best_move = None
        lb = window[0]
        ub = window[1]
        for index in idx:
            move = moves[index]
            board = next_boards[index]
            next_score = self.deep_search(board, depth-1, not red, window)
            if (red and next_score > best_score) or (not red and next_score < best_score):
                best_score = next_score
                best_move = move
            if red:
                if next_score >= ub:
                    break
                elif lb < next_score:
                    lb = next_score
            else:
                if next_score <= lb:
                    break
                elif ub > next_score:
                    ub = next_score
            window = (lb, ub)
            if depth == self.depth:
                self.moves.append(move)
                self.scores.append(next_score)
                self.boards.append(board)
        assert(best_move is not None)
        if depth == self.depth:
            assert(len(self.scores) > 0)
        self.save_hash(key, depth, best_score, best_move)
        return best_score


if __name__ == "__main__":
    engine = SearchEngine()
    board = '###aka################b######p#p#c#p######################c######R#B###B####A#####r##KA###'
#    board = '#he#kbehr####b#############p#p#pCp#p###P#####P############cc##P#####C####r#######RHEBKBEHR'
#    board = 'rhebkbehr##################p#p#p#p#p#########P#c##########P#P#P##C####C#Rc#########EBKBEHR'
    red = True
    depth = 3
    moves, scores, boards = engine.search(board.replace('#', ' '), red, depth)
    res = ec.command('search {} {} {}'.format(1 if red else 0, board, depth))
    moves2, scores2, boards2 = ast.literal_eval(res)
    assert(scores == scores2)
