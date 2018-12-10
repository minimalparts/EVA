import sys
sys.path.append("../")
import os, shutil
import sys
import random
import world, model, grammar
import distributional_semantics as ds

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

lemmas = [e.lemma for k,e in v.lexicon.items()]
test_word = random.sample(lemmas, 1)[0]

'''Start of simulation. Create a world.'''
a_world = world.World()
#a_world.populate_random("../noun-dataset.txt",5,3)
a_world.populate_from_file(sys.argv[1], v.lexicon)

'''Create a truth-theoretic model corresponding to the world.'''
true_model = model.Model()
true_model.mk_truth_theoretic(a_world, v.lexicon)

'''Create an entity space for that world.'''
print "CREATING AN ENTITY SPACE"
entity_space = ds.EntitySpace(v)
for entity in true_model.entities:
    entity_space.update_entity(entity)

'''Output world'''
print "\nPrinting world entities..."
test_noun = None
for entity in true_model.entities:
    print "ENTITY "+entity.ID
    pred_list = ""
    for p in entity.predicates:
        pred_list+=p.surface+" "
    print pred_list[:-1]

print "TESTING DENOTATION OF:",test_word
print "\n\nTrying to find the denotation of test word:",test_word
denot = true_model.denotation(test_word)
print [ d.ID for d in denot ]
