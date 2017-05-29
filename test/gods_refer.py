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
from utils import read_dataset, printer

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
a_world = world.World("../animal-dataset.txt",15,3)

'''Create a truth-theoretic model corresponding to the world.'''
true_model = model.Model()
true_model.mk_truth_theoretic(a_world)

'''Output world'''
for entity in true_model.entities:
    print "ENTITY "+entity.ID
    pred_list = ""
    for p in entity.predicates:
        pred_list+=p.form+" "
    print pred_list[:-1]

kinds, vocab = read_dataset("../animal-dataset.txt")
god1 = speaker.Speaker("Vishnu",vocab,true_model)
god2 = speaker.Speaker("Artemis",vocab,true_model)

'''Refer: generate sentences about the actual entities of the domain.'''
for entity in god1.model.entities:
    words = []
    for p in entity.predicates:
        words.append(p.form)
    sentences = grammar.generate(words)
    for s in sentences:
        print "Vishnu says about",entity.ID,":",s

        '''Sanity check. Is it really true?'''
        truth, denotation = god2.model.true_interpretation(s)
        print "Artemis thinks this sentence is",truth
        for e in denotation:
            print e.ID
