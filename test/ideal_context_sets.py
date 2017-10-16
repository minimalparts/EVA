import sys
sys.path.append("../")
import os, shutil
import sys
import numpy as np
import random
import world, model, grammar, speaker, distributional_semantics
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

S = speaker.Speaker("Ideal",v,true_model)
IW = distributional_semantics.IdealWords(v.lexicon)

'''Refer: generate sentences about the actual entities of the domain.'''
print "Generating all possible sentences from the grammar..."
sentences = grammar.generate(v.lexicon)

print "Checking which sentences are true..."
for s in sentences:
    truth, justification = true_model.interpretation_function_S(s.surface, v.lexicon)
    if truth:
        #print s, truth, print_justification(justification)
        print s.surface
        IW.get_occurrences(s,justification[0])

print IW.context_sets
