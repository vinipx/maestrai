# Maestrai Testing Guide

Complete guide to testing the Maestrai Audio Transcription Service.

## Quick Start

### Automated Setup (Recommended)

#### macOS/Linux:
```bash
./setup.sh
```

#### Windows:
```bash
setup.bat
```

The setup script will:
1. Check Python version (3.9+)
2. Install/verify FFmpeg
3. Create virtual environment
4. Install all dependencies
5. Run tests
6. Verify installation

### Manual Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For testing
   ```

3. **Verify FFmpeg:**
   ```bash
   ffmpeg -version
   ```

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_transcription.py

# Run specific test class
pytest tests/test_transcription.py::TestAudioProcessor

# Run specific test
pytest tests/test_transcription.py::TestAudioProcessor::test_ffmpeg_availability
```

### Test Results

Expected output:
```
============================= test session starts ==============================
collected 18 items

tests/test_transcription.py::TestAudioProcessor::test_ffmpeg_availability PASSED
tests/test_transcription.py::TestAudioProcessor::test_supported_formats_list PASSED
tests/test_transcription.py::TestAudioProcessor::test_validate_empty_file PASSED
tests/test_transcription.py::TestAudioProcessor::test_validate_nonexistent_file PASSED
tests/test_transcription.py::TestAudioProcessor::test_validate_unsupported_format PASSED
tests/test_transcription.py::TestTranscriptionEngine::test_invalid_model_name PASSED
tests/test_transcription.py::TestTranscriptionEngine::test_model_info_structure PASSED
tests/test_transcription.py::TestTranscriptionEngine::test_timestamp_formatting PASSED
tests/test_transcription.py::TestTranscriptionEngine::test_valid_model_names PASSED
tests/test_transcription.py::TestDataClasses::test_result_creation PASSED
tests/test_transcription.py::TestDataClasses::test_segment_creation PASSED
tests/test_transcription.py::TestDataClasses::test_word_creation PASSED
tests/test_transcription.py::TestExportFunctionality::test_srt_export_format PASSED
tests/test_transcription.py::TestExportFunctionality::test_txt_export_structure PASSED
tests/test_transcription.py::TestIntegration::test_full_pipeline_structure PASSED
tests/test_transcription.py::TestConfiguration::test_language_validation PASSED
tests/test_transcription.py::TestConfiguration::test_model_validation PASSED
tests/test_transcription.py::TestConfiguration::test_supported_formats PASSED

============================== 18 passed in 1.21s ==============================
```

## Testing with Real Audio Files

### Interactive Demo

```bash
# Activate virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run interactive demo
python scripts/demo.py
```

Follow the prompts to:
1. Select a Whisper model
2. Choose an audio file
3. View transcription results
4. Automatically export to SRT and TXT

### Quick Mode

```bash
# Transcribe a single file
python scripts/demo.py ~/Downloads/audio.mp3

# Use specific model
python scripts/demo.py ~/Downloads/audio.mp3 --model tiny

# Enable verbose logging
python scripts/demo.py ~/Downloads/audio.mp3 --verbose
```

### Example with Your Audio File

If you have `~/Downloads/o-emmanuel.mp3`:

```bash
# Quick test with tiny model (fastest)
python scripts/demo.py ~/Downloads/o-emmanuel.mp3 --model tiny

# Better accuracy with small model
python scripts/demo.py ~/Downloads/o-emmanuel.mp3 --model small

# Best accuracy with large model (slower)
python scripts/demo.py ~/Downloads/o-emmanuel.mp3 --model large
```

Expected output:
```
================================================================================
  MAESTRAI - Audio Transcription Service Demo
  Powered by OpenAI Whisper
================================================================================

Quick Mode: Transcribing /Users/vinipx/Downloads/o-emmanuel.mp3
Model: tiny


Validating audio file...
----------------------------------------
✅ File validation passed

ℹ️  Audio Information:
   Filename: o-emmanuel.mp3
   Format: mp3
   Duration: 173.84 seconds
   Size: 3.56 MB
   Codec: mp3
   Sample Rate: 48000 Hz
   Channels: 2

================================================================================
TRANSCRIPTION
================================================================================

ℹ️  Loading tiny model...
✅ Model loaded successfully

ℹ️  Starting transcription...
   (This may take a while depending on audio length and model size)

✅ Transcription completed!

[Results displayed here]
```

## Manual Testing

### 1. Test Imports

```python
from src.utils.config import Config
from src.audio_processor import AudioProcessor
from src.transcription_engine import TranscriptionEngine

print("✅ All imports successful")
```

### 2. Test Audio Validation

