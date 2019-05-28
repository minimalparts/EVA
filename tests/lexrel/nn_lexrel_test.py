"""Ideal words - extraction and aggregation functions

Usage:
  nn_lexrel_test.py --model=<file> [--ext=<file>] [--att] [--rel] [--ppmi] 
  nn_lexrel_test.py (-h | --help)
  nn_lexrel_test.py --version

Options:
  -h --help          Show this screen.
  --version          Show version.
  --model=<file>    File with parameters from validation step.
  --ext=<file>       File with external vectors (FastText, BERT...)
  --att              Process attributes.
  --rel              Process relations.
  --ppmi             Uses PPMI version of predicate matrix.

"""

import sys
sys.path.append('../../utils/')
import itertools
from docopt import docopt
from scipy.stats import spearmanr
from utils import read_external_vectors, read_probabilistic_matrix, read_nearest_neighbours, read_cosines
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as td
import numpy as np
import random
from math import sqrt
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold
from scipy.spatial.distance import cosine

device = torch.cuda.set_device(0)
#print(device)
#random.seed(77)

class MLP(nn.Module):
    def __init__(self,d1,d2,hiddensize):
        super(MLP, self).__init__()
        self.fc11 = nn.Linear(d1,hiddensize)
        self.fc2 = nn.Linear(2*hiddensize,hiddensize)
        self.fc3 = nn.Linear(hiddensize,d2)
        #self.drop1 = nn.Dropout(p=0.5)
    def forward(self, x):
        x11 = torch.relu(self.fc11(x[0]))
        x12 = torch.relu(self.fc11(x[1]))
        x2 = torch.relu(self.fc2(torch.cat((x11,x12),2)))
        x3 = torch.softmax(self.fc3(x2), dim=2)
        return x3

def make_input(data,vocab,pm):
    cdm1 = np.zeros((len(data),pm.shape[1]))
    cdm2 = np.zeros((len(data),pm.shape[1]))
    outm = np.zeros((len(data),4))
    for i in range(len(data)):
        v1 = pm[vocab.index(data[i][0])]
        v2 = pm[vocab.index(data[i][1])]
        #v = np.concatenate([v1,v2])
        cdm1[i] = v1
        cdm2[i] = v2
        outm[i] = np.array(data[i][2])
    return cdm1,cdm2,outm

def read_lexrel_data(filename):
    lexrel_data = []
    classes = {"hyper": [1,0,0,0],"coord":[0,1,0,0],"mero":[0,0,1,0],"random":[0,0,0,1]}
    with open(filename) as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        fields[2] = classes[fields[2]]
        lexrel_data.append(fields)
    return lexrel_data



def return_stats(data_scores):
    for i in range(4):
        print(" class ",i,sum(1 for s in data_scores if np.argmax(s) == i) / len(data_scores))


def test(ids_test,words1_test,words2_test,scores_test,model_file):
    print("FINAL TEST...............")
    net=torch.load(model_file)
    net.cuda()
    batch_size = 1
    test_predictions = []
    test_golds = []
    test_cosines = []
    for i in range(0,len(ids_test), batch_size):
        prediction = net([Variable(torch.FloatTensor([words1_test[ids_test[i:i+batch_size]]])).cuda(), Variable(torch.FloatTensor([words2_test[ids_test[i:i+batch_size]]])).cuda()])
        prediction = prediction.data.cpu().numpy()[0][0]
        test_predictions.append(np.argmax(prediction))
        test_golds.append(np.argmax(scores_test[ids_test[i]]))

    test_pred_score = sum(1 for x,y in zip(test_predictions,test_golds) if x == y) / len(test_golds)

    print("TEST PRED SCORE:",test_pred_score)
    return test_pred_score

def prepare_data(external_vector_file,basedir):
    #print(external_vector_file)
    if external_vector_file != "":
        vocab, pm = read_external_vectors(external_vector_file)
        vocab = [w+".n" for w in vocab]
        #print(vocab)
    else:
        #print("Reading probabilistic matrix... Please be patient...")
        vocab, pm = read_probabilistic_matrix(basedir)

    print("Reading dataset...")
    cd_train = read_lexrel_data('data/in_vg_lexrel.train.txt')
    cd_val = read_lexrel_data('data/in_vg_lexrel.val.txt')
    cd_test = read_lexrel_data('data/in_vg_lexrel.test.txt')

    words1_train,words2_train,scores_train = make_input(cd_train,vocab,pm)
    words1_val,words2_val,scores_val = make_input(cd_val,vocab,pm)
    words1_test,words2_test,scores_test = make_input(cd_test,vocab,pm)

    print("# TRAIN STATS")
    return_stats(scores_train)
    print("# VAL STATS")
    return_stats(scores_val)
    print("# TEST STATS")
    return_stats(scores_test)

    ids_train = np.array([i for i in range(words1_train.shape[0])])
    ids_val = np.array([i for i in range(words1_val.shape[0])])
    ids_test = np.array([i for i in range(words1_test.shape[0])])

    return words1_train,words2_train,scores_train,words1_test,words2_test,scores_test,ids_train,ids_test


if __name__ == '__main__':
    basedir = "syn"
    external_vector_file = ""
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"]:
        basedir = "synatt"
    if not args["--att"] and args["--rel"]:
        basedir = "synrel"
    if args["--att"] and args["--rel"]:
        basedir = "synattrel"
    if args["--ext"]:
        external_vector_file = args["--ext"]
    model_file = args["--model"]

    words1_train,words2_train,scores_train,words1_test,words2_test,scores_test,ids_train,ids_test = prepare_data(external_vector_file,basedir)
    test(ids_test,words1_test,words2_test,scores_test,model_file)

