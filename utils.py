import distributional_semantics
import grammar
import numpy as np
from math import sqrt, fabs


def normalise(v):
    '''Normalise vector between 0 and 1.'''
    max_val = np.max(v)
    if max_val == 0:
        return v
    return v / max_val

def cosine_similarity(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of same length")
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return -1
    num = np.dot(v1, v2)
    den_a = np.dot(v1, v1)
    den_b = np.dot(v2, v2)
    return num / (sqrt(den_a) * sqrt(den_b))

def printer(filename,lines):
  f = open(filename,'a')
  for l in lines:
    f.write(l+'\n')
  f.close()

def map_quantifier(quant):
  qmap = {"no":0, "few":0.05, "some":0.35, "most":0.95, "all":1}
  return qmap[quant]

def record_vocab(properties, file_name):
  '''Record vocabulary'''
  vocab_file=open(file_name,'w')
  c = 0
  for w in properties: 
    vocab.labels_to_pos[w] = c
    vocab.pos_to_labels[c] = w
    vocab_file.write(w+'\n')
    c+=1
  vocab_file.close()


def read_prob_file(data):
  animals = {}
  vocab = grammar.Vocabulary()

  f=open(data,'r')
  for l in f:
    l=l.rstrip('\n')
    fields=l.split()
    kind=fields[0]+"_N"

    if kind not in animals:
      animals[kind] = {}
      vocab.words.append(kind)

    feature=fields[1]+"_V"
    quantifier=fields[2]
    animals[kind][feature] = map_quantifier(quantifier)
    if feature not in vocab.word_strings:
      vocab.words.append(feature)
  f.close()
  
  print "The vocabulary has",len(vocab.words),"entries."
  return animals, vocab


def read_world_file(data, lexicon):
  instances = {}
  properties = []
  f=open(data,'r')
  for l in f:
    l=l.rstrip('\n')
    fields=l.split()
    ID=fields[0]

    if ID not in instances:
      instances[ID] = []

    prop=fields[1]
    properties.append(prop)
    instances[ID].append(prop)
    if prop not in lexicon:
      print "ERROR: unknown word in word file:",prop,". The world should be described in terms of the overall lexicon."
  f.close()
  
  print "The vocabulary has",len(lexicon),"entries."
  return instances


def mk_ideal_matrix(ideal_vector_space, distributional_vector_space, dim, training):
  '''Make ideal numpy matrix out of vector space object.
  If in training, only keep vocab for which we have data in ideal 
  and distributional spaces.
  '''

  known_vocab = []
  vectors = []
  i = 0
  for word,vec in ideal_vector_space.vectors.items():
    if training:
      if np.linalg.norm(vec) != 0 and np.linalg.norm(distributional_vector_space.vectors[word]) != 0:
        known_vocab.append(word)
        vectors.append(vec)
        i+=1
    else:
      known_vocab.append(word)
      vectors.append(vec)
      i+=1
      
  mat = np.zeros((len(vectors),dim))
  for i in range(len(vectors)):
    mat[i] = normalise(vectors[i])
  return mat, known_vocab


def mk_dist_matrix(dist_vector_space, dim, vocab):
  '''Make distributional numpy matrix out of vector space object,
  for the vocabulary known in the ideal matrix.'''
  mat = np.zeros((len(vocab),dim))
  i = 0
  for word,vec in dist_vector_space.vectors.items():
    if word in vocab:
      mat[i] = normalise(vec)
      i+=1
  return mat


def binarise(matrix):
  '''Hack. Return matrix to binary format.'''
  for i in range(matrix.shape[0]):
    min_val = np.min(matrix[i])
    max_val = np.max(matrix[i])
    for j in range(matrix.shape[1]):
      value = matrix[i][j]
      if fabs(value - min_val) < fabs(value - max_val):
        matrix[i][j] = 0
      else: 
        matrix[i][j] = 1
  return matrix

def print_justification(justification):
    justification_print = "JUSTIFICATION: "
    for i in justification[0]:
        justification_print+=str([e.ID for e in i])
    justification_print+=" NP:"
    for i in justification[1]:
        justification_print+=str([e.ID for e in i])
    justification_print+=" VP:"
    justification_print+=str([e.ID for e in justification[2]])
    return justification_print
