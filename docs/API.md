# Maestrai API Documentation

Complete API reference for Maestrai Audio Transcription Service.

## Table of Contents

- [TranscriptionEngine](#transcriptionengine)
- [AudioProcessor](#audioprocessor)
- [Data Classes](#data-classes)
- [Configuration](#configuration)

## TranscriptionEngine

Main class for audio transcription using OpenAI Whisper.

### Class: `TranscriptionEngine`

```python
from src.transcription_engine import TranscriptionEngine
```

#### Constructor

```python
TranscriptionEngine(
    model_name: str = "base",
    device: Optional[str] = None
)
```

**Parameters:**
- `model_name` (str): Whisper model to use
  - Options: `"tiny"`, `"base"`, `"small"`, `"medium"`, `"large"`
  - Default: `"base"`
- `device` (Optional[str]): Device to use for inference
  - Options: `"cuda"`, `"cpu"`, or `None` (auto-detect)
  - Default: `None` (auto-detects CUDA availability)

**Raises:**
- `ValueError`: If model_name is invalid
- `RuntimeError`: If model fails to load

**Example:**
```python
# Auto-detect device
engine = TranscriptionEngine(model_name="base")

# Force GPU
engine = TranscriptionEngine(model_name="small", device="cuda")

# Force CPU
engine = TranscriptionEngine(model_name="tiny", device="cpu")
```

---

#### Method: `transcribe`

```python
transcribe(
    audio_path: str | Path,
    language: Optional[str] = None,
    task: str = "transcribe",
    word_timestamps: bool = True,
    **kwargs
) -> TranscriptionResult
```

Transcribe an audio or video file.

**Parameters:**
- `audio_path` (str | Path): Path to audio or video file
- `language` (Optional[str]): Language code (e.g., 'en', 'es')
  - Default: `None` (auto-detect)
- `task` (str): Task to perform
  - Options: `"transcribe"`, `"translate"`
  - Default: `"transcribe"`
- `word_timestamps` (bool): Extract word-level timestamps
  - Default: `True`
- `**kwargs`: Additional arguments passed to Whisper

**Returns:**
- `TranscriptionResult`: Object containing transcription results

**Raises:**
- `ValueError`: If file validation fails or language is invalid
- `RuntimeError`: If transcription fails

**Example:**
```python
# Basic transcription
result = engine.transcribe("audio.mp3")

# With specific language
result = engine.transcribe("audio.mp3", language="en")

# Translation to English
result = engine.transcribe("spanish.mp3", task="translate")

# Without word timestamps (faster)
result = engine.transcribe("audio.mp3", word_timestamps=False)
```

---

#### Method: `transcribe_batch`

```python
transcribe_batch(
    audio_paths: List[str | Path],
    **kwargs
) -> List[TranscriptionResult]
```

Transcribe multiple audio files.

**Parameters:**
- `audio_paths` (List[str | Path]): List of paths to audio files
- `**kwargs`: Arguments passed to `transcribe()`

**Returns:**
- `List[TranscriptionResult]`: List of transcription results

**Example:**
```python
results = engine.transcribe_batch([
    "file1.mp3",
    "file2.wav",
    "file3.m4a"
], language="en", word_timestamps=True)

for result in results:
    print(result.text)
```

---

#### Method: `export_srt`

```python
export_srt(
    result: TranscriptionResult,
    output_path: str | Path
) -> Path
```

Export transcription to SRT subtitle format.

**Parameters:**
- `result` (TranscriptionResult): Transcription result to export
- `output_path` (str | Path): Path for output SRT file

**Returns:**
- `Path`: Path to the created SRT file

**Raises:**
- `RuntimeError`: If export fails

**Example:**
```python
result = engine.transcribe("video.mp4")
engine.export_srt(result, "subtitles.srt")
```

**SRT Format:**
```
1
00:00:00,000 --> 00:00:02,500
Hello, this is a test.

2
00:00:02,500 --> 00:00:05,000
This is the second segment.
```

---

#### Method: `export_txt`

```python
export_txt(
    result: TranscriptionResult,
    output_path: str | Path
) -> Path
```

Export transcription to plain text format with metadata.

**Parameters:**
- `result` (TranscriptionResult): Transcription result to export
- `output_path` (str | Path): Path for output text file

**Returns:**
- `Path`: Path to the created text file

**Raises:**
- `RuntimeError`: If export fails

**Example:**
```python
result = engine.transcribe("audio.mp3")
engine.export_txt(result, "transcript.txt")
```

---

#### Static Method: `format_timestamp`

```python
@staticmethod
format_timestamp(
    seconds: float,
    srt_format: bool = True
) -> str
```

Convert seconds to timestamp format.

**Parameters:**
- `seconds` (float): Time in seconds
- `srt_format` (bool): Use SRT format (HH:MM:SS,mmm) vs simple format
  - Default: `True`

**Returns:**
- `str`: Formatted timestamp string

**Example:**
```python
# SRT format
timestamp = TranscriptionEngine.format_timestamp(90.5)
# Returns: "00:01:30,500"

# Simple format
timestamp = TranscriptionEngine.format_timestamp(90.5, srt_format=False)
# Returns: "00:01:30.500"
```

---

#### Method: `get_model_info`

```python
get_model_info() -> Dict[str, Any]
```

Get information about the current model.

**Returns:**
- `Dict[str, Any]`: Dictionary containing model information

**Example:**
```python
info = engine.get_model_info()
print(info)
# {
#     'model_name': 'base',
#     'device': 'cuda',
#     'cuda_available': True,
#     'available_models': ['tiny', 'base', 'small', 'medium', 'large'],
#     'supported_languages': 99
# }
```

---

## AudioProcessor

Class for audio file validation, conversion, and processing.

### Class: `AudioProcessor`

```python
from src.audio_processor import AudioProcessor
```

#### Constructor

```python
AudioProcessor()
```

Initializes the audio processor and checks FFmpeg availability.

**Raises:**
- `RuntimeError`: If FFmpeg is not installed

**Example:**
```python
processor = AudioProcessor()
```

---

#### Method: `validate_audio_file`

```python
validate_audio_file(
    file_path: str | Path
) -> tuple[bool, Optional[str]]
```

Validate an audio file for format, size, and integrity.

**Parameters:**
- `file_path` (str | Path): Path to the audio file

**Returns:**
- `tuple[bool, Optional[str]]`: (is_valid, error_message)

**Example:**
```python
is_valid, error = processor.validate_audio_file("audio.mp3")
if is_valid:
    print("File is valid")
else:
    print(f"Validation failed: {error}")
```

---

#### Method: `get_audio_info`

```python
get_audio_info(
    file_path: str | Path
) -> Dict[str, Any]
```

Get audio file metadata using ffprobe.

**Parameters:**
- `file_path` (str | Path): Path to the audio file

**Returns:**
- `Dict[str, Any]`: Dictionary containing audio metadata

**Raises:**
- `RuntimeError`: If ffprobe fails to read the file

**Example:**
```python
info = processor.get_audio_info("audio.mp3")
print(f"Duration: {info['duration']}s")
print(f"Sample Rate: {info['sample_rate']}Hz")
```

**Returned Fields:**
- `filename` (str): File name
- `format` (str): Format name
- `duration` (float): Duration in seconds
- `size` (int): File size in bytes
- `bit_rate` (int): Bit rate
- `codec` (str): Audio codec
- `sample_rate` (int): Sample rate in Hz
- `channels` (int): Number of channels

---

#### Method: `convert_to_wav`

```python
convert_to_wav(
    input_path: str | Path,
    sample_rate: int = 16000,
    channels: int = 1
) -> Path
```

Convert audio file to WAV format optimized for Whisper.

**Parameters:**
- `input_path` (str | Path): Path to input audio file
- `sample_rate` (int): Target sample rate
  - Default: `16000` (Whisper's required rate)
- `channels` (int): Number of audio channels
  - Default: `1` (mono)

**Returns:**
- `Path`: Path to the converted WAV file

**Raises:**
- `RuntimeError`: If conversion fails

**Example:**
```python
wav_path = processor.convert_to_wav("audio.mp3")
print(f"Converted to: {wav_path}")
```

**Note:** Converted files are cached using MD5 hash to avoid re-conversion.

---

#### Method: `extract_audio_from_video`

```python
extract_audio_from_video(
    video_path: str | Path,
    sample_rate: int = 16000,
    channels: int = 1
) -> Path
```

Extract audio from video file and convert to WAV.

**Parameters:**
- `video_path` (str | Path): Path to video file
- `sample_rate` (int): Target sample rate (default: 16000)
- `channels` (int): Number of audio channels (default: 1)

**Returns:**
- `Path`: Path to the extracted WAV file

**Raises:**
- `RuntimeError`: If extraction fails
- `ValueError`: If video format is unsupported

**Example:**
```python
audio_path = processor.extract_audio_from_video("video.mp4")
print(f"Extracted audio to: {audio_path}")
```

---

#### Method: `trim_audio`

```python
trim_audio(
    input_path: str | Path,
    output_path: str | Path,
    start_time: float,
    end_time: float
) -> Path
```

Trim audio file to a specific time range.

**Parameters:**
- `input_path` (str | Path): Path to input audio file
- `output_path` (str | Path): Path for output trimmed file
- `start_time` (float): Start time in seconds
- `end_time` (float): End time in seconds

**Returns:**
- `Path`: Path to the trimmed audio file

**Raises:**
- `ValueError`: If start_time < 0 or end_time <= start_time
- `RuntimeError`: If trimming fails

**Example:**
```python
# Extract 10-30 seconds
trimmed = processor.trim_audio(
    "audio.mp3",
    "trimmed.mp3",
    start_time=10,
    end_time=30
)
```

---

#### Method: `cleanup_temp_files`

```python
cleanup_temp_files() -> None
```

Clean up temporary files created during processing.

**Example:**
```python
processor.cleanup_temp_files()
```

**Note:** Cleanup is also called automatically in the destructor.

---

## Data Classes

### Class: `Word`

Represents a single word with timestamp and confidence.

```python
from src.transcription_engine import Word
```

**Attributes:**
- `text` (str): Word text
- `start` (float): Start time in seconds
- `end` (float): End time in seconds
- `confidence` (float): Confidence score (0.0-1.0)

**Example:**
```python
word = Word(
    text="hello",
    start=0.5,
    end=1.0,
    confidence=0.95
)
print(f"{word.text}: {word.start}s-{word.end}s")
```

---

### Class: `TranscriptionSegment`

Represents a segment of transcribed text.

```python
from src.transcription_engine import TranscriptionSegment
```

**Attributes:**
- `id` (int): Segment ID
- `start` (float): Start time in seconds
- `end` (float): End time in seconds
- `text` (str): Segment text
- `words` (List[Word]): List of Word objects (default: [])
- `temperature` (float): Sampling temperature (default: 0.0)
- `avg_logprob` (float): Average log probability (default: 0.0)
- `compression_ratio` (float): Compression ratio (default: 0.0)
- `no_speech_prob` (float): No-speech probability (default: 0.0)

**Example:**
```python
segment = TranscriptionSegment(
    id=0,
    start=0.0,
    end=2.5,
    text="Hello, world!",
    words=[...]
)
```

---

### Class: `TranscriptionResult`

Complete transcription result with metadata.

```python
from src.transcription_engine import TranscriptionResult
```

**Attributes:**
- `text` (str): Full transcription text
- `language` (str): Detected language code
- `segments` (List[TranscriptionSegment]): List of segments
- `duration` (float): Audio duration in seconds
- `model_name` (str): Model used for transcription
- `word_count` (int): Number of words (auto-calculated)
- `metadata` (Dict[str, Any]): Additional metadata (default: {})

**Example:**
```python
result = TranscriptionResult(
    text="Full transcription...",
    language="en",
    segments=[...],
    duration=120.5,
    model_name="base"
)

print(f"Transcribed {result.word_count} words in {result.language}")
```

---

## Configuration

### Class: `Config`

Configuration settings for the transcription service.

```python
from src.utils.config import Config
```

**Class Attributes:**
- `DEFAULT_MODEL` (str): Default Whisper model
- `AVAILABLE_MODELS` (List[str]): List of available models
- `DEVICE` (str): Default device ('cuda' or 'cpu')
- `MAX_FILE_SIZE_MB` (int): Maximum file size in MB
- `MAX_FILE_SIZE` (int): Maximum file size in bytes
- `SUPPORTED_AUDIO_FORMATS` (List[str]): Supported audio formats
- `SUPPORTED_VIDEO_FORMATS` (List[str]): Supported video formats
- `TEMP_DIR` (Path): Temporary directory path
- `SAMPLE_RATE` (int): Audio sample rate (16000 Hz)
- `CHANNELS` (int): Audio channels (1 = mono)
- `LOG_LEVEL` (str): Logging level
- `SUPPORTED_LANGUAGES` (List[str]): List of 99+ language codes

**Class Methods:**

#### `validate_model`

```python
@classmethod
validate_model(cls, model: str) -> bool
```

Validate if the model name is supported.

#### `validate_language`

```python
@classmethod
validate_language(cls, language: str) -> bool
```

Validate if the language code is supported.

#### `get_supported_formats`

```python
@classmethod
get_supported_formats(cls) -> List[str]
```

Get all supported file formats.

#### `ensure_temp_dir`

```python
@classmethod
ensure_temp_dir(cls) -> None
```

Ensure the temporary directory exists.

**Example:**
```python
from src.utils.config import Config

# Check if model is valid
if Config.validate_model("base"):
    print("Model is valid")

# Get supported formats
formats = Config.get_supported_formats()
print(f"Supported: {formats}")

# Ensure temp directory exists
Config.ensure_temp_dir()
```

---

## Error Handling

All methods raise appropriate exceptions with descriptive messages:

- `ValueError`: Invalid input parameters
- `RuntimeError`: Operation failures (FFmpeg, Whisper, etc.)
- `FileNotFoundError`: File not found

**Example:**
```python
try:
    result = engine.transcribe("audio.mp3")
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Transcription failed: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

---

## Logging

All components use Python's logging module:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or set via environment
# LOG_LEVEL=DEBUG in .env
```

---

For more examples, see the `examples/` directory.
