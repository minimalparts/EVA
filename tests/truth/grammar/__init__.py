# -*- coding: utf-8 -*-

import re
import sys
import inspect
import numpy as np
import os.path
from random import randint

variables_in_use = []

def mk_lexicon():
    '''Takes lexicon from Visual Genome and throws in some quantifiers'''
    lexicon = open("grammar/lexicon.txt",'w')
    with open("../../data/synset_freqs.txt") as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split('\t')
        if len(fields) == 2:
            noun = fields[0][:-5]
            lexicon.write(noun+",LEMMA "+noun+",POS N,AGR sg\n")
            lexicon.write(noun+"s,LEMMA "+noun+",POS N,AGR pl\n")
    with open("../../data/attribute_freqs.txt") as f:
        lines = f.read().splitlines()
    for l in lines:
        fields = l.split('\t')
        if len(fields) == 2:
            att = fields[0]
            lexicon.write(att+",LEMMA "+att+",POS J,AGR null\n")
    lexicon.write("a,LEMMA a,POS D,AGR sg\n")
    lexicon.write("some,LEMMA some,POS D,AGR pl\n")
    lexicon.write("all,LEMMA all,POS D,AGR pl\n")
    lexicon.write("is,LEMMA be,POS V,AGR sg\n")
    lexicon.write("are,LEMMA be,POS V,AGR pl")
    lexicon.close() 


def mk_variable(typ):
    '''typ should be x or e.'''
    var = typ+str(randint(1,100))+'l'
    while var in variables_in_use:
        var = typ+str(randint(1,100))+'l'
    variables_in_use.append(var)
    return var
    

def unify(a,b):
    success = True
    if a == "null" and b != "null" :
        a = b
    if b == "null" and a != "null":
        b = a
    if a != b:
        success = False
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
    #print(classes)
    return classes

def fs_to_lf(fs):
    print(fs)

class Vocabulary(object):

    def __init__(self):
        if not os.path.isfile("grammar/lexicon.txt"):
            mk_lexicon() 
        self.lexicon = self.load_lexicon()

        self.word_strings = []
        self.labels_to_pos = {}
        self.pos_to_labels = {}
        c = 0
        for w in self.lexicon:
            self.word_strings.append(w)
            self.labels_to_pos[w] = c
            self.pos_to_labels[c] = w
            c+=1

    def load_lexicon(self):
        lexicon = {}
        f = open("grammar/lexicon.txt",'r')
        for l in f:
            l =l.rstrip('\n')
            entries = l.split(',')
            if len(entries) != 4:
                continue
            #print(entries)
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
            if surface not in lexicon:
                lexicon[surface] = [w]
            else:
                lexicon[surface].append(w)
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
        self.basis_transformation = None
        self.success = False

class Det(FS):

    def __init__(self,surface,lemma,agr):
        FS.__init__(self)
        self.surface = surface
        self.lemma = lemma
        self.pos = 'D'
        self.agr = agr
        self.arg0 = None
        self.arg1 = None
        self.arg2 = None

class Noun(FS):

    def __init__(self,surface,lemma,agr):
        FS.__init__(self)
        self.surface = surface
        self.lemma = lemma
        self.pos = 'N'
        self.agr = agr
        self.arg0 = None

class Adj(FS):

    def __init__(self,surface,lemma):
        FS.__init__(self)
        self.surface = surface
        self.lemma = lemma
        self.pos = 'J'
        self.arg0 = None
        self.arg1 = None

class Verb(FS):

    def __init__(self,surface,lemma,agr):
        FS.__init__(self)
        self.surface = surface
        self.lemma = lemma
        self.pos = 'V'
        self.agr = agr
        self.arg0 = None
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
                det.arg0 = mk_variable('x')
                self.daughters[1].arg0 = det.arg0
                det.arg1 = self.daughters[1].arg0
                self.arg0 = det.arg0
                self.success = True
                #print("Well-formed NP: %s." % self.surface)

class BareNP(FS_rule):

    def __init__(self, adj, noun):
        FS_rule.__init__(self)
        if isinstance(adj, Adj) and (isinstance(noun, Noun) or isinstance(noun, BareNP)):
            self.pos = "NP"
            self.agr = noun.agr
            self.surface = adj.surface+" "+noun.surface
            self.daughters = []
            self.daughters.append(adj)
            self.daughters.append(noun)
            adj.arg0 = self.daughters[1].arg0 if self.daughters[1].arg0 else mk_variable('x')
            self.daughters[1].arg0 = adj.arg0
            adj.arg1 = self.daughters[1].arg0
            self.arg0 = noun.arg0
            self.basis_transformation = "intersection"
            self.success = True
            #print("Well-formed BareNP: %s." % self.surface)



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
            adj.arg0 = mk_variable('x')
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
                            sentences.append(fs) 
        if len(stack) == stack_size:
            break
        else:
            stack_size = len(stack)
    return sentences


def parse_sentence(queue):
    #print("\nPARSING:",' '.join([i.surface for i in queue]))
    stack = []
    rules = find_subclasses(FS_rule)
    shift_or_reduce = True
    while shift_or_reduce and (len(queue) > 0 or len(stack) > 1):
        shift_or_reduce = False
        if len(queue) > 0:
            stack.append(queue[0])
            del(queue[0])
            #print("STACK:",stack,"LAST ON STACK:",stack[-1])
            #print("QUEUE:",queue)
            shift_or_reduce = True
        if len(stack) > 1:
            last = stack[-1]
            penul = stack[-2]
            #print("--LAST/PENUL",last,penul)
            for rule in rules:
                fs = rule(penul,last)
                if fs.success:
                    for i in range(2): 
                        stack.pop()
                    stack.append(fs)
                    shift_or_reduce = True
    if len(stack) > 1:
        #print("Parse failed.\n")
        return -1
    else:
        '''stack[0] is well-formed'''
        #print("Parse succeeded.\n")
    return stack[0]

def disambiguate(sentence,lexicon):
    '''Return a set of POS-disambiguated sentences'''
    words = sentence.split()
    sentences = []
    start_candidates = lexicon[words[0]]
    for candidate in start_candidates:
        sentences.append([candidate])
    new_sentences = []
    for w in words[1:]:
        candidates = lexicon[w]
        for i in range(len(sentences)):
            for candidate in candidates:
                sentence = sentences[i].copy()
                sentence.append(candidate)
                new_sentences.append(sentence)
        sentences = new_sentences
    sentences = [s for s in sentences if len(s) == len(words)]	#delete all intermediate steps
    return sentences
            
def get_space_operations(parse):
    lf = ""
    space_operations = []
    constituents = parse.daughters
    c1,c2 = constituents[0],constituents[1]
    space_operations.append((parse.basis_transformation,c1.surface+'_'+c1.pos,c2.surface+'_'+c2.pos))
    while len(constituents) > 0:
        dcs = []	#daughter constituents
        for c in constituents:
            if isinstance(c,FS_rule): 
                for d in c.daughters:
                    dcs.append(d)
                space_operations.append((c.basis_transformation,dcs[0].surface+'_'+dcs[0].pos,dcs[1].surface+'_'+dcs[1].pos))
            else:
                lf+=c.surface+"("+c.arg0+") "
        constituents = dcs
    print("PRINTING LF:",lf)
    print("PRINTING SPACE TRANSFORMATIONS:",space_operations)
    return lf,space_operations[::-1]	#return list in reverse order so that we start with the leaves
