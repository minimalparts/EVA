import sys
sys.path.append('../../utils/')
from utils import read_entity_matrix, read_inverse_entity_matrix, read_vocab, read_cosines
from collections import Counter
import itertools

threshold = 100   #Frequency threshold for considering an attribute (with respect to a predicate P)

print("Reading entity matrix... Please be patient...\n\n")
p_to_e = read_entity_matrix()
e_to_p = read_inverse_entity_matrix()

candidate_antonyms = {}

for predicate in p_to_e:
    if ".n." not in predicate or '(' in predicate:    #Looping over nominal attributes
       continue
    entities = p_to_e[predicate]
    attributes = []
    for e in entities:
        attributes.extend([p for p in e_to_p[e] if ".n." not in p and '(' not in p])	#Get attributes of entities that instantiate the predicate

    most_common_attributes = []    #This will hold the most common attributes across entities
    for i,j in Counter(attributes).most_common():
        if j > threshold:
            most_common_attributes.append(i)

    attribute_pairs = list(itertools.combinations(most_common_attributes, 2))    #Make all possible attribute pairs

    for pair in attribute_pairs:
        keep = True
        for e in entities:
            attributes = e_to_p[e]
            if set([pair[0],pair[1]]).issubset(attributes):    #If both attributes are found in the same entity, reject
                keep = False
                break
        if keep:
            p = (pair[0],pair[1])
            if p in candidate_antonyms:
                candidate_antonyms[p].append(predicate)
            else:
                candidate_antonyms[p] = [predicate]
            #print("CANDIDATE FOR",predicate,":",pair[0],pair[1],len(entities))

items_to_remove = []
for pair in candidate_antonyms:
    for e in entities:
        attributes = e_to_p[e]
        if set([pair[0],pair[1]]).issubset(attributes):
            items_to_remove.append(pair)
            break
           

final_candidate_antonyms = [ p for p in candidate_antonyms if p not in items_to_remove ]

i_to_p, p_to_i = read_vocab()
cosines = read_cosines()

antonyms = {}
for pair in final_candidate_antonyms:
    cosine = cosines[pair[0]][p_to_i[pair[1]]]    #Recording cosine between word pairs -- antonyms are usally similar
    antonyms[pair] = cosine

print("\nINCOMPATIBLE ITEMS, RANKED BY COSINE SIMILARITY:\n")
for p in sorted(antonyms, key=antonyms.get, reverse=True):
  print(p[0], p[1], antonyms[p], "PREDICATES:",' '.join([w for w in candidate_antonyms[p]]))
