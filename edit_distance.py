import music21 as ms
from music21.common import opFrac
import numpy as np


def getLev400Distance(first_stream, second_stream):
    pass

# Edit distance is implemented according to the algorithm given by:
# E. Unal, E. Chew, P. Georgiou, and S. Narayanan. Challenging uncertainty
# in query by humming systems: a fingerprinting approach. Transactions on
# Audio Speech and Language Processing, 16(2):359–371, 2008.
def ioir_edit_distance(q, x):
    m=len(q)+1
    n=len(x)+1

    tbl = {}
    for i in range(m): tbl[i,0]=i
    for j in range(n): tbl[0,j]=0
    for i in range(1, m-1):
        for j in range(1, n-1):
            cost = 1/2*abs((q[i][0]-x[j][0])/24)+1/2*abs(1-min(q[i][1],x[j][1])/max(q[i][1],x[j][1]))
            tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)
    return tbl[i,j]

def edit_distance_norm(s1, s2):
    if len(s1) + len(s2) == 0: return 0.0
    return min(edit_distance(s1, s2) / float(len(s1) + len(s2)), 0.5)

