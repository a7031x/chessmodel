import torch
import torch.nn as nn
import numpy as np
import random
import models
import func
import data
import chessdb
from time import time

__loss = models.build_loss()


def evaluate(model, batch_board_red_score, _):
    feed = data.create_train_feed(model, batch_board_red_score)
    score = model(feed['square'], feed['length'], feed['basic_score'])
    loss = __loss(score, feed['target'])
    return loss.tolist()


def train(model, batch_board_red_score, optimizer):
    feed = data.create_train_feed(model, batch_board_red_score)
    score = model(feed['square'], feed['length'], feed['basic_score'])
    loss = __loss(score, feed['target'])
    optimizer.zero_grad()
    loss.backward()
    nn.utils.clip_grad_norm_(model.parameters(), 5.0)
    optimizer.step()
    return loss.tolist()


def run_epoch(taskname, model, dataset, method):
    batch_size = 128
    total_loss = 0
    total = 0
    count = 0
    st = time()
    optimizer = torch.optim.Adam(model.parameters(), lr=1E-3)
    num_records = len(dataset)
    for cursor in range(0, num_records, batch_size):
        size = min(len(dataset) - cursor, batch_size)
        batch = dataset[cursor:(cursor+size)]
        loss = method(model, batch, optimizer)
        total_loss += loss
        count += 1
        total += size
        et = time()
        if et - st >= 20:
            print(f'{cursor/num_records*100:>.2F} loss: {loss/size:>.4F}')
            st = et
    print('finish', taskname, 'loss: {:.4f}'.format(
        np.sqrt(total_loss / total)))
    return total_loss / total


def flip(board):
    r = ''
    for y in range(10):
        for x in range(9):
            r += board[y * 9 + (8 - x)]
    return r


def enrich(dataset):
    boards = set()
    r = []
    for board, red, score in dataset:
        if board not in boards:
            boards.add(board)
            r.append((board, red, score))
        board = flip(board)
        if board not in boards:
            boards.add(board)
            r.append((board, red, score))
    return r


def run_train():
    model = models.build_model()
    dataset = list(chessdb.read_database())
    dataset = [(board, red, score)
               for board, red, score in dataset if abs(score) <= 5000]
    random.seed(1)
    random.shuffle(dataset)
    training_size = int(0.98 * len(dataset))
    training_set = dataset[:training_size]
    training_set = enrich(training_set)
    random.shuffle(training_set)
    validation_set = dataset[training_size:]
    print('training set:', len(training_set),
          'validation set:', len(validation_set))
    last_error = run_epoch('validing', model, validation_set, evaluate)
    while True:
        random.shuffle(training_set)
        run_epoch('training', model, training_set, train)
        error = run_epoch('validing', model, validation_set, evaluate)
        if error < last_error:
            func.save_model(model, './model.ckpt')


if __name__ == '__main__':
    run_train()
