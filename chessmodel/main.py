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
                    basic_score = rule.basic_score(board)
                    if abs(basic_score) >= 50000:
                        print(basic_score)
                    else:
                        feed = create_feed(model, [(board, is_red)], None)
                        score = model.evaluate(sess, feed)
                        score = unfeed(score, is_red)
                        print(score[0])
                elif command == 'train' or command == 'default':
                    iteration = 0
                    while True:
                        board = rule.initial_board()
                        red = random.randint(0, 1) != 0
                        total_loss = 0
                        steps = 0
                        while True:
                            moves = rule.next_steps(board, red)
                            next_boards = [rule.next_board(board, move) for move in moves]
                            next_scores = [rule.basic_score(b) for b in next_boards]
                            game_over = any([abs(x) >= 50000 for x in next_scores])
                            if game_over is False and random.randint(0, 100) <= 90:
                                feed = create_feed(model, [(b, not red) for b in next_boards], None)
                                next_scores = model.evaluate(sess, feed)
                                next_scores = unfeed(next_scores, not red)
                            t3 = sorted(zip(next_scores, next_boards))
                            if red:
                                t3 = t3[::-1]
                            score, next_board = t3[0]
                            feed = create_feed(model, [(board, red)], [score])
                            score, loss = model.train(sess, feed)
                            score = unfeed(score, red)
                            total_loss += loss ** 0.5
                            steps += 1
                            if game_over or steps >= 100:
                                break
                            _, board = random.sample(t3[0:3], 1)[0]
                            red = not red
                        print('iteration: {}, loss: {:.2f}, steps: {}'.format(iteration, total_loss / steps, steps))
                        iteration += 1
                        sv.saver.save(sess, FLAGS.output_dir, global_step=sv.global_step)


if __name__ == "__main__":
    tf.app.run()
