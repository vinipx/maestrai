"""Configuration management for Maestrai."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the transcription service."""

    # Model settings
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "base")
    AVAILABLE_MODELS: list[str] = ["tiny", "base", "small", "medium", "large"]

    # Device settings
    DEVICE: str = os.getenv("DEVICE", "cuda")  # Will auto-detect if cuda available

    # File settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    MAX_FILE_SIZE: int = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes

    # Supported formats
    SUPPORTED_AUDIO_FORMATS: list[str] = [
        ".mp3",
        ".wav",
        ".m4a",
        ".flac",
        ".ogg",
        ".webm",
    ]
    SUPPORTED_VIDEO_FORMATS: list[str] = [".mp4", ".avi", ".mov", ".mkv"]

    # Processing settings
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "/tmp/maestrai"))
    SAMPLE_RATE: int = 16000  # Whisper's required sample rate
    CHANNELS: int = 1  # Mono audio

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Language support (99+ languages)
    SUPPORTED_LANGUAGES: list[str] = [
        "af",
        "am",
        "ar",
        "as",
        "az",
        "ba",
        "be",
        "bg",
        "bn",
        "bo",
        "br",
        "bs",
        "ca",
        "cs",
        "cy",
        "da",
        "de",
        "el",
        "en",
        "es",
        "et",
        "eu",
        "fa",
        "fi",
        "fo",
        "fr",
        "gl",
        "gu",
        "ha",
        "haw",
        "he",
        "hi",
        "hr",
        "ht",
        "hu",
        "hy",
        "id",
        "is",
        "it",
        "ja",
        "jw",
        "ka",
        "kk",
        "km",
        "kn",
        "ko",
        "la",
        "lb",
        "ln",
        "lo",
        "lt",
        "lv",
        "mg",
        "mi",
        "mk",
        "ml",
        "mn",
        "mr",
        "ms",
        "mt",
        "my",
        "ne",
        "nl",
        "nn",
        "no",
        "oc",
        "pa",
        "pl",
        "ps",
        "pt",
        "ro",
        "ru",
        "sa",
        "sd",
        "si",
        "sk",
        "sl",
        "sn",
        "so",
        "sq",
        "sr",
        "su",
        "sv",
        "sw",
        "ta",
        "te",
        "tg",
        "th",
        "tk",
        "tl",
        "tr",
        "tt",
        "uk",
        "ur",
        "uz",
        "vi",
        "yi",
        "yo",
        "zh",
    ]

    @classmethod
    def validate_model(cls, model: str) -> bool:
        """Validate if the model name is supported.

        Args:
            model: Model name to validate

        Returns:
            True if model is valid, False otherwise
        """
        return model in cls.AVAILABLE_MODELS

    @classmethod
    def validate_language(cls, language: str) -> bool:
        """Validate if the language code is supported.

        Args:
            language: Language code to validate

        Returns:
            True if language is valid, False otherwise
        """
        return language in cls.SUPPORTED_LANGUAGES

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get all supported file formats.

        Returns:
            List of supported audio and video formats
        """
        return cls.SUPPORTED_AUDIO_FORMATS + cls.SUPPORTED_VIDEO_FORMATS

    @classmethod
    def ensure_temp_dir(cls) -> None:
        """Ensure the temporary directory exists."""
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
