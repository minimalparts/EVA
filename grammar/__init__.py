# -*- coding: utf-8 -*-

import re
import numpy as np
from random import randint

class Vocabulary(object):

    def __init__(self):
        self.words = []
        self.contexts_to_id = {}
        self.id_to_contexts = {}



class Noun(object):

    def __init__(self,noun):
        '''Surface form is without POS tag.'''
        self.surface = noun[:-2]
        self.form = noun
        self.arg0 = 'x'+str(randint(1,100))+'l'

class Verb(object):

    def __init__(self,verb):
        '''Surface form is without POS tag or underscores.'''
        self.surface = verb[:-2].replace("_"," ")
        self.form = verb
        self.arg0 = 'e'+str(randint(1,100))+'l'
        self.arg1 = None

class Sentence(object):

    def __init__(self,noun,verb):
        self.surface=""
        self.lf=""
        self.head=None
        if isinstance(noun,Noun) and isinstance(verb,Verb):
            self.head = verb.arg0
            verb.arg1 = noun.arg0
            '''Surface form is concatenation of surfaces of noun and verb.'''
            self.surface = noun.surface+" "+verb.surface
            #self.lf = "a("+noun.arg0+"),"+noun.surface+u"\u00b0("+noun.arg0+"), "+verb.surface+u"\u00b0("+verb.arg0+","+verb.arg1+")]"
            self.lf = "a("+noun.arg0+"), "+noun.form+"("+noun.arg0+"), "+verb.form+"("+verb.arg0+","+verb.arg1+")"
        else:
            raise ValueError('The passed arguments are not a noun and a verb.')            

def convert_word_to_pred(w):
    predicate = None
    if w[-1] == 'N':
        predicate = Noun(w)
    if w[-1] == 'V':
        predicate = Verb(w)
    return predicate

def generate(words):
    '''Generate all possible sentences from a set of words.'''
    sentences = []
    for w1 in words:
        for w2 in words:
            p1 = convert_word_to_pred(w1)
            p2 = convert_word_to_pred(w2)
            if isinstance(p1,Noun) and isinstance(p2,Verb):
                s = Sentence(p1,p2)
                sentences.append(s.lf)
                #print s.lf
    return sentences


def parse_sentence(sentence):
    #m = re.search(r"^<\[\((.*)\), (.*)\(.*\)\](.*)>",utterance)
    m = re.search("a\(.*\), (.*)\((.*)\), (.*)\(.*\)",sentence)
    predicate1 = convert_word_to_pred(m.group(1))
    predicate2 = convert_word_to_pred(m.group(3))
    ID = m.group(2)
    #situation = m.group(3)
    return ID, predicate1, predicate2