```python
from src.audio_processor import AudioProcessor

processor = AudioProcessor()

# Test with your file
is_valid, error = processor.validate_audio_file("~/Downloads/o-emmanuel.mp3")
if is_valid:
    print("✅ File is valid")
    info = processor.get_audio_info("~/Downloads/o-emmanuel.mp3")
    print(f"Duration: {info['duration']:.2f}s")
    print(f"Format: {info['format']}")
else:
    print(f"❌ Validation failed: {error}")
```

### 3. Test Transcription

```python
from src.transcription_engine import TranscriptionEngine

# Initialize with tiny model for quick testing
engine = TranscriptionEngine(model_name="tiny")

# Get model info
info = engine.get_model_info()
print(f"Model: {info['model_name']}")
print(f"Device: {info['device']}")

# Transcribe (this will download the model on first run)
result = engine.transcribe("~/Downloads/o-emmanuel.mp3")
print(f"\nTranscribed {result.word_count} words in {result.language}")
print(f"\nFirst 100 characters:\n{result.text[:100]}...")
```

### 4. Test Export Functions

```python
from src.transcription_engine import TranscriptionEngine

engine = TranscriptionEngine(model_name="tiny")
result = engine.transcribe("~/Downloads/o-emmanuel.mp3")

# Export to SRT
srt_path = engine.export_srt(result, "output.srt")
print(f"✅ SRT exported to: {srt_path}")

# Export to TXT
txt_path = engine.export_txt(result, "output.txt")
print(f"✅ TXT exported to: {txt_path}")
```

## Example Scripts

### Basic Usage

```bash
python examples/basic_usage.py
```

Update the `audio_file` path in the script to point to your audio file.

### Batch Processing

```bash
python examples/batch_processing.py
```

Update the `audio_files` list with your file paths.

### Video Transcription

```bash
python examples/video_transcription.py
```

Update the `video_file` path to point to your video file.

## Common Issues

### Issue: FFmpeg not found

**Error:**
```
RuntimeError: FFmpeg is not installed or not in PATH.
```

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

### Issue: SSL Certificate Error

**Error:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
This occurs when downloading Whisper models for the first time. The models will be cached after the first download.

On macOS:
```bash
# Option 1: Run the certificate installer
/Applications/Python\ 3.10/Install\ Certificates.command

# Option 2: Update certifi
pip install --upgrade certifi
```

### Issue: CUDA Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
```python
# Use a smaller model
engine = TranscriptionEngine(model_name="tiny")

# Or force CPU mode
engine = TranscriptionEngine(model_name="base", device="cpu")
```

### Issue: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'whisper'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

## Performance Testing

### Benchmark Different Models

Test file: `~/Downloads/o-emmanuel.mp3` (173 seconds, 3.56 MB)

```bash
# Tiny (fastest)
time python scripts/demo.py ~/Downloads/o-emmanuel.mp3 --model tiny

# Base
time python scripts/demo.py ~/Downloads/o-emmanuel.mp3 --model base

# Small
time python scripts/demo.py ~/Downloads/o-emmanuel.mp3 --model small

# Medium
time python scripts/demo.py ~/Downloads/o-emmanuel.mp3 --model medium

# Large (best quality)
time python scripts/demo.py ~/Downloads/o-emmanuel.mp3 --model large
```

Expected processing times (on CPU):
- **tiny**: ~5-10 seconds
- **base**: ~10-20 seconds
- **small**: ~30-60 seconds
- **medium**: ~2-3 minutes
- **large**: ~5-10 minutes

With GPU (CUDA), these times can be 10-50x faster!

## Test Coverage

Current test coverage:

```
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/__init__.py                   5      0   100%
src/audio_processor.py          133     92    31%
src/transcription_engine.py     167    105    37%
src/utils/__init__.py             2      0   100%
src/utils/config.py              30      0   100%
-------------------------------------------------
TOTAL                           337    197    42%
```

To improve coverage, run full integration tests with actual audio files.

## Continuous Integration

Tests are automatically run on GitHub Actions for:
- Python 3.9, 3.10, 3.11, 3.12
- Ubuntu, macOS, Windows

See `.github/workflows/tests.yml`

## Next Steps

After successful testing:

1. **Try different audio files**: Test with various formats (MP3, WAV, M4A, etc.)
2. **Test video files**: Extract and transcribe audio from videos
3. **Batch processing**: Transcribe multiple files at once
4. **Experiment with models**: Compare accuracy vs speed trade-offs
5. **Export options**: Generate SRT subtitles and text transcripts

## Getting Help

- **Documentation**: README.md, SETUP.md, QUICK_REFERENCE.md
- **API Reference**: docs/API.md
- **Examples**: examples/ directory
- **Issues**: Report bugs at GitHub Issues

---

Happy testing! 🎉
