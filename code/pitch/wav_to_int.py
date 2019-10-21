import argparse
import csv
import vamp
import librosa
import os
import numpy as np
from scipy.signal import convolve
from midiutil.MidiFile import MIDIFile
import scipy.signal as sig
from scipy.signal import argrelextrema
from scipy.signal import medfilt
import scipy

def write_temp_midi(notes):
    track = 0
    time = 0
    tempo = 130
    midifile = MIDIFile(1, adjust_origin=False)

    # Add track name and tempo.
    midifile.addTrackName(track, time, "MIDI TRACK")
    midifile.addTempo(track, time, tempo)

    channel = 0
    volume = 100
    for note in notes:
        onset = note[0] * (tempo/60.)
        duration = note[1] * (tempo/60.)
        pitch = int(note[2])
        midifile.addNote(track, channel, pitch, onset, duration, volume)
    binfile = open('temp.mid', 'wb')
    midifile.writeFile(binfile)
    binfile.close()
    os.system('midicsv temp.mid > temp.csv')

# Convert an array of Hz elements to Midi scale.
def hz2midi(hz):
    hz_nonneg = hz.copy()
    midi = np.zeros(len(hz))
    midi[hz > 0] = 69 + 12*np.log2(hz_nonneg[hz > 0]/440.)

    return midi

def get_intervals_and_save_as_npy(path, gen_int=True, gen_ioir=False):
    f = open('temp.csv', 'r')
    parsed = csv.reader(f, delimiter=',')
    events = []
    notes = []
    durations = []
    onsets = []
    last_time = None
    last_note = None
    for row in parsed:
        if row[2]==' Header':
            ppqn = int(row[5])
        if row[2]==' Tempo':
            tempo = int(row[3])
        if row[2]==' Note_on_c':
            time = int(row[1])
            note = int(row[4])
            is_on = bool(int(row[5]))
            if not is_on:
                events+=[[time-last_time,note]]
                notes+=[note]
                durations+=[time-last_time]
                onsets+=[time]
                #events+=[note]*(time-len(events))
            if(last_time==None or last_note==note): last_time = time
            last_note = note
        if row[2]==' Note_off_c':
            time = int(row[1])
            note = int(row[4])
            is_on = False
            events+=[[time-last_time,note]]
            notes+=[note]
            durations+=[time-last_time]
            onsets+=[time]
            last_time = time
    events = np.asarray(events)
    notes = np.asarray(notes)
    durations = np.asarray(durations)
    onsets = np.asarray(onsets)
    intervals = notes[1:]-notes[:-1]
    if gen_ioir:
        main_onsets = onsets
        ioi = main_onsets[1:]-main_onsets[:-1]
        ioir = np.log2(ioi[1:]/ioi[:-1])
        np.save(path+'.ioir', ioir)
    if gen_int:
        intervals = intervals[np.nonzero(intervals)]
        np.save(path+'.int', intervals)

def transcribe_to_mid_file(midi_array, sr, hop, transition, filter_duration):
    rate = float(hop)/sr
    filter_size = int(filter_duration * sr / float(hop))
    if filter_size % 2 == 0:
        filter_size += 1
    nonzero = np.nonzero(midi_array)
    midi_filt = np.zeros(len(midi_array))
    midi_filt[nonzero] = convolve(midi_array[nonzero], np.ones(filter_size)/filter_size)[int(filter_size/2):-int(filter_size/2)]
    midi_filt[np.where(np.abs(np.diff(midi_filt))>transition)[0]] = -10
    up = np.where(midi_filt[1:]-midi_filt[:-1]>24)[0]
    down = np.where(midi_filt[1:]-midi_filt[:-1]<-24)[0]
    if len(up)>len(down):
        up = up[:-1]
    if len(up)<len(down):
        down = down[1:]
    len_sec = (down-up)/(sr/float(hop))
    small_contours = np.where(len_sec<0.1)[0]
    for e in small_contours:
        midi_filt[up[e]:down[e]+1]=-10
    midi_filt = np.round(midi_filt)

    minduration = filter_duration
    notes = []
    p_prev = -2
    duration = 0
    onset = 0
    initial_note = 0
    true_initial_note = 0
    notes_out = []
    for n, p in enumerate(midi_filt):
        if abs(p-p_prev)<2:
            if(duration == 1): onset = n
            duration += 1
        else:
            # treat 0 as silence
            if p_prev != None and p_prev > 0:
                # add note
                duration_sec = duration * rate
                # only add notes that are long enough
                if duration_sec >= minduration:
                    onset_sec = (onset-initial_note) * rate
                    if(len(notes)==0): 
                        initial_note = onset
                        onset_sec = (onset-initial_note) * rate
                    elif(onset_sec-(notes[-1][0]+notes[-1][1])>1): 
                        notes = []
                        initial_note = onset
                        onset_sec = (onset-initial_note) * rate
                    note = midi_filt[onset:onset+duration]
                    median = scipy.stats.mode(note[np.where(note>0)])[0]
                    notes.append((onset_sec, duration_sec, median))
                    if(len(notes)>len(notes_out)):
                        notes_out = notes
                        true_initial_note = initial_note

            if p_prev != None and p_prev == -10 and p == 0 and len(notes)>0:
                onset_sec = (onset-initial_note) * rate
                duration_sec = duration * rate
                if notes[-1][0]!=onset_sec and duration_sec>=minduration:
                    note = midi_filt[onset:onset+duration]
                    median = scipy.stats.mode(note[np.where(note>0)])[0]
                    if(median!=[]): notes.append((onset_sec, duration_sec, median))
                else:
                    new_note = np.asarray(notes[-1])
                    new_note[1] = new_note[1]+duration*rate
                    notes[-1] = tuple(new_note)

            if not (p_prev != None and p_prev == -10 and p > 0):
                # start new note
                onset = n
                duration = 1
            p_prev = p

    if p_prev > 0:
        duration_sec = duration * rate
        if duration_sec >= minduration:
            onset_sec = onset * rate
            notes.append((onset_sec, duration_sec, p_prev))
    write_temp_midi(notes_out)


# Load wav infile and extract midi scale f0 array.
def load_wav_as_midi_array(infile, sr):
    data, sr = librosa.load(infile, sr=sr, mono=True)
    melody = vamp.collect(data, sr, "mtg-melodia:melodia")
    pitch_array = melody['vector'][1]
    return hz2midi(pitch_array)

# Extract a interval array from a wav file.
def wav_to_int(infile, sr, hop, transition, filter_duration, mid):
    if mid:
        os.system('midicsv '+ infile +' > temp.csv')
    else:
        midi_array = load_wav_as_midi_array(infile, sr)
        transcribe_to_mid_file(midi_array, sr, hop, transition, filter_duration)
    get_intervals_and_save_as_npy(infile)
    os.system('rm temp.mid temp.csv')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Path to input audio file.")
    parser.add_argument("--mid", help="Use this flag for mid files input.", action="store_true")
    parser.add_argument("sr", help="File sample rate.", default=8000, type=int, nargs='?')
    parser.add_argument("hop", help="Hop size for filtering window in transcription step.", default=0.0029, type=float, nargs='?')
    parser.add_argument("transition", help="This parameter will be used to set apart notes from transition intervals in transcription step.", default=0.0005, type=float, nargs='?')
    parser.add_argument("filter_duration", help="Length of window for mean filter applied in transcription step.", default=0.2, type=float, nargs='?')
    args = parser.parse_args()

    wav_to_int(args.infile, args.sr, args.sr*args.hop, 1.0/(args.transition*args.sr), args.filter_duration, args.mid)
