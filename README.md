# Maestrai — AI-Powered Music Transcription & Score Generation

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Turn audio recordings into playable MIDI and fully rendered sheet music (MusicXML / PDF) using modern ML tools.
Maestrai focuses on high-quality music transcription (audio → notes → score) powered by Spotify's Basic Pitch and a compact audio analysis pipeline.

Why this project exists
- Convert performances or recordings into editable sheet music quickly.
- Produce MIDI and MusicXML for DAWs and notation software (MuseScore, Finale, Sibelius).
- Provide a programmatic API plus simple command-line utilities for batch processing.

Highlights
- Polyphonic audio-to-MIDI using Basic Pitch
- MusicXML export and PDF rendering (via MuseScore)
- Advanced audio analysis powered by madmom (neural network-based):
  - DBN beat/downbeat tracking with RNN activation
  - CNN-based key detection with confidence scores
  - Deep chroma chord recognition
  - Multi-tempo estimation
- Multi-format outputs: MIDI, MusicXML, PDF
- Lightweight Python API for integration into tools and pipelines

Quick Start

Automated setup (macOS/Linux):

```bash
./setup.sh
```

Manual setup (venv + pip):

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

Usage — CLI (recommended)

```bash
# Music transcription - convert an audio file to score and MIDI
./run.sh music /path/to/song.mp3

# Music transcription - convert an audio file to score and MIDI (detailed)
./run.sh music --input /path/to/song.mp3 --output output/ \
  --format musicxml --midi --pdf \
  --model basic-pitch \
  --sample-rate 44100 \
  --musescore-path "/Applications/MuseScore 3.app/Contents/MacOS/mscore"

# Short form (if supported by your run.sh wrapper):
# ./run.sh music -i /path/to/song.mp3 -o output/ --musicxml --midi

# Show help
./run.sh --help
```

Default outputs are written to the `output/` directory.

Usage — Python API

```python
from src import MusicTranscriptionEngine, AudioAnalyzer, ScoreGenerator

engine = MusicTranscriptionEngine()
analysis = AudioAnalyzer().analyze("song.mp3")
print(f"Tempo: {analysis.tempo} BPM, Key: {analysis.key}")

result = engine.transcribe("song.mp3")  # result contains note events, tempo, meta
print(f"Notes detected: {result.note_count}")

# Full example showing the shape of the returned `result` and how to access note events
from src.music_transcription_engine import MusicTranscriptionEngine
from src.audio_analyzer import AudioAnalyzer
from src.score_generator import ScoreGenerator

engine = MusicTranscriptionEngine()  # pass model name via config or constructor if supported by your version
analysis = AudioAnalyzer().analyze("song.mp3")
print(f"Tempo: {analysis.tempo} BPM, Key: {analysis.key}")

result = engine.transcribe("song.mp3")

# Typical `result` attributes (example structure):
# result.duration -> float (seconds)
# result.tempo -> float (BPM)
# result.key -> str (e.g. 'C major')
# result.time_signature -> str (e.g. '4/4')
# result.note_count -> int
# result.note_events -> list of dicts, each with keys:
#    { 'onset': float, 'offset': float, 'duration': float,
#      'pitch': 'C4', 'midi': 60, 'velocity': int, 'confidence': float }

print(f"Duration: {result.duration:.2f}s, notes: {result.note_count}")
for n in result.note_events[:10]:
    print(f"{n['onset']:.3f}s -> {n['duration']:.3f}s | {n['pitch']} (MIDI {n['midi']}) conf={n.get('confidence', 0):.2f}")

# Export outputs
engine.export_midi(result, "output/song.mid")
ScoreGenerator().export_musicxml(result, "output/song.musicxml")
# PDF export requires MuseScore command-line path; configuration may vary by platform
ScoreGenerator().export_pdf(result, "output/song.pdf")
```

Examples and scripts
- `scripts/music_demo.py` — one-off music transcription demo
- `examples/` — small usage examples and batch scripts

Outputs
- output/song.mid — MIDI file (playable)
- output/song.musicxml — MusicXML (notation interchange)
- output/song.pdf — Rendered sheet music (MuseScore required)

Example analysis output
```
File: piano_song.mp3
Duration: 173.84 seconds
Tempo: 136.0 BPM
  Alternative tempos: 136.0 (0.45), 68.0 (0.32), 272.0 (0.12)
Key: A# major
  Key confidence: 0.85
Time Signature: 4/4
Beats detected: 394
Downbeats detected: 99
Chords detected: 42

Chord Progression (first 5):
    0.00s -   3.20s: A#:maj
    3.20s -   6.40s: D#:maj
    6.40s -   9.60s: Gm
    9.60s -  12.80s: F:maj
   12.80s -  16.00s: A#:maj

Notes detected: 1,090
```

Project structure

```
maestrai/
├── src/
│   ├── music_transcription_engine.py  # Audio to MIDI (Basic Pitch)
│   ├── audio_analyzer.py              # Advanced MIR analysis (madmom)
│   ├── score_generator.py             # MusicXML/PDF export (music21)
│   ├── audio_processor.py             # Audio file handling
│   └── utils/
│       └── config.py
├── scripts/
│   └── music_demo.py
├── examples/
├── tests/
└── docs/
```

Requirements
- Python 3.9+
- FFmpeg (audio handling)
- TensorFlow (Basic Pitch backend)
- MuseScore (optional — PDF rendering)

Key dependencies
```
basic-pitch>=0.3.0    # Spotify's audio-to-MIDI
madmom>=0.16.1        # Neural network-based MIR (beat/chord/key detection)
music21>=9.1.0        # MusicXML/PDF generation
pretty_midi>=0.2.10   # MIDI manipulation
tensorflow>=2.0.0     # Model runtime
```

Note: For Python 3.10+, install madmom from git for compatibility:
```bash
pip install cython
pip install git+https://github.com/CPJKU/madmom.git
```

Testing

```bash
# Run unit tests
pytest tests/

# Try a quick transcription
python scripts/music_demo.py ~/Music/song.mp3
```

Documentation
- docs/SETUP.md — installation and platform notes
- docs/API.md — API reference
- docs/QUICK_REFERENCE.md — common tasks and examples

Roadmap
- Phase 2 (current): Full music transcription pipeline — polyphonic audio to MusicXML/PDF
- Improve accuracy for dense polyphony and percussive instruments
- Optional web UI and REST API for remote processing

Notes about speech transcription
- The project previously included speech-to-text components; the repository has shifted focus to music transcription and score generation. Any legacy speech scripts are deprecated and may be removed in future releases.

Contributing
See `docs/CONTRIBUTING.md` for contribution guidelines, development setup, and testing instructions.

License
MIT — see `LICENSE` for details.
