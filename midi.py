import mido
help={}
help["song"]="List of tracks. Track 1 contains events that apply to all tracks, the other tracks contain individual events."
help["track"]="List of events."
help["event"]="An event has the form [description, position, values...]. The possible descriptions are \"ticks\", \"tempo\", \"time\", \"key\", \"note\", and \"bar\"."
help["ticks"]="This type of event has the form [\"ticks\", position, number of ticks per quarter note]."
help["tempo"]="This type of event has the form [\"tempo\", position, number of microseconds per quarter note]."
help["time"]="This type of event has the form [\"time\", position, top of time signature, bottom]."
help["key"]="This type of event has the form [\"key\", position, number of sharps in key signature, major(0) or minor(1)]."
help["note"]="This type of event has the form [\"note\", position, duration, channel, note number]."
help["bar"]="This type of event has the form [\"bar\", position]."
help["transpose"]="transpose(song, amount) transposes song in place up by number of semitones specified in amount."
help["bar"]="bar(song) adds bars to song in place. Note positions are recalculated relative to the last bar."
help["unbar"]="unbar(song) removes bars from song in place."
help["playing"]="playing(song, time) returns a list, each element is a list of notes playing, or [\"rest\"] if none are playing. The element number in the higher list corresponds to the track number (ignoring track 1)."
help["harmony"]="harmony(song) returns a list of harmonies. Each harmony is a list of what note is playing in each track (ignoring track 1) plus the frequency of the harmony."
help["write"]="write(filename, song)"


def reverse_table(table):
    """Return value: key for dictionary."""
    return {value: key for (key, value) in table.items()}

key_signature_decode = {
        (-7, 0): 'Cb',
        (-6, 0): 'Gb',
        (-5, 0): 'Db',
        (-4, 0): 'Ab',
        (-3, 0): 'Eb',
        (-2, 0): 'Bb',
        (-1, 0): 'F',
        (0, 0): 'C',
        (1, 0): 'G',
        (2, 0): 'D',
        (3, 0): 'A',
        (4, 0): 'E',
        (5, 0): 'B',
        (6, 0): 'F#',
        (7, 0): 'C#',
        (-7, 1): 'Abm',
        (-6, 1): 'Ebm',
        (-5, 1): 'Bbm',
        (-4, 1): 'Fm',
        (-3, 1): 'Cm',
        (-2, 1): 'Gm',
        (-1, 1): 'Dm',
        (0, 1): 'Am',
        (1, 1): 'Em',
        (2, 1): 'Bm',
        (3, 1): 'F#m',
        (4, 1): 'C#m',
        (5, 1): 'G#m',
        (6, 1): 'D#m',
        (7, 1): 'A#m',
    }
key_signature_encode = reverse_table(key_signature_decode)


#Parse a midi bytes and return a song
#Return -1 in case of error
def parse(midifile):
    song = [[["ticks", 0, midifile.ticks_per_beat]]]
    song.append([])
    for i, track in enumerate(midifile.tracks):
        tracklist = []
        occured=[]
        ticks = 0
        for j, message in enumerate(track):
            ticks += message.time
            if isinstance(message, mido.MetaMessage):
                if message.type == 'set_tempo':
                    tracklist += [["tempo", message.time, message.tempo]]
                if message.type == 'time_signature':
                    tracklist += [["time", message.time, message.numerator, message.denominator]]
                if message.type == 'key_signature':
                    encoded_key = key_signature_encode[message.key]
                    tracklist += [["key", message.time, encoded_key[0], encoded_key[1]]]
            else:
                if message.type == 'note_on' and message.velocity > 0:
                    duration = 0
                    # go through rest of commands
                    for offcommand in track[j+1:]:
                        duration += offcommand.time
                        if ((offcommand.type =='note_on' and offcommand.velocity == 0) or offcommand.type == 'note_off') and offcommand.note == message.note:
                            break
                    song[1] += [['note', ticks, duration, 0, message.note]]


        song[0] += tracklist
    return song
#Read a midi file and return a nicely constructed list that represents the song in the midi.
#Return -1 in case of error
#The list is structured as follows:
#It is a list of tracks.
#The first track specifies things that correspond to all tracks.
#The other tracks specify things specific to themselves.
#Each track is a list of events.
#An event has the form [description, position, values...]
#description is a string describing the type of event.
#position is the position of the event in the song in ticks.
#values is a bunch of values based on which kind of event it is.
#Here's a list of description and their corresponding values
#"ticks": Value is number of ticks per quarter note.
#"tempo": Value is number of microseconds per quarter note.
#"time": Values are top of time signature, bottom of time signature.
#"key": Values are number of sharps (negative means flats), major (0) or minor (1)
#"note": Values are duration, channel, note number
def read(filename):
    midifile=mido.MidiFile(filename)
    return parse(midifile)

#Write a midi track to a file based on a list of bytes.
#The track header and end message are appended automatically, so they should not be included in bytes.
def writetrack(file, bytetemp):
    bytetemp =["\0","\xff","\x01","\0"]+bytetemp+["\x01","\xff","\x2f","\0"]#Put a 1 here to match Sibelius 2.
    size0=len(bytetemp)%0x100
    size1=(len(bytetemp)>>8)%0x100
    size2=(len(bytetemp)>>16)%0x100
    size3=(len(bytetemp)>>24)
    trackheader=["M","T","r","k",chr(size3),chr(size2),chr(size1),chr(size0)]
    bytetemp=trackheader+bytetemp
    for byte in bytetemp:
        file.write(byte)
    return

