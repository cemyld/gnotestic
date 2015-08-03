import data
import analyze
import midi
import experiments
import patterns
import cmm
from IPython import embed


class Suggester():

    def __init__(self):
        self.classifier = patterns.fetch_classifier()
        self.midipaths = []
        self.transitions = {}
        self.testedpiece = None
        self.tolerance = 0.8

        segmentation = True
        all_keys = False

    def add_midi(self, midipath):
        musicpiece = data.piece(midipath)
        segmented = experiments.analysis(musicpiece, self.classifier)
        chosenscore, chosen, labelled_sections = segmented.chosenscore, segmented.chosen, segmented.labelled_sections
        for i, segment_score in enumerate(chosenscore):
            # get rid of low scores and last segment
            if segment_score[1] < 1 or i >= len(chosenscore) - 1:
                continue
            start, duration = segment_score[0]
            first = musicpiece.segment_by_bars(start, start + duration)
            first.label = "file: {} start: {} end: {}".format(
                first.label, start, start + duration)
            start, duration = chosenscore[i + 1][0]
            second = musicpiece.segment_by_bars(start, start + duration)
            second.label = "file: {} start: {} end: {}".format(
                second.label, start, start + duration)
            self.update_transitions((first, second))
        return segmented

    def update_transitions(self, segment_pair):
        if (segment_pair[0] in self.transitions):
            print('already in transition', segment_pair[0])
            self.transitions[segment_pair[0]] += [segment_pair[1]]
        else:
            self.transitions[segment_pair[0]] = [segment_pair[1]]

    def get_suggestions(self):
        suggestions = []
        for piece in list(self.transitions.keys()):
            if self.testedpiece.is_similar(piece, self.classifier, self.tolerance):
                suggestions.append(self.transitions[piece])
        return suggestions

    def save_midi(self, piece):
        midi.write("testingstuff.mid", piece)

    def set_target_piece(self, path):
        self.testedpiece = data.piece(path)

if __name__ == '__main__':
    sugg = Suggester()
    a = "mid/hilarity.mid"
    b = "mid/froglegs.mid"
    c = "mid/easywinners.mid"
    sugg.testedpiece = data.piece(a).segment_by_bars(0, 16)
    aresult = sugg.add_midi(a)
    bresult = sugg.add_midi(b)
    cresult = sugg.add_midi(c)
    embed()
