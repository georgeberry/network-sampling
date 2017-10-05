"""
Examples of how our correction procedure works
"""

import numpy as np
from numpy.linalg import inv

p = np.array([0.8, 0.2])

# the confusion matrix of counts
# rows are true values, columns are predicted values
# element (i,j) represents the count of people in i classified as j
# for simplicity we assume 100 people in each group
conf_mat = np.array([
    [80, 20],
    [10, 90],
])

# divide by row sums
C_t = conf_mat / conf_mat.sum(axis=1)
C = C_t.transpose()
C_inv = inv(C)

# the measured probabilities

m = C.dot(p)

# the correction for nodes

C_inv.dot(m)

# tie probabilities

s = np.array([0.3, 0.4, 0.3])

#

M = np.array([
    [C[0,0]**2,     C[0,0]*C[0,1],     C[0,1]**2],
    [C[0,0]*C[1,0], C[0,0]*C[1,1], C[1,1]*C[0,1]],
    [C[1,0]**2,     C[1,0]*C[1,1],     C[1,1]**2],
])

#

t = M.dot(s)

# 
