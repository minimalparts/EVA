import os, shutil
import sys
import numpy as np
import random
import world
import speaker
import distributional_semantics
from utils import read_dataset, cosine_similarity, printer, mk_ideal_matrix, mk_dist_matrix, binarise, normalise

np.set_printoptions(suppress=True)

'''Create data directory if it does not exist.'''
if not os.path.exists("./data"):
    os.makedirs("./data")


'''Remove content of data/ directory.'''
folder = './data/'
for f in os.listdir(folder):
    file_path = os.path.join(folder, f)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)

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
world_file=open("./data/world.txt",'w')
for s in a_world.situations:
  for e in s.entities:
    for f in e.features:
      world_file.write(s.ID+","+e.name+","+e.species+","+f+"\n")
world_file.close()



'''Now create speakers'''
S1 = speaker.Speaker("S1",vocabulary)
S2 = speaker.Speaker("S2",vocabulary)

'''Situations S1 was exposed to. 100 of them.'''
s1_situations = random.sample(a_world.situations,500)
for s in s1_situations:
  #print "S1 experiences",e.ID
  S1.experience(s)

'''Situations S2 was exposed to. 500 of them.'''
s2_situations = random.sample(a_world.situations,500)
for s in s2_situations:
  S2.experience(s)

'''S1 says stuff about the world. S2 listens.'''
s1_utterances = []
for s in S1.situations:
  s1_utterances = S1.tell(s)
  S2.hear(s1_utterances)
        
S1.mk_vectors(True)
S2.mk_vectors(True)
S2.mk_vectors(False)

'''Performing linear regression on the info that S2
has heard about (their distributional space) vs what 
they know (their ideal space).'''
s2_ideal_space, tmp_vocab = mk_ideal_matrix(S2.ideal_vector_space, S2.distributional_vector_space, len(vocabulary.words), True)
s2_dist_space = mk_dist_matrix(S2.distributional_vector_space, len(vocabulary.words), tmp_vocab)
ones = np.ones((1,s2_dist_space.shape[0]))
s2_dist_space = np.hstack((s2_dist_space,ones.T))
w = distributional_semantics.linalg(s2_dist_space, s2_ideal_space)

tmp_vocab = []
for word in vocabulary.words:
  tmp_vocab.append(vocabulary.contexts_to_id[word])
entire_dist_space = mk_dist_matrix(S2.distributional_vector_space, len(vocabulary.words), tmp_vocab)
ones = np.ones((1,entire_dist_space.shape[0]))
entire_dist_space = np.hstack((entire_dist_space,ones.T))
inferences = normalise(np.dot(entire_dist_space,w))

#Sanity check. Do we recover the original values of the ideal space?
#print vocabulary.id_to_contexts
#print "\n\nChecking we are roughly recovering original 'ideal' values \
#after linear regression... (Only printing 'high values'.)"
#s2_ideal_space, all_vocab = mk_ideal_matrix(S2.ideal_vector_space, S2.distributional_vector_space, len(vocabulary.words), False)
#for i in range(len(rest_dist_space)):
#  word = vocabulary.contexts_to_id[vocabulary.words[i]]
#  if word in tmp_vocab:
#    print "\n",vocabulary.id_to_contexts[word], cosine_similarity(s2_ideal_space[i],normalise(test[i]))
#    for j in range(len(test[i])):
#      if s2_ideal_space[i][j] > 0.05:
#        print vocabulary.id_to_contexts[j], s2_ideal_space[i][j], test[i][j]
    
#Now output all values
print "\n\nNow let's check what S2 has inferred from the learnt regression. \
Also for concepts they did not know before."
for i in range(len(S2.distributional_vector_space.vectors)):
  print "\n",i,vocabulary.words[i]
  for j in range(len(inferences[i])):
    if inferences[i][j] > 0.05:
      print vocabulary.id_to_contexts[j], inferences[i][j]
