from collections import defaultdict
import mido, os
from utils.utils import to_snake_case, get_file_name, open_midi, extract_key
import argparse
from tqdm import tqdm


# ignore warnings
import warnings
warnings.filterwarnings("ignore")

"""
Checking validity of midi files

Convert type 0 midi files to type 1 midi files

"""

class Preprocess():
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.path_list = self.get_path_list(self.root_dir)

    def get_path_list(self, folder_path):
        path_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".mid"):
                    path_list.append(os.path.join(root, file))
        return path_list
    
    def is_valid_midi(self, path):
        try:
            m = mido.MidiFile(path)
            return True
        except:
            return False

    def read_midi(self, path):
        '''Read a midi file and return a list of message dicts'''
        m = mido.MidiFile(path)
        return m
    
    def get_midi_type(self, midi):
        '''Return the type of a midi file'''
        return midi.type

    def subdivide_midi_tracks(self, midi):
        '''Convert a type 0 midi file to a type 1 midi file'''

        m = midi # load the original type-0 midi file
        messages = [] # a list of message dicts, one per track
        for track in m.tracks:
            time = 0 # store time in aggregate units
            track_messages = []
            for idx, i in enumerate(track):
                i = i.dict()
                if i.get('time', None): time += i.get('time')
                i['time'] = time
                track_messages.append(i)
            messages.append(track_messages)
        # build a dictionary of the events for each channel
        d = defaultdict(list) # d[channel_id] = [notes]
        for track_idx, track in enumerate(messages):
            for i in track:
                channel = i.get('channel', -1)
                d[channel].append(i)
        # covert time units in each program back to relative units
        for channel in d:
            total_time = 0
            for i in sorted(d[channel], key=lambda i: i['time']):
                t = i['time']       
                i['time'] = t - total_time
                total_time = t
        # create a midi file and add a track for each channel
        m2 = mido.MidiFile()
        for channel in sorted(d.keys()):
            track = mido.midifiles.tracks.MidiTrack()
            # add the notes to this track
            for note in d[channel]:
                note_type = note['type']
                del note['type']
                # if this is a meta message, append a meta message else a messaege
                try:
                    track.append(mido.MetaMessage(note_type, **note))
                except:
                    track.append(mido.Message(note_type, **note))
            m2.tracks.append(track)
        # ensure the time quantization is the same in the new midi file
        m2.ticks_per_beat = m.ticks_per_beat
        return m2

    def start(self):
        root_dir = self.root_dir
        path_list = self.path_list
        count = 0
        skip = 0
        not_valid = 0

        processed_folder = os.path.join(root_dir, 'processed')
        if not os.path.exists(processed_folder):
            os.mkdir(processed_folder)

        print(f'found {len(path_list)} midi files)')

        for idx, path in tqdm(enumerate(path_list)):

            check = self.is_valid_midi(path)

            if not check:
                not_valid += 1
                continue

            midi = self.read_midi(path)
            midi_type = self.get_midi_type(midi)
            file_name = to_snake_case(get_file_name(path)) + '.mid'
            if midi_type == 0:
                midi = self.subdivide_midi_tracks(midi)
                midi.save(os.path.join(processed_folder, file_name))
                count += 1
            else:
                midi.save(os.path.join(processed_folder, file_name))
                skip += 1
            
            if idx % 100 == 0:
                print(f'{idx} files are processed,', f'{count} files are converted to type 1 midi file,', f'{skip} files are skipped,', f'{not_valid} files are not valid')
            
        print(f'{count} files are converted to type 1 midi file', f'{skip} files are skipped', f'{not_valid} files are not valid')

        # transpose_folder = os.path.join(root_dir, 'transposed')
        # if not os.path.exists(transpose_folder):
        #     os.mkdir(transpose_folder)
        
        # key_transpose = Transpose(root_dir, processed_folder, transpose_folder)
        # key_transpose.transpose_start()

        # tempo_modified_folder = os.path.join(folder_path, 'tempo_modified')

        # if not os.path.exists(tempo_modified_folder):
        #     os.mkdir(tempo_modified_folder)

        # modifying_tempo = Modify(root_dir, transpose_folder, tempo_modified_folder)
        # modifying_tempo.tempo_modification_start()




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='preprocess midi files')

    parser.add_argument('--data_folder', type=str, help='folder path of midi files')

    args = parser.parse_args()

    data_folder = args.data_folder

    p = Preprocess(data_folder)
    p.start()


