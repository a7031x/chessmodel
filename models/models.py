import torch
import torch.nn as nn
import math
import func

EMBEDDING_SIZE = 16


class Model(nn.Module):
    def __init__(self):
        super(__class__, self).__init__()
        self.square_embedding = nn.Embedding(15 * 4, EMBEDDING_SIZE)
        self.layer0 = self.transform_layer(
            90 * EMBEDDING_SIZE * 2, 128, nn.ReLU)
        self.layer1 = self.transform_layer(128, 64, nn.Tanh)
        self.layer2 = self.transform_layer(128, 64, nn.ReLU)
        self.layer3 = self.transform_layer(64, 32, nn.Tanh)
        self.layer4 = self.transform_layer(32, 32, nn.ReLU)
        self.layer51 = self.transform_layer(32, 16, nn.ReLU)
        self.layer52 = self.transform_layer(64, 16, nn.Tanh)
        self.layer5 = self.transform_layer(32, 32, nn.ReLU)
        self.layer6 = self.transform_layer(32, 1, None)

    def forward(self, square, length):
        square = func.tensor(square)
        length = func.tensor(length)
        batch, sn, tp, _ = square.shape
        #emb = self.square_embedding(square[:, :, :, 0]).view(batch, sn, tp, 4, EMBEDDING_SIZE)
        #emb = torch.gather(emb, 3, square[:, :, :, ])
        idx = square[:, :, :, 0] * 4 + square[:, :, :, 1]
        emb = self.square_embedding(idx).view(batch, sn, tp, EMBEDDING_SIZE)
        reduced_sum = emb.sum(2)
        reduced_prod = (reduced_sum * reduced_sum - emb.mul(emb).sum(2)) / 2
        reduced_emb = torch.cat([reduced_sum, reduced_prod], dim=2)
        flattened = reduced_emb.view(-1, 90 * EMBEDDING_SIZE * 2)
        layer0 = self.layer0(flattened)
        layer1 = self.layer1(layer0)
        layer2 = self.layer2(torch.cat([layer1, layer1 * layer1], dim=-1))
        layer3 = self.layer3(layer2)
        layer4 = self.layer4(layer3)
        layer51 = self.layer51(layer4)
        layer52 = self.layer52(layer2)
        layer5 = self.layer5(torch.cat([layer51, layer52], dim=-1))
        layer6 = self.layer6(layer5)
        score = layer6.squeeze(-1)
        return score

    def transform_layer(self, input_dim, output_dim, activation):
        linear = nn.Linear(input_dim, output_dim)
        if activation is not None:
            return nn.Sequential(linear, activation())
        else:
            return linear


class Loss(nn.Module):
    def __init__(self):
        super(__class__, self).__init__()
        self.criterion = nn.BCEWithLogitsLoss(reduction='sum')

    def forward(self, score, target):
        return self.criterion(score, func.tensor(target).float())


def build_model():
    return func.cuda(Model())


def build_loss():
    return func.cuda(Loss())
