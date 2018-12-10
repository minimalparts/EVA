import numpy as np
import grammar

class DLFTuple(object):
    '''A DLF tuple -- it has an argument and an LF composed of a single elementary predication'''
    def __init__(self,arg, lf):
        self.arg = arg
        self.lf = lf

class ContextSet(object):
    '''A context set comprising several DLFTuple objects'''
    def __init__(self):
        self.dlfs = []

class EntitySpace(object):

    def __init__(self, vocab):
        dimension = len(vocab.lexicon)
        self.mat = np.zeros(dimension)
        self.mat = self.mat.reshape(1,dimension)
        '''Define rows'''
        self.eID_to_pos = {}
        self.pos_to_eID = {}
        '''Define cols'''
        self.labels_to_pos = vocab.labels_to_pos
        self.pos_to_labels = vocab.pos_to_labels
        print "COLUMNS:",self.pos_to_labels

    def update_entity(self,e):
        if e.ID not in self.eID_to_pos:
            pos = len(self.eID_to_pos)
            self.eID_to_pos[e.ID] = pos
            self.pos_to_eID[pos] = e.ID
            self.mat = np.vstack([self.mat,np.zeros(len(self.mat[0]))])
        self.pred_to_vec(e)
        print e.ID,self.mat[self.eID_to_pos[e.ID]]

    def pred_to_vec(self,e):
        for predicate in e.predicates:
            p = predicate.surface
            self.mat[self.eID_to_pos[e.ID]][self.labels_to_pos[p]] = 1

    def denotation(self,predicates):
        '''TODO: does it make sense to have a 'distributional' denotation?'''
        return 0


class WordSpace(object):

    def __init__(self, vocab, context_sets):
        '''Make square matrix.'''
        dimension = len(vocab.lexicon)
        self.mat = np.zeros((dimension,dimension))
        self.labels_to_pos = vocab.labels_to_pos
        self.pos_to_labels = vocab.pos_to_labels
        '''Use ideal words to fill in matrix.'''
        for k,v in context_sets.items():
            if v != []:
                for tup in v:
                    self.mat[self.labels_to_pos[k]][self.labels_to_pos[tup[1]]]+=1
        print "LABELS:",self.pos_to_labels
        print "MATRIX:\n",self.mat

    def get_predicates(self,vector):
        '''Return the predicates corresponding to non-zero items in vector.'''
        predicates = []
        for i in range(len(vector)):
            if vector[i] > 0:
                predicates.append(self.pos_to_labels[i])
        return predicates



class IdealWords(object):

    def __init__(self, lexicon):
        '''Make context sets for ideal word representations.'''
        self.context_sets = {}
        for k,v in lexicon.items():
            if v.lemma not in self.context_sets and v.pos != 'D':
                self.context_sets[v.lemma] = []

    def get_occurrences(self, LF, justification):
        '''Get co-occurrences from a sentence LF and add to context set.'''
        entities = [e for entity_set in justification for e in entity_set]
        predicates = []
        constituents = LF.daughters
        while len(constituents) > 0:
            daughter_constituents = []
            for c in constituents:
                if isinstance(c,grammar.FS_rule):
                    for d in c.daughters:
                        daughter_constituents.append(d)
                else:
                    if c.pos != 'D':
                        predicates.append(c.lemma)
            constituents = daughter_constituents
        for i in range(len(predicates)-1):
            for j in range(i+1,len(predicates)):
                for e in entities:
                    if [e.ID,predicates[j]] not in self.context_sets[predicates[i]]:
                        self.context_sets[predicates[i]].append([e.ID,predicates[j]])
                    if [e.ID,predicates[i]] not in self.context_sets[predicates[j]]:
                        self.context_sets[predicates[j]].append([e.ID,predicates[i]])

 
    

def linalg(mat_heard,mat_known):

    #mat_heard = np.vstack((mat_heard,np.ones(mat_heard.shape[0])))
    w = np.linalg.lstsq(mat_heard,mat_known)[0] # obtaining the parameters
    return w

