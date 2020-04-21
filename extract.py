"""Ideal words - extraction and aggregation functions

Usage:
  extract.py [--att] [--rel] [--sit]
  extract.py (-h | --help)
  extract.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Process attributes.
  --rel         Process relations.
  --sit         Process co-occurrences within situation.

"""

import os
import sys
sys.path.append('./utils/')
import re
from docopt import docopt
import numpy as np
from utils import read_entities, write_dictionary, write_numpy_matrix, normalise, compute_PCA, ppmi
from messaging import output_logo

minfreq = 100	#Min frequency of predicates 
basedir = "syn"

if __name__ == '__main__':
    output_logo()
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"] and not args["--sit"]:
        basedir = "synatt"
    if args["--rel"] and not args["--att"] and not args["--sit"]:
        basedir = "synrel"
    if args["--sit"] and not args["--att"] and not args["--rel"]:
        basedir = "synsit"
    if args["--att"] and args["--rel"] and not args["--sit"]:
        basedir = "synattrel"
    if args["--att"] and args["--sit"] and not args["--rel"]:
        basedir = "synattsit"
    if not args["--att"] and args["--rel"] and args["--sit"]:
        basedir = "synrelsit"
    if args["--att"] and args["--rel"] and args["--sit"]:
        basedir = "synattrelsit"

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


def build_situations(ideal_language_lines):
    print("Building situations...")
    situation_cooccurrences = {}
    coocs = set()
    for l in ideal_language_lines:
        if "<situation" in l:
            if len(coocs) > 1:
                for e in coocs:
                    if e not in situation_cooccurrences:
                        situation_cooccurrences[e] = coocs
                    else:
                        situation_cooccurrences[e] = situation_cooccurrences[e].union(coocs)
            coocs = set()
        if "<entity" in l:
            m = re.search('entity id=(.*)>', l)
            if m:
                eid = m.group(1)
                coocs.add(eid)
    return situation_cooccurrences

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

print("Reading entity record...")
entities = read_entities()
print("Reading predicate record... keeping predicates with frequency >",minfreq,"...")
i_to_predicates, predicates_to_i = make_predicates(args["--att"],args["--rel"])

print("Processing ideal language... This will take a while...")
print("Go and get tea/coffee...")
with open("data/ideallanguage.txt") as f:
    ideal_language_lines = f.read().splitlines()

eid = ''
entity_matrix = {}
inverse_entity_matrix = {}
processed_ids = set()
if args["--sit"]:
    situation_cooccurrences = build_situations(ideal_language_lines)


for l in ideal_language_lines:
    if "<entity" in l:
        m = re.search('entity id=(.*)>',l)
        if m:
            eid = m.group(1)
            if eid not in inverse_entity_matrix:		#The VS json file sometimes has two unrelated synsets under one ID: see entity 605310 for an example
                inverse_entity_matrix[eid] = []
            else:
                continue
    if ".n." in l:
        m = re.search('(\S*\.n\.[0-9]*)\(([0-9]*)\)',l)
        if m.group(2) == eid:
            if len(inverse_entity_matrix[eid]) > 0:		#Activate whenever the several synsets per ID should be ignored (they seem to be a bug of the VG.)
                continue
            synset = m.group(1)[:-3]    			#The synsets are mostly .n.01, so collapsing every sense coocs to alleviate sparsity.
            if synset in predicates_to_i:
                if synset in entity_matrix:
                    entity_matrix[synset].append(eid)
                else:
                    entity_matrix[synset] = [eid]
                if synset not in inverse_entity_matrix[eid]:	
                    inverse_entity_matrix[eid].append(synset)
            if args["--sit"]  and inverse_entity_matrix[eid] != []: 
                try:
                    for neigh in situation_cooccurrences[eid]:
                        if neigh != eid and neigh not in processed_ids:
                            etype = entities[neigh]
                            if etype in predicates_to_i:
                                if etype in entity_matrix:
                                    entity_matrix[etype].append(eid)
                                else:
                                    entity_matrix[etype] = [eid]
                                inverse_entity_matrix[eid].append(etype)
                            processed_ids.add(neigh)
                except:
                    pass

    if ".n." not in l:
        m = re.search('(\S*)\(([0-9]*)\)',l)
        #If no synset found for this entity (e.g. because the synset was of too low frequency and was not considered) don't go further
        if m and m.group(2) == eid and args["--att"] and inverse_entity_matrix[eid] != []:			
            att = m.group(1)
            if att in predicates_to_i:
                if att in entity_matrix:
                    entity_matrix[att].append(eid)
                else:
                    entity_matrix[att] = [eid]
                if att not in inverse_entity_matrix[eid]:
                    inverse_entity_matrix[eid].append(att)
        
        m = re.search('(\S*)\(([0-9]*),([0-9]*)\)',l)
        if m and args["--rel"]  and inverse_entity_matrix[eid] != []: 
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

pca_matrix = compute_PCA(normalise(predicate_matrix),300)
write_numpy_matrix(pca_matrix, i_to_predicates, spacedir+"predicate_matrix_pca.dm")

ppmi_matrix = ppmi(predicate_matrix)
write_numpy_matrix(ppmi_matrix, i_to_predicates, spacedir+"predicate_matrix_ppmi.dm")

ppmi_pca_matrix = compute_PCA(normalise(ppmi_matrix),300)
write_numpy_matrix(ppmi_pca_matrix, i_to_predicates, spacedir+"predicate_matrix_ppmi_pca.dm")
