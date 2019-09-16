import numpy as np
from math import log
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA
from scipy import linalg as LA
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

def read_external_vectors(vector_file):
    vocab = []
    vectors = []
    with open(vector_file) as f:
        dmlines=f.read().splitlines()
    for l in dmlines:
        items=l.split()
        target = items[0]
        vocab.append(target)
        vec=[float(i) for i in items[1:]] 	#list of lists	
        vectors.append(vec)
    m = np.array(vectors)
    return vocab, m

def read_predicate_matrix(subspace,ppmi=False,pca=False):
    vocab = []
    vectors = []
    loc = base+"/spaces/"+subspace+"/predicate_matrix.dm"
    if ppmi:
        loc = loc.replace(".dm","_ppmi.dm")
    if pca:
        loc = loc.replace(".dm","_pca.dm")
    print("Loading",loc,"...")
    with open(loc) as f:
        dmlines=f.read().splitlines()
    for l in dmlines:
        items=l.split()
        target = items[0]
        vocab.append(target)
        vec=[float(i) for i in items[1:]]
        vectors.append(vec)
    m = np.array(vectors)
    return vocab, m

def read_probabilistic_matrix(subspace):
    vocab = []
    vectors = []
    loc = base+"/spaces/"+subspace+"/probabilistic_matrix.dm"
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

def read_entity_matrix(subspace):
    p_entities = {}
    loc = base+"/spaces/"+subspace+"/entity_matrix.dm"
    with open(loc) as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        p = fields[0]
        entities = [e for e in fields[1:]] 
        p_entities[p] = entities
    return p_entities

def read_inverse_entity_matrix(subspace):
    e_predicates = {}
    loc = base+"/spaces/"+subspace+"/inverse_entity_matrix.dm"
    with open(loc) as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split()
        e = fields[0]
        predicates = [p for p in fields[1:]] 
        e_predicates[e] = predicates
    return e_predicates

def read_cosines(subspace,ppmi=False):
    p_cosines = {}
    if ppmi:
        filename = base+"/data/"+subspace+"/cosines_ppmi.txt"
    else:
        filename = base+"/data/"+subspace+"/cosines.txt"
    with open(filename) as f:
        lines = f.read().splitlines()
    for l in lines:
        items = l.split()
        p = items[0]
        vec=[float(i) for i in items[1:]] 	#list of lists	
        p_cosines[p] = vec
    return p_cosines

def read_vocab(subspace):
    i_to_p = {}
    p_to_i = {}
    filename = base+"/data/"+subspace+"/vocab.txt"
    with open(filename) as f:
        lines = f.read().splitlines()
    for line in lines:
        i,p = line.split()
        i_to_p[int(i)] = p
        p_to_i[p] = int(i)
    return i_to_p,p_to_i

def read_nearest_neighbours(subspace,typ):
    '''typ is: syn, rel, att'''
    if typ == "syn":
        fnns = base+"/data/"+subspace+"/syn_nns.txt"
    elif typ == "rel":
        fnns = base+"/data/"+subspace+"/rel_nns.txt"
    elif typ == "att":
        fnns = base+"/data/"+subspace+"att_nns.txt"
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


def ppmi(matrix):
    ppmi_matrix = np.zeros(matrix.shape)
    N = np.sum(matrix)
    row_sums = np.sum(matrix, axis=1)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if i != j:		#i !=j cos for operations like similarity, better have 0s on the diagonal	
                try:
                    ppmi_matrix[i][j] = max(0,log(matrix[i][j] * N / (row_sums[i] * row_sums[j])))
                except:
                    pass
    return ppmi_matrix


def compute_cosines(m):
    return 1-pairwise_distances(m, metric="cosine")

def compute_PCA(m,dim):
    np.fill_diagonal(m, 0)			#Make sure diagonal is 0
    m -= np.mean(m, axis = 0)
    pca = PCA(n_components=dim)
    pca.fit(m)
    return pca.transform(m)


def write_cosines(words, cosines ,filename):
    f = open(filename,'w',encoding='utf-8')
    for i in range(len(words)):
       word = words[i]
       v_string = ' '.join([str(round(val,5)) for val in cosines[i]])
       f.write('%s %s\n' %(word,v_string))
    f.close()

def compute_nearest_neighbours(cosines,words):
    syn_nns = {}
    att_nns = {}
    rel_nns = {}
    word_indices = {i:w for i,w in enumerate(words)}
    for word in words:
        word_cos = np.array(cosines[word])
        ranking = np.argsort(-word_cos)
        if ".n" in word and "(" not in word:
            neighbours = [word_indices[n]+" ("+str(round(word_cos[n],5))+")" for n in ranking if ".n" in word_indices[n] and "(" not in word_indices[n]][:50]
            syn_nns[word] = neighbours
        if ".n" not in word and "(" not in word:
            neighbours = [word_indices[n]+" ("+str(round(word_cos[n],5))+")" for n in ranking if ".n" not in word_indices[n] and "(" not in word_indices[n]][:50]
            att_nns[word] = neighbours
        if "(" in word:
            neighbours = [word_indices[n]+" ("+str(round(word_cos[n],5))+")" for n in ranking if "(" in word_indices[n]][:50]
            rel_nns[word] = neighbours
    return syn_nns,att_nns,rel_nns

def write_nearest_neighbours(neighbours_dic,wordtype,subspace,ppmi=False):
    if ppmi:
        f = open(base+"/data/"+subspace+"/"+wordtype+"_nns_ppmi.txt",'w',encoding='utf-8')
    else:
        f = open(base+"/data/"+subspace+"/"+wordtype+"_nns.txt",'w',encoding='utf-8')
    for word,neighbours in neighbours_dic.items():
            f.write('%s %s\n' %(word,' '.join([n for n in neighbours])))
    f.close()

def write_vocabulary(words, filename):
    f = open(filename,'w',encoding='utf-8')
    for i in range(len(words)):
       f.write('%s %s\n' %(i,words[i]))
    f.close()

def normalise(predicate_matrix):
    norm_matrix = np.zeros(predicate_matrix.shape)
    for i in range(predicate_matrix.shape[0]):
        norm_matrix[i] = predicate_matrix[i] / np.sum(predicate_matrix[i])
    return norm_matrix

