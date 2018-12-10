from numpy import linalg, array, dot, sqrt, math


def readDM(dm_file):
    dm_dict = {}
    with open(dm_file) as f:
        dmlines=f.readlines()
    f.close()

    #Make dictionary with key=row, value=vector
    c = 0
    for l in dmlines:
        items=l.rstrip().split()
        row=items[0][:-5]		#deleting WordNet suffix of the type .n.01
        vec=[float(i) for i in items[1:]]
        vec=array(vec)
        dm_dict[row]=vec
    return dm_dict

def convert_to_array(vector):
  return array([float(i) for i in vector.split(' ')])

def convert_to_string(vec):
    s = ""
    for i in range(len(vec)):
        s+=str(vec[i])+" "
    return s[:-1]

def sim_to_matrix(dm_dict,vec,n):
    cosines={}
    c=0
    for k,v in dm_dict.items():
        try:
            cos = cosine_similarity(vec, v)
            cosines[k]=cos
            c+=1
        except:
            pass
    c=0
    neighbours = []
    for t in sorted(cosines, key=cosines.get, reverse=True):
        if c<n:
            if t.isalpha():
                #print(t,cosines[t])
                neighbours.append(t)
                c+=1
        else:
            break
    return neighbours


def normalise(v):
    norm = linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def cosine_similarity(peer_v, query_v):
    if len(peer_v) != len(query_v):
        raise ValueError("Peer vector and query vector must be "
                         " of same length")
    num = dot(peer_v, query_v)
    den_a = dot(peer_v, peer_v)
    den_b = dot(query_v, query_v)
    return num / (sqrt(den_a) * sqrt(den_b))


