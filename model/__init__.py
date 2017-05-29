#A model. We can set it up so that it is *the* model in a truth-theoretic way
#or a speaker's model in 'speaker-dependent truth' setup.

import random
import world
import grammar

class Entity(object):
    '''An entity in the model corresponds to a thing in the world.
    Attributes are converted to predicates here.'''
    def __init__(self, thing):
        self.ID = thing.ID
        self.predicates = []
        self.situations = []
        for a in thing.attributes:
            '''This entity is in a particular set, denoted by a particular predicate.'''
            if a[-1] == 'N':
                predicate = grammar.Noun(a)
            if a[-1] == 'V':
                predicate = grammar.Verb(a)
            self.predicates.append(predicate)
        for s in thing.scenes:
            self.situations.append(s)

class Situation(object):
    '''A situation in the model corresponds to a scene in the world.'''
    def __init__(self, scene):
        self.ID = scene.ID
        self.entities = []
        for thing in scene.things:
            self.entities.append(thing)

class Model(object):

    def __init__(self):
	'''The domain is made of collections of entities and situations in the world.'''
        self.entities = []
        self.situations = []

    def mk_truth_theoretic(self, world):
	'''In this setup, the model is a perfect reflection of the world.'''
        for thing in world.things:
            e = Entity(thing)
            self.entities.append(e)

	for scene in world.scenes:
            s = Situation(scene)
	    self.situations.append(s)

    def mk_speaker_model(self, world, num_entities):
	'''In this setup, the model is initialised with a random set of
        experiences for the speaker.'''
        things = random.sample(world.things,num_entities)
        for thing in things:
            e = Entity(thing)
	    self.entities.append(e)
        #TODO: sort out situations

    def true_interpretation(self, u):
	'''The interpretation function in a truth-theoretic setting. 
        Given an utterance (proposition or predication), return a 
        truth-value (proposition) and/or a set (predication).'''

        truth_value = None
        denotation = []
        if isinstance(u,grammar.Noun) or isinstance(u,grammar.Verb):
            for entity in self.entities:
                for predicate in entity.predicates:
                    if predicate.surface == u.surface: 
                        #print "Match:",entity.ID
                        denotation.append(entity)
            denotation = set(denotation)

        if isinstance(u,basestring):
            ID, pred1, pred2 = grammar.parse_sentence(u)
            t1, denotation1 = self.true_interpretation(pred1)
            t2, denotation2 = self.true_interpretation(pred2)
            denotation = denotation1.intersection(denotation2)
            
        if  len(denotation) > 0:
            truth_value = True
        else:
            truth_value = False
        return truth_value,denotation

    def print_me(self): 
        '''Output model'''
        for entity in self.entities:
            print "ENTITY "+entity.ID
            pred_list = ""
            for p in entity.predicates:
                pred_list+=p.form+" "
            print pred_list[:-1]
