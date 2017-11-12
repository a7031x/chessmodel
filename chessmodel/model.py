import numpy as np
import tensorflow as tf
import inspect
import sys
import random
from options import FLAGS

EMBEDDING_SIZE = 128
HIDDEN_SIZE = 256
NUMBER_LAYERS = 2
FEATURE_SIZE = 64

class Model:
    def __init__(self):
        input = tf.placeholder(tf.int32, shape=[None, 90], name='input')
        label = tf.placeholder(tf.int32, shape=[None], name='label')
        output = self.calc_output(input)
        loss = self.calc_loss(output, label)
        optimizer = self.create_optimizer(loss)

        self.input = input
        self.label = label
        self.output = output
        self.loss = loss
        self.optimizer = optimizer


    def calc_output(self, input):
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
            hidden = tf.reshape(hidden, [-1, HIDDEN_SIZE * 90], 'feature')
            weight_feature = tf.get_variable('weight_feature', [HIDDEN_SIZE*90, FEATURE_SIZE], tf.float32)
            bias_feature = tf.get_variable('bias_feature', [FEATURE_SIZE], tf.float32)
            feature = tf.nn.sigmoid(tf.matmul(hidden, weight_feature) + bias_feature, name='feature')
            weight_output = tf.get_variable('weight_output', [FEATURE_SIZE, 90*90], tf.float32)
            bias_output = tf.get_variable('bias_output', [90*90], tf.float32)
            output = tf.matmul(feature, weight_output)
            return output


    def calc_loss(self, output, label):
        with tf.name_scope('loss'):
            loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=label, logits=output, name='loss')
            return tf.reduce_sum(loss)


    def create_optimizer(self, loss):
        with tf.name_scope('optimizer'):
            tvars = tf.trainable_variables()
            grads, _ = tf.clip_by_global_norm(tf.gradients(loss, tvars), 5)
            optimizer = tf.train.GradientDescentOptimizer(0.1)
            train_optimizer = optimizer.apply_gradients(zip(grads, tvars), global_step=tf.contrib.framework.get_or_create_global_step())
            return train_optimizer


    def train(self, sess, feed):
        output, loss, _ = sess.run([self.output, self.loss, self.optimizer], feed_dict=feed)
        return output, loss


    def evaluate(self, sess, feed):
        output = sess.run(self.output, feed_dict=feed)
        output = [np.argmax(x) for x in output]
        output = [(x%90, x//90) for x in output]
        return output


    def infer(self, sess, feed):
        output = sess.run(self.output, feed_dict=feed)
        return output

