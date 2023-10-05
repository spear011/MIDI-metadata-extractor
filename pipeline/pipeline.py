import os
import glob
import pandas as pd

from pipeline.truncator import Truncator
from pipeline.refintor import Refintor

from tqdm import tqdm

import argparse

import warnings
warnings.filterwarnings("ignore")

class Pipeline:
    """
    Preprocess data for training.
    """

    def __init__(self, data_folder, num_bars, output_folder, genre, crop_mode):
        self.data_folder = data_folder
        self.num_bars = num_bars
        self.file_path = glob.glob(f'{self.data_folder}/*.mid')
        self.output_folder = output_folder
        self.p_df = pd.read_csv(r'csv/program_change.csv')
        self.genre = genre
        self.crop_mode = crop_mode
    
    def start(self):

        num_bars = self.num_bars
        file_path = self.file_path
        output_folder = self.output_folder
        p_df = self.p_df
        genre = self.genre
        crop_mode = self.crop_mode

        error = 0

        df = pd.DataFrame(columns=['song_midi', 'file_name', 'program_change_value' ,'program_change_msg', 
                                   'start_position', 'end_position', 'num_bars', 'tempo', 'key', 'min_pitch', 'max_pitch', 'mean_pitch',
                                   'min_velocity', 'max_velocity', 'time_signature'])
        
        error_df = pd.DataFrame(columns=['midi_path', 'error_msg'])

        for idx, path in tqdm(enumerate(file_path)):
            
            current_df, df_type_msg = Truncator(path, num_bars, output_folder, p_df).truncate_midi_by_bars(crop_mode=crop_mode)

            if current_df is None:
                error += 1
                continue
            
            if df_type_msg == 'error':
                error_df = pd.concat([error_df, current_df], ignore_index=True)
                continue
            
            if crop_mode == 'by_bars':

                checked_df = Refintor(path, current_df, output_folder).check_duplicate()
                df = pd.concat([df, checked_df], ignore_index=True)
            
            elif crop_mode == 'by_inst':
    
                df = pd.concat([df, current_df], ignore_index=True) 

            if idx % 100 == 0 and idx != 0:
                print(f'Saved {idx} files', 'Error: ', error)
        
        df.to_csv( genre + '.csv', index=False)
        error_df.to_csv( genre + '_error.csv', index=False)

        return df, error_df
    
if __name__ == '__main__':
        
        parser = argparse.ArgumentParser(description='Preprocess data for training.')
        
        parser.add_argument('--data_folder', type=str, help='Path to the folder containing midi files.')
        parser.add_argument('--num_bars', type=int, help='Number of bars to crop.')
        parser.add_argument('--output_folder', type=str, help='Path to the folder to save cropped midi files.')
        parser.add_argument('--genre', type=str, help='Genre of midi files.')
        parser.add_argument('--crop_mode', type=str, help='Crop mode: by_bars or by_inst')
    
        args = parser.parse_args()
    
        data_folder = args.data_folder
        num_bars = args.num_bars
        output_folder = args.output_folder
        genre = args.genre
        crop_mode = args.crop_mode
    
        Pipeline(data_folder, num_bars, output_folder, genre, crop_mode).start()
        