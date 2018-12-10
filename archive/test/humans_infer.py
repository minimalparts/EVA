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
from utils import read_prob_file, printer

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
real_world = world.World()
real_world.populate_random("../animal-dataset.txt",500,30)

kinds, vocab = read_prob_file("../animal-dataset.txt")

'''Make S1'''
print "Making speaker S1..."
m1 = model.Model()
m1.mk_speaker_model(real_world,300,"1")
m1.print_me()
S1 = speaker.Speaker("Kim",vocab,m1)


'''Refer: generate sentences about the entities the speaker knows about.
From the generated utterances, learn to infer what is known. The speaker
is basically talking to himself/herself.'''
for entity in S1.model.entities:
    sentences = S1.tell(entity)
    for s in sentences:
        print "S1 says about",entity.ID,":",s
        truth, denotation = S1.model.true_interpretation(s)
