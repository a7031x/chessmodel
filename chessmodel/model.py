import numpy as np
import tensorflow as tf
import inspect
import sys
import random
from options import FLAGS

EMBEDDING_SIZE = 128
HIDDEN_SIZE = 256
NUMBER_LAYERS = 2

class Model:
    def __init__(self):
        input = tf.placeholder(tf.int32, shape=[None, 90], name='input')
        label = tf.placeholder(tf.float32, shape=[None], name='label')
        score = self.calc_score(input)
        loss = self.calc_loss(score, label)
        optimizer = self.create_optimizer(loss)

        self.input = input
        self.label = label
        self.score = score
        self.loss = loss
        self.optimizer = optimizer


    def calc_score(self, input):
        with tf.name_scope('score'):
            #hidden = tf.reshape(input, [-1, 90 * EMBEDDING_SIZE])
            embeddings = tf.get_variable('embedding', [8, EMBEDDING_SIZE], tf.float32)
            hidden = tf.map_fn(
                lambda x: tf.cond(
                    tf.greater_equal(x, 0),
                    lambda: tf.nn.embedding_lookup(embeddings, x),
                    lambda: tf.nn.embedding_lookup(embeddings, -x)),
                tf.reshape(input, [-1]),
                dtype=tf.float32)
            hidden = tf.reshape(hidden, [-1, EMBEDDING_SIZE])
            for layer in range(NUMBER_LAYERS):
                weight = tf.get_variable(
                    'weight_{}'.format(layer),
                    [EMBEDDING_SIZE if 0 == layer else HIDDEN_SIZE, HIDDEN_SIZE],
                    dtype=tf.float32)
                bias = tf.get_variable('bias_{}'.format(layer), [HIDDEN_SIZE], dtype=tf.float32)
                hidden = tf.matmul(hidden, weight) + bias
                hidden = tf.tanh(hidden, 'hidden_{}'.format(layer))
            feature = tf.reshape(hidden, [-1, HIDDEN_SIZE * 90], 'feature')
            weight_output = tf.get_variable('weight_output', [HIDDEN_SIZE * 90, 1], tf.float32)
            score = tf.matmul(feature, weight_output)
            score = tf.reshape(score, [-1], 'score')
            return score


    def calc_loss(self, score, label):
        with tf.name_scope('loss'):
            loss = tf.losses.mean_squared_error(label, score)
            return loss
          #  return tf.reduce_sum(loss)


    def create_optimizer(self, loss):
        with tf.name_scope('optimizer'):
            tvars = tf.trainable_variables()
            grads, _ = tf.clip_by_global_norm(tf.gradients(loss, tvars), 5)
            optimizer = tf.train.AdamOptimizer(0.001)
            train_optimizer = optimizer.apply_gradients(zip(grads, tvars), global_step=tf.contrib.framework.get_or_create_global_step())
            return train_optimizer


    def train(self, sess, feed):
        score, loss, _ = sess.run([self.score, self.loss, self.optimizer], feed_dict=feed)
        return score, loss


    def evaluate(self, sess, feed):
        score = sess.run(self.score, feed_dict=feed)
        return score


    def infer(self, sess, feed):
        output = sess.run(self.output, feed_dict=feed)
        output = output[0]
        return output

