import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
import re

def read_predicate_matrix(dm_file,typ=""):
    vocab = []
    vectors = []
    with open(dm_file) as f:
        dmlines=f.read().splitlines()

    for l in dmlines:
        process = False
        items=l.split()
        target = items[0]
        if typ == "synsets":
            m = re.search("\.[a-z]\.[0-9]*$",target)
            if m:
                process = True
        else:
            process = True
        if process:
            vocab.append(target)
            vec=[float(i) for i in items[1:]] 	#list of lists	
            vectors.append(vec)
            process = False
    m = np.array(vectors)
    return vocab, m

def read_inverse_entity_matrix(filename):
    e_predicates = {}
    with open(filename) as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        e = fields[0]
        predicates = [p for p in fields[1:]] 
        e_predicates[e] = predicates
    return e_predicates

    

def compute_cosines(m):
    return 1-pairwise_distances(m, metric="cosine")

def find_entities(pred,filename):
    entities = []
    with open(filename) as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        p = fields[0][:-5]
        if p == pred:
            entities = [e for e in fields[1:]] 
            break
    return entities

