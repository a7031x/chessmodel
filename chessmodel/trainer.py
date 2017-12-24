import rule
from square_rule import *
from feed import *

def predict(sess, model, batch_board_red):
    feed = create_feed(model, batch_board_red)
    scores = sess.run(model.score, feed)
    return unfeed(scores, [red for _, red in batch_board_red])


def train(sess, model, batch_board_red_score):
    feed = create_train_feed(model, batch_board_red_score)
    loss, _ = sess.run([model.loss, model.optimizer], feed)
    return loss / len(batch_board_red_score)
