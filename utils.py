import distributional_semantics
import numpy as np
from math import sqrt

def cosine_similarity(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of same length")
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
    vocab.words_to_id[w] = c
    c+=1

  f.close()
  return animals, vocab

  
