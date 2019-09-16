from nn_acceptability import prepare_data, train_model
from math import isnan
import os


batchsize = 674
epochs = 457
hiddensize = 166
lrate = 0.008
wdecay = 0.006

#external_vector_file = ""
external_vector_file = "../../spaces/synsit/ext2vec.dm"
basedir = "synsit"
base_checkpointsdir = "./checkpoints/eva/ext2vec/synsit/"
if "fasttext" in external_vector_file:
    checkpointsdir = "./checkpoints/fasttext/optim/"
if "w2v" in external_vector_file:
    checkpointsdir = "./checkpoints/w2v/optim/"

words1_train,words2_train,scores_train,words1_val,words2_val,scores_val,ids_train,ids_val = prepare_data(external_vector_file,basedir)

def acceptability(hiddensize,lrate,wdecay,batchsize,epochs):
    score = train_model(words1_train,words2_train,scores_train,words1_val,words2_val,scores_val,ids_train,ids_val,int(hiddensize),lrate,wdecay,int(batchsize),int(epochs),checkpointsdir)
    if isnan(score):
        score = 0
    return score

for i in range(10):
    checkpointsdir=base_checkpointsdir+'5/'+str(i)+'/'
    if not os.path.exists(checkpointsdir):
        os.makedirs(checkpointsdir)
    score = acceptability(hiddensize,lrate,wdecay,batchsize,epochs)
    print("RUN",i,":",score)
