#A model. We can set it up so that it is *the* model in a truth-theoretic way
#or a speaker's model in 'speaker-dependent truth' setup.

import random
import world
import grammar

class Entity(object):
    '''An entity in the model corresponds to a thing in the world.
    Attributes are converted to predicates here. We separate ID in 
    the model (ID) and ID in the world -- grounded (IDg).'''
    def __init__(self, thing, lexicon):
        self.ID = thing.ID
        self.IDg = thing.ID
        self.predicates = []
        self.situations = []
        for a in thing.attributes:
            self.predicates.append(lexicon[a])
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

    def mk_truth_theoretic(self, world, lexicon):
	'''In this setup, the model is a perfect reflection of the world.'''
        for thing in world.things:
            e = Entity(thing, lexicon)
            self.entities.append(e)

	for scene in world.scenes:
            s = Situation(scene)
	    self.situations.append(s)

    def mk_speaker_model(self, world, num_entities, name):
	'''In this setup, the model is initialised with a random set of
        experiences for the speaker.'''
        things = random.sample(world.things,num_entities)
        for thing in things:
            e = Entity(thing)
            e.ID = e.ID+"_"+name	#Distinguish IDs for different speakers
	    self.entities.append(e)
        #TODO: sort out situations

    def interpretation_function_S(self, s, lexicon):
	'''The interpretation function in a truth-theoretic setting. 
        Given an utterance (proposition or predication), return a 
        truth-value (proposition).'''

        truth_value = False
        justification = []
        parse = grammar.parse_sentence(s, lexicon)
        if isinstance(parse,grammar.S):
            NP = parse.daughters[0]
            VP = parse.daughters[1]
            np_sets = self.interpretation_function_NP(NP)
            #print "NP DENOTATION:",np_sets
            vp_set = self.interpretation_function_VP(VP)
            #print "VP DENOTATION:",vp_set
            for s in np_sets:
                intersect = list(set(s).intersection(set(vp_set))) 
                if len(intersect) > 0:
                    truth_value =True
                    for e in intersect:
                        justification.append(e)
        return truth_value, justification

    def interpretation_function_NP(self, np):
	'''The interpretation function in a truth-theoretic setting. 
        Given an NP, return a set of sets. This functions hard-codes
        two quantifiers (to be improved!)'''

        np_sets = []
        #print np.daughters
        restrictor = self.denotation(np.daughters[1].lemma)
        if len(np.daughters) > 2:
            for w in np.daughters[1:]:
                restrictor = restrictor.intersection(self.denotation(w.lemma))
        #print "DENOTATION",np.daughters[1].lemma,restrictor
        det = np.daughters[0]
        if det.surface == "a":
           for e in list(restrictor):
               singleton = [e]
               np_sets.append(singleton)
        if det.surface == "all":
           np_sets.append(list(restrictor)) 
        return np_sets


    def interpretation_function_VP(self,vp):
	'''The interpretation function in a truth-theoretic setting. 
        Given a VP, return a set.'''

        return list(self.denotation(vp.daughters[0].lemma))
        
        
    def denotation(self, word):
        '''Return the denotation of word. E.g. denotation('cat') will
        return the set of cats in the world.'''

        denotation = []
        for entity in self.entities:
            for predicate in entity.predicates:
                if predicate.surface == word: 
                    #print "Match:",entity.ID
                    denotation.append(entity)
        return set(denotation)
        


    def print_me(self): 
        '''Output model'''
        for entity in self.entities:
            print "ENTITY "+entity.ID
            pred_list = ""
            for p in entity.predicates:
                pred_list+=p.form+" "
            print pred_list[:-1]
