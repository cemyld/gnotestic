import copy
import music21 as ms
from music21.common import opFrac
# Implemented according to revised skyline algorithm by:
# W. Chai, Melody Retrieval on the Web, MS Thesis, Massachusetts Institute
# of Technology, Boston, 2000
# Extracts the melody according to IOIR format represented in paper below:
# B. Pardo and W. Birmingham. Encoding timing information
# for musical query matching. In ISMIR, pages 267–268, 2002
def extractMelody(music_stream):
    def getOverlap(a, b):
        return max(0, min(a[1], b[1]) - max(a[0], b[0]))

    def notedurspan(n):
        return (n.offset, opFrac(n.offset + n.duration.quarterLength))

    def getTop(n):
        def getMelodyOverlap():
            overlap = 0
            ndurspan = notedurspan(n)
            for interval in melodyline:
                overlap += getOverlap(interval, ndurspan)
            return overlap
        return getMelodyOverlap() / n.duration.quarterLength

    def chordToHighNote(_stream):
        for musicobj in _stream:
            if 'Stream' in musicobj.classes:
                chordToHighNote(musicobj)
            if 'Chord' in musicobj.classes:
                # select highest pitch
                hpitch = max(musicobj.pitches, key=lambda x: x.midi)
                # create new note with same pitch,offset,duration
                hnote = ms.note.Note(hpitch)
                _stream.append(hnote)
                hnote.offset, hnote.duration = musicobj.offset, musicobj.duration
                # remove chord
                _stream.remove(musicobj)

    Tstar = 0.5
    mstream = copy.deepcopy(music_stream)
    melodyline = []
    # change chords to notes with selecting highest pitch
    chordToHighNote(mstream)
    sortedNotes = sorted(mstream.flat.notes, key=lambda x: x.ps)
    melodyNotes = []
    while sortedNotes:
        note = sortedNotes.pop()
        if getTop(note) < Tstar:
            # add note to melody, split if overlapping
            notespan = notedurspan(note)
            for melospan in melodyline:
                if getOverlap(melospan, notespan) > 0:
                    notespan = max(melospan[0], notespan[0]), min(
                        melospan[1], notespan[1])

            melodyline.append((notespan[0], notespan[1], note))

    # convert to IOIR notation
    IOIRNotation = []
    for index, noteval in enumerate(melodyline):
        if index < len(melodyline) - 1:
            start, end, note = noteval
            nstart, nend, nnote = melodyline[index + 1]
            ioir = (nend - nstart) / (end - start)
            pitchinterval = abs(nnote.midi - note.midi) % 12
            pitchinterval = -pitchinterval if nnote.midi - \
                note.midi < 0 else pitchinterval
            IOIRNotation.append((pitchinterval, ioir))

    return IOIRNotation
