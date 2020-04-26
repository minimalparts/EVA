"""Ideal words - extraction and aggregation functions

Usage:
  nn_compatibility_test.py --model=<file> [--ext=<file>] [--att] [--sit] [--rel] [--ppmi] 
  nn_compatibility_test.py (-h | --help)
  nn_compatibility_test.py --version

Options:
  -h --help          Show this screen.
  --version          Show version.
  --model=<file>     File with parameters from validation step.
  --ext=<file>       File with external vectors (FastText, BERT...)
  --att              Process attributes.
  --rel              Process relations.
  --sit              Process situations.
  --ppmi             Uses PPMI version of predicate matrix.

"""

import sys
sys.path.append('../../utils/')
import itertools
from docopt import docopt
from scipy.stats import spearmanr
from utils import read_external_vectors, read_probabilistic_matrix, read_predicate_matrix, read_nearest_neighbours, read_cosines
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

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#print(device)
#random.seed(77)



class MLP(nn.Module):
    def __init__(self,d1,d2,hiddensize):
        super(MLP, self).__init__()
        self.fc11 = nn.Linear(d1,hiddensize)
        self.fc2 = nn.Linear(2*hiddensize,hiddensize)
        self.fc3 = nn.Linear(hiddensize,d2)
    def forward(self, x):
        x11 = torch.relu(self.fc11(x[0]))
        x12 = torch.relu(self.fc11(x[1]))
        x2 = torch.relu(self.fc2(torch.cat((x11,x12),2)))
        x3 = self.fc3(x2)
        return x3

def make_input(data,vocab,pm):
    cdm1 = np.zeros((len(data),pm.shape[1]))
    cdm2 = np.zeros((len(data),pm.shape[1]))
    outm = np.zeros((len(data),1))
    for i in range(len(data)):
        v1 = pm[vocab.index(data[i][0]+".n")]
        v2 = pm[vocab.index(data[i][1]+".n")]
        cdm1[i] = v1
        cdm2[i] = v2
        outm[i] = np.array([float(data[i][2])])
    return cdm1,cdm2,outm

def read_compatibility_data(filename):
    compatibility_data = []
    with open(filename) as f:
        lines = f.read().splitlines()
    for l in lines:
        compatibility_data.append(l.split())
    return compatibility_data

def return_stats(data_scores):
    for i in range(2,7):
        print(i-1,"<= score <",i,sum(1 for s in data_scores if s >= i-1 and s < i))


def test(ids_test,words1_test,words2_test,scores_test,model_file):
    print("FINAL TEST...............")
    net=torch.load(model_file)
    net.to(device)
    batch_size = 1
    test_predictions = []
    test_golds = []
    test_cosines = []
    for i in range(0,len(ids_test), batch_size):
        prediction = net([Variable(torch.FloatTensor([words1_test[ids_test[i:i+batch_size]]])).to(device), Variable(torch.FloatTensor([words2_test[ids_test[i:i+batch_size]]])).to(device)])
        test_predictions.append(prediction.data.cpu().numpy()[0][0])
        test_golds.append(scores_test[ids_test[i]])
        test_cosines.append(1-cosine(words1_test[ids_test[i]],words2_test[ids_test[i]]))
        #print("PRED:",prediction.data.cpu().numpy()[0][0],"COS:",test_cosines[i],"GOLD:",test_golds[i])

    test_pred_score = spearmanr(test_predictions,test_golds)[0]
    test_cos_score = spearmanr(test_cosines,test_golds)[0]

    print("TEST SCORE (SPEARMAN RHO):",test_pred_score)
    print("COSINE BASELINE (SPEARMAN RHO):",test_cos_score)
    return(test_pred_score,test_cos_score)

def prepare_data(external_vector_file,basedir):
    #print(external_vector_file)
    if external_vector_file != "":
        vocab, pm = read_external_vectors(external_vector_file)
        #vocab = [w+".n" for w in vocab]
    else:
        #print("Reading probabilistic matrix... Please be patient...")
        #vocab, pm = read_probabilistic_matrix(basedir)
        vocab, pm = read_predicate_matrix(basedir,ppmi=True,pca=True)

    print("Reading dataset...")
    cd_test = read_compatibility_data('data/in_vg_compatibility.test.txt')

    words1_test,words2_test,scores_test = make_input(cd_test,vocab,pm)

    print("# TEST STATS")
    return_stats(scores_test)

    ids_test = np.array([i for i in range(words1_test.shape[0])])

    return words1_test,words2_test,scores_test,ids_test


if __name__ == '__main__':
    basedir = "syn"
    external_vector_file = ""
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--sit"] and not args["--rel"]:
        basedir = "synsit"
    if not args["--sit"] and args["--rel"]:
        basedir = "synrel"
    if args["--att"] and args["--rel"]:
        basedir = "synattrel"
    if args["--ext"]:
        external_vector_file = args["--ext"]
    model_file = args["--model"]

    words1_test,words2_test,scores_test,ids_test = prepare_data(external_vector_file,basedir)
    test(ids_test,words1_test,words2_test,scores_test,model_file)

