"""
Maestrai - AI-Powered Audio & Music Transcription Service

Features:
- Speech-to-text transcription (OpenAI Whisper)
- Music-to-notation transcription (Spotify Basic Pitch)
- Audio analysis (tempo, key, beats)
- Export to MIDI, MusicXML, PDF
"""

__version__ = "2.0.0"
__author__ = "Maestrai Team"

# Speech transcription (Phase 1)
from .transcription_engine import (
    TranscriptionEngine,
    TranscriptionResult,
    TranscriptionSegment,
    Word,
)
from .audio_processor import AudioProcessor

# Music transcription (Phase 2)
from .music_transcription_engine import (
    MusicTranscriptionEngine,
    MusicTranscriptionResult,
    Note,
)
from .audio_analyzer import AudioAnalyzer, AudioAnalysis
from .score_generator import ScoreGenerator

__all__ = [
    # Speech transcription
    "TranscriptionEngine",
    "TranscriptionResult",
    "TranscriptionSegment",
    "Word",
    "AudioProcessor",
    # Music transcription
    "MusicTranscriptionEngine",
    "MusicTranscriptionResult",
    "Note",
    "AudioAnalyzer",
    "AudioAnalysis",
    "ScoreGenerator",
]
