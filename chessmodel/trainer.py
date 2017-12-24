import rule
import tensorflow as tf
import rule
import numpy as np
from model import Model
from options import *
from board_queue import BoardQueue
from square_rule import *
from feed import *
from tdleaf import *

def predict(sess, model, batch_board_red):
    feed = create_feed(model, batch_board_red)
    scores = sess.run(model.score, feed)
    return unfeed(scores, [red for _, red in batch_board_red])


def train(sess, model, batch_board_red_score):
    feed = create_train_feed(model, batch_board_red_score)
    score, loss, _ = sess.run([model.score, model.loss, model.optimizer], feed)
#    print('score: ', unfeed(score, [red for _, red, _ in batch_board_red_score]))
#    print('label: ', [x for _, _, x in batch_board_red_score])
    return loss


def run_train(sess, model):
    iteration = 0
    queue = BoardQueue()
    training_set = []
    while True:
        board, red = queue.dequeue()
        steps = 0
        score, series = tdleaf(sess, model, board, red)
        for b, r in series:
            if not rule.gameover_position(b):
                queue.probable_enqueue(b, r)
        training_set.append((board, red, score))
        if len(training_set) >= 10:
            loss = train(sess, model, training_set)
            loss = np.sqrt(max(loss, 0))
            training_set = []
            print('depth: {}, loss: {}'.format(len(series), loss))


if __name__ == '__main__':
    initializer = tf.random_uniform_initializer(-0.05, 0.05)
    with tf.variable_scope('Model', reuse=None, initializer=initializer):
        model = Model()
    sv = tf.train.Supervisor(logdir=FLAGS.output_dir)
    with sv.managed_session() as sess:
        run_train(sess, model)