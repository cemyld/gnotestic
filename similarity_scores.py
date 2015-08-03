import math
import music21


# Edit distance is implemented according to the algorithm given by:
# E. Unal, E. Chew, P. Georgiou, and S. Narayanan. Challenging uncertainty
# in query by humming systems: a fingerprinting approach. 2008
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

# Normalizes by length, if less than threshold, returns 0.5
def ioir_edit_distance_norm(s1, s2):
    if len(s1) + len(s2) == 0: return 0.0
    return min(ioir_edit_distance(s1, s2) / max(len(s1), len(s2)), 0.5)

# Euclidean distance based on bag-of-words approach, compares the ratios of notes
def getEuclideanDistance(first_stream, second_stream):
    def getNoteRatios(music_stream):
        notescount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for p in music_stream.pitches:
            notescount[p.midi % 12] += 1
        s = sum(notescount)
        normalized = [float(i) / s for i in notescount]
        return normalized
    first = getNoteRatios(first_stream)
    second = getNoteRatios(second_stream)

    return math.sqrt(sum([(first[i] - second[i])**2 for i in range(12)]))

# Compare similarity scores for sections in different approaches
if __name__ == '__main__':
    import pickle
    pairs = pickle.load(open('similar_streams.p', 'rb'))

    #Calculate edit distance
    import melody_extractor
    for index,pair in enumerate(pairs):
        fmelo = melody_extractor.extractMelody(pair[0])
        smelo = melody_extractor.extractMelody(pair[1])
        print(index, ioir_edit_distance_norm(fmelo,smelo))

