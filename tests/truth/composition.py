import sys
sys.path.append('../../utils/')
from utils import read_entity_matrix, mk_entity_vectors, mk_full_predicate_vectors, read_inverse_entity_matrix
import numpy as np
import grammar

def intersection(sets):
    intersection = set.intersection(*sets)
    return intersection

def wordnetize(w):
    if w[-2:] == "_N":
        w = w.replace("_N",".n.01")		#HACK -- fix WN sense
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
    e_to_p = read_inverse_entity_matrix()
    p_to_e = read_entity_matrix()
    
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
        
