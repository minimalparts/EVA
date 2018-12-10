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

#kinds, vocab = read_prob_file("../animal-dataset.txt")
god1 = speaker.Speaker("Vishnu",v,true_model)
god2 = speaker.Speaker("Artemis",v,true_model)

        

'''Refer: generate sentences about the actual entities of the domain.'''
for entity in god1.model.entities:
    words = god1.function_words(v.lexicon)
    for p in entity.predicates:
        words[p.surface] = v.lexicon[p.surface]
    sentences = grammar.generate(words)
    for s in sentences:
        print "\nVishnu says about",entity.ID,":",s.surface

        '''Sanity check. Is it really true?'''
        truth, justification = god2.model.interpretation_function_S(s.surface,v.lexicon)
        print "Artemis thinks this sentence is",truth
        print print_justification(justification)
