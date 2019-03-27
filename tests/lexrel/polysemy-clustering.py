import sys
sys.path.append('../../utils/')
from utils import find_predicate_entities, read_inverse_entity_matrix, read_predicate_matrix, mk_entity_vectors
from sklearn.cluster import DBSCAN
#from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
import random

predicate = sys.argv[1]
threshold = int(sys.argv[2])    #This is the number of predicates an entity must have to be turned into a vector


print("Reading predicate and entity matrices... Please be patient...")
vocab, predicate_matrix = read_predicate_matrix()
inverse_entity_matrix = read_inverse_entity_matrix()
entities = find_predicate_entities(predicate)


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
    print("CLASS",c+1,"RANDOM SAMPLE")
    for i in random.sample(classified[c],min(5,len(classified[c]))):
        print(c,i)
    print("\n","FEATURE COUNTER\n",Counter(class_atts[c]))
    print("\n\n")
