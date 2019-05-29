"""Ideal words

Usage:
  preprocess.py [--att] [--rel]
  preprocess.py (-h | --help)
  preprocess.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Process attributes.
  --rel         Process relations.

"""

import csv
import sys
sys.path.append('../../../utils/')
from docopt import docopt
from utils import read_vocab
import random
import re

random.seed(77)
basedir = "syn"

if __name__ == '__main__':
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"]:
        basedir = "synatt"
    if not args["--att"] and args["--rel"]:
        basedir = "synrel"
    if args["--att"] and args["--rel"]:
        basedir = "synattrel"

i_to_p,p_to_i = read_vocab(basedir)

def write_file(item_list,filename):
    out = open(filename,'w')
    for i in item_list:
        out.write(i+'\n')
    out.close()

#Write all lines with items included in VG
shuffled_lines = []
single_words = []
infile =  open('BLESS.txt','r')
for l in infile:
    l = l.rstrip('\n').replace("-n",".n")
    fields = l.split('\t')
    if ".n" in fields[0] and ".n" in fields[3] and fields[0] in p_to_i and fields[3] in p_to_i:
        line = fields[0]+' '+fields[3]+' '+fields[2]
        line = re.sub('random..', 'random', line)
        shuffled_lines.append(line) 
        single_words.append(fields[0])
        single_words.append(fields[3])
infile.close()
write_file(shuffled_lines,'in_vg_lexrel.txt')
write_file(list(set(single_words)),'single_words_lexrel.txt')


#Shuffle and make train / val / test
random.shuffle(shuffled_lines)

write_file(shuffled_lines[:1200],'in_vg_lexrel.train.txt')
write_file(shuffled_lines[1200:1500],'in_vg_lexrel.val.txt')
write_file(shuffled_lines[1500:],'in_vg_lexrel.test.txt')


