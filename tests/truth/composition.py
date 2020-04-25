"""Ideal words

Usage:
  composition.py [--att] [--rel]
  composition.py (-h | --help)
  composition.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Use attributes.
  --rel         Use relations.

"""


import sys
from docopt import docopt
sys.path.append('../../utils/')
from utils import read_entity_matrix, mk_entity_vectors, mk_full_predicate_vectors, read_inverse_entity_matrix
import numpy as np
import grammar
from collections import Counter,OrderedDict

basedir = "syn"

if __name__ == '__main__':
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"]:
        basedir = "synatt"
    if not args["--att"] and args["--rel"]:
        basedir = "synrel"
    if args["--att"] and args["--rel"]:
        basedir = "synattrel"

def intersection(sets):
    intersection = set.intersection(*sets)
    return intersection

def wordnetize(w):
    if w[-2:] == "_N":
        w = w.replace("_N",".n")		#HACK -- fix WN sense
    else:
        w = w[:-2]
    return w



ops = {"intersection":intersection}

v = grammar.Vocabulary()
phrase = input("Please enter a phrase: ")

if not set(phrase.split()).issubset(set(v.lexicon.keys())):
    print("Sorry, one of those words does not seem to be in the vocabulary. Good bye.")
    sys.exit(0)


candidate_phrases = grammar.disambiguate(phrase,v.lexicon)	#Hack due to Visual Genome inconsistency re. POS
#print("Possible POS for sentence:")
#for c in candidate_phrases:
#    print(' '.join([w.surface+' '+w.pos for w in c]))


for candidate in candidate_phrases:
    parse = grammar.parse_sentence(candidate)
    if parse == -1:
        continue
    
    lf,space_operations = grammar.get_space_operations(parse)

    print("\nPARSE FOUND. Reading entity matrix... Please be patient...")
    predicates = []
    e_to_p = read_inverse_entity_matrix(basedir)
    p_to_e = read_entity_matrix(basedir)
    
    o = space_operations[0]
    words = [wordnetize(o[1]),wordnetize(o[2])] 
    sets = []
    for w in words:
        w_set = set(p_to_e[w]) if w in p_to_e else set()
        sets.append(w_set)
    current_attention = ops[o[0]](sets)
    #print(current_attention)

    for o in space_operations[1:]:
        w = wordnetize(o[1])
        w_set = set(p_to_e[w]) if w in p_to_e else set()
        sets = [current_attention,w_set]
        current_attention = ops[o[0]](sets)
        #print(current_attention)
    if len(current_attention) == 0:
        print("Empty set.")
        sys.exit(0)
    for e in current_attention:
        print(e, e_to_p[e])
        predicates.extend([p for p in e_to_p[e]])
    counts = Counter(predicates)
    num_instances = len(current_attention)
    print("\nCOUNTS FOR THIS READING:")
    for k,v in counts.items():
        counts[k] = v/num_instances

            
    ordered_predicates = OrderedDict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    for k,v in ordered_predicates.items():
        print(k,v)
