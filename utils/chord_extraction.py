import pandas as pd
import numpy as np

import glob
import os

from music21 import converter, midi, key, instrument, meter, interval, note, pitch, stream, tempo, chord
from utils import open_midi

from difflib import get_close_matches

class Chord_Extractor():
    def __init__(self, path):
        self.path = path
        self.chord_df = pd.read_csv('csv/chord_list.csv')
        self.chord_list = self.get_chord_list(self.chord_df)
    
    def get_path_list(self, folder_path):
        path_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".mid"):
                    path_list.append(os.path.join(root, file))
        return path_list
    
    def get_chord_list(self, chord_df):
        cl = chord_df['NOTES'].to_list()

        for idx, v in enumerate(cl):
            cl[idx] = v.replace(',', '')

        for idx, v in enumerate(cl):
            cl[idx] = v.replace('b', '-')
        return cl

    def extract_chord_expression(self, score):

        chord_progression = list()
        cp = list()

        cl = self.chord_list
        chord_df = self.chord_df

        length = score.recurse().getElementsByClass('Measure')[-1].number

        for i in range(length):
    
            note_list = list()

            for obj in score.measures(i+1, i+1).recurse():
                if isinstance(obj, note.Note):
                    if obj.duration.quarterLength > 0:
                        note_list.append(obj.name)  
                elif isinstance(obj, chord.Chord):
                    for p in obj.pitches:   
                        note_list.append(p.name) 

            current_chord = list()

            for value in note_list:
                if value not in current_chord:
                    current_chord.append(value)

            if len(current_chord) == 0:
                cp.append('Bar_None')

            if len(current_chord) == 1:
                cp.append(str(current_chord[0]))

            if len(current_chord) > 1:

                notes = str()
                
                for i in current_chord:
                    notes += i
                
                if len(notes) > 5:
                    notes = notes[:5]
                
                close_matches = get_close_matches(notes, cl , 1, 0.6)
            
                if not close_matches:
                    close_matches = get_close_matches(notes, cl , 1, 0.5)
                
                if not close_matches:
                    close_matches = get_close_matches(notes, cl , 1, 0.4)

                tnl = list()
                for i in range(len(str(close_matches[0]))):
                    if close_matches[0][i] == '#':
                        tnl.append(close_matches[0][i-1] + '#')
                        tnl.remove(close_matches[0][i-1])
                    elif close_matches[0][i] == '-':
                        tnl.append(close_matches[0][i-1] + 'b')
                        tnl.remove(close_matches[0][i-1])
                    else:
                        tnl.append(close_matches[0][i])

                basic = chord_df[chord_df['Notes_list_string'] == str (tnl)]['CHORD_ROOT'].values[0]
                chord_type = chord_df[chord_df['Notes_list_string'] == str(tnl)]['CHORD_TYPE'].values[0]
                if chord_type == '5':
                    chord_type = ''
                if chord_type == 'm5':
                    chord_type = 'm'
                cp.append(str(basic + chord_type))

        if set(cp) == {'Bar_None'}:
            return ['Bar_None']
                    
        for c in cp:
            for i in range(8):
                chord_progression.append(c)
        
        return chord_progression

    def start(self, path):
        score = open_midi(path)
        chord_progression = self.extract_chord_expression(score)
        return chord_progression

