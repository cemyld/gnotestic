import similarity_scores
import melody_extractor
import pickle
import os
import data
import experiments
import patterns
import melody_extractor
import similarity_scores
from music21 import midi, converter
segments_folder = 'song_segments'
def _loadtransitiontable():
    if os.path.isfile('segment_transitions.p'):
        return pickle.load(open('segment_transitions.p', 'rb'))
    print('Could not find segment_transitions.p file, creating new transitions table')
    return {}
def _savetransitiontable(_tbl):
    pickle.dump(_tbl, open('segment_transitions.p', 'wb'))

def addMidiSong(songmidi):
    def savetreamtomidi(filename, stream):
        filepath = os.path.join(segments_folder, filename)
        mf = midi.translate.streamToMidiFile(stream)
        mf.open(filepath, 'wb')
        mf.write()
        mf.close()
    transitions = _loadtransitiontable()
    musicpiece = data.piece(songmidi)
    segmented = experiments.analysis(musicpiece, patterns.fetch_classifier())
    chosenscore, chosen, labelled_sections = segmented.chosenscore, segmented.chosen, segmented.labelled_sections
    musicstream = converter.parse(songmidi)
    filename = os.path.splitext(os.path.basename(songmidi))[0]
    for i, segment_score in enumerate(chosenscore):
        # cant process last segment
        if i >= len(chosenscore) - 1:
            continue
        start, duration = segment_score[0]
        first = musicstream.measures(start, start + duration)
        first_seg_str = "{}_{}_{}.mid".format(filename, start, start+duration)
        savetreamtomidi(first_seg_str, first)
        start, duration = chosenscore[i + 1][0]
        second = musicstream.measures(start, start + duration)
        second_seg_str = "{}_{}_{}.mid".format(filename, start, start+duration)
        savetreamtomidi(second_seg_str, second)
        #update transitions
        if (first_seg_str in transitions):
            transitions[first_seg_str] += [second_seg_str]
        else:
            transitions[first_seg_str] = [second_seg_str]
    _savetransitiontable(transitions)
def suggestMidi(querymidi, numofsugg):
    transitions = _loadtransitiontable()
    return [transitions[score_key[1]] for score_key in searchSegment(querymidi)[:numofsugg] if score_key[1] in transitions]

#searches the midi files in song_segments folder
def searchSegment(querymidi):
    qstream = converter.parse(querymidi)
    qmelo = melody_extractor.extractMelody(qstream)
    results = []

    # get similarity scores for each segment
    for filename in os.listdir(segments_folder):
        if filename.endswith('.mid'):
            filepath = os.path.join(segments_folder, filename)
            stream = converter.parse(filepath)
            melo = melody_extractor.extractMelody(stream)
            score = similarity_scores.ioir_edit_distance_norm(qmelo,melo)
            results.append((score, filename))
    return sorted(results)





