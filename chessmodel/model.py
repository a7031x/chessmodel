import numpy as np
import tensorflow as tf
import inspect
import sys
import random
from options import FLAGS

#https://www.youtube.com/embed/bJfqn4Ysvsk

EMBEDDING_SIZE = 128
HIDDEN_SIZE = 256
NUMBER_LAYERS = 2

class Model:
    def __init__(self):
        input = tf.placeholder(tf.float32, shape=[None, 90], name='input')
        label = tf.placeholder(tf.float32, shape=[None], name='label')
        score = self.calc_score(input)
        loss = self.calc_loss(score, label)
        optimizer = self.create_optimizer(loss)

        self.input = input
        self.label = label
        self.score = score
        self.loss = loss
        self.optimizer = optimizer


    def conv_layer(self, input, weight, bias, name):
        conv = tf.nn.conv2d(input, weight, [1, 1, 1, 1], 'VALID')
        r = tf.nn.bias_add(conv, bias)
        r = tf.nn.relu(r)
        tf.identity(r, name)
        return r


    def calc_score(self, input):
        with tf.name_scope('score'):
            board = tf.reshape(input, [-1, 9, 10, 1], 'board')
            w_conv1 = tf.get_variable('w_conv1', [7, 8, 1, 32], tf.float32)
            b_conv1 = tf.get_variable('b_conv1', [32], tf.float32)
            output = self.conv_layer(board, w_conv1, b_conv1, 'conv1')

            w_conv2 = tf.get_variable('w_conv2', [2, 2, 32, 64], tf.float32)
            b_conv2 = tf.get_variable('b_conv2', [64], tf.float32)
            output = self.conv_layer(output, w_conv2, b_conv2, name='conv2')

            output = tf.reshape(output, [-1, 2*2*64])

            w_feature = tf.get_variable('w_feature', [2*2*64, 1024], tf.float32)
            b_feature = tf.get_variable('b_feature', [1024], tf.float32)
            output = tf.matmul(output, w_feature) + b_feature
            feature = tf.identity(output, 'feature')
       #     feature = tf.nn.dropout(feature, 0.5)

            w_out = tf.get_variable('w_out', [1024, 1], tf.float32)
            b_out = tf.get_variable('b_out', [1], tf.float32)
            out = tf.matmul(feature, w_out) + b_out

            score = tf.reshape(out, [-1], 'score')
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


if __name__ == "__main__":
    Model()
