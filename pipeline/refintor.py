import mido
import os
import numpy as np
from utils.utils import get_file_name

from music21 import converter, note, chord

class Refintor:
    """
    Compare MIDI files.
    """

    def __init__(self, path, df, output_folder):
        self.path = path
        self.df = df
        self.output_folder = output_folder

    def manhattan_distance(self, list1, list2):
        distance = 0
        for sub1, sub2 in zip(list1, list2):
            sub_distance = 0
            for x, y in zip(sub1, sub2):
                sub_distance += abs(x - y)
            distance += sub_distance
        return distance

    def compare_midi_files(self, file1, file2):
        # Load midi files
        try:
            score1 = converter.parse(file1)
            score2 = converter.parse(file2)
        except:
            return 'read_error'

        # Extract notes from midi files and group adjacent pitches together
        notes1 = []

        for obj in score1.recurse():
            if isinstance(obj, note.Note):
                notes1.append([obj.pitch.midi])
            elif isinstance(obj, chord.Chord):
                for p in obj.pitches:
                    notes1.append([p.midi])

        notes2 = []

        for obj in score2.recurse():
            if isinstance(obj, note.Note):
                notes2.append([obj.pitch.midi])
            elif isinstance(obj, chord.Chord):
                for p in obj.pitches:
                    notes2.append([p.midi])
                    
        # Calculate similarity for each group of pitches
        return self.manhattan_distance(notes1, notes2)

    def check_duplicate(self):

        df = self.df
        output_folder = self.output_folder

        song_file_name = get_file_name(self.path)

        current_instr = None
        comparing_instr = None
        current_file = None
        duplicated = {}
        duplicate_detected = []

        midi_folder = os.path.join(output_folder, song_file_name)
        midi_files = df['file_name']
        midi_files_path = [os.path.join(midi_folder, file) for file in midi_files]

        df['repeated'] = np.nan

        for i in range(len(df)):
            current_instr = df.loc[i, 'instrument_name']
            current_file = df.loc[i, 'file_name']

            if current_file in duplicate_detected:
                continue

            for j in range(len(df)):
                comparing_instr = df.loc[j, 'instrument_name']

                if current_instr == comparing_instr:
                    if i == j:
                        continue
                    else:
                        similarity = self.compare_midi_files(midi_files_path[i], midi_files_path[j])
                        if similarity == 0:
                            duplicated[df['file_name'][i]] = df['file_name'][j]
                            duplicate_detected.append(df['file_name'][j])
                            df.loc[i, 'repeated'] = df['file_name'][j]
                            
                        elif similarity == 'read_error':
                            df.loc[i, 'repeated'] = 'read_error'

                elif current_instr != comparing_instr:
                    continue
            
        return df