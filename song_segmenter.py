import experiments
import analyze
import data
import midi
import patterns
import sys
from IPython import embed
from music21 import corpus, converter, midi
import os
if __name__ == '__main__':
    c = patterns.fetch_classifier()
    segments_folder = 'song_segments'
    piece_paths = ["mid/twinkle_twinkle.mid"]
    if len(sys.argv) == 2:
        musicpiece = data.piece(sys.argv[1])
        musicpiece = musicpiece.segment_by_bars(
            int(sys.argv[2]), int(sys.argv[3]))

    for path in piece_paths:
        songpiece = data.piece(path)
        segmented = experiments.analysis(songpiece, c)
        # create folder to store segments
        filename = os.path.splitext(os.path.basename(path))[0]
        directory = os.path.join(segments_folder, filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        #segment the song and create music21 streams to save midi
        song_stream = converter.parse(path)
        chosenscore, chosen, labelled_sections = segmented.chosenscore, segmented.chosen, segmented.labelled_sections
        print(chosenscore)
        for i, segment_score in enumerate(chosenscore):
            if segment_score[1] < 1:
                continue
            start, duration = segment_score[0]
            segment = song_stream.measures(start, start+duration)
            filename = '{}_{}.mid'.format(start, start+duration)
            filepath = os.path.join(directory, filename)
            mf = midi.translate.streamToMidiFile(segment)
            mf.open(filepath, 'wb')
            mf.write()
            mf.close()
    embed()
