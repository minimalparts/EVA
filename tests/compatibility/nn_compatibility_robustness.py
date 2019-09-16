from nn_compatibility import prepare_data, train_model
from math import isnan
import os

batchsize = 88
epochs = 236
hiddensize = 272
lrate = 0.002
wdecay = 0.005

#external_vector_file = "data/models/compatibility_w2v_vg_desc_vecs.txt"
external_vector_file = "../../spaces/synattsit/ext2vec.dm"
#external_vector_file = ""
basedir = "synattsit"
base_checkpointsdir = "./checkpoints/eva/ext2vec/synattsit/"
if "fasttext" in external_vector_file:
    checkpointsdir = "./checkpoints/fasttext/optim/"
if "bert" in external_vector_file:
    checkpointsdir = "./checkpoints/bert/optim/"
if "w2v" in external_vector_file:
    checkpointsdir = "./checkpoints/w2v/optim/"

words1_train,words2_train,scores_train,words1_val,words2_val,scores_val,ids_train,ids_val = prepare_data(external_vector_file,basedir)

def compatibility(hiddensize,lrate,wdecay,batchsize,epochs,checkpointsdir):
    score = train_model(words1_train,words2_train,scores_train,words1_val,words2_val,scores_val,ids_train,ids_val,int(hiddensize),lrate,wdecay,int(batchsize),int(epochs),checkpointsdir)
    if isnan(score):
        score = 0
    return score

for i in range(10):
    checkpointsdir=base_checkpointsdir+'5/'+str(i)+'/'
    if not os.path.exists(checkpointsdir):
        os.makedirs(checkpointsdir)
    score = compatibility(hiddensize,lrate,wdecay,batchsize,epochs,checkpointsdir)
    print("RUN",i,":",score)
