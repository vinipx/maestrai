# Maestrai Quick Reference

Cheat sheet for common tasks and quick lookups.

## One-Minute Installation

```bash
git clone https://github.com/yourusername/maestrai.git
cd maestrai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
brew install ffmpeg  # macOS (or apt install ffmpeg on Linux)
```

## Basic Usage

### Transcribe a File

```python
from src.transcription_engine import TranscriptionEngine

engine = TranscriptionEngine(model_name="base")
result = engine.transcribe("audio.mp3")
print(result.text)
```

### Quick Demo

```bash
python scripts/demo.py audio.mp3
```

## Common Tasks

### 1. Video to Subtitles

```python
engine = TranscriptionEngine(model_name="base")
result = engine.transcribe("video.mp4")
engine.export_srt(result, "subtitles.srt")
```

### 2. Batch Processing

```python
engine = TranscriptionEngine(model_name="small")
results = engine.transcribe_batch(["file1.mp3", "file2.mp3", "file3.mp3"])
```

### 3. Get Word Timestamps

```python
result = engine.transcribe("audio.mp3", word_timestamps=True)
for segment in result.segments:
    for word in segment.words:
        print(f"{word.text}: {word.start:.2f}s")
```

### 4. Specify Language

```python
result = engine.transcribe("audio.mp3", language="es")  # Spanish
```

### 5. Translation (to English)

```python
result = engine.transcribe("spanish.mp3", task="translate")
```

## Model Selection Guide

| If you need... | Use this model | Command |
|---------------|---------------|---------|
| Speed test | `tiny` | `model_name="tiny"` |
| Quick draft | `base` | `model_name="base"` |
| Good quality | `small` | `model_name="small"` |
| High accuracy | `medium` | `model_name="medium"` |
| Best possible | `large` | `model_name="large"` |

## API Quick Reference

### TranscriptionEngine

```python
# Initialize
engine = TranscriptionEngine(
    model_name="base",  # tiny, base, small, medium, large
    device=None  # Auto-detect, or "cuda"/"cpu"
)

# Transcribe
result = engine.transcribe(
    audio_path="file.mp3",
    language=None,  # Auto-detect or "en", "es", etc.
    task="transcribe",  # or "translate"
    word_timestamps=True
)

# Batch
results = engine.transcribe_batch(
    audio_paths=["file1.mp3", "file2.mp3"],
    language=None,
    word_timestamps=True
)

# Export
engine.export_srt(result, "output.srt")
engine.export_txt(result, "output.txt")

# Get info
info = engine.get_model_info()
```

### AudioProcessor

```python
from src.audio_processor import AudioProcessor

processor = AudioProcessor()

# Validate
is_valid, error = processor.validate_audio_file("audio.mp3")

# Get info
info = processor.get_audio_info("audio.mp3")

# Convert
wav_path = processor.convert_to_wav("audio.mp3")

# Extract from video
audio_path = processor.extract_audio_from_video("video.mp4")

# Trim
trimmed = processor.trim_audio("audio.mp3", "out.mp3", 10, 30)

# Cleanup
processor.cleanup_temp_files()
```

### TranscriptionResult

```python
result.text              # Full transcription text
result.language          # Detected language
result.segments          # List of TranscriptionSegment
result.duration          # Audio duration in seconds
result.word_count        # Number of words
result.model_name        # Model used
result.metadata          # Additional metadata
```

### TranscriptionSegment

```python
segment.id               # Segment ID
segment.start            # Start time (seconds)
segment.end              # End time (seconds)
segment.text             # Segment text
segment.words            # List of Word objects
segment.avg_logprob      # Average log probability
segment.no_speech_prob   # Probability of no speech
```

### Word

```python
word.text                # Word text
word.start               # Start time (seconds)
word.end                 # End time (seconds)
word.confidence          # Confidence score
```

## Supported Formats

### Audio
- MP3 (`.mp3`)
- WAV (`.wav`)
- M4A (`.m4a`)
- FLAC (`.flac`)
- OGG (`.ogg`)
- WEBM (`.webm`)

### Video
- MP4 (`.mp4`)
- AVI (`.avi`)
- MOV (`.mov`)
- MKV (`.mkv`)

## Supported Languages

99+ languages including:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean
- `ar` - Arabic
- `ru` - Russian

[Full list in `src/utils/config.py`]

## Troubleshooting Quick Fixes

### FFmpeg not found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

### CUDA out of memory
```python
# Use smaller model
engine = TranscriptionEngine(model_name="tiny")

# Or force CPU
engine = TranscriptionEngine(model_name="base", device="cpu")
```

### Import errors
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate

# Reinstall
pip install -r requirements.txt
```

### File too large
```python
# Create .env file
echo "MAX_FILE_SIZE_MB=1000" > .env
```

## Environment Variables

Create `.env` file:
```
DEFAULT_MODEL=base
DEVICE=cuda
MAX_FILE_SIZE_MB=500
TEMP_DIR=/tmp/maestrai
LOG_LEVEL=INFO
```

## Pro Tips

1. **Cache is your friend**: Converted files are cached automatically
2. **GPU makes it fast**: Install CUDA for 10-50x speedup
3. **Batch for efficiency**: Process multiple files at once
4. **Start small**: Test with `tiny` model first
5. **SRT for videos**: Use `.srt` files with video players
6. **Timestamps are precise**: Word-level timing is very accurate

## One-Liners

```bash
# Quick transcribe
python -c "from src.transcription_engine import TranscriptionEngine; e=TranscriptionEngine('base'); r=e.transcribe('audio.mp3'); print(r.text)"

# Check CUDA
python -c "import torch; print('CUDA' if torch.cuda.is_available() else 'CPU')"

# Run tests
pytest tests/

# Run demo
python scripts/demo.py
```

## Performance Tips

| Scenario | Recommendation |
|----------|---------------|
| Quick test | Use `tiny` model |
| Production subtitles | Use `small` or `medium` |
| Academic transcription | Use `large` |
| Real-time preview | Use `base` on GPU |
| Batch overnight | Use `large` on multiple GPUs |

## Example Workflows

### Workflow 1: Podcast Transcription
```python
engine = TranscriptionEngine("small")
result = engine.transcribe("podcast.mp3", word_timestamps=True)
engine.export_txt(result, "transcript.txt")
```

### Workflow 2: Video Subtitles
```python
engine = TranscriptionEngine("base")
result = engine.transcribe("video.mp4")
engine.export_srt(result, "subtitles.srt")
```

### Workflow 3: Batch Processing
```python
import glob
engine = TranscriptionEngine("small")
files = glob.glob("lectures/*.mp3")
results = engine.transcribe_batch(files)
for i, r in enumerate(results):
    engine.export_txt(r, f"transcript_{i+1}.txt")
```

---

For detailed documentation, see:
- [SETUP.md](SETUP.md) - Full setup guide
- [README.md](README.md) - Project overview
- [docs/API.md](docs/API.md) - API documentation
