from music21 import converter, instrument
import pretty_midi

import re

def get_file_name(path):
    return path.split('/')[-1].split('.')[0]

def open_midi(midi_path):
    """
    Open the MIDI file and return the score.

    Returns:
        Score object.
    """
    score = converter.parse(midi_path)

    remove_drums = ['Percussion','percussion', 'Drumset', 'Drum Set', 'Drumkit', 'Drum Kit', 'Drums', 'Drum', 'drums', 'drum']
    percs_num = [i for i in range(112, 128)]
    percs_num.append(47)

    # Remove percussion staff.
    for part in score.parts:
        
        if part.partName in remove_drums:
            score.remove(part)

        if part.getInstruments().pop(0).instrumentName in remove_drums:
            score.remove(part)

        if part.getInstruments().pop(0).midiProgram == None:
            score.remove(part)

        if part.getInstruments().pop(0).midiProgram in percs_num:
            score.remove(part)

        for element in part.recurse():
            if isinstance(element, instrument.UnpitchedPercussion):
                score.remove(part)
        
    return score

def voices_to_parts(midi_path):

    score = converter.parse(midi_path)
    score = score.voicesToParts()
    return score

def extract_tempo(score):
    """
    Extract the tempo from the score.

    Returns:
        Tempo, in beats per minute.
    """
    for element in score.flat:
        if 'MetronomeMark' in element.classes:
            return element.number

    return None

def get_tempo(path):
    pm = pretty_midi.PrettyMIDI(path)
    tempo_estimated = pm.estimate_tempo()
    _, tempo = pm.get_tempo_changes()
    return tempo.tolist()[0]

def extract_key(score):
    """
    Extract the key signature from the score.

    Returns:
        Key signature.
    """
    for element in score.flat:
        if 'KeySignature' in element.classes:
            return str(element)

    return None

def to_snake_case(text):
    text = text.lower().replace(" ", "_")
    text_rmv = re.sub(r'[-=+,#/\?:&^.@*"※$%~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·<>]','', text)
    text_rmv = re.sub(r'\xa0', '_', text_rmv)
    return text_rmv


def chord_type_checker(chord_type):

    if chord_type == 'note':
        chord_type = ''

    if chord_type == 'perfect_octave':
        chord_type = ''

    if chord_type == 'perfect_fifth':
        chord_type = ''

    if chord_type == 'major_triad':
        chord_type = ''
    
    if chord_type == 'major_sixth':
        chord_type = '6'
    
    if chord_type == 'major_seventh':
        chord_type = '7'
    
    if chord_type == 'diminished_triad':
        chord_type = 'dim'
    
    if chord_type == 'diminished_seventh':
        chord_type = 'dim7'
    
    if chord_type == 'augmented_triad':
        chord_type = '+'
    
    if chord_type == 'minor_triad':
        chord_type = 'm'
    
    if chord_type == 'minor_sixth':
        chord_type = 'm6'
    
    if chord_type == 'minor_seventh':
        chord_type = 'm7'

    if chord_type == 'minor_seventh_flat_five':
        chord_type = 'm7b5'
    
    if chord_type == 'suspended_second':
        chord_type = 'sus2'

    if chord_type == 'suspended_fourth':
        chord_type = 'sus4'
    
    if chord_type == 'suspended_fourth_seventh':
        chord_type = '7sus4'
    
    if chord_type == 'minor_major_seventh':
        chord_type = 'mM7'
    
    if chord_type == 'added_second':
        chord_type = 'add2'
    
    if chord_type == 'minor_added_second':
        chord_type = 'madd2'

    else:
        chord_type = chord_type

    return chord_type
