# MIDI-metadata-extractor

MIDI-metadata-extractor is a powerful utility that enables you to transform any multi-track MIDI file into the format of a ComMU dataset. 
This tool allows you to break down a multi-track MIDI file into individual instrument tracks, extract detailed metadata for each track, and provides the flexibility to truncate and save tracks based on a specified number of measures (e.g., 8 measures).

## What is ComMU Dataset?

The ComMU dataset is a collection of short, single-instrumental MIDI sequences of 4-16 bars, each enriched with 12 metadata fields.

- [Paper](https://arxiv.org/pdf/2211.09385.pdf) [Demo Page](https://pozalabs.github.io/ComMU/) [Dataset](https://github.com/POZAlabs/ComMU-code/tree/master/dataset)

## Table of Contents

- [MIDI-metadata-extractor](#midi-metadata-extractor)
  - [What is ComMU Dataset?](#what-is-commu-dataset)
  - [Table of Contents](#table-of-contents)
- [Features](#features)
- [Installation](#installation)

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
```