def comparetime(message1, message2):
    if message1[1]<message2[1]:
        #raise Exception("error")
        return -1
    elif message1[1]==message2[1]:
        return 0
    else:
        return 1

def ilog2(x):
    result=-1
    while x!=0:
        x>>=1
        result+=1
    return result

#Write a midi file based on a nicely contructed list.
def write(filename, song):
    file=open(filename,"wb")
    ticks=0
    for event in song[0]:
        if event[0]=="ticks":
            ticks=event[2]
    if ticks==0:
        raise Exception("error")
        return -1
    tracks=len(song)
    header=["M","T","h","d","\0","\0","\0","\6","\0","\1","\0",chr(tracks),chr(ticks>>8),chr(ticks&0xff)]
    for byte in header:
        file.write(byte)
    bytetemp=[]
    lasttime=0
    for event in song[0]:
        if event[0]=="tempo":
            bytetemp+=delta(event[1]-lasttime)
            bytetemp+=["\xff","\x51","\x03"]
            bytetemp+=[chr(event[2]>>16),chr((event[2]>>8)&0xff),chr(event[2]&0xff)]
        elif event[0]=="time":
            bytetemp+=delta(event[1]-lasttime)
            bytetemp+=["\xff","\x58","\x04"]
            bytetemp+=[chr(event[2]),chr(ilog2(event[3])),chr(24),chr(8)]
        elif event[0]=="key":
            bytetemp+=delta(event[1]-lasttime)
            bytetemp+=["\xff","\x59","\x02"]
            sharps=event[2]
            if sharps<0:
                sharps=0x100+sharps
            bytetemp+=[chr(sharps),chr(event[3])]
        lasttime=event[1]
    writetrack(file, bytetemp)
    for track in song[1:]:
        messages=[]
        for event in track:
            if event[0]=="note":
                messages+=[["on",event[1],event[3],event[4]]]
                messages+=[["off",event[1]+event[2],event[3],event[4]]]
        messages.sort(comparetime)
        lasttime=0
        for i in range(len(messages)):
            temp=messages[i][1]
            messages[i][1]=messages[i][1]-lasttime
            lasttime=temp
        bytetemp=[]
        for message in messages:
            if message[0]=="on":
                bytetemp+=delta(message[1])
                bytetemp+=[chr(0x90|message[2])]
                bytetemp+=[chr(message[3])]
                bytetemp+=["\x79"]
            elif message[0]=="off":
                bytetemp+=delta(message[1])
                bytetemp+=[chr(0x80|message[2])]
                bytetemp+=[chr(message[3])]
                bytetemp+=["\0"]
        writetrack(file, bytetemp)
    file.close()
    return

def transpose(song, amount):
    for i in range(len(song)):
        for j in range(len(song[i])):
            if song[i][j][0]=="note":
                song[i][j][4]+=amount
            elif song[i][j][0]=="key":
                song[i][j][2]+=amount
    return

def bar(song):
    for event in song[0]:
        if event[0]=="ticks":
            ticks=event[2]
        elif event[0]=="time":#make this better -- time sig could change
            top=event[2]
            bottom=event[3]
    bar=4*ticks*top/bottom
    for i in range(len(song)):
        offset=bar
        j=0
        while j<len(song[i]):
            while song[i][j][1]>=offset:
                song[i].insert(j,["bar",offset])
                offset+=bar
                j+=1
            song[i][j][1]%=bar
            j+=1
    return

def unbar(song):
    for i in range(len(song)):
        bar=0
        j=0
        while j<len(song[i]):
            if song[i][j][0]=="bar":
                bar=song[i][j][1]
                del song[i][j]
            else:
                song[i][j][1]+=bar
                j+=1
    return

def playing(song, time):
    result=[]
    for track in song[1:]:
        result+=[["rest"]]
        for event in track:
            if event[0]=="note":
                if event[1]+event[2]>time:
                    if event[1]<=time:
                        if result[-1]==["rest"]:
                            result[-1]=[event[4]]
                        else:
                            result[-1]+=[event[4]]
            if event[1]>time:
                break
    return result

def harmony(song):
    tracks=song[1:]
    i=[0]*len(tracks)
    result=[]
    while True:
        #find minimum time, doesn't have to be unique
        ind=len(i)#poison value
        min=-1
        dur=0
        for j in range(len(i)):
            if i[j]<len(tracks[j]) and (tracks[j][i[j]][1]<min or min==-1):
                min=tracks[j][i[j]][1]
                dur=tracks[j][i[j]][2]
                ind=j
        if min==-1:
            print("no minimum time found.")
        #find pairs of concurrent notes
        import rel
        temp=rel.cproduct(playing(song, tracks[ind][i[ind]][1]))
        #Add to result
        for x in temp:
            if x in [y[0:2] for y in result]:
                result[[y[0:2] for y in result].index(x)][2]+=1
            else:
                result+=[x+[1]]
        #increment the track we just looked at so we don't count it again
        i[ind]+=1
        #see if we need to quit
        quit=True
        for j in range(len(i)):
            if i[j]<len(tracks[j]):
                quit=False
        if quit:
            break
    return result
