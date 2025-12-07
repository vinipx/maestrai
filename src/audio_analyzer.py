"""Advanced Audio Analysis Module for Maestrai.

Uses madmom library for state-of-the-art music information retrieval:
- Neural network-based beat/downbeat tracking
- Deep learning tempo estimation
- CNN-based key detection
- Deep chroma chord recognition
- RNN onset detection

References:
- https://github.com/CPJKU/madmom
- Böck et al., "madmom: A New Python Audio and Music Signal Processing Library"
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import numpy as np

# Madmom imports for advanced music analysis
import madmom
from madmom.features.beats import DBNBeatTrackingProcessor, RNNBeatProcessor
from madmom.features.tempo import TempoEstimationProcessor
from madmom.features.downbeats import DBNDownBeatTrackingProcessor, RNNDownBeatProcessor
from madmom.features.chords import DeepChromaChordRecognitionProcessor
from madmom.audio.chroma import DeepChromaProcessor
from madmom.features.key import CNNKeyRecognitionProcessor
from madmom.features.onsets import RNNOnsetProcessor, OnsetPeakPickingProcessor
from madmom.processors import SequentialProcessor

logger = logging.getLogger(__name__)


@dataclass
class Chord:
    """Represents a detected chord."""

    start: float  # Start time in seconds
    end: float  # End time in seconds
    label: str  # Chord label (e.g., "C:maj", "Am", "G:min")

    @property
    def duration(self) -> float:
        return self.end - self.start

    def __repr__(self) -> str:
        return f"Chord({self.label}, {self.start:.2f}s-{self.end:.2f}s)"


@dataclass
class Downbeat:
    """Represents a detected downbeat (first beat of a measure)."""

    time: float  # Time in seconds
    beat_position: int  # Position within measure (1 = downbeat)

    def __repr__(self) -> str:
        return f"Downbeat({self.time:.2f}s, pos={self.beat_position})"


@dataclass
class AudioAnalysis:
    """Complete audio analysis result with advanced features."""

    # Basic info
    duration: float  # Duration in seconds
    sample_rate: int  # Sample rate in Hz

    # Tempo and rhythm
    tempo: float  # Primary tempo in BPM
    tempo_strengths: List[Tuple[float, float]] = field(
        default_factory=list
    )  # (tempo, strength) pairs
    beats: List[float] = field(default_factory=list)  # Beat times in seconds
    downbeats: List[Downbeat] = field(default_factory=list)  # Downbeat positions
    time_signature: str = "4/4"  # Estimated time signature

    # Harmony
    key: str = "Unknown"  # Detected key (e.g., "C major", "A minor")
    key_confidence: float = 0.0  # Confidence of key detection
    chords: List[Chord] = field(default_factory=list)  # Chord progression

    # Note events
    onsets: List[float] = field(default_factory=list)  # Onset times in seconds

    # Spectral features
    spectral_centroid: Optional[float] = None  # Average spectral centroid
    rms_energy: Optional[float] = None  # Average RMS energy

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"AudioAnalysis(tempo={self.tempo:.1f} BPM, key={self.key}, "
            f"time_sig={self.time_signature}, duration={self.duration:.2f}s, "
            f"beats={len(self.beats)}, chords={len(self.chords)})"
        )

    def get_chord_at(self, time: float) -> Optional[Chord]:
        """Get the chord playing at a specific time."""
        for chord in self.chords:
            if chord.start <= time < chord.end:
                return chord
        return None

    def get_measures(self) -> List[List[float]]:
        """Group beats into measures based on downbeats."""
        if not self.downbeats or not self.beats:
            return []

        measures = []
        downbeat_times = [d.time for d in self.downbeats]

        for i, db_time in enumerate(downbeat_times):
            next_db = downbeat_times[i + 1] if i + 1 < len(downbeat_times) else None
            measure_beats = [
                b for b in self.beats if b >= db_time and (next_db is None or b < next_db)
            ]
            if measure_beats:
                measures.append(measure_beats)

        return measures


class AudioAnalyzer:
    """Advanced audio analysis engine using madmom.

    Provides state-of-the-art music information retrieval using deep learning:
    - DBN beat tracking with RNN activation
    - DBN downbeat tracking for measure detection
    - CNN-based key recognition
    - Deep chroma chord recognition
    - RNN onset detection
    - Multi-tempo estimation

    References:
        - Böck et al., "Joint Beat and Downbeat Tracking with RNNs" (ISMIR 2016)
        - Korzeniowski & Widmer, "Feature Learning for Chord Recognition" (ISMIR 2016)
        - Korzeniowski & Widmer, "Genre-Agnostic Key Classification with CNNs" (ISMIR 2017)
    """

    def __init__(
        self,
        fps: int = 100,  # Frames per second for processing
        beats_per_bar: List[int] = None,  # Allowed beats per bar for downbeat tracking
    ):
        """Initialize the audio analyzer.

        Args:
            fps: Frames per second for audio processing
            beats_per_bar: Allowed beats per bar (default: [3, 4] for 3/4 and 4/4)
        """
        self.fps = fps
        self.beats_per_bar = beats_per_bar or [3, 4]

        logger.info(f"AudioAnalyzer initialized with madmom (fps={fps})")
        logger.info(f"  madmom version: {madmom.__version__}")

        # Initialize processors (lazy loading for performance)
        self._beat_processor = None
        self._downbeat_processor = None
        self._tempo_processor = None
        self._key_processor = None
        self._chord_processor = None
        self._onset_processor = None

    def _get_beat_processor(self):
        """Get or create beat tracking processor."""
        if self._beat_processor is None:
            logger.debug("Initializing beat tracking processor...")
            self._beat_processor = SequentialProcessor([
                RNNBeatProcessor(),
                DBNBeatTrackingProcessor(fps=self.fps),
            ])
        return self._beat_processor

    def _get_downbeat_processor(self):
        """Get or create downbeat tracking processor."""
        if self._downbeat_processor is None:
            logger.debug("Initializing downbeat tracking processor...")
            self._downbeat_processor = SequentialProcessor([
                RNNDownBeatProcessor(),
                DBNDownBeatTrackingProcessor(
                    beats_per_bar=self.beats_per_bar, fps=self.fps
                ),
            ])
        return self._downbeat_processor

    def _get_tempo_processor(self):
        """Get or create tempo estimation processor."""
        if self._tempo_processor is None:
            logger.debug("Initializing tempo estimation processor...")
            self._tempo_processor = TempoEstimationProcessor(fps=self.fps)
        return self._tempo_processor

    def _get_key_processor(self):
        """Get or create key recognition processor."""
        if self._key_processor is None:
            logger.debug("Initializing key recognition processor...")
            self._key_processor = CNNKeyRecognitionProcessor()
        return self._key_processor

    def _get_chord_processor(self):
        """Get or create chord recognition processor."""
        if self._chord_processor is None:
            logger.debug("Initializing chord recognition processor...")
            self._chord_processor = SequentialProcessor([
                DeepChromaProcessor(),
                DeepChromaChordRecognitionProcessor(),
            ])
        return self._chord_processor

    def _get_onset_processor(self):
        """Get or create onset detection processor."""
        if self._onset_processor is None:
            logger.debug("Initializing onset detection processor...")
            self._onset_processor = SequentialProcessor([
                RNNOnsetProcessor(),
                OnsetPeakPickingProcessor(fps=self.fps),
            ])
        return self._onset_processor

    def analyze(self, audio_path: str | Path) -> AudioAnalysis:
        """Perform comprehensive audio analysis using madmom.

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
        audio_str = str(audio_path)

        try:
            # Get duration using madmom's signal module
            from madmom.audio.signal import Signal

            signal = Signal(audio_str, sample_rate=44100, num_channels=1)
            duration = len(signal) / signal.sample_rate
            sample_rate = signal.sample_rate

            logger.info(f"Loaded audio: {duration:.2f}s at {sample_rate}Hz")

            # Detect beats
            beats = self._detect_beats(audio_str)
            logger.info(f"Detected {len(beats)} beats")

            # Detect downbeats and time signature
            downbeats, time_signature = self._detect_downbeats(audio_str)
            logger.info(
                f"Detected {len(downbeats)} downbeats, time signature: {time_signature}"
            )

            # Estimate tempo
            tempo, tempo_strengths = self._estimate_tempo(audio_str)
            logger.info(f"Estimated tempo: {tempo:.1f} BPM")

            # Detect key
            key, key_confidence = self._detect_key(audio_str)
            logger.info(f"Detected key: {key} (confidence: {key_confidence:.2f})")

            # Detect chords
            chords = self._detect_chords(audio_str)
            logger.info(f"Detected {len(chords)} chord changes")

            # Detect onsets
            onsets = self._detect_onsets(audio_str)
            logger.info(f"Detected {len(onsets)} onsets")

            result = AudioAnalysis(
                duration=duration,
                sample_rate=sample_rate,
                tempo=tempo,
                tempo_strengths=tempo_strengths,
                beats=beats,
                downbeats=downbeats,
                time_signature=time_signature,
                key=key,
                key_confidence=key_confidence,
                chords=chords,
                onsets=onsets,
                metadata={
                    "source_file": str(audio_path),
                    "analyzer": "madmom",
                    "madmom_version": madmom.__version__,
                    "fps": self.fps,
                },
            )

            logger.info(f"Analysis complete: {result}")
            return result

        except Exception as e:
            error_msg = f"Audio analysis failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _detect_beats(self, audio_path: str) -> List[float]:
        """Detect beat positions using DBN beat tracker.

        Args:
            audio_path: Path to audio file

        Returns:
            List of beat times in seconds
        """
        processor = self._get_beat_processor()
        beats = processor(audio_path)
        return beats.tolist()

    def _detect_downbeats(
        self, audio_path: str
    ) -> Tuple[List[Downbeat], str]:
        """Detect downbeats and estimate time signature.

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (list of Downbeats, time signature string)
        """
        processor = self._get_downbeat_processor()
        result = processor(audio_path)

        downbeats = []
        beat_counts = []

        for time, beat_pos in result:
            downbeats.append(Downbeat(time=float(time), beat_position=int(beat_pos)))
            if int(beat_pos) == 1:
                beat_counts.append(1)
            elif beat_counts:
                beat_counts[-1] += 1

        # Estimate time signature from most common beat count
        if beat_counts:
            from collections import Counter

            most_common = Counter(beat_counts).most_common(1)[0][0]
            time_signature = f"{most_common}/4"
        else:
            time_signature = "4/4"

        return downbeats, time_signature

    def _estimate_tempo(self, audio_path: str) -> Tuple[float, List[Tuple[float, float]]]:
        """Estimate tempo using multi-tempo estimation.

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (primary tempo, list of (tempo, strength) pairs)
        """
        # Use RNN beat processor for tempo estimation
        act_processor = RNNBeatProcessor()
        activations = act_processor(audio_path)

        tempo_processor = self._get_tempo_processor()
        tempos = tempo_processor(activations)

        if len(tempos) > 0:
            # tempos is array of (tempo, strength) pairs
            tempo_strengths = [(float(t), float(s)) for t, s in tempos]
            primary_tempo = tempo_strengths[0][0]
        else:
            primary_tempo = 120.0
            tempo_strengths = [(120.0, 1.0)]

        return primary_tempo, tempo_strengths

    def _detect_key(self, audio_path: str) -> Tuple[str, float]:
        """Detect musical key using CNN-based recognition.

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (key string, confidence)
        """
        processor = self._get_key_processor()
        result = processor(audio_path)

        # CNNKeyRecognitionProcessor returns array of 24 probabilities:
        # 12 major keys (C, C#, D, ..., B) followed by 12 minor keys
        key_labels = [
            "C major", "C# major", "D major", "D# major", "E major", "F major",
            "F# major", "G major", "G# major", "A major", "A# major", "B major",
            "C minor", "C# minor", "D minor", "D# minor", "E minor", "F minor",
            "F# minor", "G minor", "G# minor", "A minor", "A# minor", "B minor",
        ]

        if isinstance(result, np.ndarray):
            # Flatten if needed and get the best key
            probs = result.flatten()
            if len(probs) >= 24:
                best_idx = int(np.argmax(probs[:24]))
                confidence = float(probs[best_idx])
                key_label = key_labels[best_idx]
            else:
                # Fallback
                key_label = "C major"
                confidence = 0.0
        elif isinstance(result, tuple):
            key_label, confidence = result
            key_label = self._format_key(str(key_label))
        else:
            key_label = self._format_key(str(result))
            confidence = 1.0

        return key_label, confidence

    def _format_key(self, key_label: str) -> str:
        """Format key label to readable string.

        Args:
            key_label: Raw key label from madmom

        Returns:
            Formatted key string (e.g., "C major", "A minor")
        """
        # Handle various formats from madmom
        key_label = str(key_label).strip()

        # Already formatted
        if " major" in key_label or " minor" in key_label:
            return key_label

        # Format like "C" or "Cm" or "C:maj" or "C:min"
        if ":maj" in key_label:
            return key_label.replace(":maj", " major")
        elif ":min" in key_label:
            return key_label.replace(":min", " minor")
        elif key_label.endswith("m"):
            return f"{key_label[:-1]} minor"
        else:
            return f"{key_label} major"

    def _detect_chords(self, audio_path: str) -> List[Chord]:
        """Detect chord progression using deep chroma.

        Args:
            audio_path: Path to audio file

        Returns:
            List of Chord objects
        """
        processor = self._get_chord_processor()
        result = processor(audio_path)

        chords = []
        for start, end, label in result:
            chords.append(
                Chord(start=float(start), end=float(end), label=str(label))
            )

        return chords

    def _detect_onsets(self, audio_path: str) -> List[float]:
        """Detect note onsets using RNN.

        Args:
            audio_path: Path to audio file

        Returns:
            List of onset times in seconds
        """
        processor = self._get_onset_processor()
        onsets = processor(audio_path)
        return onsets.tolist()

    # Convenience methods for quick analysis

    def get_tempo(self, audio_path: str | Path) -> float:
        """Quick tempo detection.

        Args:
            audio_path: Path to audio file

        Returns:
            Tempo in BPM
        """
        tempo, _ = self._estimate_tempo(str(audio_path))
        return tempo

    def get_key(self, audio_path: str | Path) -> str:
        """Quick key detection.

        Args:
            audio_path: Path to audio file

        Returns:
            Key signature string
        """
        key, _ = self._detect_key(str(audio_path))
        return key

    def get_beats(self, audio_path: str | Path) -> List[float]:
        """Quick beat detection.

        Args:
            audio_path: Path to audio file

        Returns:
            List of beat times in seconds
        """
        return self._detect_beats(str(audio_path))

    def get_chords(self, audio_path: str | Path) -> List[Chord]:
        """Quick chord detection.

        Args:
            audio_path: Path to audio file

        Returns:
            List of Chord objects
        """
        return self._detect_chords(str(audio_path))

    def get_downbeats(self, audio_path: str | Path) -> List[float]:
        """Quick downbeat detection.

        Args:
            audio_path: Path to audio file

        Returns:
            List of downbeat times in seconds
        """
        downbeats, _ = self._detect_downbeats(str(audio_path))
        return [d.time for d in downbeats if d.beat_position == 1]
