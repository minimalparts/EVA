
#Do quantification with probabilistic matrix

kinds = ['tree','car']
attributes = ['green','parked']

def VP(a,b):
    r = '-'
    if a == 'is' and b in attributes:
        r = "VP"
    return r

def NP(a,b):
    r = '-'
    if a == 'a' and b in kinds:
        r = "NP"
    return r

def NPcoord(a,b):
    r = '-'
    if a == "NP" and b == "RC":
        r = "NP"
    return r

def Rcoord(a,b):
    r = '-'
    if a == 

def S(a,b):
    r = '-'
    if a == "NP" and b == "VP":
        r = "S"
    return r



