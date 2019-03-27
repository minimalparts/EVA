import csv
import sys
sys.path.append('../../../utils/')
from utils import read_vocab

i_to_p,p_to_i = read_vocab()

out = open('in_vg_compatibility.txt','w')

with open('compatibility_ds.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['word1']+".n.01" in p_to_i and row['word2']+".n.01" in p_to_i:
            out.write(row['word1']+' '+row['word2']+' '+row['compatibility_mean']+'\n')
out.close()
