# MIDI-metadata-extractor

MIDI-metadata-extractor is a powerful utility that enables you to transform any multi-track MIDI file into the format of a ComMU dataset [1]. 
This tool allows you to break down a multi-track MIDI file into individual instrument tracks, extract detailed metadata for each track, and provides the flexibility to truncate and save tracks based on a specified number of measures (e.g., 8 measures).

## What is ComMU Dataset?

The ComMU dataset is a collection of short, single-instrumental MIDI sequences of 4-16 bars, each enriched with 12 metadata fields.

- [[Paper]](https://arxiv.org/pdf/2211.09385.pdf) [[Demo Page]](https://pozalabs.github.io/ComMU/) [[Dataset]](https://github.com/POZAlabs/ComMU-code/tree/master/dataset)

## Table of Contents

- [MIDI-metadata-extractor](#midi-metadata-extractor)
  - [What is ComMU Dataset?](#what-is-commu-dataset)
  - [Table of Contents](#table-of-contents)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Preprocess](#1-preprocess)
  - [2. Truncate and Metadata Extraction](#2-truncate-and-metadata-extraction)
- [Results](#results)
- [Reference](#reference)

# Features

- **Preprocess:** Check the validity of MIDI files, convert type 0 MIDI files to type 1 MIDI files.
- **Keys & Tempo Modification:** Transpose songs into C-major or A-minor keys. Modify tempo to the nearest tempo provided in the ComMU dataset.
- **Multi-track to Single Tracks:** Convert multi-track MIDI files into individual instrument tracks.
- **Customizable Cutting:** Cut and save tracks based on a specified number of measures (e.g., 8 measures).
- **Metadata Extraction:** Extract comprehensive metadata for each instrument track. In 'by_bars' truncate mode, it provides sequence position information and repeated sequence names.

# Installation

To get started with MIDI-metadata-extractor, simply clone this repository:

```bash
# Clone the repository
git clone https://github.com/your-username/midi-metadata-extractor.git

# Change directory
cd midi-metadata-extractor

# Install Python requirements
pip install -r requirements.txt
```

# Usage

## 1. Preprocess

Check the validity of MIDI files, convert type 0 MIDI files to type 1 MIDI files.

```bash
python preprocess.py --data_folder example
```

After successful preprocessing, project tree would be like this, 

```
    .
    └── example
        ├── raw
            ├── song01.mid
            ├── song02.mid
            ├── song03.mid
        ├── processed
            ├── song01.mid
            ├── song02.mid
            └── song03.mid
```

## 2. Truncate and Metadata Extraction

- **crop_mode:** Choose between 'by_inst' or 'by_bars' cropping modes.
- **num_bars (optional):** Number of bars to truncate the tracks. If not provided, it defaults to 8 bars.

```bash
python pipeline.py --data_folder example --crop_mode by_bars --num_bars 8 
```

After successful preprocessing, project tree would be like this, 

```
    .
    └── example
        ├── results.csv
        ├── error_files.csv
        ├── raw
            ├── song01.mid
            ├── song02.mid
            ├── song03.mid
        ├── processed
            ├── song01.mid
            ├── song02.mid
            └── song03.mid
        ├── by_bars
            ├── song01
                ├── 01_acoustic_bass_00.mid
                ├── 01_acoustic_bass_01.mid
                ├── 01_acoustic_bass_02.mid
                ├── 02_string_00.mid
                ├── 02_string_01.mid
                ├── 02_string_02.mid
                ├── ...
            ├── song02
                ├── 01_violin_00.mid
                ├── 01_violin_01.mid
                ├── 02_contrabass_00.mid
                ├── 02_contrabass_01.mid
                ├── ...
            ├── song03
                └── ...
```
# Results
- **MIDI Files:** MIDI files divided by instrument according to the crop mode you specify, or divided by instrument and then truncated to a specified number of measures.
- **results.csv:** Contains all 12 pieces of metadata provided by ComMU, including the program message number assigned to each instrument and the name of the instrument it corresponds to, as well as the midi file title of the original song and the location where each sequence was placed.
  - song_midi
  - file_name
  - program_change_value, program_change_msg
  - start_position, end_position, num_bars
  - tempo
  - key
  - min_pitch, max_pitch, mean_pitch, pitch_range
  - min_velocity, max_velocity
  - time_signature
  - sample_rhythm
  - chord_progressions
  - instrument_name
- **error_files.csv:** The name of the error file and the corresponding message. ('open' for unable to open and 'parts' for unable to divide because there is only one instrument in the midi).
aa
# Reference

[1] LEE, Hyun, et al. ComMU: Dataset for Combinatorial Music Generation. Advances in Neural Information Processing Systems, 2022, 35: 39103-39114.

[2] Facoetti, G. Chords Structure and note names, 2020, https://data.world/gianca1976/chords-structure-and-note-names