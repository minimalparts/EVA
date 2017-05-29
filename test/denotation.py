import sys
sys.path.append("../")
import os, shutil
import sys
import world
import model
import grammar

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
a_world = world.World("../animal-dataset.txt",50,30)

'''Create a truth-theoretic model corresponding to the world.'''
true_model = model.Model()
true_model.mk_truth_theoretic(a_world)

'''Output world and pick test animal'''
print "Printing world entities..."
test_animal = None
for entity in true_model.entities:
    if test_animal == None:
       test_animal = entity.predicates[0]
    print "ENTITY "+entity.ID
    pred_list = ""
    for p in entity.predicates:
        pred_list+=p.surface+" "
    print pred_list[:-1]

print "\n\nTrying to find the denotation of test animal:",test_animal.surface
truth,test_set = true_model.true_interpretation(test_animal)

to_print = (' '.join(e.ID for e in test_set))
print "\n",test_animal.surface,":",to_print
