import distributional_semantics
import world
import random
import utils
import re
import numpy as np
import grammar

class Speaker(object):

    def __init__(self, name, vocab, model):
        self.name = name
        self.model = model
        self.vocab = vocab
        self.told = []
        self.heard = []
        self.distributional_vector_space = distributional_semantics.Space(vocab)
        self.ideal_vector_space = distributional_semantics.Space(vocab)


    def experience(self, entity):
        '''Experiencing a new situation means appending it to the stored situations
        and updating the entity store.'''
        self.model.entities.append(entity)
        self.update_entity_sets(entity,True)


    def update_entity_sets(self,entity,experienced):
        '''Assumption: also filling linguistic entities from experiences (not just utterances the speaker was exposed to)'''
        '''For now, we are just appending 'e/h' to entity ID, to convert it into a linguistic entity of type 'experienced' or 'heard'.'''
        '''The correspondence between linguistic and world entity is however not necessarily known to the speaker/hearer.'''

        linguistic_entity = entity.ID+'k' if experienced else entity.ID+'h'
        if linguistic_entity not in self.model.entities:
            se = distributional_semantics.SparseEntity(linguistic_entity)
            #In this simple implementation, we know that cardinality of entities is 1
            se.cardinality = 1
            self.sparse_entities[linguistic_entity] = se
        se = self.sparse_entities[linguistic_entity]
        for predicate in entity.predicates:
            context = distributional_semantics.Context(se.ID,situation.ID)
            context.dlfs.append(predicate)
            se.contexts.append(context)
        context_set = []
        for context in se.contexts:
            for lf in context.dlfs:
                context_set.append(str(context.args)+' '+lf+' '+context.situation)
        utils.printer("./data/"+self.name+".context_sets.txt", context_set)
                

    def mk_vectors(self, know):
        '''This creates vectors for each word in the speaker's 
        distributions. We separate things the speaker has heard
        (distributional space) from things they know (ideal space). 
        Note: if the same entity occurs in several situations, the 
        count for a particular context is incremented once per situation.
        '''

        vector_type = 'k' if know else 'h'
        vector_space = self.ideal_vector_space if know else self.distributional_vector_space
        for ID,se in self.sparse_entities.items():
            #print se.word, se.ID, se.cardinality, [c.dlfs for c in se.contexts]
            if ID[-1] == vector_type:
                word = vector_space.contexts_to_id[se.word]
                for feature in (feature for c in se.contexts for feature in c.dlfs):
                    feature = vector_space.contexts_to_id[feature]
                    for vec, context in ((word, feature), (feature, word)):
                        vector_space.vectors[vec][context] += 1
        out = []
        for k,v in vector_space.vectors.items():
          out.append(vector_space.id_to_contexts[k]+" "+' '.join([str(n) for n in v]))
        utils.printer("./data/"+self.name+"."+vector_type+".vectors.txt",out)
        


    def tell(self,situation,test_kind):
        '''Tell *some* stuff about the situation (in logical forms).
	Make sure to tell about the test kind (so that we have enough data!'''

        print "\n",self.name,"tells things about situation",situation.ID,"..."
        es = []
        fs = []
        utterances = []
        for e in situation.entities:
          if any(p == test_kind for p in e.predicates):
            es.append(e)
        num_es = random.randint(1,len(situation.entities))
        es = list(set(es + random.sample(situation.entities,num_es)))
        #es = situation.entities
    
        for e in es:
           #Only report on a maximum of 3 features
           num_fs = random.randint(1,3)
           fs = random.sample(e.predicates, num_fs)
           for f in fs:
           #for f in e.features:
               #print e.ID, e.kind, f
               u = "<[("+e.ID+"), "+f+"("+e.ID+")]"+situation.ID+">"
               print u
               utterances.append(u)
        return utterances


    def hear(self,utterances):
        '''Hear what another speaker has said about a situation. The hearer is supposed to know which situation is talked about.
        I.e. for now, we assume that the hearer knows whether s/he shared the experience with the speaker.
        We also assume that speaker and hearer agree on what they have seen.
        '''

        #print self.name,"hears..."
        situation = grammar.parse_utterance(utterances[0])[2]
        if situation in self.situations:
           return -1						#situation is known to the hearer
        s = world.Situation(situation,[])			#temporary situation to store entities from the speaker's utterances
        self.situations.append(situation)        
        for u in utterances:
            ID, predicate, situation = grammar.parse_utterance(u)
            if not any(e.ID == ID for e in s.entities):
              x = world.Entity(ID,[])
              s.entities.append(x)
            for e in s.entities:
              if e.ID == ID:
                e.predicates.append(predicate)
                #print "Heard:",e.ID,feature
        self.update_sparse_entities(s,False)
       
