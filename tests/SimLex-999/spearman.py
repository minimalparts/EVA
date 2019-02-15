import sys
sys.path.append('..')
import utils
from scipy.stats import spearmanr

#This could be done better... which rows of the matrix should we choose? Just WN? Just first sense? Etc.
dm_dict = utils.readDM(sys.argv[1])
system = []
gold = []

with open("SimLex-999.txt",'r') as f:
    lines = f.read().splitlines()

for l in lines[1:]:
    fields = l.split('\t')
    w1 = fields[0]
    w2 = fields[1]
    score = float(fields[3])
    if w1 in dm_dict and w2 in dm_dict:
        cos = utils.cosine_similarity(dm_dict[w1],dm_dict[w2])
        system.append(cos)
        gold.append(score)
        print(w1,w2,cos,score)
f.close()

print("SPEARMAN:",spearmanr(system,gold))
print("("+str(len(system))+" pairs out of the original 999 could be processed, due to vocabulary size.)")
