"""Ideal words - extraction and aggregation functions

Usage:
  extract.py [--att] [--rel]
  extract.py (-h | --help)
  extract.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Process attributes.
  --rel         Process relations.

"""

import os
import sys
sys.path.append('./utils/')
import re
from docopt import docopt
import numpy as np
from utils import read_entities, write_dictionary, write_numpy_matrix

minfreq = 100	#Min frequency of predicates 
basedir = "syn"

if __name__ == '__main__':
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"]:
        basedir = "synatt"
    if not args["--att"] and args["--rel"]:
        basedir = "synrel"
    if args["--att"] and args["--rel"]:
        basedir = "synattrel"

spacedir = "spaces/"+basedir+"/"
if not os.path.exists(spacedir):
    os.makedirs(spacedir)

def make_predicates(att,rel):
    predicate_count = 0
    i_to_predicates = {}
    predicates_to_i = {}

    def record_predicates(filename, predicate_count):
        with open(filename) as f:
            lines = f.read().splitlines()
        for pair in lines:
            pred,freq = pair.split('\t')
            if ".n." in pred:
               pred = pred[:-3]
            if int(freq) > minfreq:
                i_to_predicates[predicate_count] = pred
                predicates_to_i[pred] = predicate_count
                predicate_count+=1
        return predicate_count

    predicate_count = record_predicates("data/synset_freqs.txt", predicate_count)
    if att:
        predicate_count = record_predicates("data/attribute_freqs.txt", predicate_count)
    if rel:
        predicate_count = record_predicates("data/relation_freqs.txt", predicate_count)
    #print(i_to_predicates)
    return i_to_predicates, predicates_to_i


def aggregation(entity_matrix, inverse_entity_matrix, predicates_to_i):
    '''This is the aggregation function A_M'''
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

def ppmi(matrix):
    ppmi_matrix = np.zeros(matrix.shape)
    N = np.sum(matrix)
    row_sums = np.sum(matrix, axis=1)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ppmi_matrix[i][j] = matrix[i][j] * N / (row_sums[i] * row_sums[j])
    return ppmi_matrix

print("Reading entity record...")
entities = read_entities()
print("Reading predicate record... keeping predicates with frequency >",minfreq,"...")
i_to_predicates, predicates_to_i = make_predicates(args["--att"],args["--rel"])

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
            if eid not in inverse_entity_matrix:	#The VS json file sometimes has two unrelated synsets under one ID: see entity 605310 for an example
                inverse_entity_matrix[eid] = []
            else:
                continue
    if ".n." in l:
        m = re.search('(\S*\.n\.[0-9]*)\(([0-9]*)\)',l)
        if m.group(2) == eid:
            synset = m.group(1)[:-3]    #The synsets are mostly .n.01, so collapsing every sense together to alleviate sparsity.
            if synset in predicates_to_i:
                if synset in entity_matrix:
                    entity_matrix[synset].append(eid)
                else:
                    entity_matrix[synset] = [eid]
                if synset not in inverse_entity_matrix[eid]:
                    inverse_entity_matrix[eid].append(synset)
    if ".n." not in l:
        m = re.search('(\S*)\(([0-9]*)\)',l)
        if m and m.group(2) == eid and args["--att"]:
            att = m.group(1)
            if att in predicates_to_i:
                if att in entity_matrix:
                    entity_matrix[att].append(eid)
                else:
                    entity_matrix[att] = [eid]
                if att not in inverse_entity_matrix[eid]:
                    inverse_entity_matrix[eid].append(att)
        
        m = re.search('(\S*)\(([0-9]*),([0-9]*)\)',l)
        if m and args["--rel"]:
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
                

write_dictionary(entity_matrix,spacedir+"entity_matrix.dm")
write_dictionary(inverse_entity_matrix, spacedir+"inverse_entity_matrix.dm")

predicate_matrix = aggregation(entity_matrix,inverse_entity_matrix, predicates_to_i)
write_numpy_matrix(predicate_matrix, i_to_predicates, spacedir+"predicate_matrix.dm")

prob_matrix = prob_interpretation(predicate_matrix)
write_numpy_matrix(prob_matrix, i_to_predicates, spacedir+"probabilistic_matrix.dm")

ppmi_matrix = ppmi(predicate_matrix)
write_numpy_matrix(ppmi_matrix, i_to_predicates, spacedir+"predicate_matrix_ppmi.dm")
