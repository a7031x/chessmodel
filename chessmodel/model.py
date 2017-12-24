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
        self.create_input()
        self.create_score()


    def create_input(self):
        with tf.name_scope('input'):
            self.input_square = tf.placeholder(tf.int32, shape=[None, 90, None, 2], name='input_square')
            self.input_length = tf.placeholder(tf.int32, shape=[None, 90], name='input_length')
            self.input_score = tf.placeholder(tf.float32, shape=[None], name='input_score')


    def create_score(self):
        with tf.name_scope('score'):
            embedding = tf.get_variable('embedding', [14, 3, EMBEDDING_SIZE], tf.float32)
            zero = tf.zeros([1, 3, EMBEDDING_SIZE])
            combined_embedding = tf.concat([embedding, zero], axis=0)
            #embed = tf.gather_nd(combined_embedding, self.input_square)#[None, 90, EMBEDDING_SIZE]
            embed = tf.gather(combined_embedding, self.input_square)#[None, 90, None, EMBEDDING_SIZE]
            reduced_embed = tf.reduce_sum(embed, axis=2)#[None, 90, EMBEDDING_SIZE]
            flattened = tf.reshape(reduced_embed, [-1, 90 * EMBEDDING_SIZE])
            layer0 = self.transform(0, flattened, 512)
            layer1 = self.transform(1, layer0, 256)
            layer2 = self.transform(2, layer1, 128)
            output = self.transform(3, layer2, 64, 'tanh')#[None, 64]
            self.score = tf.reduce_sum(output, -1)#[None]


    def create_loss(self):
        with tf.name_scope('loss'):
            loss = tf.nn.l2_loss(self.score - self.input_score)
            loss = tf.reduce_sum(loss)
            self.loss = loss


    def create_optimizer(self):
        with tf.name_scope('optimizer'):
            tvars = tf.trainable_variables()
            grads, _ = tf.clip_by_global_norm(tf.gradients(self.loss, tvars), 5)
            optimizer = tf.train.AdamOptimizer(1)
            train_optimizer = optimizer.apply_gradients(zip(grads, tvars), global_step=tf.contrib.framework.get_or_create_global_step())
            self.optimizer = train_optimizer


    def transform(self, layerid, input, output_dim, activation='relu'):
        input_dim = input.shape[-1]
        weight = tf.get_variable('weight{}'.format(layerid), [input_dim, output_dim], tf.float32)
        bias = tf.get_variable('bias{}'.format(layerid), [output_dim], tf.float32)
        output = tf.matmul(input, weight) + bias
        if activation == 'relu':
            return tf.nn.relu(output)
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
