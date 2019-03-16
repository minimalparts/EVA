import sys
sys.path.append('../../utils/')
from utils import read_entity_matrix, read_inverse_entity_matrix, read_vocab, read_cosines
from collections import Counter
import itertools

p_to_e = read_entity_matrix()
e_to_p = read_inverse_entity_matrix()


candidate_antonyms = []
for predicate in p_to_e:
    if ".n." not in predicate or '(' in predicate:
       continue
    predicates = []
    entities = p_to_e[predicate]
    #print("Considering",predicate,"...")
    for e in entities:
        predicates.extend([p for p in e_to_p[e] if ".n." not in p and '(' not in p])	#Only keep attributes

    most_common_predicates = []
    c = 0
    for i,j in Counter(predicates).most_common():
        #print(i,j)
        if j > 100: #and j > 0.01 * len(entities):
            most_common_predicates.append(i)
            c+=1
        #if c > 10:
        #    break

    #print(most_common_predicates)
    predicate_pairs = list(itertools.combinations(most_common_predicates, 2))
    #print(candidate_antonyms)

    for pair in predicate_pairs:
        keep = True
        for e in entities:
            predicates = e_to_p[e]
            if set([pair[0],pair[1]]).issubset(predicates):
                #print(pair,"SUBSET",predicates)
                keep = False
                break
        if keep:
            candidate_antonyms.append([pair[0],pair[1]])
            print("CANDIDATE FOR",predicate,":",pair[0],pair[1],len(entities))

    items_to_remove = []
    for pair in candidate_antonyms:
        for e in entities:
            predicates = e_to_p[e]
            if set([pair[0],pair[1]]).issubset(predicates):
                items_to_remove.append(pair)
                break

    candidate_antonyms = [ p for p in candidate_antonyms if p not in items_to_remove ]


i_to_p, p_to_i = read_vocab()
cosines = read_cosines()

antonyms = {}
for pair in candidate_antonyms:
    cosine = cosines[pair[0]][p_to_i[pair[1]]]
    antonyms[pair[0]+' '+pair[1]] = cosine

for p in sorted(antonyms, key=antonyms.get, reverse=True):
  print(p, antonyms[p])
