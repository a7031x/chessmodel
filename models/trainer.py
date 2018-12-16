import torch.nn as nn
import rule
import numpy as np
from model import Model
from options import *
from board_queue import BoardQueue
from square_rule import *
import data
from tdleaf import *
from chessdb import *


def run_train(sess, model, sv):
    iteration = 0
    queue = BoardQueue()
    training_set = []
    while True:
        board, red = queue.dequeue()
        score = queryscore(board, red)
        if score is None:
            continue
        _, series = tdleaf(sess, model, board, red)
        for b, r in series:
            if not rule.gameover_position(b):
                queue.probable_enqueue(b, r)
        training_set.append((board, red, score))
        if len(training_set) >= 100:
            loss = train(sess, model, training_set)
            loss = np.sqrt(max(loss, 0))
            training_set = []
            print('depth: {}, loss: {:.4f}'.format(len(series), loss))
            sv.saver.save(sess, FLAGS.output_dir, global_step=sv.global_step)


if __name__ == '__main__':
    initializer = tf.random_uniform_initializer(-0.05, 0.05)
    with tf.variable_scope('Model', reuse=None, initializer=initializer):
        model = Model()
    sv = tf.train.Supervisor(logdir=FLAGS.output_dir)
    with sv.managed_session() as sess:
        run_train(sess, model, sv)