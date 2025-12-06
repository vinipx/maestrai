# Maestrai Setup Guide

Complete setup and installation guide for Maestrai Audio Transcription Service.

## Table of Contents

- [Prerequisites](#prerequisites)
- [FFmpeg Installation](#ffmpeg-installation)
- [Python Environment Setup](#python-environment-setup)
- [Dependency Installation](#dependency-installation)
- [Verification](#verification)
- [Quick Start](#quick-start)
- [Model Selection](#model-selection)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required

- **Python 3.9 or higher**
  ```bash
  python --version  # Should show 3.9+
  ```

- **FFmpeg** (for audio/video processing)
  - See [FFmpeg Installation](#ffmpeg-installation) below

### Optional

- **CUDA Toolkit** (for GPU acceleration)
  - NVIDIA GPU with CUDA support
  - CUDA 11.7 or higher recommended
  - Significantly speeds up transcription

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4 GB | 8 GB+ |
| Storage | 5 GB | 20 GB+ |
| GPU VRAM | N/A | 4 GB+ |

## FFmpeg Installation

FFmpeg is required for audio/video processing.

### macOS

```bash
# Using Homebrew
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install FFmpeg
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

### Windows

#### Option 1: Using Chocolatey (Recommended)

```powershell
# Install Chocolatey if not already installed
# See https://chocolatey.org/install

# Install FFmpeg
choco install ffmpeg

# Verify installation
ffmpeg -version
```

#### Option 2: Manual Installation

1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add to PATH:
   - Open "Environment Variables"
   - Edit "Path" variable
   - Add `C:\ffmpeg\bin`
   - Restart terminal

## Python Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/maestrai.git
cd maestrai
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

## Dependency Installation

### Standard Installation

```bash
# Install all required dependencies
pip install -r requirements.txt
```

### Development Installation

```bash
# Install with development tools
pip install -r requirements-dev.txt
```

### Package Installation

```bash
# Install as editable package
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### GPU Support (CUDA)

If you have an NVIDIA GPU:

```bash
# Install PyTorch with CUDA support
# Visit https://pytorch.org/ for specific CUDA version

# Example for CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Verification

### 1. Check Python Imports

```bash
python -c "from src.transcription_engine import TranscriptionEngine; print('✅ Imports successful')"
```

### 2. Check FFmpeg

```bash
python -c "from src.audio_processor import AudioProcessor; AudioProcessor(); print('✅ FFmpeg available')"
```

### 3. Check CUDA (Optional)

```bash
python -c "import torch; print('✅ CUDA available' if torch.cuda.is_available() else '⚠️  CUDA not available (CPU mode)')"
```

### 4. Run Tests

```bash
# Run test suite
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Quick Start

### Interactive Demo

```bash
python scripts/demo.py
```

Follow the interactive prompts to:
1. Select a model
2. Choose an audio file
3. View transcription results
4. Export to SRT/TXT

### Quick Transcription

```bash
# Transcribe a single file
python scripts/demo.py path/to/audio.mp3

# Use a specific model
python scripts/demo.py path/to/audio.mp3 --model small

# Enable verbose logging
python scripts/demo.py path/to/audio.mp3 --verbose
```

### Programmatic Usage

```python
from src.transcription_engine import TranscriptionEngine

# Initialize engine
engine = TranscriptionEngine(model_name="base")

# Transcribe
result = engine.transcribe("audio.mp3")

# Export
engine.export_srt(result, "output.srt")
engine.export_txt(result, "output.txt")
```

## Model Selection

Choose a model based on your needs:

### For Testing/Development
```python
engine = TranscriptionEngine(model_name="tiny")  # Fastest
```

### For General Use
```python
engine = TranscriptionEngine(model_name="base")  # Balanced
```

### For High Accuracy
```python
engine = TranscriptionEngine(model_name="small")  # Good accuracy
engine = TranscriptionEngine(model_name="medium")  # Better accuracy
engine = TranscriptionEngine(model_name="large")  # Best accuracy
```

## Performance Optimization

### 1. Use GPU Acceleration

```python
# Auto-detect (recommended)
engine = TranscriptionEngine(model_name="base")

# Force CUDA
engine = TranscriptionEngine(model_name="base", device="cuda")

# Force CPU
engine = TranscriptionEngine(model_name="base", device="cpu")
```

### 2. Choose Appropriate Model

- **Quick drafts**: Use `tiny` or `base`
- **Production**: Use `small` or `medium`
- **Professional**: Use `large`

### 3. Batch Processing

```python
# More efficient than processing individually
results = engine.transcribe_batch([
    "file1.mp3",
    "file2.mp3",
    "file3.mp3"
])
```

### 4. Cache Management

The system automatically caches converted audio files to avoid re-conversion:

```python
# Files are cached in TEMP_DIR (default: /tmp/maestrai)
# Cleanup happens automatically
```

## Troubleshooting

### FFmpeg Not Found

**Error**: `FFmpeg is not installed or not in PATH`

**Solution**:
```bash
# Verify FFmpeg installation
ffmpeg -version

# If not found, install using instructions above

# On Linux/macOS, ensure it's in PATH
which ffmpeg

# On Windows, check Environment Variables
```

### CUDA Out of Memory

**Error**: `RuntimeError: CUDA out of memory`

**Solution**:
```python
# Use smaller model
engine = TranscriptionEngine(model_name="tiny")  # or "base"

# Or force CPU mode
engine = TranscriptionEngine(model_name="base", device="cpu")
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'whisper'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Slow Transcription

**Issue**: Transcription is very slow

**Solutions**:
1. Check if using GPU:
   ```python
   info = engine.get_model_info()
   print(info['device'])  # Should show 'cuda' if GPU available
   ```

2. Use smaller model:
   ```python
   engine = TranscriptionEngine(model_name="tiny")
   ```

3. Install CUDA-enabled PyTorch:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### File Validation Errors

**Error**: `Unsupported format` or `File too large`

**Solution**:
```python
# Check supported formats
from src.utils.config import Config
print(Config.get_supported_formats())

# Adjust max file size in .env
MAX_FILE_SIZE_MB=1000
```

### Permission Errors

**Error**: `Permission denied` when accessing temp directory

**Solution**:
```bash
# Create custom temp directory
mkdir ~/maestrai_temp

# Set in .env
TEMP_DIR=~/maestrai_temp
```

## Environment Configuration

Create a `.env` file for custom configuration:

```bash
# Copy example
cp .env.example .env

# Edit with your preferences
nano .env
```

Example `.env`:
```
DEFAULT_MODEL=base
DEVICE=cuda
MAX_FILE_SIZE_MB=500
TEMP_DIR=/tmp/maestrai
LOG_LEVEL=INFO
```

## Next Steps

1. **Run Examples**: Check out `examples/` directory
2. **Read API Docs**: See `docs/API.md`
3. **View Quick Reference**: See `QUICK_REFERENCE.md`
4. **Run Tests**: `pytest tests/`

## Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: https://github.com/yourusername/maestrai/issues
- **Examples**: See `examples/` directory

---

**Setup complete!** You're ready to start transcribing audio files with Maestrai.
