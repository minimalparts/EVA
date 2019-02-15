import sys
sys.path.append('..')
from utils import read_entity_matrix, mk_entity_vectors, mk_full_predicate_vectors, read_inverse_entity_matrix
import numpy as np
import grammar

def intersection(words):
    intersection = predicate_matrix[words[0]]
    for i in range(1, len(words)):
        intersection = intersection * predicate_matrix[words[i]]
    return intersection


v = grammar.Vocabulary()
phrase = input("Please enter a phrase: ")
parse = grammar.parse_sentence(phrase,v.lexicon)

inverse_entity_matrix = read_inverse_entity_matrix("../../spaces/inverse_entity_matrix.dm")
p_entities, all_entities = read_entity_matrix("../../spaces/entity_matrix.dm")
predicate_matrix = mk_full_predicate_vectors(p_entities, all_entities)

i_to_entities = {}
for i,e in enumerate(all_entities):
    i_to_entities[i] = e

print(parse,parse.daughters)
for d in parse.daughters:
    if d.pos == 'N':
        d.surface+=".n.01"		#HACK -- fix WN sense

if parse.pos == "NP":
    '''Intersection'''
    words = [d.surface for d in parse.daughters]
    vector = intersection(words)
    for x, y in np.ndenumerate(vector):
        if y > 0:
            print(x[0], y, inverse_entity_matrix[i_to_entities[x[0]]])
        
