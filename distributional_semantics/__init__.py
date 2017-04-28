import numpy as np

class Vocabulary(object):

    def __init__(self):
        self.words = []
        self.words_to_id = {}

class Distribution(object):

    def __init__(self, word):
        self.word = word
        self.contexts = {}

class Context(object):

    def __init__(self, args, situation):
        self.args = args
        self.situation = situation
        self.dlfs = []

class Space(object):

    def __init__(self, vocab):
        self.vectors={}
        self.words_to_id = vocab.words_to_id
        for w in vocab.words:
            self.vectors[w] = np.zeros(len(vocab.words))
