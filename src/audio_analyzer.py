"""Audio Analysis Module for Maestrai.

Provides audio analysis features including:
- Tempo/BPM detection
- Key signature detection
- Beat tracking
- Onset detection
- Spectral analysis
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import numpy as np

import librosa

logger = logging.getLogger(__name__)


@dataclass
class AudioAnalysis:
    """Complete audio analysis result."""

    tempo: float  # Estimated tempo in BPM
    key: str  # Detected key (e.g., "C major", "A minor")
    time_signature: str  # Estimated time signature (e.g., "4/4")
    duration: float  # Duration in seconds
    sample_rate: int  # Sample rate in Hz
    beats: List[float] = field(default_factory=list)  # Beat times in seconds
    onsets: List[float] = field(default_factory=list)  # Onset times in seconds
    chroma: Optional[np.ndarray] = None  # Chromagram
    spectral_centroid: Optional[float] = None  # Average spectral centroid
    rms_energy: Optional[float] = None  # Average RMS energy
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"AudioAnalysis(tempo={self.tempo:.1f} BPM, key={self.key}, "
            f"time_sig={self.time_signature}, duration={self.duration:.2f}s)"
        )


class AudioAnalyzer:
    """Audio analysis engine using librosa.

    Provides comprehensive audio analysis for music files including:
    - Tempo estimation
    - Key detection
    - Beat tracking
    - Onset detection
    - Spectral analysis
    """

    # Key names for chroma analysis
    KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # Major and minor key profiles (Krumhansl-Schmuckler)
    MAJOR_PROFILE = np.array(
        [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    )
    MINOR_PROFILE = np.array(
        [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    )

    def __init__(
        self,
        sample_rate: int = 22050,
        hop_length: int = 512,
    ):
        """Initialize the audio analyzer.

        Args:
            sample_rate: Target sample rate for analysis
            hop_length: Hop length for spectral analysis
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length

        logger.info(f"AudioAnalyzer initialized (sr={sample_rate}, hop={hop_length})")

    def analyze(self, audio_path: str | Path) -> AudioAnalysis:
        """Perform comprehensive audio analysis.

        Args:
            audio_path: Path to audio file

        Returns:
            AudioAnalysis with all detected features

        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If analysis fails
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Analyzing audio: {audio_path.name}")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=self.sample_rate, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)

            logger.info(f"Loaded audio: {duration:.2f}s at {sr}Hz")

            # Perform analyses
            tempo, beats = self._detect_tempo_and_beats(y, sr)
            key = self._detect_key(y, sr)
            time_signature = self._estimate_time_signature(tempo, beats)
            onsets = self._detect_onsets(y, sr)
            spectral_centroid = self._compute_spectral_centroid(y, sr)
            rms_energy = self._compute_rms_energy(y)

            result = AudioAnalysis(
                tempo=tempo,
                key=key,
                time_signature=time_signature,
                duration=duration,
                sample_rate=sr,
                beats=beats.tolist() if isinstance(beats, np.ndarray) else beats,
                onsets=onsets.tolist() if isinstance(onsets, np.ndarray) else onsets,
                spectral_centroid=spectral_centroid,
                rms_energy=rms_energy,
                metadata={
                    "source_file": str(audio_path),
                    "hop_length": self.hop_length,
                },
            )

            logger.info(f"Analysis complete: {result}")
            return result

        except Exception as e:
            error_msg = f"Audio analysis failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _detect_tempo_and_beats(self, y: np.ndarray, sr: int) -> Tuple[float, np.ndarray]:
        """Detect tempo and beat positions.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Tuple of (tempo in BPM, beat times in seconds)
        """
        logger.debug("Detecting tempo and beats...")

        # Get tempo and beat frames
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)

        # Convert frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)

        # Handle tempo as array (newer librosa versions)
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if len(tempo) > 0 else 120.0

        logger.info(f"Detected tempo: {tempo:.1f} BPM, {len(beat_times)} beats")

        return float(tempo), beat_times

    def _detect_key(self, y: np.ndarray, sr: int) -> str:
        """Detect musical key using chromagram analysis.

        Uses Krumhansl-Schmuckler key-finding algorithm.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Key signature string (e.g., "C major", "A minor")
        """
        logger.debug("Detecting key signature...")

        # Compute chromagram
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)

        # Get mean chroma vector
        chroma_mean = np.mean(chroma, axis=1)

        # Correlate with key profiles
        best_key = None
        best_correlation = -1

        for i in range(12):
            # Rotate profiles to match each key
            major_rotated = np.roll(self.MAJOR_PROFILE, i)
            minor_rotated = np.roll(self.MINOR_PROFILE, i)

            # Calculate correlation
            major_corr = np.corrcoef(chroma_mean, major_rotated)[0, 1]
            minor_corr = np.corrcoef(chroma_mean, minor_rotated)[0, 1]

            if major_corr > best_correlation:
                best_correlation = major_corr
                best_key = f"{self.KEY_NAMES[i]} major"

            if minor_corr > best_correlation:
                best_correlation = minor_corr
                best_key = f"{self.KEY_NAMES[i]} minor"

        logger.info(f"Detected key: {best_key} (correlation: {best_correlation:.3f})")

        return best_key or "Unknown"

    def _estimate_time_signature(self, tempo: float, beats: np.ndarray) -> str:
        """Estimate time signature from tempo and beat pattern.

        This is a simplified estimation based on tempo ranges.

        Args:
            tempo: Detected tempo in BPM
            beats: Beat times in seconds

        Returns:
            Time signature string (e.g., "4/4", "3/4")
        """
        logger.debug("Estimating time signature...")

        # Simple heuristic based on tempo
        # Most music is 4/4, but we can make educated guesses
        if 60 <= tempo <= 80:
            # Could be 3/4 waltz tempo
            return "3/4"
        elif 100 <= tempo <= 140:
            return "4/4"
        elif 140 <= tempo <= 180:
            # Could be 4/4 or 2/4
            return "4/4"
        else:
            return "4/4"  # Default to 4/4

    def _detect_onsets(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Detect note onsets in audio.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Array of onset times in seconds
        """
        logger.debug("Detecting onsets...")

        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=self.hop_length)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)

        logger.info(f"Detected {len(onset_times)} onsets")

        return onset_times

    def _compute_spectral_centroid(self, y: np.ndarray, sr: int) -> float:
        """Compute average spectral centroid (brightness indicator).

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Average spectral centroid in Hz
        """
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)
        return float(np.mean(centroid))

    def _compute_rms_energy(self, y: np.ndarray) -> float:
        """Compute average RMS energy (loudness indicator).

        Args:
            y: Audio time series

        Returns:
            Average RMS energy
        """
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)
        return float(np.mean(rms))

    def get_tempo(self, audio_path: str | Path) -> float:
        """Quick tempo detection.

        Args:
            audio_path: Path to audio file

        Returns:
            Tempo in BPM
        """
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate, mono=True)
        tempo, _ = self._detect_tempo_and_beats(y, sr)
        return tempo

    def get_key(self, audio_path: str | Path) -> str:
        """Quick key detection.

        Args:
            audio_path: Path to audio file

        Returns:
            Key signature string
        """
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate, mono=True)
        return self._detect_key(y, sr)

    def get_beat_times(self, audio_path: str | Path) -> List[float]:
        """Get beat times for an audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            List of beat times in seconds
        """
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate, mono=True)
        _, beat_times = self._detect_tempo_and_beats(y, sr)
        return beat_times.tolist()
