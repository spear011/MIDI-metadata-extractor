from collections import defaultdict
import mido, os
from utils import get_file_name, open_midi, extract_key
from music21 import converter, midi, interval, pitch, key
import pretty_midi
from tqdm import tqdm


class Transpose():
    def __init__(self, root_dir, data_dir, output_dir):
        self.root_dir = root_dir
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.path_list = self.get_path_list(self.data_dir)

    def get_path_list(self, folder_path):
        path_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".mid"):
                    path_list.append(os.path.join(root, file))
        return path_list
    
    def check_analysis_valid(self, score):
        try:
            key = score.analyze('key')
            return True
        except:
            return False

    def transpose_start(self):

        transpose_list = self.path_list
        output_dir = self.output_dir
        transposed = 0
        skip = 0
        failed = 0

        failed_analysis = []
        not_valid_list = []

        print('Found {} midi files. Start transpose'.format(len(transpose_list)))
        for idx, path in tqdm(enumerate(transpose_list)):

            file_name = get_file_name(path) + '.mid'

            try:
                score = open_midi(path)
            except:
                not_valid_list.append(file_name)
                print('Not valid midi file: {}'.format(file_name))
                continue
            

            if len(score.parts) > 1:

                check = self.check_analysis_valid(score)

                if not check:
                    failed_analysis.append(file_name)
                    failed += 1
                    continue
                
                analyzed_key = score.analyze('key')
                tonic, mode = (analyzed_key.tonic, analyzed_key.mode)

                if mode == 'major':

                    if tonic != 'C':
                        score.transpose(interval.Interval(pitch.Pitch(tonic), pitch.Pitch('C')), inPlace=True)

                        c_maj = key.Key('C', 'major')
                        elements = score.flat.getElementsByClass('KeySignature').elements
                        
                        if elements is None:
                            score.insert(0, key.Key('C', 'major'))
                        
                        else:
                            for i in range(len(elements)):
                                score.replace(elements[i], c_maj, recurse=True)

                
                elif mode == 'minor':

                    if tonic != 'A':
                        score.transpose(interval.Interval(pitch.Pitch(tonic), pitch.Pitch('A')), inPlace=True)
                    
                        a_min = key.Key('A', 'minor')
                        elements = score.flat.getElementsByClass('KeySignature').elements

                        if elements is None:
                            score.insert(0, key.Key('A', 'minor'))
                        
                        else:
                            for i in range(len(elements)):
                                score.replace(elements[i], a_min, recurse=True)


            else:
                print(f'{file_name} has only one track. Skip')
                skip += 1

            if idx % 100 == 0 and idx != 0:
                print(f'{idx} files processed.', f'{transposed} files are transposed,', f'{skip} files are skipped,', f'{failed} files are failed.')

        print(f'{transposed} files are transposed,', f'{skip} files are skipped,', f'{failed} files are failed.')
        print(f'Failed analysis: {failed_analysis}')
        print(f'Not valid midi files: {not_valid_list}')
