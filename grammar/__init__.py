# -*- coding: utf-8 -*-

import re
import sys
import inspect
import numpy as np
from random import randint

variables_in_use = []

def mk_variable(typ):
    '''typ should be x or e.'''
    var = typ+str(randint(1,100))+'l'
    while var in variables_in_use:
        var = typ+str(randint(1,100))+'l'
    return var
    

def unify(a,b):
    success = True
    if a != b:
        success = False
    if a == "null" and b != "null" :
        a = b
    if b == "null" and a != "null":
        b = a
    return a,b,success

def find_subclasses(desired_class):
    classes = []
    module = sys.modules[__name__] #get current module
    for name in dir(module):
        o = getattr(module, name)
        try:
            if (o != desired_class) and issubclass(o, desired_class):
                classes.append(o)
        except TypeError: pass
    return classes

def fs_to_lf(fs):
    print fs

class Vocabulary(object):

    def __init__(self,lexicon_file):
        self.lexicon = self.load_lexicon(lexicon_file)

        self.word_strings = []
        self.labels_to_pos = {}
        self.pos_to_labels = {}
        c = 0
        for w in self.lexicon:
            self.word_strings.append(w)
            self.labels_to_pos[w] = c
            self.pos_to_labels[c] = w
            c+=1

    def load_lexicon(self,lexicon_file):
        lexicon = {}
        f = open(lexicon_file,'r')
        for l in f:
            l =l.rstrip('\n')
            entries = l.split(',')
            #print entries
            surface = entries[0]
            lemma = entries[1].split()[1]
            pos = entries[2].split()[1]
            agr = entries[3].split()[1]
            if pos == 'N':
                w = Noun(surface,lemma,agr)
            if pos == 'V':
                w = Verb(surface,lemma,agr)
            if pos == 'D':
                w = Det(surface,lemma,agr)
            if pos == 'J':
                w = Adj(surface,lemma)
            lexicon[surface] = w
        f.close()
        return lexicon
               
 
class FS(object):

    def __init__(self):
        self.surface = None
        self.pos = None
        self.agr = None
        self.arg0 = None

class FS_rule(FS):

    def __init__(self):
        FS.__init__(self)
        self.success = False

class Det(FS):

    def __init__(self,surface,lemma,agr):
        FS.__init__(self)
        self.surface = surface
        self.lemma = lemma
        self.pos = 'D'
        self.agr = agr
        self.arg0 = mk_variable('x')
        self.arg1 = None
        self.arg2 = None

class Noun(FS):

    def __init__(self,surface,lemma,agr):
        FS.__init__(self)
        self.surface = surface
        self.lemma = lemma
        self.pos = 'N'
        self.agr = agr
        self.arg0 = mk_variable('x')

class Adj(FS):

    def __init__(self,surface,lemma):
        FS.__init__(self)
        self.surface = surface
        self.lemma = lemma
        self.pos = 'J'
        self.arg0 = mk_variable('x')
        self.arg1 = None

class Verb(FS):

    def __init__(self,surface,lemma,agr):
        FS.__init__(self)
        self.surface = surface
        self.lemma = lemma
        self.pos = 'V'
        self.agr = agr
        self.arg0 = mk_variable('e')
        self.arg1 = None

class NP(FS_rule):

    def __init__(self, det, noun):
        FS_rule.__init__(self)
        if isinstance(det, Det) and isinstance(noun, Noun):
            det.agr, noun.agr, u = unify(det.agr, noun.agr)
            if u:
                self.pos = "NP"
                self.agr = noun.agr
                self.surface = det.surface+" "+noun.surface
                self.daughters = []
                self.daughters.append(det)
                self.daughters.append(noun)
                self.daughters[1].arg0 = det.arg0
                det.arg1 = self.daughters[1].arg0
                self.arg0 = det.arg0
                self.success = True
                #print "Well-formed NP: %s." % self.surface


class VP(FS_rule):

    def __init__(self, copula, adj):
        FS_rule.__init__(self)
        if copula.surface in ["is", "are"] and isinstance(adj, Adj):
            self.pos = "VP"
            self.agr = copula.agr
            self.surface = copula.surface+" "+adj.surface
            self.daughters = []
            #self.daughters.append(copula)
            self.daughters.append(adj)
            self.arg0 = adj.arg0
            self.success = True
            #print "Well-formed VP: %s." % self.surface

class S(FS_rule):

    def __init__(self, np, vp):
        FS_rule.__init__(self)
        if isinstance(np, NP) and isinstance(vp,VP):
            np.agr, vp.agr, u = unify(np.agr, vp.agr)
            if u:
                self.pos = 'S'
                self.agr = vp.agr
                self.surface = np.surface+" "+vp.surface
                self.daughters = []
                self.daughters.append(np) 
                self.daughters.append(vp) 
                self.arg0 = vp.arg0
                np.daughters[0].arg2 = vp.arg0
                vp.daughters[0].arg0 = np.arg0
                self.success = True
                #print "Well-formed sentence: %s." % self.surface
    def __repr__(self):
        return "<Rule_S_V result pos:%s agr:%s>" % (self.pos, self.agr)


def generate(lexicon):
    '''Generate all possible sentences from a set of words.'''
    sentences = []
    stack = []
    #print "Find subclasses of FS"
    rules = find_subclasses(FS_rule)
    for k,w in lexicon.items():
        stack.append(w)
    while True:
        stack_size = len(stack)
        for rule in rules:
            for w1 in stack:
                for w2 in stack:
                    fs = rule(w1,w2)
                    if fs.success and fs.surface not in [ f.surface for f in stack ]:
                        stack.append(fs)
                        if fs.pos == 'S':
                            sentences.append(fs.surface) 
        if len(stack) == stack_size:
            break
        else:
            stack_size = len(stack)
    return sentences


def parse_sentence(sentence, lexicon):
    #print "PARSING:",sentence
    stack = []
    queue = sentence.split()
    rules = find_subclasses(FS_rule)
    shift_or_reduce = True
    while shift_or_reduce and (len(queue) > 0 or len(stack) > 1):
        shift_or_reduce = False
        if len(queue) > 0:
            stack.append(queue[0])
            if stack[-1] in lexicon:
                stack.pop()
                stack.append(lexicon[queue[0]])
                del(queue[0])
                shift_or_reduce = True
        if len(stack) > 1:
            last = stack[-1]
            penul = stack[-2]
            for rule in rules:
                fs = rule(penul,last)
                if fs.success:
                    for i in range(2): 
                        stack.pop()
                    stack.append(fs)
                    shift_or_reduce = True
    if len(stack) > 1:
        print "Parse failed."
    else:
        '''stack[0] is a sentence'''
        #print "PARSE:", stack[0].daughters
        print_LF(stack[0])
    return stack[0]
            
def print_LF(parse):
    lf = ""
    constituents = parse.daughters
    while len(constituents) > 0:
        daughter_constituents = []
        for c in constituents:
            #print "CONSTITUENT",c
            if isinstance(c,FS_rule): 
                for d in c.daughters:
                    daughter_constituents.append(d)
                #print "APPENDING DAUGHTERS",daughter_constituents
            else:
                lf+=c.surface+"("+c.arg0+") "
        constituents = daughter_constituents
    print lf
   
