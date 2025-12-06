# Maestrai - Advanced Audio Transcription Service

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/yourusername/maestrai/workflows/tests/badge.svg)](https://github.com/yourusername/maestrai/actions)

Advanced audio and video transcription service powered by OpenAI Whisper with multi-model support, word-level timestamps, and comprehensive export options.

## Features

- **Multi-Model Support** - Choose from 5 Whisper models (tiny, base, small, medium, large)
- **Word-Level Timestamps** - Extract precise timing for every word
- **99+ Languages** - Support for all Whisper-compatible languages
- **Multiple Formats** - Process MP3, WAV, M4A, FLAC, OGG, WEBM audio files
- **Video Support** - Extract and transcribe audio from MP4, AVI, MOV, MKV videos
- **Export Options** - Generate SRT subtitles and formatted text transcripts
- **GPU Acceleration** - Automatic CUDA detection with CPU fallback
- **Batch Processing** - Transcribe multiple files efficiently
- **Error Handling** - Comprehensive validation and error messages

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/maestrai.git
cd maestrai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### Basic Usage

```python
from src.transcription_engine import TranscriptionEngine

# Initialize engine
engine = TranscriptionEngine(model_name="base")

# Transcribe audio file
result = engine.transcribe("audio.mp3")

# Access results
print(f"Language: {result.language}")
print(f"Text: {result.text}")

# Export to SRT and TXT
engine.export_srt(result, "output.srt")
engine.export_txt(result, "output.txt")
```

### Interactive Demo

```bash
# Run interactive demo
python scripts/demo.py

# Quick transcription
python scripts/demo.py audio.mp3 --model small
```

## Model Comparison

| Model  | Speed      | Accuracy | VRAM   | Best For                |
|--------|-----------|----------|--------|-------------------------|
| tiny   | Fastest   | Good     | ~1GB   | Quick drafts, testing   |
| base   | Fast      | Better   | ~1GB   | General use, demos      |
| small  | Medium    | Great    | ~2GB   | Balanced performance    |
| medium | Slow      | Excellent| ~5GB   | High accuracy needs     |
| large  | Slowest   | Best     | ~10GB  | Professional transcripts|

## Performance Metrics

- **tiny**: ~32x faster than real-time
- **base**: ~16x faster than real-time
- **small**: ~6x faster than real-time
- **medium**: ~2x faster than real-time
- **large**: ~1x real-time (varies by hardware)

*Benchmarks performed on NVIDIA RTX 3090*

## Documentation

All documentation is now organized in the `docs/` directory:

- [Setup Guide](SETUP.md) - Complete installation and configuration
- [Quick Reference](QUICK_REFERENCE.md) - Cheat sheet and common tasks
- [Testing Guide](TESTING.md) - How to test the application
- [API Documentation](API.md) - Detailed API reference
- [Contributing](CONTRIBUTING.md) - Contribution guidelines
- [Phase 1 Complete](PHASE1_COMPLETE.md) - Implementation details

## Examples

### Transcribe Video

```python
from src.transcription_engine import TranscriptionEngine

engine = TranscriptionEngine(model_name="base")
result = engine.transcribe("video.mp4")
engine.export_srt(result, "subtitles.srt")
```

### Batch Processing

```python
from src.transcription_engine import TranscriptionEngine

engine = TranscriptionEngine(model_name="small")
results = engine.transcribe_batch([
    "file1.mp3",
    "file2.wav",
    "file3.m4a"
])

for i, result in enumerate(results):
    print(f"File {i+1}: {result.word_count} words")
```

### Word-Level Timestamps

```python
from src.transcription_engine import TranscriptionEngine

engine = TranscriptionEngine(model_name="base")
result = engine.transcribe("audio.mp3", word_timestamps=True)

for segment in result.segments:
    for word in segment.words:
        print(f"{word.text}: {word.start:.2f}s - {word.end:.2f}s")
```

## Project Structure

```
maestrai/
├── src/
│   ├── transcription_engine.py  # Core transcription logic
│   ├── audio_processor.py       # Audio/video processing
│   └── utils/
│       └── config.py            # Configuration management
├── tests/
│   └── test_transcription.py    # Test suite
├── scripts/
│   └── demo.py                  # Interactive demo
├── examples/
│   ├── basic_usage.py           # Basic examples
│   ├── batch_processing.py      # Batch processing
│   └── video_transcription.py   # Video examples
└── docs/                        # Documentation
```

## Requirements

- Python 3.9+
- FFmpeg
- CUDA Toolkit (optional, for GPU acceleration)
- 4GB+ RAM (8GB+ recommended for larger models)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [OpenAI Whisper](https://github.com/openai/whisper)
- Audio processing by [FFmpeg](https://ffmpeg.org/)

## Support

- Report issues on [GitHub Issues](https://github.com/yourusername/maestrai/issues)
- See [SETUP.md](SETUP.md) for troubleshooting

## Roadmap

### Phase 1 (Current)
- ✅ Core transcription engine
- ✅ Multi-model support
- ✅ Word-level timestamps
- ✅ Export to SRT/TXT
- ✅ Batch processing

### Phase 2 (Planned)
- REST API server
- Web interface
- Real-time transcription
- Speaker diarization
- Custom vocabulary support

---

Made with ❤️ by the Maestrai Team
