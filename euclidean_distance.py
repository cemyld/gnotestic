import music21
import math


def getEuclideanDistance(first_stream, second_stream):
    first = getNoteRatios(first_stream)
    second = getNoteRatios(second_stream)

    return math.sqrt(sum([(first[i] - second[i])**2 for i in range(12)]))


def getNoteRatios(music_stream):
    notescount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for p in music_stream.pitches:
        notescount[p.midi % 12] += 1
    s = sum(notescount)
    normalized = [float(i) / s for i in notescount]
    return normalized
