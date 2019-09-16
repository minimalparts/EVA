"""Ideal words

Usage:
  preprocess.py [--att] [--rel]
  preprocess.py (-h | --help)
  proprocess.py --version

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
        out.write(i)
    out.close()

#Write all lines with items included in VG
shuffled_lines = []
with open('compatibility_ds.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['word1']+".n" in p_to_i and row['word2']+".n" in p_to_i:
            line = row['word1']+' '+row['word2']+' '+row['compatibility_mean']+'\n'
            shuffled_lines.append(line) 
write_file(shuffled_lines,'in_vg_compatibility.txt')    #Not actually shuffled yet!


#Shuffle and make train / val / test
random.shuffle(shuffled_lines)

write_file(shuffled_lines[:1500],'in_vg_compatibility.train.txt')
write_file(shuffled_lines[1500:1800],'in_vg_compatibility.val.txt')
write_file(shuffled_lines[1800:],'in_vg_compatibility.test.txt')


