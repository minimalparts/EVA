"""Ideal words - run extensional W2V

Usage:
  spearman.py [--att] [--rel] [--sit] [--ppmi] [--pca]
  spearman.py (-h | --help)
  spearman.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Use attributes.
  --rel         Use relations.
  --sit         Use situtation cooccurrences.
  --ppmi        Uses PPMI version of predicate matrix.
  --pca         Uses PCA version of predicate matrix.

"""

import re
import sys
sys.path.append('./utils/')
import random
import numpy as np
from collections import defaultdict
from docopt import docopt
from utils import read_predicate_matrix
from ext2vec import ext2vec
from messaging import output_logo

subspace = "syn"

if __name__ == '__main__':
    output_logo()
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"] and not args["--sit"]:
        subspace = "synatt"
    if args["--rel"] and not args["--att"] and not args["--sit"]:
        subspace = "synrel"
    if args["--sit"] and not args["--att"] and not args["--rel"]:
        subspace = "synsit"
    if args["--att"] and args["--rel"] and not args["--sit"]:
        subspace = "synattrel"
    if args["--att"] and args["--sit"] and not args["--rel"]:
        subspace = "synattsit"
    if not args["--att"] and args["--rel"] and args["--sit"]:
        subspace = "synrelsit"
    if args["--att"] and args["--rel"] and args["--sit"]:
        subspace = "synattrelsit"

vocab, m = read_predicate_matrix(subspace)
print("Length of vocab:",len(vocab))
corpus = []


print("Running ext2vec...")
settings = {}
settings['n'] = 300                   # dimension of word embeddings
settings['epochs'] = 30           # number of training epochs
settings['neg_samp'] = 1           # number of negative words to use during training
settings['learning_rate'] = 0.001    # learning rate
np.random.seed(0)                   # set the seed for reproducibility


# INITIALIZE E2V MODEL
e2v = ext2vec(vocab, subspace, settings)
e2v.train(m,vocab)
e2v.pretty_print(vocab)
