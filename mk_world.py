import sys
import numpy as np
import random
import world
import speaker
import distributional_semantics
from utils import read_dataset, cosine_similarity

'''Start of simulation. Create a world.'''
a_world = world.World([])

'''Record probability data to generate the world'''
animals, vocabulary = read_dataset("animal-dataset.txt")

'''Produce all instances in this world. 1000 of them.'''
entities = []
for n in range(1000):
  x = world.sample_animal("x"+str(n),animals)
  entities.append(x)

'''Produce all situations for this world. 10000 of them.'''
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

'''Situations S1 was exposed to. 500 of them.'''
for n in range(500):
  S1.experience(random.choice(a_world.situations))

for w,v in S1.distributions.items():
  for context in v:
    for lf in context.dlfs:
      print w,context.args,lf, context.situation

S1.mk_standard_vectors()


  
  

'''Say stuff about the world'''
#for s in S1.situations:
#  print s.entities
#  tell(s)
  


