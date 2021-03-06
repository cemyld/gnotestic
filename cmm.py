# Markov Model thingy
import random, sys, time
import data, analyze, midi, experiments, patterns, chords
from decimal import Decimal as fixed
from IPython import embed

class Markov(object):

    '''
    Generic object for a Markov model

    trains state and state transitions by reading statechains
    statechain: a list of states
    state: a concrete class derived from State (described below)

    '''
    START_TOKEN = 'start_token'
    STOP_TOKEN = 'stop_token'

    def __init__(self, chain_length=1):
        self.chain_length = chain_length
        self.markov = {}
        self.states = set()
        self.state_chains = [[]]

    def add(self, chain):
        '''
        add a statechain to the markov model (i.e. perform training)

        '''
        self.state_chains.append(chain)
        buf = [Markov.START_TOKEN] * self.chain_length
        for state in chain:
            v = self.markov.get(tuple(buf), [])
            v.append(state)
            self.markov[tuple(buf)] = v
            buf = buf[1:] + [state]
            self.states.add(state)
        v = self.markov.get(tuple(buf), [])
        v.append(Markov.STOP_TOKEN)
        self.markov[tuple(buf)] = v

    def generate(self, seed=[]):
        '''
        generate a statechain
        seed is optional; if provided, will build statechain from seed
        (note: seed is untested)

        '''
        buf = [Markov.START_TOKEN] * self.chain_length
        if seed and len(seed) > self.chain_length:
            buf = seed[-self.chain_length:]
        elif seed:
            buf[-len(seed):] = seed
        state_chain = []
        count = 0
        while not state_chain or count < 10:
            elem = random.choice(self.markov[tuple(buf)])
            while elem != Markov.STOP_TOKEN:
                state_chain.append(elem.copy())
                buf = buf[1:] + [elem]
                elem = random.choice(self.markov[tuple(buf)])
            count += 1
        if not state_chain:
            print("Warning: state_chain empty; seed={}".format(seed))
        return state_chain

    def copy(self):
        mm = Markov()
        # shallow copies (TODO: deep copy?)
        mm.chain_length = self.chain_length
        mm.markov = self.markov.copy()
        mm.states = self.states.copy()
        mm.state_chains = [ chain[:] for chain in self.state_chains ]
        return mm

    def add_model(self, model):
        '''
        union of the states and state transitions of self and model
        returns a new markov model
        '''
        mm = self.copy()
        for chain in model.state_chains:
            mm.add(chain)
        return mm

