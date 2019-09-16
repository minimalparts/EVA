from bayes_opt import BayesianOptimization
from bayes_opt.observer import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
from nn_acceptability import prepare_data, train_model
from math import isnan

logger = JSONLogger(path="eva.ext2vec.synsit.optimisation_logs.r1.json")

# Bounded region of parameter space
pbounds = {'hiddensize': (100, 300), 'lrate': (0.001, 0.01), 'wdecay': (0.001,0.01), 'batchsize': (32,1024), 'epochs': (100,500)}

#hiddensize = 100
#lrate = 0.01
#wdecay = 0.001
#batchsize = 512
#epochs = 200

external_vector_file = "../../spaces/synsit/ext2vec.dm"
#external_vector_file = ""
basedir = "synsit"
checkpointsdir = "./checkpoints/eva/ext2vec/synsit/"
if "w2v" in external_vector_file:
    checkpointsdir = "./checkpoints/w2v/optim/"
if "w2v" in external_vector_file:
    checkpointsdir = "./checkpoints/w2v/optim/"

words1_train,words2_train,scores_train,words1_val,words2_val,scores_val,ids_train,ids_val = prepare_data(external_vector_file,basedir)

def compatibility(hiddensize,lrate,wdecay,batchsize,epochs):
    score = train_model(words1_train,words2_train,scores_train,words1_val,words2_val,scores_val,ids_train,ids_val,int(hiddensize),lrate,wdecay,int(batchsize),int(epochs),checkpointsdir)
    if isnan(score):
        score = 0
    return score

optimizer = BayesianOptimization(
    f=compatibility,
    pbounds=pbounds,
    random_state=1,
)

optimizer.subscribe(Events.OPTMIZATION_STEP, logger)
#load_logs(optimizer, logs=["eva.optimisation_logs.r1.json"])

optimizer.maximize(
    init_points=2,
    n_iter=200,
)

print(optimizer.max)
