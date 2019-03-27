"""Ideal words - test on MEN dataset

Usage:
  spearman.py [--att] [--rel] [--ppmi]
  spearman.py (-h | --help)
  spearman.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Process attributes.
  --rel         Process relations.
  --ppmi        Uses PPMI version of predicate matrix.

"""


import sys
sys.path.append('../../utils/')
from docopt import docopt
from utils import read_predicate_matrix
from scipy.stats import spearmanr
from scipy.spatial import distance

subspace = "syn"

if __name__ == '__main__':
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"]:
        subspace = "synatt"
    if not args["--att"] and args["--rel"]:
        subspace = "synrel"
    if args["--att"] and args["--rel"]:
        subspace = "synattrel"

vocab, m = read_predicate_matrix(subspace,ppmi=args["--ppmi"])

system = []
gold = []

f = open("MEN_dataset_lemma_form_full",'r')

for l in f:
    fields = l.rstrip('\n').split()
    w1 = fields[0].replace("-n",".n")    #harmonising formats
    w2 = fields[1].replace("-n",".n")
    score = float(fields[2])
    if w1 in vocab and w2 in vocab:
        cos = 1 - distance.cosine(m[vocab.index(w1)],m[vocab.index(w2)])
        system.append(cos)
        gold.append(score)
        print(w1,w2,cos,score)
f.close()

print("SPEARMAN:",spearmanr(system,gold))
print("("+str(len(system))+" pairs out of the original 3000 could be processed, due to vocabulary size.)")
