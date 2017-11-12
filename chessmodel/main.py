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
import math
from datetime import datetime
from search import SearchEngine
from engine import example


def main(_):
    initializer = tf.random_uniform_initializer(-0.05, 0.05)
    engine = SearchEngine(FLAGS.output_dir)
    with tf.Graph().as_default():
        with tf.variable_scope('Model', reuse=None, initializer=initializer):
            model = Model()
        sv = tf.train.Supervisor(logdir=FLAGS.output_dir)
        with sv.managed_session() as sess:
            print("ready")
            while True:
                command, parameter = console.read()
                if command == 'get_moves':
                    red, board = parameter
                    moves = rule.next_steps(board, red)
                    print(moves)
                elif command == 'evaluate':
                    red, board = parameter
                    basic_score = rule.basic_score(board)
                    if abs(basic_score) >= rule.GAMEOVER_THRESHOLD:
                        print(basic_score)
                    else:
                        feed = create_feed(model, [(board, red)], None)
                        score = model.evaluate(sess, feed)
                        score = unfeed(score, red)
                        print(score[0], SearchEngine().search(board, red, 4)[1][0])
                elif command == 'train' or command == 'default':
                    iteration = 0
                    while True:
                        board = rule.initial_board()
                        red = random.randint(0, 1) != 0
                        steps = 0
                        record_boards = []
                        record_scores = []
                        record_sides = []
                        start_time = datetime.utcnow()
                        while True:
                            perf = engine.performance_counter
                            _, scores, boards = engine.search(board, red, 3)
                            score = scores[0]
                            record_boards.append(board)
                            record_scores.append(score)
                            record_sides.append(red)
                            steps += 1
                            if abs(score) >= rule.GAMEOVER_THRESHOLD or steps >= 200:
                                break
                            if steps % 20 == 0:
                                print('step {}, score {}, hash: {}/{}'.format(steps, score, perf.hash_hit, perf.hash_size))
                            board = random.sample(boards[0:(3 if steps > 1 else len(boards))], 1)[0]
                            red = not red
                        end_time = datetime.utcnow()
                        feed = create_feed(model, [(board, red) for board, red in zip(record_boards, record_sides)], record_scores)
                        _, total_loss = model.train(sess, feed)
                        loss = math.sqrt(total_loss / steps)
                        duration = end_time - start_time
                        print('iteration: {}, elapsed: {}, steps: {}, score: {}, loss: {:.2f}'
                              .format(iteration, duration.seconds, steps, record_scores[-1], loss))
                        iteration += 1
                        sv.saver.save(sess, FLAGS.output_dir, global_step=sv.global_step)
                        engine.save()


if __name__ == "__main__":
    tf.app.run()
