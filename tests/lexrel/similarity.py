from utils import read_predicate_matrix, compute_cosines
import numpy as np

def write_cosines(words, cosines ,filename):
    f = open(filename,'w',encoding='utf-8')
    for i in range(len(words)):
       word = words[i]
       v_string = ' '.join([str(val) for val in cosines[i]])
       f.write('%s %s\n' %(word,v_string))
    f.close()

def write_vocabulary(words, filename):
    f = open(filename,'w',encoding='utf-8')
    for i in range(len(words)):
       f.write('%s %s\n' %(i,words[i]))
    f.close()

def write_nearest_neighbours(cosines,words,filename):
    f = open(filename,'w',encoding='utf-8')
    word_indices = {}
    for i, val in enumerate(words):
        word_indices[i] = val
    for i in range(cosines.shape[0]):
        #maxima = np.argpartition(cosines[i], -10)[-10:]
        maxima = np.argsort(-cosines[i])[:10]
        neighbours = [word_indices[n]+" ("+str(round(cosines[i][n],5))+")" for n in maxima]
        f.write('%s %s\n' %(words[i],' '.join([n for n in neighbours])))
    f.close()
            

words, m = read_predicate_matrix("../../spaces/predicate_matrix.dm","synsets")
cosines = compute_cosines(m)

write_cosines(words, cosines, "cosines.dm")
write_vocabulary(words, "vocab.txt")

write_nearest_neighbours(cosines,words,"neighbours.txt")
