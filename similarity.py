"""Ideal vocab - similarity function

Usage:
  similarity.py [--att] [--rel] [--ppmi]
  similarity.py (-h | --help)
  similarity.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --att         Process attributes.
  --rel         Process relations.
  --ppmi        Uses PPMI version of predicate matrix.

"""

import os
import sys
import numpy as np
sys.path.append('utils/')
from docopt import docopt
from utils import read_predicate_matrix, compute_cosines, write_cosines, write_vocabulary, compute_nearest_neighbours, write_nearest_neighbours, read_cosines

subspace = "syn"

if __name__ == '__main__':
    args = docopt(__doc__, version='Ideal Words 0.1')
    if args["--att"] and not args["--rel"]:
        subspace = "synatt"
    if not args["--att"] and args["--rel"]:
        subspace = "synrel"
    if args["--att"] and args["--rel"]:
        subspace = "synattrel"

datadir = "data/"+subspace+"/"
if not os.path.exists(datadir):
    os.makedirs(datadir)

print("Reading the predicate matrix...")
vocab, m = read_predicate_matrix(subspace,ppmi=args["--ppmi"])

print("Recording vocabulary...")
write_vocabulary(vocab, datadir+"vocab.txt")

print("Computing cosines...")
cosines = compute_cosines(m)
print("Writing cosines...")
if args["--ppmi"]:
    write_cosines(vocab, cosines, datadir+"cosines_ppmi.txt")
else:
    write_cosines(vocab, cosines, datadir+"cosines.txt")

print("Computing nearest neighbours...")
cosines = read_cosines(subspace,ppmi=args["--ppmi"])
syn_nns,att_nns,rel_nns = compute_nearest_neighbours(cosines,vocab)
print(syn_nns[vocab[0]])
write_nearest_neighbours(syn_nns,"syn",subspace,ppmi=args["--ppmi"])
write_nearest_neighbours(att_nns,"att",subspace,ppmi=args["--ppmi"])
write_nearest_neighbours(rel_nns,"rel",subspace,ppmi=args["--ppmi"])
