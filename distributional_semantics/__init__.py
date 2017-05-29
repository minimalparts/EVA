import numpy as np

class EntitySet(object):
    '''An set with its contexts, which in principle could be of any cardinality.'''
    def __init__(self, var_ID):
        self.ID = var_ID
        self.cardinality = -1		#cardinality of the set. -1 for unknown
        self.contexts = []		

class Context(object):
    '''A context set is for one particular situation'''
    '''In this simple implementation, we only have one logical form per context, but generally dlfs should be a list.'''
    def __init__(self, args, situation):
        self.args = args
        self.situation = situation
        self.dlfs = []

class Space(object):

    def __init__(self, vocab):
        self.vectors={}
        self.contexts_to_id = vocab.contexts_to_id
        self.id_to_contexts = vocab.id_to_contexts
        for word_id in self.id_to_contexts:
            self.vectors[word_id] = np.zeros(len(vocab.words))

def linalg(mat_heard,mat_known):

    #mat_heard = np.vstack((mat_heard,np.ones(mat_heard.shape[0])))
    w = np.linalg.lstsq(mat_heard,mat_known)[0] # obtaining the parameters
    return w

