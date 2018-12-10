import sys
sys.path.append("../")
import os, shutil
import sys
import numpy as np
import random
import world
import model
import grammar
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

'''Start of simulation. Create a world.'''
a_world = world.World()
#a_world.populate_random("../animal-dataset.txt",5,3)
a_world.populate_from_file(sys.argv[1], v.lexicon)

'''Create a truth-theoretic model corresponding to the world.'''
true_model = model.Model()
true_model.mk_truth_theoretic(a_world, v.lexicon)

'''Output world'''
for entity in true_model.entities:
    print "ENTITY "+entity.ID
    pred_list = ""
    for p in entity.predicates:
        pred_list+=p.surface+" "
    print pred_list[:-1]

'''Generate all possible sentences from vocabulary'''
#kinds, vocabulary = read_prob_file("../animal-dataset.txt")

print "Generating all possible sentences from the grammar..."
sentences = grammar.generate(v.lexicon)
print sentences

for s in sentences:
    truth, justification = true_model.interpretation_function_S(s, v.lexicon)
    #print s, truth, [e.ID for e in justification]
    print s, truth, print_justification(justification)
