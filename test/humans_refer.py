import sys
sys.path.append("../")
import os, shutil
import sys
import numpy as np
import random
import world
import model
import grammar
import speaker
from utils import read_prob_file, read_world_file, printer, print_justification

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

v = grammar.Vocabulary("../grammar/lexicon.txt")

'''Start of simulation. Create a world and let's assume this is
the real world.'''
real_world = world.World()
real_world.populate_from_file(sys.argv[1], v.lexicon)


'''Let's share the vocab between speakers for now.'''
#kinds, vocab = read_prob_file("../animal-dataset.txt")

'''Make S1'''
print "\nMaking speaker S1..."
m1 = model.Model()
m1.mk_speaker_model(real_world,v.lexicon,5,"1")
m1.print_me()
S1 = speaker.Speaker("Kim",v,m1)

'''Make S2'''
print "\nMaking speaker S2..."
m2 = model.Model()
m2.mk_speaker_model(real_world,v.lexicon,2,"2")
m2.print_me()
S2 = speaker.Speaker("Sandy",v,m2)

print "\nSpeaker overlap (the instances that both speakers know about)...\n"
s1_e=[]
for e in S1.model.entities:
    s1_e.append(e.IDg)
s2_e=[]
for e in S2.model.entities:
    s2_e.append(e.IDg)
print set(s1_e).intersection(set(s2_e))

'''Refer: generate sentences about the actual entities of the domain.'''
    sentences = S1.tell(entity, v)
    for s in sentences:
        print "S1 says about",entity.ID,":",s

        '''S2 checks. Is it really true?'''
        truth, justification = S2.model.interpretation_function_S(s,v.lexicon)
        print "S2 thinks this sentence is",truth
        print print_justification(justification)
