import os
import random
import time
import pyaudio
import wave
import numpy as np

from flask import Flask, Response,render_template
import pyaudio

path_sounds = './sounds/'
path_melodies = './melodies/'
path_notes = './notes/'

path_sounds = './sounds/'
path_melodies = './melodies/'
path_notes = './notes/'

files_sounds = {"morning":[], "afternoon":[], "evening":[]}
for r, d, f in os.walk(path_sounds):
    for file in f:
        if '.wav' in file and ".svn" not in file and "._" not in file:
            if "morning" in r:
                files_sounds["morning"].append(os.path.join(r, file))
            elif "afternoon" in r:
                files_sounds["afternoon"].append(os.path.join(r, file))
            elif "evening" in r:
                files_sounds["evening"].append(os.path.join(r, file))

files_melodies = {"morning":[], "afternoon":[], "evening":[]}
for r, d, f in os.walk(path_melodies):
    for file in f:
        if '.wav' in file and ".svn" not in file and "._" not in file:
            if "morning" in r:
                files_melodies["morning"].append(os.path.join(r, file))
            elif "afternoon" in r:
                files_melodies["afternoon"].append(os.path.join(r, file))
            elif "evening" in r:
                files_melodies["evening"].append(os.path.join(r, file))

files_notes = {"morning":[], "afternoon":[], "evening":[]}
for r, d, f in os.walk(path_notes):
    for file in f:
        if '.wav' in file and ".svn" not in file and "._" not in file:
            if "morning" in r:
                files_notes["morning"].append(os.path.join(r, file))
            elif "afternoon" in r:
                files_notes["afternoon"].append(os.path.join(r, file))
            elif "evening" in r:
                files_notes["evening"].append(os.path.join(r, file))


def getTrack(trackType):
    t = time.localtime()
    if t.tm_hour<=11:
        if trackType == "sound":
            return wave.open(random.choice(files_sounds["morning"]), 'rb')
        elif trackType == "melody":
            return wave.open(random.choice(files_melodies["morning"]), 'rb')
        elif trackType == "note":
            return wave.open(random.choice(files_notes["morning"]), 'rb')
        else:
            return Error()
    elif 11<t.tm_hour<19:
        if trackType == "sound":
            return wave.open(random.choice(files_sounds["afternoon"]), 'rb')
        elif trackType == "melody":
            return wave.open(random.choice(files_melodies["afternoon"]), 'rb')
        elif trackType == "note":
            return wave.open(random.choice(files_notes["afternoon"]), 'rb')
        else:
            return Error()
    elif 19<=t.tm_hour:
        if trackType == "sound":
            return wave.open(random.choice(files_sounds["evening"]), 'rb')
        elif trackType == "melody":
            return wave.open(random.choice(files_melodies["evening"]), 'rb')
        elif trackType == "note":
            return wave.open(random.choice(files_notes["evening"]), 'rb')
        else:
            return Error()


app = Flask(__name__)


def genHeader(sampleRate, bitsPerSample, channels, samples):
    datasize = 10240000 # Some veeery big number here instead of: #samples * channels * bitsPerSample // 8
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o



sound_wf = getTrack("sound")
melody_wf = getTrack("melody")
note_wf = getTrack("note")

# instantiate PyAudio
p = pyaudio.PyAudio()

FORMAT = p.get_format_from_width(sound_wf.getsampwidth())
CHUNK = 1024
RATE = sound_wf.getframerate()
bitsPerSample = 16 #16?
CHANNELS = sound_wf.getnchannels()
wav_header = genHeader(RATE, bitsPerSample, CHANNELS, CHUNK)


stream = p.open(format=p.get_format_from_width(sound_wf.getsampwidth()),
                channels=sound_wf.getnchannels(),
                rate=sound_wf.getframerate(),
                output=True)

@app.route('/audio_unlim')
def audio_unlim():
    # start Recording
    def sound():
        global sound_wf, melody_wf, note_wf
        data = wav_header
        yield(data)
        while True:
            sound=(np.frombuffer(sound_wf.readframes(CHUNK), dtype='<i2')).astype(np.float64) 
            melody=(np.frombuffer(melody_wf.readframes(CHUNK), dtype='<i2')).astype(np.float64)
            note=(np.frombuffer(note_wf.readframes(CHUNK), dtype='<i2')).astype(np.float64)
            sound_aux = sound
            melody_aux = melody
            note_aux = note


            if len(sound_aux)<2048:
                sound_aux = np.zeros((2048,))
                sound_aux[:len(sound)] = sound
                sound_wf = getTrack("sound")
            if len(melody_aux)<2048:
                melody_aux = np.zeros((2048,))
                melody_aux[:len(melody)] = melody
                melody_wf = getTrack("melody")
            if len(note_aux)<2048:
                note_aux = np.zeros((2048,))
                note_aux[:len(note)] = note
                note_wf = getTrack("note")

            total = (sound_aux+melody_aux+note_aux)/3
            data = total.astype('<i2').tobytes()

            yield(data)

    return Response(sound(), mimetype="audio/x-wav")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True,port=5000)