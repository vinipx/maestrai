# Maestrai - AI-Powered Music & Audio Transcription

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/vinipx/maestrai/workflows/Tests/badge.svg)](https://github.com/vinipx/maestrai/actions)

Transform audio recordings into sheet music with AI. Maestrai combines Spotify's Basic Pitch for music transcription and OpenAI Whisper for speech-to-text.

## Features

### Music Transcription (Phase 2)
- **Audio to MIDI** - Convert any instrument recording to MIDI
- **Sheet Music Generation** - Export to MusicXML and PDF
- **Audio Analysis** - Detect tempo, key signature, time signature
- **Multi-format Export** - MIDI, MusicXML, PDF output

### Speech Transcription (Phase 1)
- **Multi-Model Support** - 5 Whisper models (tiny to large)
- **Word-Level Timestamps** - Precise timing for every word
- **99+ Languages** - Automatic language detection
- **Export Options** - SRT subtitles and text transcripts

## Quick Start

### Automated Setup

```bash
# macOS/Linux
./setup.sh

# Windows
setup.bat
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

## Usage

### Music Transcription

```bash
# Transcribe music to sheet music
python scripts/music_demo.py song.mp3

# Interactive mode
python scripts/music_demo.py
```

**Output:**
- `song.mid` - MIDI file
- `song.musicxml` - Sheet music (MusicXML)
- `song.pdf` - Rendered sheet music (requires MuseScore)

### Programmatic Usage

```python
from src import MusicTranscriptionEngine, AudioAnalyzer, ScoreGenerator

# Initialize engines
engine = MusicTranscriptionEngine()
analyzer = AudioAnalyzer()
score_gen = ScoreGenerator()

# Analyze audio
analysis = analyzer.analyze("song.mp3")
print(f"Tempo: {analysis.tempo} BPM")
print(f"Key: {analysis.key}")

# Transcribe to notes
result = engine.transcribe("song.mp3")
print(f"Notes detected: {result.note_count}")

# Export to various formats
engine.export_midi(result, "output.mid")
score_gen.export_musicxml(result, "output.musicxml")
score_gen.export_pdf(result, "output.pdf")
```

### Speech Transcription

```bash
# Transcribe speech/audio to text
python scripts/demo.py audio.mp3 --model base
```

```python
from src import TranscriptionEngine

engine = TranscriptionEngine(model_name="base")
result = engine.transcribe("podcast.mp3")

print(f"Text: {result.text}")
engine.export_srt(result, "subtitles.srt")
```

## Output Examples

### Music Analysis
```
File: piano_song.mp3
Duration: 173.84 seconds
Tempo: 136.0 BPM
Key: A# major
Time Signature: 4/4
Notes detected: 1,090
```

### Generated Sheet Music Preview
```
Tempo: 136 BPM
Key: A# major
Time Signature: 4/4

Notes:
  B-3   | offset: 0.12 | dur: 1.00q
  F4    | offset: 0.50 | dur: 1.00q
  D5    | offset: 1.00 | dur: 1.00q
  ...
```

## Model Comparison

### Music Transcription
Powered by Spotify's Basic Pitch:
- Polyphonic (multiple notes at once)
- Instrument-agnostic
- Pitch bend detection
- Lightweight (<20 MB)

### Speech Transcription
| Model  | Speed    | Accuracy | VRAM   | Best For              |
|--------|----------|----------|--------|-----------------------|
| tiny   | Fastest  | Good     | ~1GB   | Quick drafts          |
| base   | Fast     | Better   | ~1GB   | General use           |
| small  | Medium   | Great    | ~2GB   | Balanced              |
| medium | Slow     | Excellent| ~5GB   | High accuracy         |
| large  | Slowest  | Best     | ~10GB  | Professional work     |

## Project Structure

```
maestrai/
├── src/
│   ├── music_transcription_engine.py  # Audio to MIDI (Basic Pitch)
│   ├── audio_analyzer.py              # Tempo/key detection (librosa)
│   ├── score_generator.py             # MusicXML/PDF export (music21)
│   ├── transcription_engine.py        # Speech to text (Whisper)
│   ├── audio_processor.py             # Audio file handling
│   └── utils/
│       └── config.py                  # Configuration
├── scripts/
│   ├── music_demo.py                  # Music transcription demo
│   └── demo.py                        # Speech transcription demo
├── tests/
│   └── test_transcription.py          # Test suite
├── examples/
│   └── *.py                           # Usage examples
└── docs/
    └── *.md                           # Documentation
```

## Requirements

- Python 3.9+
- FFmpeg
- TensorFlow (for Basic Pitch)
- MuseScore (optional, for PDF export)

### Key Dependencies

```
# Music Transcription
basic-pitch>=0.3.0    # Spotify's audio-to-MIDI
librosa>=0.10.0       # Audio analysis
music21>=9.1.0        # Sheet music generation
pretty_midi>=0.2.10   # MIDI manipulation

# Speech Transcription
openai-whisper        # Speech-to-text
torch>=2.0.0          # Deep learning
```

## Documentation

- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [Quick Reference](docs/QUICK_REFERENCE.md) - Common tasks
- [API Documentation](docs/API.md) - Detailed API reference
- [Phase 2 Plan](PHASE2_MUSIC_TRANSCRIPTION_PLAN.md) - Music transcription roadmap

## Testing

```bash
# Run tests
pytest tests/

# Test with your audio file
python scripts/music_demo.py ~/Music/song.mp3
```

## Roadmap

### Phase 1 - Speech Transcription
- Core Whisper integration
- Multi-model support
- Word-level timestamps
- SRT/TXT export

### Phase 2 - Music Transcription
- Basic Pitch integration
- Audio analysis (tempo, key)
- MusicXML export
- PDF sheet music generation

### Phase 3 (Planned)
- Real-time transcription
- Web interface
- REST API
- MIDI playback

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Spotify Basic Pitch](https://github.com/spotify/basic-pitch) - Audio-to-MIDI
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech-to-text
- [music21](https://web.mit.edu/music21/) - Music notation
- [librosa](https://librosa.org/) - Audio analysis
- [FFmpeg](https://ffmpeg.org/) - Audio processing

---

Made with love by the Maestrai Team
