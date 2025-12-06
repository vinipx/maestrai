"""Music Transcription Engine for Maestrai using Spotify's Basic Pitch.

Converts audio recordings into MIDI files with pitch, timing, and velocity data.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import numpy as np

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

logger = logging.getLogger(__name__)


@dataclass
class Note:
    """Represents a single musical note."""

    pitch: int  # MIDI pitch (0-127)
    start: float  # Start time in seconds
    end: float  # End time in seconds
    velocity: int  # Note velocity (0-127)
    frequency: float = 0.0  # Frequency in Hz

    @property
    def duration(self) -> float:
        """Get note duration in seconds."""
        return self.end - self.start

    @property
    def note_name(self) -> str:
        """Convert MIDI pitch to note name (e.g., C4, A#3)."""
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (self.pitch // 12) - 1
        note = note_names[self.pitch % 12]
        return f"{note}{octave}"

    def __repr__(self) -> str:
        return (
            f"Note({self.note_name}, start={self.start:.2f}s, "
            f"dur={self.duration:.2f}s, vel={self.velocity})"
        )


@dataclass
class MusicTranscriptionResult:
    """Complete music transcription result with metadata."""

    notes: List[Note]
    duration: float  # Total duration in seconds
    tempo: Optional[float] = None  # Estimated tempo in BPM
    key: Optional[str] = None  # Detected key signature
    time_signature: Optional[str] = None  # Detected time signature
    pitch_range: Tuple[int, int] = (0, 127)  # Min/max MIDI pitch
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate derived properties."""
        if self.notes:
            pitches = [n.pitch for n in self.notes]
            self.pitch_range = (min(pitches), max(pitches))

    @property
    def note_count(self) -> int:
        """Get total number of notes."""
        return len(self.notes)

    @property
    def pitch_range_names(self) -> Tuple[str, str]:
        """Get pitch range as note names."""
        if not self.notes:
            return ("N/A", "N/A")
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        low_oct = (self.pitch_range[0] // 12) - 1
        low_note = note_names[self.pitch_range[0] % 12]
        high_oct = (self.pitch_range[1] // 12) - 1
        high_note = note_names[self.pitch_range[1] % 12]
        return (f"{low_note}{low_oct}", f"{high_note}{high_oct}")

    def __repr__(self) -> str:
        return (
            f"MusicTranscriptionResult(notes={self.note_count}, "
            f"duration={self.duration:.2f}s, "
            f"range={self.pitch_range_names[0]}-{self.pitch_range_names[1]})"
        )


class MusicTranscriptionEngine:
    """Main music transcription engine using Spotify's Basic Pitch.

    Converts audio files into MIDI representations with:
    - Pitch detection (polyphonic)
    - Note timing (onset/offset)
    - Velocity estimation
    - Pitch bend detection
    """

    def __init__(
        self,
        onset_threshold: float = 0.5,
        frame_threshold: float = 0.3,
        minimum_note_length: float = 58,
        minimum_frequency: Optional[float] = None,
        maximum_frequency: Optional[float] = None,
        multiple_pitch_bends: bool = False,
        melodia_trick: bool = True,
    ):
        """Initialize the music transcription engine.

        Args:
            onset_threshold: Threshold for note onset detection (0-1).
                Higher values = fewer but more confident notes.
            frame_threshold: Threshold for frame-level pitch detection (0-1).
                Higher values = cleaner but possibly missing notes.
            minimum_note_length: Minimum note length in milliseconds.
            minimum_frequency: Minimum frequency to detect (Hz). None = no limit.
            maximum_frequency: Maximum frequency to detect (Hz). None = no limit.
            multiple_pitch_bends: Allow multiple simultaneous pitch bends.
            melodia_trick: Use melodia trick for monophonic sources.
        """
        self.onset_threshold = onset_threshold
        self.frame_threshold = frame_threshold
        self.minimum_note_length = minimum_note_length
        self.minimum_frequency = minimum_frequency
        self.maximum_frequency = maximum_frequency
        self.multiple_pitch_bends = multiple_pitch_bends
        self.melodia_trick = melodia_trick

        logger.info("MusicTranscriptionEngine initialized with Basic Pitch")
        logger.info(f"  Onset threshold: {onset_threshold}")
        logger.info(f"  Frame threshold: {frame_threshold}")
        logger.info(f"  Minimum note length: {minimum_note_length}ms")

    def transcribe(
        self,
        audio_path: str | Path,
        save_midi: bool = False,
        midi_path: Optional[str | Path] = None,
    ) -> MusicTranscriptionResult:
        """Transcribe audio file to musical notes.

        Args:
            audio_path: Path to audio file (MP3, WAV, FLAC, etc.)
            save_midi: Whether to save MIDI file
            midi_path: Custom path for MIDI output (optional)

        Returns:
            MusicTranscriptionResult with detected notes and metadata

        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing music from: {audio_path.name}")

        try:
            # Run Basic Pitch inference
            model_output, midi_data, note_events = predict(
                str(audio_path),
                onset_threshold=self.onset_threshold,
                frame_threshold=self.frame_threshold,
                minimum_note_length=self.minimum_note_length,
                minimum_frequency=self.minimum_frequency,
                maximum_frequency=self.maximum_frequency,
                multiple_pitch_bends=self.multiple_pitch_bends,
                melodia_trick=self.melodia_trick,
            )

            # Parse note events into Note objects
            notes = self._parse_notes(note_events)

            # Get duration from MIDI data
            duration = midi_data.get_end_time() if midi_data else 0.0

            # Create result
            result = MusicTranscriptionResult(
                notes=notes,
                duration=duration,
                metadata={
                    "source_file": str(audio_path),
                    "onset_threshold": self.onset_threshold,
                    "frame_threshold": self.frame_threshold,
                },
            )

            logger.info(
                f"Transcription completed: {result.note_count} notes, "
                f"duration={result.duration:.2f}s"
            )

            # Save MIDI if requested
            if save_midi:
                if midi_path is None:
                    midi_path = audio_path.with_suffix(".mid")
                self.export_midi(midi_data, midi_path)

            # Store midi_data for later export
            result.metadata["midi_data"] = midi_data

            return result

        except Exception as e:
            error_msg = f"Music transcription failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _parse_notes(self, note_events: List) -> List[Note]:
        """Parse Basic Pitch note events into Note objects.

        Args:
            note_events: List of note events from Basic Pitch

        Returns:
            List of Note objects
        """
        notes = []

        for event in note_events:
            start_time, end_time, pitch, velocity, pitch_bend = event

            # Convert velocity to 0-127 range
            velocity_int = int(min(127, max(0, velocity * 127)))

            # Calculate frequency from MIDI pitch
            frequency = 440.0 * (2 ** ((pitch - 69) / 12))

            note = Note(
                pitch=int(pitch),
                start=float(start_time),
                end=float(end_time),
                velocity=velocity_int,
                frequency=frequency,
            )
            notes.append(note)

        # Sort by start time
        notes.sort(key=lambda n: n.start)

        return notes

    def export_midi(
        self,
        midi_data_or_result: Any,
        output_path: str | Path,
    ) -> Path:
        """Export transcription to MIDI file.

        Args:
            midi_data_or_result: PrettyMIDI object or MusicTranscriptionResult
            output_path: Path for output MIDI file

        Returns:
            Path to created MIDI file
        """
        output_path = Path(output_path)

        # Handle both PrettyMIDI and MusicTranscriptionResult
        if hasattr(midi_data_or_result, "metadata"):
            midi_data = midi_data_or_result.metadata.get("midi_data")
            if midi_data is None:
                raise ValueError("No MIDI data available in result")
        else:
            midi_data = midi_data_or_result

        logger.info(f"Exporting MIDI to: {output_path}")

        try:
            midi_data.write(str(output_path))
            logger.info(f"MIDI exported successfully")
            return output_path
        except Exception as e:
            error_msg = f"Failed to export MIDI: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def transcribe_batch(
        self,
        audio_paths: List[str | Path],
        save_midi: bool = False,
        output_dir: Optional[str | Path] = None,
    ) -> List[MusicTranscriptionResult]:
        """Transcribe multiple audio files.

        Args:
            audio_paths: List of paths to audio files
            save_midi: Whether to save MIDI files
            output_dir: Directory for MIDI outputs

        Returns:
            List of MusicTranscriptionResult objects
        """
        logger.info(f"Starting batch transcription of {len(audio_paths)} files")

        results = []
        for i, audio_path in enumerate(audio_paths, 1):
            audio_path = Path(audio_path)
            logger.info(f"Processing file {i}/{len(audio_paths)}: {audio_path.name}")

            try:
                midi_path = None
                if save_midi and output_dir:
                    midi_path = Path(output_dir) / f"{audio_path.stem}.mid"

                result = self.transcribe(
                    audio_path,
                    save_midi=save_midi,
                    midi_path=midi_path,
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to transcribe {audio_path}: {e}")
                continue

        logger.info(f"Batch transcription completed: {len(results)}/{len(audio_paths)} successful")
        return results

    def get_statistics(self, result: MusicTranscriptionResult) -> Dict[str, Any]:
        """Get detailed statistics about a transcription.

        Args:
            result: MusicTranscriptionResult to analyze

        Returns:
            Dictionary with transcription statistics
        """
        if not result.notes:
            return {
                "note_count": 0,
                "duration": result.duration,
                "notes_per_second": 0,
                "pitch_range": (0, 0),
                "average_velocity": 0,
                "average_note_duration": 0,
            }

        velocities = [n.velocity for n in result.notes]
        durations = [n.duration for n in result.notes]

        return {
            "note_count": result.note_count,
            "duration": result.duration,
            "notes_per_second": result.note_count / result.duration if result.duration > 0 else 0,
            "pitch_range": result.pitch_range,
            "pitch_range_names": result.pitch_range_names,
            "average_velocity": sum(velocities) / len(velocities),
            "average_note_duration": sum(durations) / len(durations),
            "min_note_duration": min(durations),
            "max_note_duration": max(durations),
            "tempo": result.tempo,
            "key": result.key,
        }
