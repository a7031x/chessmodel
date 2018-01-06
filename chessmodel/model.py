import numpy as np
import tensorflow as tf
import inspect
import sys
import random
from options import FLAGS

#https://www.youtube.com/embed/bJfqn4Ysvsk

EMBEDDING_SIZE = 256
HIDDEN_SIZE = 256

class Model:
    def __init__(self):
        self.create_input()
        self.create_score()
        self.create_loss()
        self.create_optimizer()


    def create_input(self):
        with tf.name_scope('input'):
            self.input_square = tf.placeholder(tf.int32, shape=[None, 90, None, 2], name='input_square')
            self.input_length = tf.placeholder(tf.int32, shape=[None, 90], name='input_length')
            self.input_score = tf.placeholder(tf.float32, shape=[None], name='input_score')


    def create_score(self):
        with tf.name_scope('score'):
            embedding = tf.get_variable('embedding', [14, 4, EMBEDDING_SIZE], tf.float32)
            zero = tf.zeros([1, 4, EMBEDDING_SIZE])
            combined_embedding = tf.concat([embedding, zero], axis=0)
            #embed = tf.gather_nd(combined_embedding, self.input_square)#[None, 90, EMBEDDING_SIZE]
            embed = tf.gather_nd(combined_embedding, self.input_square)#[None, 90, None, EMBEDDING_SIZE]
            reduced_embed = tf.reduce_prod(embed, axis=2)#[None, 90, EMBEDDING_SIZE]
            flattened = tf.reshape(reduced_embed, [-1, 90 * EMBEDDING_SIZE])
            layer0 = self.transform(0, flattened, 512, 'relu')
            layer1 = self.transform(1, layer0, 256, 'relu')
            layer2 = self.transform(2, layer1, 128, 'relu')
            layer3 = self.transform(3, layer2, 64, None)#[None, 64]
            feature = self.transform(4, layer3, 32, None)#[None, 64]
           # feature = self.transform(0, flattened, 512, None)
            self.score = tf.reduce_sum(feature, -1)#[None]


    def create_loss(self):
        with tf.name_scope('loss'):
            loss = tf.nn.l2_loss(self.score - self.input_score) * 2 / tf.cast(tf.shape(self.input_square)[0], tf.float32)
            self.loss = loss


    def create_optimizer(self):
        with tf.name_scope('optimizer'):
            tvars = tf.trainable_variables()
            grads, _ = tf.clip_by_global_norm(tf.gradients(self.loss, tvars), 5)
            optimizer = tf.train.AdamOptimizer(0.01)
            train_optimizer = optimizer.apply_gradients(zip(grads, tvars), global_step=tf.train.get_or_create_global_step())
            self.optimizer = train_optimizer


    def transform(self, layerid, input, output_dim, activation):
        input_dim = input.shape[-1]
        weight = tf.get_variable('weight{}'.format(layerid), [input_dim, output_dim], tf.float32)
        bias = tf.get_variable('bias{}'.format(layerid), [output_dim], tf.float32)
        output = tf.matmul(input, weight) + bias
        if activation == 'relu':
            return tf.nn.relu(output)
        elif activation == 'sigmoid':
            return tf.nn.sigmoid(output)
        elif activation == 'tanh':
            return tf.nn.tanh(output)
        else:
            return output


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
