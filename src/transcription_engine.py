"""Core transcription engine for Maestrai using OpenAI Whisper."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
import torch
import whisper

from .utils.config import Config
from .audio_processor import AudioProcessor

logger = logging.getLogger(__name__)


@dataclass
class Word:
    """Represents a single word with timestamp and confidence."""

    text: str
    start: float
    end: float
    confidence: float

    def __repr__(self) -> str:
        return f"Word(text='{self.text}', start={self.start:.2f}s, end={self.end:.2f}s, confidence={self.confidence:.2f})"


@dataclass
class TranscriptionSegment:
    """Represents a segment of transcribed text."""

    id: int
    start: float
    end: float
    text: str
    words: List[Word] = field(default_factory=list)
    temperature: float = 0.0
    avg_logprob: float = 0.0
    compression_ratio: float = 0.0
    no_speech_prob: float = 0.0

    def __repr__(self) -> str:
        return f"Segment(id={self.id}, start={self.start:.2f}s, end={self.end:.2f}s, text='{self.text[:50]}...')"


@dataclass
class TranscriptionResult:
    """Complete transcription result with metadata."""

    text: str
    language: str
    segments: List[TranscriptionSegment]
    duration: float
    model_name: str
    word_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate word count after initialization."""
        if not self.word_count:
            self.word_count = len(self.text.split())

    def __repr__(self) -> str:
        return (
            f"TranscriptionResult(language='{self.language}', "
            f"duration={self.duration:.2f}s, "
            f"segments={len(self.segments)}, "
            f"words={self.word_count})"
        )


