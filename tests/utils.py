import numpy as np
import re

def readDM(dm_file):
    dm_dict = {}
    with open(dm_file) as f:
        dmlines=f.readlines()
    f.close()

    #Make dictionary with key=row, value=vector
    for l in dmlines:
        m = re.search('.[a-z].[0-9][0-9]',l)		#Only considering WordNet types (not attributes)
        if m:
            items=l.rstrip().split()
            row=items[0][:-5]		#deleting WordNet suffix of the type .n.01
            vec=[float(i) for i in items[1:]]
            vec=array(vec)
            dm_dict[row]=vec
    return dm_dict

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
            vec=[float(i) for i in items[1:]]   #list of lists  
            vectors.append(vec)
            process = False
    m = np.array(vectors)
    return vocab, m


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

def mk_entity_vectors(entities, inverse_entity_matrix, predicates_to_i):
    size = len(predicates_to_i.keys())
    entity_vectors = []
    entity_ids = []
    for e in entities:
        ev = np.zeros(size)
        e_preds = inverse_entity_matrix[e]
        for e_pred in e_preds:
            ev[predicates_to_i[e_pred]]=1
        entity_vectors.append(ev)
        entity_ids.append(e)
    return entity_ids, entity_vectors

def read_entity_matrix(filename):
    p_entities = {}    #predicate-entity matrix
    all_entities = []      #list of entities
    with open(filename) as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        p = fields[0]
        entities = [e for e in fields[1:]]
        p_entities[p] = entities
        all_entities.extend(entities)
    return p_entities, all_entities

def mk_full_predicate_vectors(entity_matrix, entity_list):
    size = len(entity_list)
    entities_to_i = {}
    for i,e in enumerate(entity_list):
        entities_to_i[e] = i

    predicate_vectors = {}
    for p in entity_matrix.keys():
        pv = np.zeros(size)
        p_ents = entity_matrix[p]
        for p_ent in p_ents:
            pv[entities_to_i[p_ent]]=1
            predicate_vectors[p] = pv
    return predicate_vectors



def convert_to_array(vector):
  return np.array([float(i) for i in vector.split(' ')])

def convert_to_string(vec):
    s = ""
    for i in range(len(vec)):
        s+=str(vec[i])+" "
    return s[:-1]

def sim_to_matrix(dm_dict,vec,n):
    cosines={}
    c=0
    for k,v in dm_dict.items():
        try:
            cos = cosine_similarity(vec, v)
            cosines[k]=cos
            c+=1
        except:
            pass
    c=0
    neighbours = []
    for t in sorted(cosines, key=cosines.get, reverse=True):
        if c<n:
            if t.isalpha():
                #print(t,cosines[t])
                neighbours.append(t)
                c+=1
        else:
            break
    return neighbours


def normalise(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def cosine_similarity(peer_v, query_v):
    if len(peer_v) != len(query_v):
        raise ValueError("Peer vector and query vector must be "
                         " of same length")
    num = np.dot(peer_v, query_v)
    den_a = np.dot(peer_v, peer_v)
    den_b = np.dot(query_v, query_v)
    return num / (np.sqrt(den_a) * np.sqrt(den_b))


