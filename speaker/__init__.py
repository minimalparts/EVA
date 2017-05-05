import distributional_semantics
import world
import random
import utils
import re
import numpy as np

class Speaker(object):

    def __init__(self, name, vocab):
        self.name = name
        self.situations = []
        self.told = []
        self.heard = []
        self.sparse_entities = {}						#A dictionary of sets, whether entities, plurals, or whatever.
        self.distributional_vector_space = distributional_semantics.Space(vocab)
        self.ideal_vector_space = distributional_semantics.Space(vocab)

    def experience(self, situation):
        '''Experiencing a situation means appending it to the stored situations
        and updating the entity store.'''
        self.situations.append(situation)
        self.update_sparse_entities(situation,True)



    def update_sparse_entities(self,situation,experienced):
        '''Assumption: also filling linguistic entities from experiences (not just utterances the speaker was exposed to)'''
        '''For now, we are just appending 'e/h' to entity name, to convert it into a linguistic entity of type 'experienced' or 'heard'.'''
        '''The correspondence between linguistic and world entity is however not necessarily known to the speaker/hearer.'''

        for entity in situation.entities:
            linguistic_entity = entity.name+'k' if experienced else entity.name+'h'
            if linguistic_entity not in self.sparse_entities:
                se = distributional_semantics.SparseEntity(entity.species,linguistic_entity)
                #In this simple implementation, we know that cardinality of entities is 1
                se.cardinality = 1
                self.sparse_entities[linguistic_entity] = se
            se = self.sparse_entities[linguistic_entity]
            for feature in entity.features:
                context = distributional_semantics.Context(se.name,situation.ID)
                context.dlfs.append(feature)
                se.contexts.append(context)
            context_set = []
            for context in se.contexts:
                for lf in context.dlfs:
                    context_set.append(se.word+' '+str(context.args)+' '+lf+' '+context.situation)
            utils.printer("./data/"+self.name+".context_set.txt", context_set)
                

    def mk_vectors(self, know):
        '''This creates vectors for each word in the speaker's 
        distributions. We separate things the speaker has heard
        (distributional space) from things they know (ideal space). 
        Note: if the same entity occurs in several situations, the 
        count for a particular context is incremented once per situation.
        '''

        vector_type = 'k' if know else 'h'
        vector_space = self.ideal_vector_space if know else self.distributional_vector_space
        for name,se in self.sparse_entities.items():
            #print se.word, se.name, se.cardinality, [c.dlfs for c in se.contexts]
            if name[-1] == vector_type:
                word = vector_space.contexts_to_id[se.word]
                for feature in (feature for c in se.contexts for feature in c.dlfs):
                    feature = vector_space.contexts_to_id[feature]
                    for vec, context in ((word, feature), (feature, word)):
                        vector_space.vectors[vec][context] += 1
        out = []
        for k,v in vector_space.vectors.items():
          out.append(vector_space.id_to_contexts[k]+" "+' '.join([str(n) for n in v]))
        utils.printer("./data/"+self.name+"."+vector_type+".vectors.txt",out)
        


    def tell(self,situation):
        '''Tell *some* stuff about the situation (in logical forms)'''

        #print "\n",self.name,"tells things about situation",situation.ID,"..."
        es = []
        fs = []
        utterances = []
        num_es = random.randint(1,len(situation.entities))
        es = random.sample(situation.entities,num_es)
        #es = situation.entities
    
        for e in es:
           #Only report on a maximum of 3 features
           num_fs = random.randint(1,3)
           fs = random.sample(e.features, num_fs)
           for f in fs:
           #for f in e.features:
               #print e.name, e.species, f
               u = "<[a("+e.name+"), "+e.species+"("+e.name+"), "+f+"("+e.name+")]"+situation.ID+">"
               #print u
               utterances.append(u)
        return utterances

    def parse_utterance(self,utterance):
        m = re.search(r"^<\[a\(.*, (.*)\((.*)\), (.*)\(.*\)\](.*)>",utterance)
        word = m.group(1)
        name = m.group(2)
        feature = m.group(3)
        situation = m.group(4)
        return word, name, feature, situation

    def hear(self,utterances):
        '''Hear what another speaker has said about a situation. The hearer is supposed to know which situation is talked about.
        I.e. for now, we assume that the hearer knows whether s/he shared the experience with the speaker.
        We also assume that speaker and hearer agree on what they have seen.
        '''

        #print self.name,"hears..."
        situation = self.parse_utterance(utterances[0])[3]
        if situation in self.situations:
           return -1						#situation is known to the hearer
        s = world.Situation(situation,[])			#temporary situation to store entities from the speaker's utterances
        self.situations.append(situation)        
        for u in utterances:
            word, name, feature, situation = self.parse_utterance(u)
            if not any(e.name == name for e in s.entities):
              x = world.Entity(name,word,[])
              s.entities.append(x)
            for e in s.entities:
              if e.name == name:
                e.features.append(feature)
                #print "Heard:",e.name,feature
        self.update_sparse_entities(s,False)
       
