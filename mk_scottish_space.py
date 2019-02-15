import re
import numpy as np

minfreq = 100	#Min frequency of predicates 

def read_entities():
    entities = {}
    with open("data/entities.txt") as f:
        lines = f.read().splitlines()
    for pair in lines:
        eid,etype = pair.split()
        entities[eid] = etype
    return entities

def write_dictionary(m,filename):
    f = open(filename,'w',encoding='utf-8')
    for k,v in m.items():
       v_string = ' '.join([str(val) for val in v])
       f.write('%s %s\n' %(k,v_string))
    f.close()

def write_numpy_matrix(m,i_to_predicates,filename):
    f = open(filename,'w',encoding='utf-8')
    for i,p in i_to_predicates.items():
       row = p
       v_string = ' '.join([str(val) for val in m[i]])
       f.write('%s %s\n' %(p,v_string))
    f.close()

def make_predicates():
    predicate_count = 0
    i_to_predicates = {}
    predicates_to_i = {}

    def record_predicates(filename, predicate_count):
        with open(filename) as f:
            lines = f.read().splitlines()
        for pair in lines:
            pred,freq = pair.split('\t')
            if int(freq) > minfreq:
                i_to_predicates[predicate_count] = pred
                predicates_to_i[pred] = predicate_count
                predicate_count+=1
        return predicate_count

    predicate_count = record_predicates("data/synset_freqs.txt", predicate_count)
    predicate_count = record_predicates("data/attribute_freqs.txt", predicate_count)
    record_predicates("data/relation_freqs.txt", predicate_count)
    #print(i_to_predicates)
    return i_to_predicates, predicates_to_i


def aggregation(entity_matrix, inverse_entity_matrix, predicates_to_i):
    size = len(entity_matrix.keys())
    predicate_matrix = np.zeros((size,size))
    for pred,entities in entity_matrix.items():
        for e in entities:
            e_preds = inverse_entity_matrix[e]
            for e_pred in e_preds:
                predicate_matrix[predicates_to_i[pred]][predicates_to_i[e_pred]]+=1
    return predicate_matrix


def prob_interpretation(predicate_matrix):
    prob_matrix = np.zeros(predicate_matrix.shape)
    for i in range(predicate_matrix.shape[0]):
        prob_matrix[i] = predicate_matrix[i] / predicate_matrix[i][i]
    return prob_matrix


print("Reading entity record...")
entities = read_entities()
print("Reading predicate record... keeping predicates with frequency >",minfreq,"...")
i_to_predicates, predicates_to_i = make_predicates()

print("Processing ideal language... This will take a few minutes...")
with open("data/ideallanguage.txt") as f:
    lines = f.read().splitlines()

eid = ''
entity_matrix = {}
inverse_entity_matrix = {}
for l in lines:
    if "<entity" in l:
        m = re.search('entity id=(.*)>',l)
        if m:
            eid = m.group(1)
            inverse_entity_matrix[eid] = []
    if ".n." in l:
        m = re.search('(\S*\.n\.[0-9]*)\(([0-9]*)\)',l)
        if m.group(2) == eid:
            synset = m.group(1)
            if synset in predicates_to_i:
                if synset in entity_matrix:
                    entity_matrix[synset].append(eid)
                else:
                    entity_matrix[synset] = [eid]
                if synset not in inverse_entity_matrix[eid]:
                    inverse_entity_matrix[eid].append(synset)
    if ".n." not in l:
        m = re.search('(\S*)\(([0-9]*)\)',l)
        if m and m.group(2) == eid:
            att = m.group(1)
            if att in predicates_to_i:
                if att in entity_matrix:
                    entity_matrix[att].append(eid)
                else:
                    entity_matrix[att] = [eid]
                if att not in inverse_entity_matrix[eid]:
                    inverse_entity_matrix[eid].append(att)
        
        m = re.search('(\S*)\(([0-9]*),([0-9]*)\)',l)
        if m:
            if m.group(2) == eid:
                relation = m.group(1)+'(-,'+entities[m.group(3)]+')'
            if m.group(3) == eid:
                relation = m.group(1)+'('+entities[m.group(2)]+',-)'
            if relation in predicates_to_i:
                if relation in entity_matrix:
                    entity_matrix[relation].append(eid)
                else:
                    entity_matrix[relation] = [eid]
                if relation not in inverse_entity_matrix[eid]:
                    inverse_entity_matrix[eid].append(relation)
                

write_dictionary(entity_matrix,"spaces/entity_matrix.dm")
write_dictionary(inverse_entity_matrix, "spaces/inverse_entity_matrix.dm")

predicate_matrix = aggregation(entity_matrix,inverse_entity_matrix, predicates_to_i)
write_numpy_matrix(predicate_matrix, i_to_predicates, "spaces/predicate_matrix.dm")

prob_matrix = prob_interpretation(predicate_matrix)
write_numpy_matrix(prob_matrix, i_to_predicates, "spaces/probabilistic_matrix.dm")
