import os
import sys
import numpy as np
import random
import world
import speaker
import distributional_semantics
from utils import read_dataset, cosine_similarity, printer, mk_ideal_matrix, mk_dist_matrix, binarise, normalise

np.set_printoptions(suppress=True)

world_files = ["S1.knowledge.txt", "S2.knowledge.txt", "S1.h.vectors.txt", "S1.k.vectors.txt", "S2.h.vectors.txt", "S2.k.vectors.txt", "world.txt"]
for f in world_files:
  if os.path.isfile(f):
    os.remove(f)

'''Start of simulation. Create a world.'''
a_world = world.World([])

'''Record probability data to generate the world'''
animals, vocabulary = read_dataset("animal-dataset.txt")
print "The vocabulary has",len(vocabulary.words),"entries."

'''Produce all instances in this world. 1000 of them.'''
entities = []
for n in range(1000):
  x = world.sample_animal("x"+str(n),animals)
  entities.append(x)

'''Produce all situations for this world. 1000 of them.'''
situations = []
for n in range(1000):
  s = world.sample_situation("S"+str(n), entities)
  a_world.situations.append(s)

'''Record world'''
world_file=open("world.txt",'w')
for s in a_world.situations:
  for e in s.entities:
    for f in e.features:
      world_file.write(s.ID+","+e.name+","+e.species+","+f+"\n")
world_file.close()



'''Now create speakers'''
S1 = speaker.Speaker("S1",vocabulary)
S2 = speaker.Speaker("S2",vocabulary)
S3 = speaker.Speaker("S3",vocabulary)

'''Situations S1 was exposed to. 5 of them.'''
experiences = random.sample(a_world.situations,500)
for e in experiences:
  #print "S1 experiences",e.ID
  S1.experience(e)

'''Situations S2 was exposed to. 5 of them.'''
experiences = random.sample(a_world.situations,200)
for e in experiences:
  S2.experience(e)

'''S1 says stuff about the world. S2 listens.'''
s1_utterances = []
for s in S1.situations:
  s1_utterances = S1.tell(s)
  S2.hear(s1_utterances)
        
S1.mk_vectors(True)
S2.mk_vectors(True)
S2.mk_vectors(False)

s2_ideal_space, vocab = mk_ideal_matrix(S2.ideal_vector_space, S2.distributional_vector_space, len(vocabulary.words), True)
s2_dist_space = mk_dist_matrix(S2.distributional_vector_space, len(vocabulary.words), vocab)
ones = np.ones((1,s2_dist_space.shape[0]))
s2_dist_space = np.hstack((s2_dist_space,ones.T))
w = distributional_semantics.linalg(s2_dist_space, s2_ideal_space)

rest_dist_space = mk_dist_matrix(S2.distributional_vector_space, len(vocabulary.words), vocabulary.words)
ones = np.ones((1,rest_dist_space.shape[0]))
rest_dist_space = np.hstack((rest_dist_space,ones.T))
test = normalise(np.dot(rest_dist_space,w))

#Sanity check. Do we recover the original values of the ideal space?
print vocabulary.id_to_contexts
s2_ideal_space, all_vocab = mk_ideal_matrix(S2.ideal_vector_space, S2.distributional_vector_space, len(vocabulary.words), False)
for i in range(len(rest_dist_space)):
  word = vocabulary.contexts_to_id[vocabulary.words[i]]
  if word in vocab:
    print vocabulary.id_to_contexts[word], cosine_similarity(s2_ideal_space[i],normalise(test[i]))
    for j in range(len(test[i])):
      if s2_ideal_space[i][j] > 0.05:
        print vocabulary.id_to_contexts[j], s2_ideal_space[i][j], test[i][j]
    
#Now output all values
for i in range(len(S2.distributional_vector_space.vectors)):
  print i,vocabulary.words[i]
  for j in range(len(test[i])):
    if test[i][j] > 0.05:
      print vocabulary.id_to_contexts[j], test[i][j]
