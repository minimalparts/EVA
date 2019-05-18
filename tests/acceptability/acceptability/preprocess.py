"""Ideal words

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


import csv
import sys
import random
from docopt import docopt
sys.path.append('../../../utils/')
from utils import read_vocab

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
with open('karma_police.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['word1']+".n" in p_to_i and row['word2']+".n" in p_to_i:
            line = row['word1']+' '+row['word2']+' '+row['acceptability_mean']+'\n'
            shuffled_lines.append(line) 
write_file(shuffled_lines,'in_vg_acceptability.txt')    #Not actually shuffled yet!

print(len(shuffled_lines))

#Shuffle and make train / val / test
random.shuffle(shuffled_lines)

write_file(shuffled_lines[:700],'in_vg_acceptability.train.txt')
write_file(shuffled_lines[700:900],'in_vg_acceptability.val.txt')
write_file(shuffled_lines[900:],'in_vg_acceptability.test.txt')


