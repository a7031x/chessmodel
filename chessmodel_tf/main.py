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
import ast
#import engine as ec
from search import SearchEngine
from board_queue import BoardQueue
from tdleaf import *
from trainer import train


def engine_command(cmd):
    return ast.literal_eval(ec.command(cmd))


def search(board, red, depth):
    moves, scores, boards = engine_command('search {} {} {}'.format(1 if red else 0, board.replace(' ', '#'), depth))
    boards = [b.replace('#', ' ') for b in boards]
    return moves, scores, boards


def main(_):
    initializer = tf.random_uniform_initializer(-0.05, 0.05)
    with tf.Graph().as_default():
        with tf.variable_scope('Model', reuse=None, initializer=initializer):
            model = Model()
        sv = tf.train.Supervisor(logdir=FLAGS.output_dir)
        with sv.managed_session() as sess:
            print("ready")
            se = SearchEngine(sess, model)
            while True:
                command, parameter = console.read()
                if command == 'get_moves':
                    red, board = parameter
                    moves = rule.next_steps(board, red)
                    print(moves)
                    #moves2 = ec.command(command + ' ' + str(1 if red else 0) + ' ' + board.replace(' ', '#'))
                    #print(moves2)
                elif command == 'evaluate':
                    red, board = parameter
                    basic_score = rule.basic_score(board)
                    if abs(basic_score) >= rule.GAMEOVER_THRESHOLD:
                        print(basic_score)
                    else:
                        feed = create_feed(model, [(board, red)], None)
                        score = model.evaluate(sess, feed)
                        score = unfeed(score, red)
                        print(score[0], search(board, red, 4)[1][0])
                elif command == 'advice':
                    red, board = parameter
                    moves, scores, _ = se.search(board, red, 1)#search(board, red, 5)
                    print(moves[0], scores[0])
                elif command == 'train' or command == 'default':
                    run_train(sess, model, sv)


if __name__ == "__main__":
    tf.app.run()
