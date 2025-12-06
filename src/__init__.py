"""
Maestrai - Advanced Audio Transcription Service
Powered by OpenAI Whisper with multi-model support and advanced features.
"""

__version__ = "1.0.0"
__author__ = "Maestrai Team"

from .transcription_engine import (
    TranscriptionEngine,
    TranscriptionResult,
    TranscriptionSegment,
    Word,
)
from .audio_processor import AudioProcessor

__all__ = [
    "TranscriptionEngine",
    "TranscriptionResult",
    "TranscriptionSegment",
    "Word",
    "AudioProcessor",
]
