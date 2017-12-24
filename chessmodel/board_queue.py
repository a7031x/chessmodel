import rule
import random

MAX_QUEUE_LENGTH = 100


class BoardQueue:
    def __init__(self):
        self.queue = [(rule.initial_board(), 1)]


    def enqueue(self, board, red):
        if self.size() >= MAX_QUEUE_LENGTH:
            return
        self.queue.append((board, red))


    def probable_enqueue(self, board, red, prob=0.05):
        m = 10000
        if random.randint(0, m) < m * prob:
            self.enqueue(board, red)


    def dequeue(self):
        if self.size() == 0:
            return rule.initial_board(), 1
        item = random.sample(self.queue, 1)[0]
        return item


    def size(self):
        return len(self.queue)
