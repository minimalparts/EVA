import sys
sys.path.append("../")
import os, shutil
import sys
import numpy as np
import random
import world
import model
import grammar
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
a_world = world.World("../animal-dataset.txt",5,3)

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

'''Generate all possible sentences from vocabulary'''
kinds, vocabulary = read_dataset("../animal-dataset.txt")

print "Generating all possible sentences from the grammar..."
sentences = grammar.generate(vocabulary.words)

print "These sentences are true:"
for s in sentences:
    truth, denotation = true_model.true_interpretation(s)
    if truth:
        print s
