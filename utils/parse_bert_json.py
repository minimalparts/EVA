"""Parse BERT JSON

Usage:
  parse_bert_json.py <filename> [--layer=<n>]
  parse_bert_json.py (-h | --help)
  parse__bert_json.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --layer=<n>       Number of top layers to consider

"""


import json 
import codecs
import sys
import numpy as np
from docopt import docopt
from pprint import pprint

layer = 1    #by default, just one layer from the top

if __name__ == '__main__':
    args = docopt(__doc__, version='Ideal Words 0.1')
    bert_json = args['<filename>']
    if args['--layer']:
        layer = int(args['--layer'])

data = []
with codecs.open(bert_json,'rU','utf-8') as f:
    for line in f:
       data.append(json.loads(line))

for d in data:
    token = ""
    for f in d['features']:
        if f['token'] == '[CLS]':
            #vec = ' '.join(str(v) for v in f['layers'][-layer]['values'])
            vec=np.array(f['layers'][-layer]['values'])
            for i in range(-layer+1,0):
                vec+=np.array(f['layers'][i]['values'])
            vec = ' '.join(str(v) for v in list(vec))
        if f['token'] not in ['[CLS]','[SEP]']:
            token = token+f['token'].replace('#','')
        if f['token'] == '[SEP]':
            print(token,vec)
            token = ""
