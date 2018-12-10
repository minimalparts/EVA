import re
from collections import Counter

def record_entities():
    print("Building entity record...")
    with open("data/ideallanguage.txt") as f:
        lines = f.read().splitlines()
    synsets = []
    out = open("data/entities.txt",'w')
    eid = ''
    for l in lines:
        if "<entity" in l:
            m = re.search('entity id=(.*)>',l)
            if m:
                eid = m.group(1)
        if ".n." in l:
            m = re.search('(\S*\.n\.[0-9]*)\(([0-9]*)\)',l)
            if m.group(2) == eid:
                synset = m.group(1)
                out.write('%s %s\n' %(eid,synset))
                synsets.append(synset)
    out.close()
    counts = Counter(synsets)
    with open('data/synset_freqs.txt', 'w', encoding='utf-8') as w:
        for pair in counts.most_common():
            w.write(pair[0] + '\t' + str(pair[1]) + '\n')

def record_attributes():
    print("Building attribute frequencies...")
    with open("data/ideallanguage.txt") as f:
        lines = f.read().splitlines()
    attributes = []
    for l in lines:
        if ".n." not in l:
            m = re.search('(\S*)\([0-9]*\)',l)
            if m:
                attribute = m.group(1)
                attributes.append(attribute)
    counts = Counter(attributes)
    with open('data/attribute_freqs.txt', 'w', encoding='utf-8') as w:
        for pair in counts.most_common():
            w.write(pair[0] + '\t' + str(pair[1]) + '\n')

def record_relations():
    print("Building relation frequencies...")
    with open("data/ideallanguage.txt") as f:
        lines = f.read().splitlines()
    relations = []
    for l in lines:
        m = re.search('(\S*)\([0-9]*,[0-9]*\)',l)
        if m:
            relation = m.group(1)
            relations.append(relation)
    counts = Counter(relations)
    with open('data/relation_freqs.txt', 'w', encoding='utf-8') as w:
        for pair in counts.most_common():
            w.write(pair[0] + '\t' + str(pair[1]) + '\n')

record_entities()
record_attributes()
record_relations()
