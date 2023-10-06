import os
import glob
import pandas as pd

from modules.truncator import Truncator
from modules.refintor import Refintor

from tqdm import tqdm

import argparse

import warnings
warnings.filterwarnings("ignore")

class Pipeline:
    """
    Preprocess data for training.
    """

    def __init__(self, data_folder, crop_mode, num_bars=None):
        self.data_folder = data_folder
        self.processed_folder = os.path.join(self.data_folder, 'processed')
        self.num_bars = num_bars if num_bars is not None else 8
        self.file_path = glob.glob(f'{self.processed_folder}/*.mid')
        self.crop_mode = crop_mode
        self.output_folder = os.path.join(self.data_folder, f'{self.crop_mode}')
        
    def start(self):
        
        data_folder = self.data_folder
        num_bars = self.num_bars
        file_path = self.file_path
        output_folder = self.output_folder
        crop_mode = self.crop_mode

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        error = 0

        df = pd.DataFrame()
        
        error_df = pd.DataFrame(columns=['midi_path', 'error_msg'])

        for idx, path in tqdm(enumerate(file_path)):
            
            current_df, df_type_msg = Truncator(midi_path=path, output_folder=output_folder, num_bars=num_bars).truncate_midi(crop_mode=crop_mode)

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
        
        df.to_csv(os.path.join(data_folder, 'results.csv'), index=False)
        error_df.to_csv(os.path.join(data_folder,'error_files.csv'), index=False)

        return df, error_df
    
if __name__ == '__main__':
        
        parser = argparse.ArgumentParser(description='Preprocess data for training.')
        
        parser.add_argument('--data_folder', type=str, help='Path to the folder containing midi files.')
        parser.add_argument('--crop_mode', type=str, help='Crop mode: by_bars or by_inst')
        parser.add_argument('--num_bars', type=int, help='Number of bars to crop.', required=False)
    
        args = parser.parse_args()
    
        data_folder = args.data_folder
        crop_mode = args.crop_mode
        num_bars = args.num_bars
    
        Pipeline(data_folder, crop_mode, num_bars).start()
        