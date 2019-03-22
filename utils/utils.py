import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
import os
base=os.path.abspath(os.path.join(os.path.realpath(__file__), "../.."))

def read_entities():
    entities = {}
    with open(base+"/data/entities.txt") as f:
        lines = f.read().splitlines()
    for pair in lines:
        eid,etype = pair.split()
        entities[eid] = etype
    return entities

def read_predicate_matrix(subspace,ppmi=False):
    vocab = []
    vectors = []
    if ppmi:
        loc = base+"/spaces/"+subspace+"/predicate_matrix_ppmi.dm"
    else:
        loc = base+"/spaces/"+subspace+"/predicate_matrix.dm"
    print(loc)
    with open(loc) as f:
        dmlines=f.read().splitlines()
    for l in dmlines:
        items=l.split()
        target = items[0]
        vocab.append(target)
        vec=[float(i) for i in items[1:]] 	#list of lists	
        vectors.append(vec)
    m = np.array(vectors)
    return vocab, m

def read_probabilistic_matrix():
    vocab = []
    vectors = []
    with open(base+"/spaces/probabilistic_matrix.dm") as f:
        dmlines=f.read().splitlines()
    for l in dmlines:
        items=l.split()
        target = items[0]
        vocab.append(target)
        vec=[float(i) for i in items[1:]] 	#list of lists	
        vectors.append(vec)
    m = np.array(vectors)
    return vocab, m

def read_entity_matrix():
    p_entities = {}
    with open(base+"/spaces/entity_matrix.dm") as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        p = fields[0]
        entities = [e for e in fields[1:]] 
        p_entities[p] = entities
    return p_entities

def read_inverse_entity_matrix():
    e_predicates = {}
    with open(base+"/spaces/inverse_entity_matrix.dm") as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        e = fields[0]
        predicates = [p for p in fields[1:]] 
        e_predicates[e] = predicates
    return e_predicates

def read_cosines():
    p_cosines = {}
    with open(base+"/data/cosines.txt") as f:
        lines = f.read().splitlines()
    for l in lines:
        items = l.split()
        p = items[0]
        vec=[float(i) for i in items[1:]] 	#list of lists	
        p_cosines[p] = vec
    return p_cosines

def read_vocab():
    i_to_p = {}
    p_to_i = {}
    with open(base+"/data/vocab.txt") as f:
        lines = f.read().splitlines()
    for line in lines:
        i,p = line.split()
        i_to_p[int(i)] = p
        p_to_i[p] = int(i)
    return i_to_p,p_to_i

def read_nearest_neighbours(typ):
    '''typ is: synsets, relations, atts'''
    if typ == "synsets":
        fnns = base+"/data/synsets_nns.txt"
    elif typ == "relations":
        fnns = base+"/data/relationss_nns.txt"
    elif typ == "atts":
        fnns = base+"/data/attributes_nns.txt"
    neighbours = {}
    with open(fnns) as f:
        lines = f.read().splitlines()
    for line in lines:
        fields = line.split()
        predicate = fields[0]
        n = [p for i,p in enumerate(fields[1:]) if i % 2 == 0]
        neighbours[predicate] = n
    return neighbours


def find_predicate_entities(pred):
    entities = []
    with open(base+"/spaces/entity_matrix.dm") as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        p = fields[0][:-5]
        if p == pred:
            entities = [e for e in fields[1:]] 
            break
    return entities

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

def mk_full_predicate_vectors(entity_matrix, entity_list):
    size = len(entity_list)
    print("SIZE",size)
    predicate_vectors = {}
    for p in entity_matrix.keys():
        print(p)
        pv = np.zeros(size)
        p_ents = entity_matrix[p]
        for p_ent in p_ents:
            pv[entity_list.index(p_ent)]=1
        predicate_vectors[p] = pv
    return predicate_vectors

def write_dictionary(m,filename):
    f = open(filename,'w',encoding='utf-8')
    for k,v in m.items():
       v_string = ' '.join([str(val) for val in v])
       f.write('%s %s\n' %(k,v_string))
    f.close()

def write_numpy_matrix(m,i_to_predicates,filename):
    f = open(filename,'w',encoding='utf-8')
    for i,p in i_to_predicates.items():
       row = p
       v_string = ' '.join([str(round(val,5)) for val in m[i]])
       f.write('%s %s\n' %(p,v_string))
    f.close()

def compute_cosines(m):
    return 1-pairwise_distances(m, metric="cosine")

def write_cosines(words, cosines ,filename):
    f = open(filename,'w',encoding='utf-8')
    for i in range(len(words)):
       word = words[i]
       v_string = ' '.join([str(round(val,5)) for val in cosines[i]])
       f.write('%s %s\n' %(word,v_string))
    f.close()

def compute_nearest_neighbours(cosines,words):
    f1 = open(base+"/data/synsets_nns.txt",'w',encoding='utf-8')
    f2 = open(base+"/data/attributes_nns.txt",'w',encoding='utf-8')
    f3 = open(base+"/data/relations_nns.txt",'w',encoding='utf-8')
    word_indices = {i:w for i,w in enumerate(words)}
    for word in words:
        word_cos = np.array(cosines[word])
        ranking = np.argsort(-word_cos)
        if ".n." in word and "(" not in word:
            neighbours = [word_indices[n]+" ("+str(round(word_cos[n],5))+")" for n in ranking if ".n." in word_indices[n] and "(" not in word_indices[n]][:50]
            f1.write('%s %s\n' %(word,' '.join([n for n in neighbours])))
        if ".n." not in word and "(" not in word:
            neighbours = [word_indices[n]+" ("+str(round(word_cos[n],5))+")" for n in ranking if ".n." not in word_indices[n] and "(" not in word_indices[n]][:50]
            f2.write('%s %s\n' %(word,' '.join([n for n in neighbours])))
        if "(" in word:
            neighbours = [word_indices[n]+" ("+str(round(word_cos[n],5))+")" for n in ranking if "(" in word_indices[n]][:50]
            f3.write('%s %s\n' %(word,' '.join([n for n in neighbours])))
    f1.close()
    f2.close()
    f3.close()

def write_nearest_neighbours(cosines,words,filename):
    f = open(filename,'w',encoding='utf-8')
    word_indices = {}
    for i, val in enumerate(words):
        word_indices[i] = val
    for i in range(cosines.shape[0]):
        maxima = np.argsort(-cosines[i])[:10]
        neighbours = [word_indices[n]+" ("+str(round(cosines[i][n],5))+")" for n in maxima]
        f.write('%s %s\n' %(words[i],' '.join([n for n in neighbours])))
    f.close()
            

def write_vocabulary(words, filename):
    f = open(filename,'w',encoding='utf-8')
    for i in range(len(words)):
       f.write('%s %s\n' %(i,words[i]))
    f.close()

