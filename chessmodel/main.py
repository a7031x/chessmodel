import numpy as np
import sys
import os
import tensorflow as tf
import console
from options import FLAGS
from model import Model
from feed import *
from datetime import datetime
import random
import rule


BATCH_SIZE = 128

class game:
    def __init__(self):
        self.board = rule.initial_board()
        self.red = True
        self.steps = 0
        self.red_records = []
        self.black_records = []
        self.score = 0
        self.steps = 0


    def next_moves(self):
        steps = rule.next_steps(self.board, self.red)
        steps = sorted(steps, key=lambda x: abs(rule.score_map[self.board[x[1]]]), reverse=True)
        temp = steps[:5]
        random.shuffle(temp)
        steps = temp + steps[5:]
        for f, t in temp:
            if self.board[t] in ['K', 'k']:
                r = [(f, t)]
                steps.remove((f, t))
                r += steps
                return r
        return steps


    def valid_moves(self, output, total_moves=10):
        output = sorted(range(len(output)), key=lambda i: output[i], reverse=True)
        output = [(i%90, i//90) for i in output]
        output = [(f if self.red else 89 - f, t if self.red else 89 - t) for f, t in output]
        moves = self.next_moves()
        r = []
        for move in output:
            if move in moves:
                r.append(move)
                if len(r) >= total_moves:
                    break
        return r


    def game_over(self):
        return abs(self.score) >= 50000


    def move(self, best_move):
        if self.game_over():
            print('game is over!')
            sys.exit()
        self.steps += 1
        if self.red:
            self.red_records.append((self.board, best_move))
        else:
            self.black_records.append((self.board, best_move))
        self.board = rule.next_board(self.board, best_move)
        self.red = not self.red
        self.score = rule.basic_score(self.board)


    def win_records(self):
        if self.score >= 50000:
            return self.red_records
        elif self.score <= -50000:
            return self.black_records
        else:
            return None


    def win_color(self):
        if self.score >= 50000:
            return 'red'
        elif self.score <= -50000:
            return 'black'
        else:
            return None

def main(_):
    initializer = tf.random_uniform_initializer(-0.05, 0.05)
    with tf.Graph().as_default():
        with tf.variable_scope('Model', reuse=None, initializer=initializer):
            model = Model()
        sv = tf.train.Supervisor(logdir=FLAGS.output_dir)
        with sv.managed_session() as sess:
            print("ready")
            while True:
                command, parameter = console.read()
                if command == 'get_moves':
                    is_red, board = parameter
                    moves = rule.next_steps(board, is_red)
                    print(moves)
                elif command == 'evaluate':
                    red, board = parameter
                    valid_moves = evaluate(sess, model, board, red, 1)
                    print(valid_moves[0])
                elif command == 'train' or command == 'default':
                    iteration = 0
                    total_complete = 0
                    start_time = datetime.utcnow()
                    while True:
                        print('start iteration {}'.format(iteration))
                        games = [game() for _ in range(BATCH_SIZE)]
                        complete = []
                        steps = 0
                        while 0 != len(games):
                            feed = create_feed(model, [(g.board, g.red) for g in games], None)
                            #output = model.infer(sess, feed)
                            #valid_moves = [g.valid_moves(o) for g, o in zip(games, output)]
                            valid_moves = [g.next_moves() for g in games]
                            best_moves = [vm[0] for vm in valid_moves]
                            [g.move(m) for g, m in zip(games, best_moves)]
                            complete += [g for g in games if g.game_over()]
                            games = [g for g in games if not g.game_over() and g.steps < 30]
                            steps += 1
                            print('step: {} complete: {} games: {}'.format(steps, len(complete), len(games)))

                        if len(complete) == 0:
                            iteration += 1
                            continue
                        print('{} games complete'.format(len(complete)))
                        total_loss = 0
                        counter = 0
                        inputs = []
                        labels = []
                        for g in complete:
                            inputs += [(x, g.win_color() == 'red') for x, _ in g.win_records()]
                            labels += [m for _, m in g.win_records()]

                        for index in range(0, len(inputs), BATCH_SIZE):
                            batch_size = min(BATCH_SIZE, len(inputs) - index)
                            feed = create_feed(
                                model,
                                inputs[index:index+batch_size],
                                labels[index:index+batch_size])
                            _, loss = model.train(sess, feed)
                            total_loss += loss
                            counter += batch_size
                            print('{}/{}, loss: {:.2f}'.format(counter, len(inputs), loss / batch_size))

                        total_complete += len(complete)
                        duration = datetime.utcnow() - start_time
                        
                        print('iteration: {}, loss: {:.2f}, total: {}, rate: {}'
                              .format(iteration, total_loss / counter, total_complete, duration.seconds / total_complete))
                        sv.saver.save(sess, FLAGS.output_dir, global_step=sv.global_step)
                        iteration += 1


def evaluate(sess, model, board, red, total_moves=5):
    moves = rule.next_steps(board, red)
    feed = create_feed(model, [(board, red)], None)
    output = model.infer(sess, feed)[0]
    output = sorted(range(len(output)), key=lambda i: output[i], reverse=True)
    output = [(i%90, i//90) for i in output]
    output = [(f if red else 89 - f, t if red else 89 - t) for f, t in output]
    valid_moves = []
    for move in output:
        if move in moves:
            valid_moves.append(move)
            if len(valid_moves) >= total_moves:
                break

    return valid_moves


if __name__ == "__main__":
    tf.app.run()
