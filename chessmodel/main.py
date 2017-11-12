import numpy as np
import sys
import os
import tensorflow as tf
import console
from options import FLAGS
from model import Model
from feed import *
import random
import rule


class game:
    def __init__(self):
        self.board = rule.initial_board()
        self.red = True


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
                    is_red, board = parameter
                    valid_moves = evaluate(sess, model, board, is_red, 1)
                    print(valid_moves[0])
                elif command == 'train' or command == 'default':
                    iteration = 0
                    while True:
                        print('start iteration {}'.format(iteration))
                        board = rule.initial_board()
                        red = random.randint(0, 1) != 0
                        total_loss = 0
                        steps = 0
                        red_records = []
                        black_records = []
                        while True:
                            valid_moves = evaluate(sess, model, board, red)
                            best_move = random.sample(valid_moves[0:3], 1)[0]
                            if red:
                                red_records.append((board, best_move))
                            else:
                                black_records.append((board, best_move))
                            next_board = rule.next_board(board, best_move)
                            next_score = rule.basic_score(next_board)
                            red = not red
                            board = next_board
                            steps += 1
                            if abs(next_score) >= 50000 or steps >= 100:
                                break

                        if next_score >= 50000:
                            records = red_records
                            red = True
                        elif next_score <= -50000:
                            records = black_records
                            red = False
                        else:
                            iteration += 1
                            continue

                        feed = create_feed(model, [(x, red) for x, _ in records], [m for _, m in records])
                        _, loss = model.train(sess, feed)
                        steps = len(records)
                        loss /= steps
                        print('iteration: {}, loss: {:.2f}, steps: {}'.format(iteration, loss, steps))
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