class State(object):

    '''
    Basic interface of a state to be used in a Markov model
    Please override state_data() and copy()

    '''

    def state_data(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def __hash__(self):
        tup = self.state_data()
        return hash(tup)

    def __eq__(self, other):
        if isinstance(other, State):
            return self.state_data() == other.state_data()
        return False

    def __repr__(self):
        tup = self.state_data()
        return str(tup)

    def copy(self):
        raise NotImplementedError("Subclass must implement abstract method")

class SegmentState(State):

    def __init__(self, label, mm):
        self.label = label
        self.mm = mm

    def state_data(self):
        relevant = [self.label]
        return tuple(relevant)

    def copy(self):
        s = SegmentState(self.label, self.mm)
        return s

    @staticmethod
    def state_chain_to_note_states(state_chain):
        note_states = []
        for s in state_chain:
            gen = s.mm.generate()
            note_states.extend(gen)
        return note_states

class NoteState(State):

    def __init__(self, notes, bar, chord='', origin=''):
        # State now holds multiple notes, all with the same pos
        self.notes = [ n.copy() for n in sorted(notes, key=lambda x: (x.dur, x.pitch)) ]
        self.bar = bar
        self.bar_pos = fixed(self.notes[0].pos % bar) / bar
        self.state_position = fixed(self.notes[0].pos) / bar
        self.state_duration = 0 # set later
        self.chord = chord
        self.origin = origin

        for n in self.notes:
            n.dur = fixed(n.dur) / bar

    def state_data(self):
        # all of this will be hashed
        notes_info = [ (n.pitch, n.dur) for n in self.notes ]
        relevant = [self.bar_pos, self.state_duration, self.chord, tuple(notes_info)]
        return tuple(relevant)

    def copy(self):
        s = NoteState(self.notes, 1, self.chord, self.origin)
        s.bar = self.bar
        s.bar_pos = self.bar_pos
        s.state_position = self.state_position
        s.state_duration = self.state_duration
        return s

    def transpose(self, offset):
        s = self.copy()
        ctemp = self.chord.split('m')[0]
        s.chord = chords.translate(chords.untranslate(ctemp)+offset) + ('m' if 'm' in self.chord else '')
        s.origin = 'T({})'.format(offset) + s.origin
        for n in s.notes:
            n.pitch += offset
        return s

    @staticmethod
    def state_chain_to_notes(state_chain, bar):
        last_pos = 0
        notes = []
        for s in state_chain: # update note positions for each s in state_chain
            for n in s.notes:
                nc = n.copy()
                nc.pos = int(last_pos * bar)
                nc.dur = int(n.dur * bar)
                notes.append(nc)
            last_pos += s.state_duration
        return notes

    @staticmethod
    def notes_to_state_chain(notes, bar):
        bin_by_pos = {}
        for n in notes:
            v = bin_by_pos.get(n.pos, [])
            v.append(n)
            bin_by_pos[n.pos] = v

        positions = sorted(bin_by_pos.keys())
        state_chain = [NoteState(bin_by_pos[x], bar) for x in positions]

        if not len(state_chain):
            return state_chain

        for i in range(len(state_chain) - 1):
            state_chain[i].state_duration = state_chain[i+1].state_position - state_chain[i].state_position
        state_chain[-1].state_duration = max(n.dur for n in state_chain[-1].notes)

        return state_chain

    @staticmethod
    def piece_to_state_chain(piece, use_chords=True):
        bin_by_pos = {}
        for n in piece.unified_track.notes:
            v = bin_by_pos.get(n.pos, [])
            v.append(n)
            bin_by_pos[n.pos] = v

        positions = sorted(bin_by_pos.keys())
        if use_chords:
            cc = chords.fetch_classifier()
            allbars = cc.predict(piece)
            state_chain = [NoteState(bin_by_pos[x], piece.bar, chord=allbars[x/piece.bar], origin=piece.filename) for x in positions]
        else:
            state_chain = [NoteState(bin_by_pos[x], piece.bar, chord='', origin=piece.filename) for x in positions]

        if not len(state_chain):
            return state_chain

        for i in range(len(state_chain) - 1):
            state_chain[i].state_duration = state_chain[i+1].state_position - state_chain[i].state_position
        state_chain[-1].state_duration = max(n.dur for n in state_chain[-1].notes)

        return state_chain

    def __repr__(self):
        tup = self.state_data()
        return str(tup) + ' ' + str(self.notes)

def piece_to_markov_model(musicpiece, c, segmentation=False, all_keys=False):
    mm = Markov()
    print("all_keys:" + str(all_keys))
    if not segmentation:
        state_chain = NoteState.piece_to_state_chain(musicpiece, all_keys)
        mm.add(state_chain)
        if all_keys:
            for i in range(1, 6):
                shifted_state_chain = [ s.transpose(i) for s in state_chain ]
                mm.add(shifted_state_chain)
            for i in range(1, 7):
                shifted_state_chain = [ s.transpose(-i) for s in state_chain ]
                mm.add(shifted_state_chain)
    else:
        segmented = experiments.analysis(musicpiece, c)
        chosenscore, chosen, labelled_sections = segmented.chosenscore, segmented.chosen, segmented.labelled_sections
        #state_chain = [ SegmentState(labelled_sections[ch], piece_to_markov_model(musicpiece.segment_by_bars(ch[0], ch[0]+ch[1]), c)) for ch in chosen ]

        state_chain = []
        labelled_states = {}
        for ch in chosen:
            i, k = ch[0], ch[1]
            label = labelled_sections[ch]
            ss = labelled_states.get(label, None)
            segment = musicpiece.segment_by_bars(i, i+k)
            if not ss:
                ss = SegmentState(label, piece_to_markov_model(segment, c, segmentation=False, all_keys=all_keys))
                labelled_states[label] = ss
            else:
                # ss.mm holds the mm that generates notes
                _state_chain = NoteState.notes_to_state_chain(segment.unified_track.notes, segment.bar)
                ss.mm.add(_state_chain)
            state_chain.append(ss)

        print('Original Sections: ({})'.format(musicpiece.filename))
        print([ g.label for g in state_chain ])
        print(chosenscore)
        mm.add(state_chain)
    return mm

def test_variability(mm, meta, bar):
    lens = []
    for i in range(10):
        song, gen, a = generate_song(mm, meta, bar, True)
        lens.append(len(a))
    print(lens)

def generate_song(mm, meta, bar, segmentation=False):
    song = []
    song.append(meta)

    if not segmentation:
        gen = mm.generate()
        print([g.origin + ('-' if g.chord else '') + g.chord for g in gen])
    else:
        gen_seg = mm.generate()
        print('Rearranged Sections:')
        print([ g.label for g in gen_seg ])
        gen = SegmentState.state_chain_to_note_states(gen_seg)

    a = NoteState.state_chain_to_notes(gen, bar)
    if not a: return generate_song(mm, meta, bar, segmentation)
    song.append([ n.note_event() for n in a ])

    return song, gen, a

if __name__ == '__main__':
    c = patterns.fetch_classifier()
    segmentation = True
    all_keys = False

    if len(sys.argv) == 4:
        musicpiece = data.piece(sys.argv[1])
        musicpiece = musicpiece.segment_by_bars(int(sys.argv[2]), int(sys.argv[3]))
        mm = piece_to_markov_model(musicpiece, c, segmentation)
        song, gen, a = generate_song(mm, musicpiece.meta, musicpiece.bar, segmentation)

    else:
        pieces = ["mid/hilarity.mid", "mid/twinkle_twinkle.mid"]
        mm = Markov()
        for p in pieces:
            musicpiece = data.piece(p)
            _mm = piece_to_markov_model(musicpiece, c, segmentation, all_keys)
            mm = mm.add_model(_mm)
        song, gen, a = generate_song(mm, musicpiece.meta, musicpiece.bar, segmentation)

    # midi.write('output.mid', song)
    embed()
