import pickle
import music21
if __name__ == '__main__':
    pairs = []
    # Add midi to similar pairs set as a music21 stream
    def add_pair(firstmidi, secondmidi):
        first_stream = music21.converter.parse(firstmidi)
        second_stream = music21.converter.parse(secondmidi)
        pairs.append((first_stream, second_stream))
    # Add a single midi's different sections as a pair
    def add_pair_by_bars(midi, fs, fe, ss, se):
        stream = music21.converter.parse(midi)
        fsegment = stream.measures(fs, fe)
        ssegment = stream.measures(ss, se)
        pairs.append((fsegment,ssegment))

    # ADD SIMILAR PARTS
    # Scott Joplin, Easy Winners
    add_pair("mid/easywinners_1.mid", "mid/easywinners_2.mid")

    # Bach Inventions 1, 3, 4, 13
    add_pair("mid/invention1_1.mid", "mid/invention1_2.mid")
    add_pair("mid/invention1_3.mid", "mid/invention1_4.mid")
    add_pair("mid/invention3_1.mid", "mid/invention3_2.mid")
    add_pair("mid/invention3_3.mid", "mid/invention3_4.mid")
    add_pair("mid/invention4_1.mid", "mid/invention4_2.mid")
    add_pair("mid/invention4_2.mid", "mid/invention4_3.mid")
    add_pair("mid/invention4_3.mid", "mid/invention4_1.mid")
    add_pair("mid/invention4_4.mid", "mid/invention4_5.mid")
    add_pair("mid/invention4_6.mid", "mid/invention4_7.mid")
    #10
    add_pair("mid/invention13_1.mid", "mid/invention13_2.mid")
    add_pair("mid/invention13_3.mid", "mid/invention13_4.mid")
    add_pair("mid/invention13_5.mid", "mid/invention13_6.mid")

    # Chopin, The Minute Waltz
    add_pair_by_bars("mid/minute_waltz_chopin.mid", 0, 4, 0, 4)
    add_pair_by_bars("mid/minute_waltz_chopin.mid", 4, 12, 12, 20)
    add_pair_by_bars("mid/minute_waltz_chopin.mid", 8, 12, 16, 20)
    add_pair_by_bars("mid/minute_waltz_chopin.mid", 20, 22, 22, 24)
    add_pair_by_bars("mid/minute_waltz_chopin.mid", 24, 26, 32, 34)

    # Beethoven, Minuit in G Major
    add_pair("mid/minuitGmajor_1.mid", "mid/minuitGmajor_2.mid")

    # Twinkle Twinkle
    add_pair_by_bars("mid/twinkle_twinkle.mid", 0, 2, 8, 10)
    add_pair_by_bars("mid/twinkle_twinkle.mid", 2, 4, 6, 8)

    # Carol of the Bells
    add_pair_by_bars("mid/caroltest.mid", 0, 2, 2, 4)
    add_pair_by_bars("mid/caroltest.mid", 24, 26, 26, 28)

    # Owl
    add_pair_by_bars("mid/owl.mid", 0, 4, 4, 8)
    add_pair_by_bars("mid/owl.mid", 16, 20, 20, 24)

    pickle.dump(pairs, open('similar_streams.p', 'wb'))
    print('Saved similar pairs to file')