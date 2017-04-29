import distributional_semantics
import random
import utils

class Speaker(object):

    def __init__(self, name, vocab):
        self.name = name
        self.situations = []
        self.told = []
        self.heard = []
        self.sparse_entities = {}						#A dictionary of sets, whether entities, plurals, or whatever.
        self.vector_space = distributional_semantics.Space(vocab)

    def experience(self, situation):
        self.situations.append(situation)
        self.update_sparse_entities(situation)

    '''Assumption: also filling linguistic entities from experiences (not just utterances the speaker was exposed to)'''
    '''In this case, it is clear which linguistic entities correspond to the same world entities. Just appending 'l' to var name.'''
    def update_sparse_entities(self,situation):
        #print situation.ID
        for entity in situation.entities:
            #print entity.name, entity.species, entity.features
            if entity.name+'l' not in self.sparse_entities:
                var_name = entity.name+'l'
	        se = distributional_semantics.SparseEntity(entity.species,var_name)
	        se.cardinality = 1				#In this simple implementation, we know that cardinality of instances is 1
                self.sparse_entities[var_name] = se
            se = self.sparse_entities[entity.name+'l']
            if not any(context.situation == situation.ID for context in se.contexts):
		for feature in entity.features:
		    context = distributional_semantics.Context(se.name,situation.ID)
		    context.dlfs.append(feature)
		    se.contexts.append(context)
                

    '''This simply creates standard vectors for each word in the speaker's distributions.'''
    '''Note: if the same entity occurs in several situations, the count for a particular context is incremented once per situation.'''
    def mk_standard_vectors(self):
        for name,se in self.sparse_entities.items():
          #print se.word, se.name, se.cardinality, [c.dlfs for c in se.contexts]
          word = se.word
          for feature in (feature for c in se.contexts for feature in c.dlfs):
            #print feature, self.vector_space.words_to_id[feature]
            self.vector_space.vectors[word][self.vector_space.words_to_id[feature]]+=1
            self.vector_space.vectors[feature][self.vector_space.words_to_id[word]]+=1
        out = []
        for k,v in self.vector_space.vectors.items():
            out.append(k+" "+' '.join([str(n) for n in v]))
        utils.printer(self.name+".vectors.txt",out)

    '''Tell *some* stuff about the situation (in logical forms)'''
    def tell(self,situation):
        print self.name,"says..."
        es = []
        fs = []
        utterances = []
        num_es = random.randint(1,len(situation.entities))
        for i in range(num_es):
            e = random.choice(situation.entities)
            while e in es:
                e = random.choice(situation.entities)
            es.append(e)
    
        for e in es:
           #num_fs = random.randint(1,len(e.features))
           '''Only report on a maximum of 5 features'''
           num_fs = random.randint(1,5)
           for i in range(num_fs):
               f = random.choice(e.features)
               while f in fs:
                   f = random.choice(e.features)
               fs.append(f)
               #print e.name, e.species, f
               print "<[a("+e.name+"), "+e.species+"("+e.name+"), "+f+"("+e.name+")]"+situation.ID+">"
               u = "<["+e.species+"(x), "+f+"(x)]"+situation.ID+">"
               utterances.append(u)
        return utterances

