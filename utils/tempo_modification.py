from collections import defaultdict
import mido, os
from utils import get_file_name, open_midi, extract_key, extract_tempo
from music21 import converter, midi, interval, pitch, tempo
import pretty_midi
from tqdm import tqdm

class Modify():
    def __init__(self, root_dir, data_dir, output_dir):
        self.root_dir = root_dir
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.path_list = self.get_path_list(self.data_dir)
        self.bpm_list = [35,45,50,60,65,70,75,80,85,90,95,100,105,110,120,125,130,135,140,145,150,155]

    def get_path_list(self, folder_path):
        path_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".mid"):
                    path_list.append(os.path.join(root, file))
        return path_list
    
    def find_near_bpm(self, bpm_value):
        bpm_list = self.bpm_list
        answer = 0
        minValue = min(bpm_list, key=lambda x:abs(x-bpm_value))
        answer = minValue
        return answer
    
    def is_valid_midi(self, path):
        try:
            score = converter.parse(path)
            m = mido.MidiFile(path)
            return True
        except:
            return False

    
    def tempo_modification_start(self):

        print('Tempo Modification Start')

        output_dir = self.output_dir
        path_list = self.path_list

        modified = 0
        not_valid_list = []

        for idx, path in tqdm(enumerate(path_list)):

            file_name = get_file_name(path) + '.mid'

            check = self.is_valid_midi(path)

            if not check:
                not_valid_list.append(file_name)
                continue

            score = open_midi(path)
            extracted_tempo = extract_tempo(score)
            target_bpm = self.find_near_bpm(extracted_tempo)

            for i in range(len(score.parts)):
                for x in score.parts[i].recurse().getElementsByClass(tempo.MetronomeMark):
                    x.number = target_bpm
            
            try:
                score.write('midi', os.path.join(output_dir, file_name))
            except:
                print(f'Cannot write file: {file_name}')
                not_valid_list.append(file_name)
                continue

            modified += 1

            if idx % 100 == 0 and idx != 0:
                print(f'{idx} files processed.', f'{modified} files are modified.', f'{len(not_valid_list)} files are not valid.')

        print(f'{modified} files are modified.', f'{len(not_valid_list)} files are not valid.')
        print(f'Not valid list = {not_valid_list}')