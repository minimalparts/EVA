import distributional_semantics
import numpy as np

m1=[[1, 1, 1], 
[1, 1, 1]]
m2 = m1

print m1

w = distributional_semantics.linalg(m1,m2)
print w
print np.dot(m1,w)
