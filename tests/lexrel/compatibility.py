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

basedir = "syn"

if __name__ == '__main__':
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"]:
        basedir = "synatt"
    if not args["--att"] and args["--rel"]:
        basedir = "synrel"
    if args["--att"] and args["--rel"]:
        basedir = "synattrel"


print("Reading probabilistic matrix... Please be patient...")
vocab, pm = read_probabilistic_matrix(basedir)
print("Reading nearest neighbour file for smoothing...")
neighbours = read_nearest_neighbours(basedir,"syn")
print("Reading cosines for smoothing...")
cosines = read_cosines(basedir,ppmi=False)


def smooth_nn(word,dimension):
    nns =  neighbours[word]
    smoothed = 0.0
    for nn in nns:
        smoothed+=pm[vocab.index(nn)][vocab.index(dimension)]
    return smoothed / len(nns)

def smooth_cos(word,dimension):
    return cosines[word][vocab.index(dimension)]


def common_properties(word1,word2):
    common_properties = []
    scores = []
    v1 = pm[vocab.index(word1)]
    v2 = pm[vocab.index(word2)]
    for d in range(len(v1)):
        if "has(" in vocab[d] and v1[d] > 0.0 + v2[d] > 0.0:
            #print(word1,word2,vocab[d],v1[d],v2[d])
            common_properties.append(vocab[d])
            scores.append(cosines[word1][d])
            scores.append(cosines[word2][d])
    return common_properties, sum(scores)

def coherence(properties):
   pairs = list(itertools.combinations(properties, 2))
   coherence = 0.0
   for (p1,p2) in pairs:
       coherence+=cosines[p1][vocab.index(p2)]
   return coherence / len(pairs)


def read_compatibility_data():
    compatibility_data = []
    with open('compatibility/in_vg_compatibility.txt') as f:
        lines = f.read().splitlines()

    for l in lines:
        compatibility_data.append(l.split())
    return compatibility_data

cd = read_compatibility_data()

compatibility_scores = []
gold_compatibility_scores = []

for triple in cd:
    a = triple[0]+".n"
    b = triple[1]+".n"
    #p_a_given_b = smooth_nn(a,b)
    #p_a_given_b = smooth_cos(a,b)
    #p_b_given_a = smooth_nn(b,a)
    #p_b_given_a = smooth_cos(b,a)
    #print(a,b,p_a_given_b)
    #avg = (p_a_given_b + p_b_given_a) / 2
    common, score = common_properties(a,b)
    print(a,b,common,score)
    compatibility_scores.append(score+smooth_cos(a,b))    #average
    gold_compatibility_scores.append(float(triple[2]))
    print(triple[0],triple[1],triple[2],round(score,4))

print("\nSPEARMAN:",spearmanr(compatibility_scores,gold_compatibility_scores))
