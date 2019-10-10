"""Ideal words - test on SimLex-999 dataset

Usage:
  spearman.py count [--att] [--rel] [--sit] [--ppmi] [--pca]
  spearman.py ext2vec [--att] [--rel] [--sit]
  spearman.py compare [--file=<file>]
  spearman.py (-h | --help)
  spearman.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Use attributes.
  --rel         Use relations.
  --sit         Use situtation cooccurrences.
  --ppmi        Uses PPMI version of predicate matrix.
  --pca	        Uses PCA-reduced version of predicate matrix (300D).

"""


import sys
sys.path.append('../../utils/')
from docopt import docopt
import numpy as np
from utils import read_predicate_matrix, read_probabilistic_matrix, read_external_vectors
from messaging import output_logo
from scipy.stats import spearmanr
from scipy.spatial import distance

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

if args["count"]:
    vocab, m = read_predicate_matrix(subspace,ppmi=args["--ppmi"],pca=args["--pca"])
if args["ext2vec"]:
    vocab, m = read_external_vectors("../../spaces/"+subspace+"/ext2vec.dm")
if args["compare"]:
    vocab, m = read_external_vectors(args["--file"])

system = []
gold = []

with open("data/in_vg_SimLex999.txt",'r') as f:
    lines = f.read().splitlines()

for l in lines[1:]:
    fields = l.split()
    w1 = fields[0]
    w2 = fields[1]
    score = float(fields[2])
    if w1 in vocab and w2 in vocab:
        cos = 1 - distance.cosine(m[vocab.index(w1)],m[vocab.index(w2)])
        system.append(cos)
        gold.append(score)
        #print(w1,w2,cos,score)
f.close()


print("SETTING:")
print(args)
print("***\n")
print("SPEARMAN:",spearmanr(system,gold))
print("("+str(len(system))+" pairs out of the original 3000 could be processed, due to vocabulary size.)")
