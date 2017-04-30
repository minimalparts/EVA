import distributional_semantics
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

def read_dataset(data):
  animals = {}
  vocab = distributional_semantics.Vocabulary()

  f=open(data,'r')
  for l in f:
    l=l.rstrip('\n')
    fields=l.split()
    species=fields[0]

    if species not in animals:
      animals[species] = {}
      vocab.words.append(species)

    feature=fields[1]
    quantifier=fields[2]
    animals[species][feature] = map_quantifier(quantifier)
    if feature not in vocab.words:
      vocab.words.append(feature)
  
  c = 0
  for w in vocab.words: 
    vocab.contexts_to_id[w] = c
    vocab.id_to_contexts[c] = w
    c+=1

  f.close()
  return animals, vocab

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
