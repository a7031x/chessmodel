import tensorflow as tf
import numpy as np
import random
from model import Model
from options import *
from feed import *
from chessdb import *
from time import time

def evaluate(sess, model, batch_board_red_score):
    feed = create_train_feed(model, batch_board_red_score)
    loss = sess.run(model.loss, feed)
    return loss


def train(sess, model, batch_board_red_score):
    feed = create_train_feed(model, batch_board_red_score)
    loss, _ = sess.run([model.loss, model.optimizer], feed)
    return loss


def run_epoch(taskname, sess, model, dataset, method):
    batch_size = 128
    total_loss = 0
    total = 0
    count = 0
    st = time()
    for cursor in range(0, len(dataset), batch_size):
        size = min(len(dataset) - cursor, batch_size)
        batch = dataset[cursor:(cursor+size)]
        loss = method(sess, model, batch)
        total_loss += loss
        count += 1
        total += size
        et = time()
        if et - st >= 5:
            print('  ', taskname, '{:.2f}%'.format(total / len(dataset) * 100), 'loss: {:.4f}'.format(np.sqrt(total_loss / total)))
            st = et
    print('finish', taskname, 'loss: {:.4f}'.format(np.sqrt(total_loss / total)))
    return total_loss / total


def run_train(sess, model, sv):
    iteration = 0
    dataset = list(read_database())
    dataset = [(board, red, score) for board, red, score in dataset if abs(score) <= 5000]
    random.seed(1)
    random.shuffle(dataset)
    training_size = int(0.98 * len(dataset))
    training_set = dataset[:training_size]
    validation_set = dataset[training_size:]
    print('training set:', training_size, 'validation set:', len(validation_set))
    while True:
        random.shuffle(training_set)
        run_epoch('validing', sess, model, validation_set, evaluate)
        run_epoch('training', sess, model, training_set, train)
        sv.saver.save(sess, FLAGS.output_dir, global_step=sv.global_step)


if __name__ == '__main__':
    initializer = tf.random_uniform_initializer(-0.05, 0.05)
    with tf.variable_scope('Model', reuse=None, initializer=initializer):
        model = Model()
    sv = tf.train.Supervisor(logdir=FLAGS.output_dir)
    with sv.managed_session() as sess:
        run_train(sess, model, sv)