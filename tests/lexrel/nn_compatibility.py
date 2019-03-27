"""Ideal words - extraction and aggregation functions

Usage:
  compatibility.py [--att] [--rel] [--ppmi]
  compatibility.py (-h | --help)
  compatibility.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Process attributes.
  --rel         Process relations.
  --ppmi        Uses PPMI version of predicate matrix.

"""

import sys
sys.path.append('../../utils/')
import itertools
from docopt import docopt
from scipy.stats import spearmanr
from utils import read_probabilistic_matrix, read_nearest_neighbours, read_cosines
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as td
import numpy as np
from random import shuffle
from math import sqrt
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold

basedir = "syn"

if __name__ == '__main__':
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"]:
        basedir = "synatt"
    if not args["--att"] and args["--rel"]:
        basedir = "synrel"
    if args["--att"] and args["--rel"]:
        basedir = "synattrel"


class MLP(nn.Module):
    def __init__(self,d1,d2):
        super(MLP, self).__init__()
        self.fc11 = nn.Linear(d1,100)
        self.fc12 = nn.Linear(d1,100)
        self.fc2 = nn.Linear(200,d2)
        #self.drop1 = nn.Dropout(p=0.5)
    def forward(self, x):
        x11 = F.sigmoid(self.fc11(x[0]))
        x12 = F.sigmoid(self.fc12(x[1]))
        x2 = self.fc2(torch.cat((x11,x12),1))
        return x2

def make_input(data,vocab,pm):
    cdm1 = np.zeros((len(data),pm.shape[1]))
    cdm2 = np.zeros((len(data),pm.shape[1]))
    outm = np.zeros((len(data),1))
    for i in range(len(data)):
        v1 = pm[vocab.index(data[i][0]+".n")]
        v2 = pm[vocab.index(data[i][1]+".n")]
        #v = np.concatenate([v1,v2])
        cdm1[i] = v1
        cdm2[i] = v2
        outm[i] = np.array([float(data[i][2])])
    return cdm1,cdm2,outm

def read_compatibility_data():
    compatibility_data = []
    with open('compatibility/in_vg_compatibility.txt') as f:
        lines = f.read().splitlines()
    for l in lines:
        compatibility_data.append(l.split())
    return compatibility_data

cd = read_compatibility_data()
print("Reading probabilistic matrix... Please be patient...")
vocab, pm = read_probabilistic_matrix(basedir)
words1,words2,scores = make_input(read_compatibility_data(),vocab,pm)

print(words1.shape)
print(scores.shape)

ids = [i for i in range(words1.shape[0])]
shuffle(ids)
kf = KFold(n_splits=10)
sum = 0

for train, test in kf.split(ids):
    train_data = np.array(ids)[train]
    test_data = np.array(ids)[test]
    #print(train_data)
    #print(test_data)
    
    net = MLP(words1.shape[1],scores.shape[1])
    #optimizer = optim.SGD(net.parameters(), lr=1e-5)
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-3, weight_decay=1e-5)   
    criterion = nn.MSELoss()
    #criterion = nn.CosineEmbeddingLoss()

    total_loss = 0.0
    c=0
    for epoch in range(10):
        print("Epoch {}".format(epoch))
        shuffle(train_data)
        for i in train_data:
            X1, X2, Y = words1[i], words2[i], scores[i]
            X1, X2, Y = Variable(torch.FloatTensor([X1]), requires_grad=True), Variable(torch.FloatTensor([X2]), requires_grad=True), Variable(torch.FloatTensor([Y]), requires_grad=False)
            net.zero_grad()
            output = net([X1,X2])
            #loss = criterion(output, Y, torch.Tensor([1]))
            loss = criterion(output, Y)
            loss.backward()
            optimizer.step()
            total_loss+=loss.item()
            c+=1
            if c % 100 == 0:
                print(total_loss / c)
                #prediction = output.data.numpy()[0]
                #print(i,prediction[0],scores[i][0],loss.item(),r2_score(prediction,scores[i]))

    #print(list(net.parameters()))

    predictions = []
    golds = []

    for i in test_data:
        prediction = net([Variable(torch.FloatTensor([words1[i]])), Variable(torch.FloatTensor([words2[i]]))])
        gold = scores[i]
        predictions.append(prediction.data.numpy()[0])
        golds.append(gold)
        #print("PRED:",prediction,"GOLD:",gold)

    print("\nSPEARMAN:",spearmanr(predictions,golds))
