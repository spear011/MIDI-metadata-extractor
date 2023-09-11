from music21 import converter, instrument, meter, tempo, pitch, key, interval, note, chord
import os
import pandas as pd
import glob
import numpy as np

import time

from utils.utils import open_midi, get_file_name, extract_tempo, extract_key, to_snake_case, get_tempo
from tqdm import tqdm

class Truncator:
    """
    Read MIDI files and extract information.
    """

    def __init__(self, midi_path, num_bars, output_folder, p_df):
        self.midi_path = midi_path
        self.num_bars  = num_bars
        self.output_folder = output_folder
        self.p_df = p_df
        self.bpm_list = [35,45,50,60,65,70,75,80,85,90,95,100,105,110,120,125,130,135,140,145,150,155]

    def find_near_bpm(self, bpm_value):
        bpm_list = self.bpm_list
        answer = 0
        minValue = min(bpm_list, key=lambda x:abs(x-bpm_value))
        answer = minValue
        return answer
    
    def transpose_score(self, score, tonic, mode):

        c_maj = key.Key('C', 'major')
        a_min = key.Key('A', 'minor')
            
        if mode == 'major' and tonic != 'C':

            score.transpose(interval.Interval(pitch.Pitch(tonic), pitch.Pitch('C')), inPlace=True)
            score.insert(0, c_maj)

            for n in score.recurse().notes:
                if n.isNote:
                    nStep = n.pitch.step
                    rightAccidental = c_maj.accidentalByStep(nStep)
                    n.pitch.accidental = rightAccidental

            song_key = 'c_major'
            
        
        elif mode == 'minor' and tonic != 'A':

            score.transpose(interval.Interval(pitch.Pitch(tonic), pitch.Pitch('A')), inPlace=True)
            score.insert(0, a_min)

            for n in score.recurse().notes:
                if n.isNote:
                    nStep = n.pitch.step
                    rightAccidental = a_min.accidentalByStep(nStep)
                    n.pitch.accidental = rightAccidental

            song_key = 'a_minor'
        
        return score, song_key
    
    def find_pitch_range(self, df):

        very_high = [i for i in range(95, 127)]
        high = [i for i in range(86, 95)]
        mid_high = [i for i in range(75, 86)]
        mid = [i for i in range(65, 75)]
        mid_low = [i for i in range(48, 65)]
        low = [i for i in range(36, 48)]
        very_low = [i for i in range(0, 36)]
        
        df['pitch_range'] = None

        for idx, v in enumerate(df['mean_pitch']):
            current_value = round(v, 0)

            if current_value in very_high:
                df.loc[idx, 'pitch_range'] = 'very_high'
            elif current_value in high:
                df.loc[idx, 'pitch_range'] = 'high'
            elif current_value in mid_high:
                df.loc[idx, 'pitch_range'] = 'mid_high'
            elif current_value in mid:
                df.loc[idx, 'pitch_range'] = 'mid'
            elif current_value in mid_low:
                df.loc[idx, 'pitch_range'] = 'mid_low'
            elif current_value in low:
                df.loc[idx, 'pitch_range'] = 'low'
            elif current_value in very_low:
                df.loc[idx, 'pitch_range'] = 'very_low'
        return df


    def truncate_midi_by_bars(self, crop_mode='by_bars'):

        error_df = pd.DataFrame(columns=['midi_path', 'error_msg'])

        c_maj = key.Key('C', 'major')
        a_min = key.Key('A', 'minor')

        try:
            score = open_midi(self.midi_path)

            if len(score.parts) < 2:
                print(f'Parts Error: {self.midi_path}')
                error_df = error_df.append({'midi_path': self.midi_path, 'error_msg': 'Parts'}, ignore_index=True)
                df_type_msg = 'error'
                return error_df, df_type_msg
            
        except:
            print(f'Error: {self.midi_path}')
            error_df = error_df.append({'midi_path': self.midi_path, 'error_msg': 'open'}, ignore_index=True)
            df_type_msg = 'error'
            return error_df, df_type_msg

        num_bars = self.num_bars
        output_folder = self.output_folder
        file_name = get_file_name(self.midi_path)
        file_name = to_snake_case(file_name)
        p_df = self.p_df

        # extract tempo and find near bpm
        extracted_tempo = extract_tempo(score)

        if not extracted_tempo:
            extracted_tempo = get_tempo(self.midi_path)

        target_bpm = self.find_near_bpm(extracted_tempo)

        # extract key
        ex_key = extract_key(score)
        if not ex_key:
            try:
                ex_key = score.analyze('key')
                tonic, mode = (ex_key.tonic.name, ex_key.mode)
            except:
                print(f'Key Error: {self.midi_path}')
                error_df = error_df.append({'midi_path': self.midi_path, 'error_msg': 'Key'}, ignore_index=True)
                df_type_msg = 'error'
                song_key = np.nan
                return error_df, df_type_msg
        else:
            tonic, mode = (ex_key.split(' ')[0], ex_key.split(' ')[1])

        # song key transpose
        if tonic == 'C' and mode == 'major':
            song_key = 'c_major'
        
        elif tonic == 'A' and mode == 'minor':
            song_key = 'a_minor'

        else:
            score, song_key = self.transpose_score(score, tonic, mode)


        beats_per_bar = score.recurse().getElementsByClass(meter.TimeSignature)[0].numerator
        time_signature = score.recurse().getElementsByClass(meter.TimeSignature)[0].ratioString
        num_measures = int(score.duration.quarterLength / beats_per_bar)
        num_crops = int(num_measures / num_bars)

        if num_crops * num_bars < num_measures:
            num_crops += 1
        
        current_midi_folder =  f'{output_folder}/{file_name}'

        if not os.path.exists(current_midi_folder):
            os.makedirs(current_midi_folder)

        df = pd.DataFrame(columns=['song_midi', 'file_name', 'program_change_value' ,'program_change_msg', 
                                   'start_position', 'end_position', 'num_bars', 'tempo', 'key', 'min_pitch', 'max_pitch', 'mean_pitch',
                                   'min_velocity', 'max_velocity', 'time_signature'])

        cropped_scores = []
        instrument_names = []
        output_file_names = []
        start_positions = []
        end_positions = []
        num_bars_list = []
        tempos = []
        keys = []
        program_change_values = []
        program_change_msges = []
        min_pitches = []
        max_pitches = []
        mean_pitches = []
        min_velocities = []
        max_velocities = []
        time_signatures = []

        saved_count = 0
        no_notes_count = 0
        no_program_change_count = 0

        for idx, part in enumerate(score.parts):

            for x in part.recurse().getElementsByClass(tempo.MetronomeMark):
                x.number = target_bpm

            program_change_value = part.getInstruments().pop(0).midiProgram

            if not program_change_value:
                no_program_change_count += 1
                continue

            else:

                program_change_msg = p_df[p_df['Decimal_value'] == program_change_value]['Program_change'].item()
                program_change_msg = to_snake_case(program_change_msg)

                instrument_name = part.getInstruments().pop(0).instrumentName
                instrument_name = to_snake_case(instrument_name)

                if instrument_name == 'sampler':
                    instrument_name = str(idx).zfill(2) + '_' + program_change_msg
                else:
                    instrument_name = str(idx).zfill(2) + '_' + instrument_name

                # if instrument_name has '/' or '\', replace it with '_'
                instrument_name = to_snake_case(instrument_name)

                if crop_mode == 'by_bars':

                    start_position = 1
                    end_position = self.num_bars

                    for i in range(num_crops):

                        cropped_part = part.measures(int(start_position), int(end_position))

                        midi_numbers = list()
                        velocities = list()

                        for obj in cropped_part.recurse():
                            if isinstance(obj, note.Note):
                                if obj.pitch.midi < 19:
                                    cropped_part.remove(obj)
                                else:   
                                    midi_numbers.append(obj.pitch.midi)
                                    velocities.append(obj.volume.velocity)
                            elif isinstance(obj, chord.Chord):
                                for p in obj.pitches:
                                    midi_numbers.append(p.midi)
                                    velocities.append(obj.volume.velocity)

                        if len(midi_numbers) == 0:
                            no_notes_count += 1

                        else:
                            program_change_msges.append(program_change_msg)
                            program_change_values.append(program_change_value)
                            instrument_names.append(instrument_name)
                            start_positions.append(start_position)
                            end_positions.append(end_position)
                            num_bars_list.append(self.num_bars)
                            tempos.append(target_bpm)
                            time_signatures.append(time_signature)
                            keys.append(song_key)
                            min_pitches.append(min(midi_numbers))
                            max_pitches.append(max(midi_numbers))
                            mean_pitches.append((sum(midi_numbers) / len(midi_numbers)))
                            min_velocities.append(min(velocities))
                            max_velocities.append(max(velocities))
                            
                            if song_key == 'c_major':
                                cropped_part.insert(0, c_maj)
                            elif song_key == 'a_minor':
                                cropped_part.insert(0, a_min)

                            cropped_part.write('midi', f'{current_midi_folder}/{instrument_name}_{str(i).zfill(2)}.mid')
                            output_file_names.append(f'{instrument_name}_{str(i).zfill(2)}.mid')
                            saved_count += 1
                        
                        start_position += self.num_bars
                        end_position += self.num_bars
                    
                elif crop_mode == 'by_inst':

                    start_position = 0
                    end_position = num_measures

                    midi_numbers = list()
                    velocities = list()

                    for obj in part.recurse():
                        if isinstance(obj, note.Note):
                            if obj.pitch.midi < 19:
                                part.remove(obj)
                            else:   
                                midi_numbers.append(obj.pitch.midi)
                                velocities.append(obj.volume.velocity)
                        elif isinstance(obj, chord.Chord):
                            for p in obj.pitches:
                                midi_numbers.append(p.midi)
                                velocities.append(obj.volume.velocity)
                    
                    if len(midi_numbers) == 0:
                        no_notes_count += 1
                    
                    else:
                        program_change_msges.append(program_change_msg)
                        program_change_values.append(program_change_value)
                        instrument_names.append(instrument_name)
                        start_positions.append(start_position)
                        end_positions.append(end_position)
                        num_bars_list.append(num_measures)
                        tempos.append(target_bpm)
                        time_signatures.append(time_signature)
                        keys.append(song_key)
                        min_pitches.append(min(midi_numbers))
                        max_pitches.append(max(midi_numbers))
                        mean_pitches.append((sum(midi_numbers) / len(midi_numbers)))
                        min_velocities.append(min(velocities))
                        max_velocities.append(max(velocities))

                        if song_key == 'c_major':
                            part.insert(0, c_maj)
                        elif song_key == 'a_minor':
                            part.insert(0, a_min)

                        part.write('midi', f'{current_midi_folder}/{instrument_name}.mid')
                        output_file_names.append(f'{instrument_name}.mid')
                        saved_count += 1

   

        df['song_midi'] = [file_name] * len(output_file_names)
        df['file_name'] = output_file_names
        df['instrument_name'] = instrument_names
        df['start_position'] = start_positions
        df['end_position'] = end_positions
        df['num_bars'] = num_bars_list
        df['tempo'] = tempos
        df['key'] = keys
        df['program_change_value'] = program_change_values
        df['program_change_msg'] = program_change_msges
        df['time_signature'] = time_signatures

        df['min_pitch'] = min_pitches
        df['max_pitch'] = max_pitches
        df['mean_pitch'] = mean_pitches
        df['min_velocity'] = min_velocities
        df['max_velocity'] = max_velocities

        df.sort_values(by=['instrument_name', 'start_position'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df = self.find_pitch_range(df)
        df_type_msg = 'success'
        return df, df_type_msg