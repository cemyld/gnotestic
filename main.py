import midi
from IPython import embed


pieces = ["mid/twinkle_twinkle.mid"]
a = midi.read(pieces[0])

embed()
