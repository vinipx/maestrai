# Maestrai - Advanced Audio Transcription Service

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/yourusername/maestrai/workflows/tests/badge.svg)](https://github.com/yourusername/maestrai/actions)

Advanced audio and video transcription service powered by OpenAI Whisper with multi-model support, word-level timestamps, and comprehensive export options.

## ✨ Features

- **Multi-Model Support** - Choose from 5 Whisper models (tiny, base, small, medium, large)
- **Word-Level Timestamps** - Extract precise timing for every word
- **99+ Languages** - Support for all Whisper-compatible languages
- **Multiple Formats** - Process MP3, WAV, M4A, FLAC, OGG, WEBM audio files
- **Video Support** - Extract and transcribe audio from MP4, AVI, MOV, MKV videos
- **Export Options** - Generate SRT subtitles and formatted text transcripts
- **GPU Acceleration** - Automatic CUDA detection with CPU fallback
- **Batch Processing** - Transcribe multiple files efficiently

## 🚀 Quick Start

### Automated Setup (Recommended)

#### macOS/Linux:
```bash
./setup.sh
```

#### Windows:
```bash
setup.bat
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg
```

## 📖 Usage

### Interactive Demo

```bash
python scripts/demo.py
```

### Quick Transcription

```bash
# Basic usage
python scripts/demo.py audio.mp3

# Use specific model
python scripts/demo.py audio.mp3 --model small

# Enable verbose logging
python scripts/demo.py audio.mp3 --verbose
```

### Programmatic Usage

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

## 📊 Model Comparison

| Model  | Speed      | Accuracy | VRAM   | Best For                |
|--------|-----------|----------|--------|-------------------------|
| tiny   | Fastest   | Good     | ~1GB   | Quick drafts, testing   |
| base   | Fast      | Better   | ~1GB   | General use, demos      |
| small  | Medium    | Great    | ~2GB   | Balanced performance    |
| medium | Slow      | Excellent| ~5GB   | High accuracy needs     |
| large  | Slowest   | Best     | ~10GB  | Professional transcripts|

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Complete installation and configuration
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Cheat sheet and common tasks
- **[Testing Guide](docs/TESTING.md)** - How to test the application
- **[API Documentation](docs/API.md)** - Detailed API reference
- **[Contributing](docs/CONTRIBUTING.md)** - Contribution guidelines
- **[Phase 1 Complete](docs/PHASE1_COMPLETE.md)** - Implementation details

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Test with your audio file
python scripts/demo.py ~/Downloads/audio.mp3 --model tiny
```

See [TESTING.md](docs/TESTING.md) for comprehensive testing guide.

## 📁 Project Structure

```
maestrai/
├── docs/                        # All documentation
│   ├── README.md                # Detailed project overview
│   ├── SETUP.md                 # Setup guide
│   ├── QUICK_REFERENCE.md       # Quick reference guide
│   ├── TESTING.md               # Testing guide
│   ├── API.md                   # API documentation
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   └── PHASE1_COMPLETE.md       # Implementation summary
├── src/
│   ├── transcription_engine.py  # Core transcription logic
│   ├── audio_processor.py       # Audio/video processing
│   └── utils/
│       └── config.py            # Configuration management
├── tests/
│   └── test_transcription.py    # Test suite (18 tests)
├── scripts/
│   └── demo.py                  # Interactive demo
├── examples/
│   ├── basic_usage.py           # Basic examples
│   ├── batch_processing.py      # Batch processing
│   └── video_transcription.py   # Video examples
├── setup.sh                     # macOS/Linux setup script
├── setup.bat                    # Windows setup script
└── requirements.txt             # Python dependencies
```

## 🔧 Requirements

- Python 3.9+
- FFmpeg
- CUDA Toolkit (optional, for GPU acceleration)
- 4GB+ RAM (8GB+ recommended for larger models)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [OpenAI Whisper](https://github.com/openai/whisper)
- Audio processing by [FFmpeg](https://ffmpeg.org/)

## 📞 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report bugs at [GitHub Issues](https://github.com/yourusername/maestrai/issues)
- **Examples**: Check [examples/](examples/) directory

## 🗺️ Roadmap

### Phase 1 (Current) ✅
- Core transcription engine
- Multi-model support
- Word-level timestamps
- Export to SRT/TXT
- Batch processing

### Phase 2 (Planned)
- REST API server
- Web interface
- Real-time transcription
- Speaker diarization
- Custom vocabulary support

---

Made with ❤️ by the Maestrai Team
