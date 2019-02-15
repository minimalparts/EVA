from utils import find_entities, read_inverse_entity_matrix, read_predicate_matrix
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
import random
import sys

predicate = sys.argv[1]


def mk_entity_vectors(entities, inverse_entity_matrix, predicates_to_i):
    size = len(predicates_to_i.keys())
    entity_vectors = []
    entity_ids = []
    for e in entities:
        ev = np.zeros(size)
        e_preds = inverse_entity_matrix[e]
        #print(e_preds)
        if len(e_preds) > 3:
            for e_pred in e_preds:
                ev[predicates_to_i[e_pred]]=1
            entity_vectors.append(ev)
            entity_ids.append(e)
    return entity_ids, entity_vectors

vocab, predicate_matrix = read_predicate_matrix("../../spaces/predicate_matrix.dm")
inverse_entity_matrix = read_inverse_entity_matrix("../../spaces/inverse_entity_matrix.dm")
entities = find_entities(predicate, "../../spaces/entity_matrix.dm")


predicates_to_i = {}
for i,w in enumerate(vocab):
    predicates_to_i[w] = i

entity_ids, entity_vectors = mk_entity_vectors(entities, inverse_entity_matrix, predicates_to_i)

print("Clustering...")
clustering = DBSCAN(min_samples=5, metric='cosine', eps=0.3).fit(entity_vectors)
#clustering = KMeans(n_clusters=2).fit(entity_vectors)

classified = {}
class_atts = {}

for i, value in np.ndenumerate(clustering.labels_):
    i = i[0]
    if value in classified:
        classified[value].append(inverse_entity_matrix[entity_ids[i]])
        class_atts[value].extend(inverse_entity_matrix[entity_ids[i]])
    else:
        classified[value] = [inverse_entity_matrix[entity_ids[i]]]
        class_atts[value] = inverse_entity_matrix[entity_ids[i]]


for c in range(len(classified)-1):
    for i in random.sample(classified[c],min(5,len(classified[c]))):
        print(c,i)
    print("\n",Counter(class_atts[c]))
    print("\n\n")
