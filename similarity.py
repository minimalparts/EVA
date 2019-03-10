import sys
sys.path.append('utils/')
from utils import read_predicate_matrix, compute_cosines, write_cosines, write_vocabulary, write_nearest_neighbours

print("Reading the predicate matrix...")
words, m = read_predicate_matrix()
print("Recording vocabulary...")
write_vocabulary(words, "data/vocab.txt")

print("Computing cosines...")
cosines = compute_cosines(m)
print("Writing cosines...")
write_cosines(words, cosines, "data/cosines.txt")

print("Computing nearest neighbours...")
write_nearest_neighbours(cosines,words,"data/neighbours.txt")

