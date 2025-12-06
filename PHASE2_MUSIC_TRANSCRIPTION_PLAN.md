# Phase 2: Music Transcription - Implementation Plan

## Project Pivot: Speech-to-Text → Music-to-Notation

Maestrai is pivoting from speech transcription to **music transcription** - converting audio recordings into musical notation (sheet music, MIDI).

---

## 🎯 New Vision

**Maestrai** - AI-Powered Music Transcription Service
Convert any audio recording (instrument, voice, song) into:
- MIDI files
- MusicXML (sheet music)
- PDF scores
- Audio analysis reports

---

## 🔬 Research Summary

### Best Libraries for Music Transcription (2025)

#### 1. **Basic Pitch by Spotify** ⭐ RECOMMENDED
- **GitHub**: [spotify/basic-pitch](https://github.com/spotify/basic-pitch)
- **Demo**: [basicpitch.spotify.com](https://basicpitch.spotify.com/)
- **Features**:
  - Lightweight (<20 MB memory, <17K parameters)
  - Instrument-agnostic (works with any instrument)
  - Polyphonic support (multiple notes simultaneously)
  - Pitch bend detection
  - High accuracy, competes with larger AMT systems
- **Output**: MIDI files with pitch bends
- **License**: Apache 2.0 (open source, commercial friendly)

#### 2. **Supporting Libraries**

**Music Analysis:**
- **librosa** - Audio and music analysis
- **aubio** - Pitch detection, beat tracking, onset detection
- **madmom** - Beat tracking, tempo estimation

**MIDI/Score Generation:**
- **music21** - MusicXML generation, music theory
- **pretty_midi** - MIDI manipulation
- **mido** - MIDI file I/O

**Visualization:**
- **matplotlib** - Plot waveforms, spectrograms
- **seaborn** - Enhanced visualizations

---

## 🏗️ New Architecture

### Core Components

```
maestrai/
├── src/
│   ├── music_transcription_engine.py  # Main transcription (Basic Pitch)
│   ├── audio_analyzer.py              # Audio analysis (librosa, aubio)
│   ├── midi_processor.py              # MIDI generation & manipulation
│   ├── score_generator.py             # MusicXML & PDF generation
│   ├── visualization.py               # Music visualization
│   └── utils/
│       ├── config.py                  # Configuration
│       └── music_theory.py            # Music theory helpers
├── tests/
│   └── test_music_transcription.py
├── scripts/
│   └── music_demo.py                  # Interactive demo
└── examples/
    ├── basic_music_transcription.py
    ├── instrument_specific.py
    └── batch_music_processing.py
```

---

## 📋 Implementation Tasks

### Phase 2.1: Core Music Transcription (Week 1)

#### Task 1: Setup Basic Pitch Integration
- [ ] Install Basic Pitch: `pip install basic-pitch[tf]`
- [ ] Create `MusicTranscriptionEngine` class
- [ ] Implement audio → MIDI conversion
- [ ] Test with various instruments

#### Task 2: Audio Analysis
- [ ] Install librosa, aubio
- [ ] Extract tempo/BPM
- [ ] Detect key signature
- [ ] Identify time signature
- [ ] Analyze pitch range

#### Task 3: MIDI Processing
- [ ] Install pretty_midi, mido
- [ ] MIDI file validation
- [ ] MIDI metadata extraction
- [ ] Note quantization options
- [ ] Velocity normalization

### Phase 2.2: Score Generation (Week 2)

#### Task 4: MusicXML Export
- [ ] Install music21
- [ ] Convert MIDI → MusicXML
- [ ] Add clef detection
- [ ] Add key/time signature
- [ ] Handle multi-voice parts

#### Task 5: PDF Score Generation
- [ ] Integrate MuseScore/LilyPond
- [ ] MusicXML → PDF conversion
- [ ] Custom formatting options
- [ ] Multi-page handling

### Phase 2.3: Visualization & UI (Week 3)

#### Task 6: Music Visualization
- [ ] Waveform display
- [ ] Spectrogram view
- [ ] Piano roll visualization
- [ ] Sheet music preview

#### Task 7: Interactive Demo
- [ ] CLI demo with music analysis
- [ ] Multiple output formats
- [ ] Preview before export
- [ ] Batch processing support

### Phase 2.4: Testing & Documentation (Week 4)

#### Task 8: Testing
- [ ] Unit tests for each component
- [ ] Integration tests
- [ ] Test with various instruments
- [ ] Performance benchmarks

#### Task 9: Documentation
- [ ] Update README
- [ ] API documentation
- [ ] User guide
- [ ] Example gallery

---

## 🎼 Feature Comparison

### Current (Phase 1 - Speech)
- ✅ Whisper AI (speech-to-text)
- ✅ Multiple languages
- ✅ SRT subtitles
- ✅ Word timestamps
- ✅ Batch processing

### New (Phase 2 - Music)
- 🎵 Basic Pitch (audio-to-MIDI)
- 🎵 Any instrument
- 🎵 Sheet music (MusicXML, PDF)
- 🎵 Note-level timing
- 🎵 Batch processing
- 🎵 Audio analysis (tempo, key, etc.)
- 🎵 Music visualization

---

## 📦 New Dependencies

### Required
```
basic-pitch[tf]>=0.3.0    # Spotify's audio-to-MIDI
librosa>=0.10.0           # Audio analysis
aubio>=0.4.9              # Pitch detection
pretty_midi>=0.2.10       # MIDI manipulation
mido>=1.3.0               # MIDI I/O
music21>=9.1.0            # MusicXML generation
```

### Optional
```
madmom>=0.16.1            # Advanced beat tracking
matplotlib>=3.8.0         # Visualization
seaborn>=0.13.0           # Enhanced plots
pillow>=10.0.0            # Image processing
```

---

## 🎯 Target Use Cases

### 1. Musicians
- Transcribe practice sessions
- Create sheet music from recordings
- Analyze performances

### 2. Music Students
- Learn songs by ear
- Study compositions
- Practice sight-reading

### 3. Composers
- Capture musical ideas
- Convert sketches to notation
- Share compositions

### 4. Music Teachers
- Create teaching materials
- Analyze student performances
- Generate exercises

---

## 🚀 Quick Start (After Implementation)

```python
from src.music_transcription_engine import MusicTranscriptionEngine

# Initialize
engine = MusicTranscriptionEngine()

# Transcribe audio to MIDI
result = engine.transcribe("piano_recording.mp3")

# Get analysis
print(f"Tempo: {result.tempo} BPM")
print(f"Key: {result.key}")
print(f"Notes detected: {len(result.notes)}")

# Export formats
engine.export_midi(result, "output.mid")
engine.export_musicxml(result, "output.musicxml")
engine.export_pdf(result, "sheet_music.pdf")
```

---

## 🎼 Example Workflow

### Input: Audio Recording
```
piano_performance.mp3 (2:30, 5MB)
```

### Processing Pipeline
1. **Load Audio** → Basic Pitch preprocessing
2. **Analyze** → Extract tempo, key, time signature
3. **Transcribe** → Generate MIDI with note timings
4. **Process** → Quantize notes, clean up artifacts
5. **Generate** → Create MusicXML
6. **Render** → Export PDF sheet music

### Output
```
✅ MIDI: piano_performance.mid
✅ MusicXML: piano_performance.musicxml
✅ PDF: piano_performance.pdf
✅ Analysis Report:
   - Tempo: 120 BPM
   - Key: C Major
   - Time: 4/4
   - Duration: 2:30
   - Notes: 1,247
```

---

## 🎯 Success Metrics

### Technical
- MIDI generation accuracy >85%
- Processing time <5x audio duration
- Support for 10+ instruments
- Clean sheet music output

### User Experience
- One-command transcription
- Multiple output formats
- Interactive demo
- Clear error messages

---

## 📚 Resources

### Documentation
- [Basic Pitch GitHub](https://github.com/spotify/basic-pitch)
- [Basic Pitch Demo](https://basicpitch.spotify.com/)
- [librosa Documentation](https://librosa.org/)
- [music21 Documentation](https://web.mit.edu/music21/)

### Tutorials
- [Convert MP3 to MIDI Using Spotify's BasicPitch](https://www.albinsblog.com/2025/01/convert-mp3-to-midi-using-spotifys-basic-pitch-and-tenserflow.html)

### Research Papers
- Basic Pitch: A Lightweight Neural Network for Automatic Music Transcription (Spotify)

---

## 🗓️ Timeline

### Week 1: Core Transcription
- Days 1-2: Setup Basic Pitch, create engine
- Days 3-4: Audio analysis integration
- Days 5-7: MIDI processing

### Week 2: Score Generation
- Days 8-10: MusicXML export
- Days 11-14: PDF generation

### Week 3: Polish & Features
- Days 15-17: Visualization
- Days 18-21: Interactive demo

### Week 4: Testing & Release
- Days 22-24: Testing
- Days 25-27: Documentation
- Day 28: Release Phase 2

---

## 🔄 Migration Strategy

### Keep or Remove Speech Transcription?

**Option A: Complete Replacement**
- Remove Whisper/speech code
- Pure music transcription tool
- Cleaner, focused codebase

**Option B: Dual Mode** (Recommended)
- Keep both capabilities
- Unified interface
- Auto-detect audio type
- More versatile tool

### Recommended: Keep Both
```python
# Auto-detect mode
engine = MaestraiEngine()
result = engine.transcribe("audio.mp3")  # Detects speech vs music

# Or specify explicitly
speech_result = engine.transcribe("podcast.mp3", mode="speech")
music_result = engine.transcribe("song.mp3", mode="music")
```

---

## 🎬 Next Steps

1. **Review & Approve Plan**
2. **Setup Development Branch**: `git checkout -b phase2-music-transcription`
3. **Install Dependencies**
4. **Start Implementation**: Begin with MusicTranscriptionEngine
5. **Test with Sample Audio**: Use your o-emmanuel.mp3 file
6. **Iterate & Improve**

---

**Ready to transform Maestrai into the ultimate music transcription tool!** 🎵✨
