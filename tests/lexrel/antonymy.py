import sys
sys.path.append('../../utils/')
from utils import read_entity_matrix, read_inverse_entity_matrix, read_vocab, read_cosines
from collections import Counter
import itertools

p_to_e = read_entity_matrix()
e_to_p = read_inverse_entity_matrix()


candidate_antonyms = []
for predicate in p_to_e:
    predicates = []
    entities = p_to_e[predicate]
    if len(entities) < 1000:
        continue
    print("Considering",predicate,"...")
    for e in entities:
        predicates.extend(e_to_p[e])

    most_common_predicates = Counter(predicates).most_common()[:50]
    predicate_pairs = list(itertools.combinations(most_common_predicates, 2))
    #print(candidate_antonyms)

    for pair in predicate_pairs:
        keep = True
        for e in entities:
            predicates = e_to_p[e]
            if set([pair[0][0],pair[1][0]]).issubset(predicates):
                #print(pair,"SUBSET",predicates)
                keep = False
                break
        if keep:
            candidate_antonyms.append([pair[0][0],pair[1][0]])



i_to_p, p_to_i = read_vocab()
cosines = read_cosines()

antonyms = {}
for pair in candidate_antonyms:
    cosine = cosines[pair[0]][p_to_i[pair[1]]]
    antonyms[pair[0]+' '+pair[1]] = cosine

for p in sorted(antonyms, key=antonyms.get, reverse=True):
  print(p, antonyms[p])