class TranscriptionEngine:
    """Main transcription engine using OpenAI Whisper."""

    def __init__(self, model_name: str = Config.DEFAULT_MODEL, device: Optional[str] = None):
        """Initialize the transcription engine.

        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large)
            device: Device to use ('cuda' or 'cpu'). Auto-detects if None

        Raises:
            ValueError: If model_name is invalid
            RuntimeError: If model fails to load
        """
        if not Config.validate_model(model_name):
            raise ValueError(
                f"Invalid model: {model_name}. "
                f"Available models: {', '.join(Config.AVAILABLE_MODELS)}"
            )

        self.model_name = model_name

        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Initializing Whisper model '{model_name}' on device '{self.device}'")

        try:
            self.model = whisper.load_model(model_name, device=self.device)
            logger.info(f"Model '{model_name}' loaded successfully")
        except Exception as e:
            error_msg = f"Failed to load model '{model_name}': {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        self.audio_processor = AudioProcessor()

    def transcribe(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        task: str = "transcribe",
        word_timestamps: bool = True,
        **kwargs,
    ) -> TranscriptionResult:
        """Transcribe an audio file.

        Args:
            audio_path: Path to audio or video file
            language: Language code (e.g., 'en', 'es'). Auto-detects if None
            task: Task to perform ('transcribe' or 'translate')
            word_timestamps: Extract word-level timestamps
            **kwargs: Additional arguments for Whisper

        Returns:
            TranscriptionResult object

        Raises:
            ValueError: If file validation fails
            RuntimeError: If transcription fails
        """
        audio_path = Path(audio_path)

        # Validate language if provided
        if language and not Config.validate_language(language):
            raise ValueError(
                f"Unsupported language: {language}. "
                "Use None for auto-detection or check Config.SUPPORTED_LANGUAGES"
            )

        # Validate audio file
        is_valid, error_msg = self.audio_processor.validate_audio_file(audio_path)
        if not is_valid:
            raise ValueError(f"Audio validation failed: {error_msg}")

        logger.info(f"Starting transcription of: {audio_path.name}")

        # Get audio info
        audio_info = self.audio_processor.get_audio_info(audio_path)

        # Convert to WAV if needed (Whisper works best with WAV)
        if audio_path.suffix.lower() in Config.SUPPORTED_VIDEO_FORMATS:
            logger.info("Extracting audio from video...")
            processed_path = self.audio_processor.extract_audio_from_video(audio_path)
        elif audio_path.suffix.lower() != ".wav":
            logger.info("Converting to WAV format...")
            processed_path = self.audio_processor.convert_to_wav(audio_path)
        else:
            processed_path = audio_path

        try:
            # Perform transcription
            logger.info("Running Whisper transcription...")
            result = self.model.transcribe(
                str(processed_path),
                language=language,
                task=task,
                word_timestamps=word_timestamps,
                **kwargs,
            )

            # Parse segments
            segments = self._parse_segments(result.get("segments", []))

            # Create result object
            transcription_result = TranscriptionResult(
                text=result["text"].strip(),
                language=result.get("language", language or "unknown"),
                segments=segments,
                duration=audio_info.get("duration", 0.0),
                model_name=self.model_name,
                metadata={
                    "audio_info": audio_info,
                    "task": task,
                    "word_timestamps": word_timestamps,
                },
            )

            logger.info(
                f"Transcription completed: {len(segments)} segments, "
                f"{transcription_result.word_count} words"
            )

            return transcription_result

        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _parse_segments(self, segments_data: List[Dict]) -> List[TranscriptionSegment]:
        """Parse raw Whisper segments into TranscriptionSegment objects.

        Args:
            segments_data: Raw segment data from Whisper

        Returns:
            List of TranscriptionSegment objects
        """
        segments = []

        for seg_data in segments_data:
            # Parse words if available
            words = []
            if "words" in seg_data:
                for word_data in seg_data["words"]:
                    word = Word(
                        text=word_data.get("word", "").strip(),
                        start=word_data.get("start", 0.0),
                        end=word_data.get("end", 0.0),
                        confidence=word_data.get("probability", 0.0),
                    )
                    words.append(word)

            segment = TranscriptionSegment(
                id=seg_data.get("id", 0),
                start=seg_data.get("start", 0.0),
                end=seg_data.get("end", 0.0),
                text=seg_data.get("text", "").strip(),
                words=words,
                temperature=seg_data.get("temperature", 0.0),
                avg_logprob=seg_data.get("avg_logprob", 0.0),
                compression_ratio=seg_data.get("compression_ratio", 0.0),
                no_speech_prob=seg_data.get("no_speech_prob", 0.0),
            )
            segments.append(segment)

        return segments

    def transcribe_batch(
        self, audio_paths: List[str | Path], **kwargs
    ) -> List[TranscriptionResult]:
        """Transcribe multiple audio files.

        Args:
            audio_paths: List of paths to audio files
            **kwargs: Arguments passed to transcribe()

        Returns:
            List of TranscriptionResult objects
        """
        logger.info(f"Starting batch transcription of {len(audio_paths)} files")

        results = []
        for i, audio_path in enumerate(audio_paths, 1):
            logger.info(f"Processing file {i}/{len(audio_paths)}: {Path(audio_path).name}")
            try:
                result = self.transcribe(audio_path, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_path}: {e}")
                # Continue with next file
                continue

        logger.info(f"Batch transcription completed: {len(results)}/{len(audio_paths)} successful")
        return results

    @staticmethod
    def format_timestamp(seconds: float, srt_format: bool = True) -> str:
        """Convert seconds to timestamp format.

        Args:
            seconds: Time in seconds
            srt_format: Use SRT format (HH:MM:SS,mmm) vs simple format

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        if srt_format:
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def export_srt(self, result: TranscriptionResult, output_path: str | Path) -> Path:
        """Export transcription to SRT subtitle format.

        Args:
            result: TranscriptionResult to export
            output_path: Path for output SRT file

        Returns:
            Path to the created SRT file
        """
        output_path = Path(output_path)

        logger.info(f"Exporting SRT to: {output_path}")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result.segments, 1):
                    # SRT format:
                    # 1
                    # 00:00:00,000 --> 00:00:02,000
                    # Subtitle text
                    #
                    f.write(f"{i}\n")
                    f.write(
                        f"{self.format_timestamp(segment.start)} --> "
                        f"{self.format_timestamp(segment.end)}\n"
                    )
                    f.write(f"{segment.text}\n")
                    f.write("\n")

            logger.info(f"SRT exported successfully: {len(result.segments)} subtitles")
            return output_path

        except Exception as e:
            error_msg = f"Failed to export SRT: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def export_txt(self, result: TranscriptionResult, output_path: str | Path) -> Path:
        """Export transcription to plain text format.

        Args:
            result: TranscriptionResult to export
            output_path: Path for output text file

        Returns:
            Path to the created text file
        """
        output_path = Path(output_path)

        logger.info(f"Exporting text to: {output_path}")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                # Write metadata
                f.write(
                    f"Transcription of: {result.metadata.get('audio_info', {}).get('filename', 'Unknown')}\n"
                )
                f.write(f"Language: {result.language}\n")
                f.write(f"Model: {result.model_name}\n")
                f.write(f"Duration: {result.duration:.2f}s\n")
                f.write(f"Word count: {result.word_count}\n")
                f.write("=" * 80 + "\n\n")

                # Write full text
                f.write(result.text + "\n\n")

                # Write segments with timestamps
                f.write("=" * 80 + "\n")
                f.write("SEGMENTS WITH TIMESTAMPS\n")
                f.write("=" * 80 + "\n\n")

                for segment in result.segments:
                    timestamp = f"[{self.format_timestamp(segment.start, False)} --> {self.format_timestamp(segment.end, False)}]"
                    f.write(f"{timestamp}\n")
                    f.write(f"{segment.text}\n\n")

            logger.info(f"Text exported successfully")
            return output_path

        except Exception as e:
            error_msg = f"Failed to export text: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.

        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "available_models": Config.AVAILABLE_MODELS,
            "supported_languages": len(Config.SUPPORTED_LANGUAGES),
        }

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, "audio_processor"):
            self.audio_processor.cleanup_temp_files()
