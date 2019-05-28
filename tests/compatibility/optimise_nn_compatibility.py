from bayes_opt import BayesianOptimization
from bayes_opt.observer import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
from nn_compatibility import prepare_data, train_model
from math import isnan

logger = JSONLogger(path="bert.optimisation_logs.r2.json")

# Bounded region of parameter space
pbounds = {'hiddensize': (100, 769), 'lrate': (0.001, 0.01), 'wdecay': (0.001,0.01), 'batchsize': (32,1024), 'epochs': (100,500)}

#hiddensize = 100
#lrate = 0.01
#wdecay = 0.001
#batchsize = 512
#epochs = 200

external_vector_file = "compatibility/models/in_vg_compatibility_bert_4l.txt"
#external_vector_file = "compatibility/models/compatibility_fasttext_vecs.txt"
#external_vector_file = ""
basedir = "synrel"
checkpointsdir = "./checkpoints/eva/optim/"
if "fasttext" in external_vector_file:
    checkpointsdir = "./checkpoints/fasttext/optim/"
if "bert" in external_vector_file:
    checkpointsdir = "./checkpoints/bert/optim/"

words1_train,words2_train,scores_train,words1_val,words2_val,scores_val,ids_train,ids_val = prepare_data(external_vector_file,basedir)

def compatibility(hiddensize,lrate,wdecay,batchsize,epochs):
    score = train_model(words1_train,words2_train,scores_train,words1_val,words2_val,scores_val,ids_train,ids_val,int(hiddensize),lrate,wdecay,int(batchsize),int(epochs),False,checkpointsdir)
    if isnan(score):
        score = 0
    return score

optimizer = BayesianOptimization(
    f=compatibility,
    pbounds=pbounds,
    random_state=1,
)

optimizer.subscribe(Events.OPTMIZATION_STEP, logger)
load_logs(optimizer, logs=["bert.optimisation_logs.r1.json"])

optimizer.maximize(
    init_points=2,
    n_iter=150,
)

print(optimizer.max)
