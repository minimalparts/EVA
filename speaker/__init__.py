import distributional_semantics
import utils

class Speaker(object):

    def __init__(self, name, vocab):
        self.name = name
        self.situations = []
        self.told = []
        self.heard = []
        self.distributions = {}
        self.vector_space = distributional_semantics.Space(vocab)

    def experience(self, situation):
        self.situations.append(situation)
        self.update_distributions(situation)

    '''Assumption: also filling distributions from experiences (not just utterances the speaker was exposed to)'''
    '''In this case, it is clear which linguistic entities correspond to the same world entities. Just appending 'l' to var name.'''
    def update_distributions(self,situation):
        for entity in situation.entities:
            arg_name = entity.name+'l'
            for feature in entity.features:
                context = distributional_semantics.Context([arg_name],situation.ID)
                context.dlfs.append(feature)
                if entity.species in self.distributions:
                    self.distributions[entity.species].append(context)
                else:
                    self.distributions[entity.species] = [context]
                

    '''This simply creates standard vectors for each word in the speaker's distributions.'''
    def mk_standard_vectors(self):
        for word, contexts in self.distributions.items():
          for feature in (feature for c in contexts for feature in c.dlfs):
            self.vector_space.vectors[word][self.vector_space.words_to_id[feature]]+=1
        out = []
        for k,v in self.vector_space.vectors.items():
            out.append(k+" "+' '.join([str(n) for n in v]))
        utils.printer(self.name+".vectors.txt",out)

    '''Tell *some* stuff about the situation (in logical forms)'''
    def tell(situation):
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
              #print "<[a("+e.name+"), "+e.species+"("+e.name+"), "+f+"("+e.name+")]"+situation.ID+">"
              u = "<["+e.species+"(x), "+f+"(x)]"+situation.ID+">"
              utterances.append(u)
        return utterances

