import sys
sys.path.append('../../utils/')
from utils import read_probabilistic_matrix, read_nearest_neighbours, read_entity_matrix
from collections import Counter
import itertools
import random

print("Reading probabilistic matrix... Please be patient...")
vocab, pm = read_probabilistic_matrix()
print("Reading nearest neighbour file for smoothing...")
neighbours = read_nearest_neighbours()
#print("Reading the entity matrix to compute priors...")
#predicates = read_entity_matrix()

utterance = "START"

def compute_priors():
    total = sum([len(v) for p,v in predicates.items() ])
    priors = {}
    for p,v in predicates.items():
        priors[p] = len(v) / total
        #print(p,priors[p])
    return priors

def mk_random_utterance():
    nouns = [ n for n in vocab if "n.0" in n and '(' not in n ]
    atts = [ a for a in vocab if "n.0" not in a and '(' not in a ]
    utterance = ' '.join([w for w in random.sample(atts,2)])
    noun = random.sample(nouns,1)[0]
    return utterance+' '+noun

def smooth(word,dimension):
    nns =  neighbours[word]
    smoothed = 0.0
    for nn in nns:
        smoothed+=pm[vocab.index(nn)][vocab.index(dimension)]
    return smoothed / len(nns)


#priors = compute_priors()
random_utterances = {}

while True:
#for i in range(10000):

    utterance = input("\nPlease enter a phrase or press 'r' for random. (Type 'q' to quit.) ")
    if utterance == 'q':
        break

    if utterance == 'r':
        utterance = mk_random_utterance()
    #print("Processing",utterance,"...")

    words = utterance.split()

    process = True
    for w in words:
        if w not in vocab:
            if w+".n.01" in vocab:
                words[words.index(w)] = w+".n.01"
            else:
                print(w,"not in vocab.")
                process = False

    if not process:
        continue
    
    probs = {}
    for w1 in words:
        probs[w1] = {}
        for w2 in words:
            probs[w1][w2] = pm[vocab.index(w1)][vocab.index(w2)]
            if probs[w1][w2] == 0:
                probs[w1][w2] = smooth(w1,w2)

    #for k,v in probs.items():
    #    print(k,v)


    permutations = list(itertools.permutations(words,len(words)))

    chain_probs = []
    for p in permutations:
        prob = 1
        current = p[0]
        for w in p[1:]:
            prob = prob * probs[current][w]
            current = w
        #print(p,prob)
        chain_probs.append(prob)
    random_utterances[utterance] = max(chain_probs)
    print(utterance,random_utterances[utterance])

for u in sorted(random_utterances, key=random_utterances.get, reverse=True):
  print(random_utterances[u],u)


