import distributional_semantics
import model
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
        #self.distributional_vector_space = distributional_semantics.Space(vocab)
        #self.ideal_vector_space = distributional_semantics.Space(vocab)

    def function_words(self,lexicon):
        '''Get function words from lexicon'''
        function_words = {}
        for k,v in lexicon.items():
            if v.pos == 'D' or v.lemma == "be":
                function_words[v.surface] = v
        return function_words

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
            #se = distributional_semantics.SparseEntity(linguistic_entity)
            #In this simple implementation, we know that cardinality of entities is 1
            se.cardinality = 1
            self.sparse_entities[linguistic_entity] = se
        se = self.sparse_entities[linguistic_entity]
        for predicate in entity.predicates:
            #context = distributional_semantics.Context(se.ID,situation.ID)
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
                word = vector_space.labels_to_pos[se.word]
                for feature in (feature for c in se.contexts for feature in c.dlfs):
                    feature = vector_space.labels_to_pos[feature]
                    for vec, context in ((word, feature), (feature, word)):
                        vector_space.vectors[vec][context] += 1
        out = []
        for k,v in vector_space.vectors.items():
          out.append(vector_space.id_to_contexts[k]+" "+' '.join([str(n) for n in v]))
        utils.printer("./data/"+self.name+"."+vector_type+".vectors.txt",out)
        
    def mk_set_vector(self,e):
        '''Create a frequency vector for a set.'''

        vector_space = self.ideal_vector_space if e.ID[-1] == 'h' else self.distributional_vector_space
        #print vector_space.pos_to_labels
        if e.ID not in vector_space.labels_to_pos:
            new_pos = len(vector_space.labels_to_pos)
            vector_space.labels_to_pos[e.ID] = new_pos
            vector_space.pos_to_labels[new_pos] = e.ID
            vector_space.vectors[new_pos] = np.zeros(len(vector_space.vectors[0])) 
        for predicate in e.predicates:
	    pred_pos = vector_space.labels_to_pos[predicate.form]
	    set_pos = vector_space.labels_to_pos[e.ID]
	    vector_space.vectors[set_pos][pred_pos] += 1

        print e.ID,vector_space.vectors[vector_space.labels_to_pos[e.ID]]
        vector_space.update_kinds(e)
         


    def tell(self,model,v):
        '''Tell stuff about a situation (a submodel).'''
        sentences = grammar.generate(v.lexicon)
        for s in sentences:
            truth, justification = true_model.interpretation_function_S(s, v.lexicon)
            print s, truth, print_justification(justification)
        return sentences


    def hear(self,utterance):
        '''Hear what another speaker has said about a set of entities.
        If the sentence is true to the hearer, the assumption is that the speaker
        is referring to someting known to the hearer. Otherwise, update model.
        '''
        #print self.name,"hears..."
        truth, denotation = self.model.true_interpretation(utterance)
        print "INTERPRET",truth, 
        for e in denotation:
            print e.ID
        '''If the interpretation of the sentence is false, add info to model.
        The hearer trusts the speaker completely. One new entity is produced
        for each sentence (we don't know about co-reference).'''
        if not truth:
            ID, p1, p2 = grammar.parse_sentence(utterance)
            print "PARSE", ID, p1.form, p2.form
            t = world.Thing(ID.replace('l','h'),[p1.form,p2.form])
            print t.attributes
            e = model.Entity(t)
            #print e.ID,e.IDg,e.predicates
            print "Appending entity to model", e.ID
            self.model.entities.append(e)
            self.mk_set_vector(e)
        return truth    
