import pandas as pd
import numpy as np

import glob
import os

from music21 import converter, midi, key, instrument, meter, interval, note, pitch, stream, tempo, chord
from utils import open_midi

from difflib import get_close_matches

class Chord_Extractor():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.path_list = self.get_path_list(self.data_dir)
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

