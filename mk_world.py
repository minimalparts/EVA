import os
import sys
import numpy as np
import random
import world
import speaker
import distributional_semantics
from utils import read_dataset, cosine_similarity, printer

world_files = ["S1.knowledge.txt", "S2.knowledge.txt", "S1.vectors.txt", "S2.vectors.txt", "world.txt"]
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

'''Produce all situations for this world. 10 of them.'''
situations = []
for n in range(10):
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
experiences = random.sample(a_world.situations,5)
for e in experiences:
  #print "S1 experiences",e.ID
  S1.experience(e)

'''Situations S2 was exposed to. 5 of them.'''
experiences = random.sample(a_world.situations,5)
for e in experiences:
  S2.experience(e)

'''S1 says stuff about the world. S2 listens.'''
s1_utterances = []
for s in S1.situations:
  s1_utterances = S1.tell(s)
  S2.hear(s1_utterances)
        
S1.mk_standard_vectors()
S2.mk_standard_vectors()
