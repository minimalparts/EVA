#------------------------------------------------------------------------------+
#
# Code inspired from the word2vec implementation by LakHeyM:
# https://github.com/LakheyM/word2vec/blob/master/word2vec_SGNS_git.ipynb
#
#------------------------------------------------------------------------------+


import numpy as np
import re
import os
from math import sqrt
from collections import defaultdict
import torch
import torch.nn as nn
import torch.optim as optim

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
base=os.path.abspath(os.path.join(os.path.realpath(__file__), "../.."))




class ext2vec():
    def __init__ (self, vocab, subspace, settings):
        self.n = settings['n']
        self.eta = settings['learning_rate']
        self.epochs = settings['epochs']
        self.neg_samps = settings['neg_samp']
        self.subspace = subspace

        self.target_matrix, self.context_matrix, self.criterion, self.optimizer = self.make_model(vocab, settings)
        torch.nn.init.xavier_uniform_(self.target_matrix.weight)
        torch.nn.init.xavier_uniform_(self.context_matrix.weight)


    def subsample_pair(self,p1,p2):
        r1 = np.random.rand()
        r2 = np.random.rand()
        if r1 < p1 or r2 < p2:
            return True
        else:
            return False


    def generate_coocs(self, predicate_matrix, vocab):
        true_data = []
        neg_data = []

        # GENERATE WORD COUNTS
        counts = list(predicate_matrix.sum(axis=1))

        #SUBSAMPLING
        subsampl_probs = [ 1 - sqrt(100 / f) for f in counts]

        words_sub = dict(zip(vocab, subsampl_probs))

        # GENERATE LOOKUP DICTIONARIES
        word_index = dict((word, i) for i, word in enumerate(vocab))
        index_word = dict((i, word) for i, word in enumerate(vocab))

        # CYCLE THROUGH EACH ROW OF THE MATRIX
        for i in range(len(vocab)):
            if vocab[i][-2:] != ".n":
                continue
            row = predicate_matrix[i]
            nz = np.nonzero(row)[0]
            #print(vocab[i],' '.join([vocab[s]+' '+str(row[s]) for s in range(len(row))]))
            for j in nz:
                p1 = subsampl_probs[i]
                p2 = subsampl_probs[j]
                for k in range(int(row[j])):
                    if not self.subsample_pair(p1,p2):
                        true_data.append([i,j,1])
                        #print(vocab[i],vocab[j],'1')
                        negs = np.where(row == 0)[0]
                        #print(vocab[i],' '.join([vocab[n] for n in negs]))
                        if len(negs) == 0:
                           negs = nz        #Hack to prevent problems when vector does not have non-zero entries
                        neg_samples = np.random.choice(negs,size=self.neg_samps)
                        for neg in neg_samples:
                            neg_data.append([i,neg,0])
                            #print(vocab[i],vocab[neg],'0')
        print(len(true_data),len(neg_data))
        return true_data, neg_data

    

    #Concatenate true_list, false_list
    #False list keeps changing each time joint list is drawn
    def gen_joint_list(self, true_list, false_list):
        joint_list = np.concatenate((np.array(true_list), np.array(false_list)), axis = 0)
        np.random.shuffle(joint_list)
        return joint_list


    def gen_batch(self, joint_list, batch_size, i):
        if i < len(joint_list)//batch_size:
            batch = joint_list[i*batch_size:i*batch_size+batch_size]
        
        else:
            batch = joint_list[i*batch_size:]
        return batch


    def one_hot_auto_batchwise(self, batch, vocab):
    
        iol_tensor = torch.Tensor(batch).long()
    
    
        middle_word_arr = torch.zeros(iol_tensor.shape[0], len(vocab))
        context_arr = torch.zeros(iol_tensor.shape[0], len(vocab))
        for i in range(len(iol_tensor)):
            middle_word_arr[i, iol_tensor[i, 0]] = 1
            context_arr[i, iol_tensor[i, 1]] = 1
        labels = iol_tensor[:, 2].float()
        return (middle_word_arr, context_arr, labels)


    def make_model(self, vocab, settings):
        embed_size = settings['n']
        LR = settings['learning_rate']
    
        target_matrix = nn.Linear(len(vocab), embed_size, bias = False)
        context_matrix = nn.Linear(len(vocab), embed_size, bias = False)

        target_matrix = target_matrix.to(device)
        context_matrix = context_matrix.to(device)

    
        criterion = nn.BCELoss()
    
        params = list(target_matrix.parameters()) + list(context_matrix.parameters())
        optimizer = optim.Adam(params, lr = LR)
    
        return(target_matrix, context_matrix, criterion, optimizer )



    def train(self, predicate_matrix, vocab):

        batch_size = 1000
        losses = []
        avg_losses = []

        #save files containing weights whenever losses are min
        save_path1 = base+'/spaces/'+self.subspace+'/e2v.target_dict.pth'
        save_path2 = base+'/spaces/'+self.subspace+'/e2v.context_dict.pth'
        save_path3 = base+'/spaces/'+self.subspace+'/e2v.target_wt.pth'


        for epoch in range(self.epochs):

            print("EPOCH",epoch)
    
            #Get fresh joint list with different random false samples
            true_data, neg_data = self.generate_coocs(predicate_matrix, vocab)
            joint_list = self.gen_joint_list(true_data, neg_data)
            num_batches = (len(joint_list)//batch_size) +1
    
            #Get i.th batch from joint list and proceed forward, backward
            for i in range(num_batches):  
        
                batch = self.gen_batch(joint_list, batch_size, i)
                target_oh, context_oh, labels = self.one_hot_auto_batchwise(batch, vocab)
    
    
                z_target = self.target_matrix(torch.Tensor(target_oh))
        
                z_context = self.context_matrix(torch.Tensor(context_oh))
        
                #vector product of word as input and word as target, not the product is parallelized and not looped
                #after training product/score for true pairs will be high and low/neg for false pairs
                dot_inp_tar = torch.sum(torch.mul(z_target, z_context), dim =1).reshape(-1, 1)
        
                #sigmoid activation squashes the scores to 1 or 0
                sig_logits = nn.Sigmoid()(dot_inp_tar)
        
                self.optimizer.zero_grad()
                loss = self.criterion(sig_logits, torch.Tensor(labels).view(sig_logits.shape[0], 1))
                loss.backward()
                self.optimizer.step()
       
                if i % 10 == 0: 
                    losses.append(loss.item())
                    avg = sum(losses) / len(losses)
                    avg_losses.append(avg)
                    losses.clear()
                    #print("AVG LOSS",avg,min(avg_losses))
        
                    if len(avg_losses) > 1 and avg < np.min(avg_losses[:-1]):
                        print(avg, np.min(avg_losses[:-1]))
                        torch.save(self.target_matrix.state_dict(), save_path1)
                        torch.save(self.context_matrix.state_dict(), save_path2)
                        torch.save(self.target_matrix.weight, save_path3)
    

    def pretty_print(self,vocab): 
        filename = base+'/spaces/'+self.subspace+'/ext2vec.dm'
        f = open(filename,'w')
        pretrained = torch.load(base+'/spaces/'+self.subspace+'/e2v.target_wt.pth')
        vectors = pretrained.t().data.cpu().numpy()
        for i in range(len(vocab)):
            f.write(vocab[i]+' '+' '.join([str(f) for f in vectors[i]])+'\n')
