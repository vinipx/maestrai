"""Audio processing utilities for Maestrai."""

import hashlib
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import json
import ffmpeg

from .utils.config import Config

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio file validation, conversion, and processing using FFmpeg."""

    def __init__(self):
        """Initialize the AudioProcessor."""
        Config.ensure_temp_dir()
        self._temp_files: list[Path] = []
        self._check_ffmpeg()

    def _check_ffmpeg(self) -> None:
        """Check if FFmpeg is installed and available.

        Raises:
            RuntimeError: If FFmpeg is not installed
        """
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            logger.info("FFmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            error_msg = (
                "FFmpeg is not installed or not in PATH. "
                "Please install FFmpeg to use this service. "
                "Visit https://ffmpeg.org/download.html for installation instructions."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def validate_audio_file(self, file_path: str | Path) -> tuple[bool, Optional[str]]:
        """Validate an audio file for format, size, and integrity.

        Args:
            file_path: Path to the audio file

        Returns:
            Tuple of (is_valid, error_message)
        """
        file_path = Path(file_path)

        # Check if file exists
        if not file_path.exists():
            return False, f"File not found: {file_path}"

        # Check if it's a file
        if not file_path.is_file():
            return False, f"Not a file: {file_path}"

        # Check file extension
        supported_formats = Config.get_supported_formats()
        if file_path.suffix.lower() not in supported_formats:
            return False, (
                f"Unsupported format: {file_path.suffix}. "
                f"Supported formats: {', '.join(supported_formats)}"
            )

        # Check file size
        file_size = file_path.stat().st_size
        if file_size == 0:
            return False, "File is empty"

        if file_size > Config.MAX_FILE_SIZE:
            return False, (
                f"File too large: {file_size / (1024**2):.2f} MB. "
                f"Max size: {Config.MAX_FILE_SIZE_MB} MB"
            )

        # Verify file integrity with ffprobe
        try:
            self.get_audio_info(file_path)
        except Exception as e:
            return False, f"File integrity check failed: {str(e)}"

        return True, None

    def get_audio_info(self, file_path: str | Path) -> Dict[str, Any]:
        """Get audio file metadata using ffprobe.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary containing audio metadata

        Raises:
            RuntimeError: If ffprobe fails to read the file
        """
        file_path = Path(file_path)

        try:
            probe = ffmpeg.probe(str(file_path))

            # Extract audio stream information
            audio_streams = [
                stream for stream in probe["streams"] if stream["codec_type"] == "audio"
            ]

            if not audio_streams:
                raise RuntimeError("No audio stream found in file")

            audio_info = audio_streams[0]

            metadata = {
                "filename": file_path.name,
                "format": probe["format"]["format_name"],
                "duration": float(probe["format"].get("duration", 0)),
                "size": int(probe["format"].get("size", 0)),
                "bit_rate": int(probe["format"].get("bit_rate", 0)),
                "codec": audio_info.get("codec_name", "unknown"),
                "sample_rate": int(audio_info.get("sample_rate", 0)),
                "channels": int(audio_info.get("channels", 0)),
            }

            logger.info(f"Audio info for {file_path.name}: {metadata}")
            return metadata

        except ffmpeg.Error as e:
            error_msg = f"FFprobe error: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to get audio info: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file for caching purposes.

        Args:
            file_path: Path to the file

        Returns:
            MD5 hash string
        """
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def convert_to_wav(
        self,
        input_path: str | Path,
        sample_rate: int = Config.SAMPLE_RATE,
        channels: int = Config.CHANNELS,
    ) -> Path:
        """Convert audio file to WAV format optimized for Whisper.

        Args:
            input_path: Path to input audio file
            sample_rate: Target sample rate (default: 16000 Hz for Whisper)
            channels: Number of audio channels (default: 1 for mono)

        Returns:
            Path to the converted WAV file

        Raises:
            RuntimeError: If conversion fails
        """
        input_path = Path(input_path)

        # Generate cache-friendly output filename using hash
        file_hash = self._get_file_hash(input_path)
        output_filename = f"{file_hash}_{sample_rate}hz_{channels}ch.wav"
        output_path = Config.TEMP_DIR / output_filename

        # Check if cached version exists
        if output_path.exists():
            logger.info(f"Using cached WAV file: {output_path}")
            return output_path

        logger.info(f"Converting {input_path.name} to WAV format...")

        try:
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec="pcm_s16le",
                ar=sample_rate,
                ac=channels,
            )
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            self._temp_files.append(output_path)
            logger.info(f"Converted to: {output_path}")
            return output_path

        except ffmpeg.Error as e:
            error_msg = f"FFmpeg conversion error: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Audio conversion failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def extract_audio_from_video(
        self,
        video_path: str | Path,
        sample_rate: int = Config.SAMPLE_RATE,
        channels: int = Config.CHANNELS,
    ) -> Path:
        """Extract audio from video file and convert to WAV.

        Args:
            video_path: Path to video file
            sample_rate: Target sample rate (default: 16000 Hz)
            channels: Number of audio channels (default: 1 for mono)

        Returns:
            Path to the extracted WAV file

        Raises:
            RuntimeError: If extraction fails
        """
        video_path = Path(video_path)

        # Validate video format
        if video_path.suffix.lower() not in Config.SUPPORTED_VIDEO_FORMATS:
            raise ValueError(
                f"Unsupported video format: {video_path.suffix}. "
                f"Supported formats: {', '.join(Config.SUPPORTED_VIDEO_FORMATS)}"
            )

        logger.info(f"Extracting audio from video: {video_path.name}")

        # Use the same conversion logic, ffmpeg handles both audio and video
        return self.convert_to_wav(video_path, sample_rate, channels)

    def trim_audio(
        self,
        input_path: str | Path,
        output_path: str | Path,
        start_time: float,
        end_time: float,
    ) -> Path:
        """Trim audio file to a specific time range.

        Args:
            input_path: Path to input audio file
            output_path: Path for output trimmed file
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            Path to the trimmed audio file

        Raises:
            RuntimeError: If trimming fails
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if start_time < 0:
            raise ValueError("Start time cannot be negative")

        if end_time <= start_time:
            raise ValueError("End time must be greater than start time")

        logger.info(f"Trimming {input_path.name} from {start_time}s to {end_time}s")

        try:
            duration = end_time - start_time
            stream = ffmpeg.input(str(input_path), ss=start_time, t=duration)
            stream = ffmpeg.output(stream, str(output_path), acodec="copy")
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            logger.info(f"Trimmed audio saved to: {output_path}")
            return output_path

        except ffmpeg.Error as e:
            error_msg = f"FFmpeg trim error: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Audio trimming failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def cleanup_temp_files(self) -> None:
        """Clean up temporary files created during processing."""
        logger.info(f"Cleaning up {len(self._temp_files)} temporary files...")

        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Deleted: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to delete {temp_file}: {e}")

        self._temp_files.clear()
        logger.info("Cleanup completed")

    def __del__(self):
        """Destructor to ensure temp files are cleaned up."""
        if hasattr(self, "_temp_files") and self._temp_files:
            self.cleanup_temp_files()
