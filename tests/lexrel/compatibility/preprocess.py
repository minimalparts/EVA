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
sys.path.append('../../../utils/')
from docopt import docopt
from utils import read_vocab

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

out = open('in_vg_compatibility.txt','w')

with open('compatibility_ds.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['word1']+".n.01" in p_to_i and row['word2']+".n.01" in p_to_i:
            out.write(row['word1']+' '+row['word2']+' '+row['compatibility_mean']+'\n')
out.close()
