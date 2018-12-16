import rule
import random

MAX_QUEUE_LENGTH = 100


class BoardQueue:
    def __init__(self):
        self.queue = []


    def enqueue(self, board, red):
        if self.size() >= MAX_QUEUE_LENGTH:
            return
        if board not in [x for x, y in self.queue if y == red]:
            self.queue.append((board, red))


    def probable_enqueue(self, board, red, prob=0.1):
        m = 10000
        if random.randint(0, m) < m * prob:
            self.enqueue(board, red)


    def dequeue(self):
        if self.size() == 0:
            board = rule.initial_board()
            steps = rule.next_steps(board, True)
            move = random.sample(steps, 1)[0]
            board = rule.next_board(board, move)
            return board, False
        item = random.sample(self.queue, 1)[0]
        self.queue.remove(item)
        return item


    def size(self):
        return len(self.queue)
