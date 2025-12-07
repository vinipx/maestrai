"""Score Generator Module for Maestrai.

Converts MIDI/transcription data into sheet music formats:
- MusicXML
- PDF (via external tools)
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import tempfile
import subprocess
import shutil

from collections import defaultdict

from music21 import converter, stream, note, chord, meter, key, tempo, clef
from music21 import harmony, metadata
from music21 import environment as m21env
import pretty_midi

from .music_transcription_engine import MusicTranscriptionResult, Note
from .audio_analyzer import Chord as AnalysisChord

logger = logging.getLogger(__name__)


class ScoreGenerator:
    """Generate sheet music from MIDI or transcription data.

    Supports output formats:
    - MusicXML (.musicxml, .xml)
    - PDF (requires MuseScore or LilyPond)
    - MIDI (re-export)
    """

    def __init__(
        self,
        quantize: bool = True,
        quantize_resolution: float = 0.125,  # 1/8th note
        default_time_signature: str = "4/4",
        default_key: str = "C major",
    ):
        """Initialize the score generator.

        Args:
            quantize: Whether to quantize note timings
            quantize_resolution: Quantization grid in quarter notes
            default_time_signature: Default time signature if not detected
            default_key: Default key signature if not detected
        """
        self.quantize = quantize
        self.quantize_resolution = quantize_resolution
        self.default_time_signature = default_time_signature
        self.default_key = default_key

        # Check for PDF rendering tools
        self._check_pdf_tools()

        logger.info(
            f"ScoreGenerator initialized (quantize={quantize}, "
            f"resolution={quantize_resolution})"
        )

    def _check_pdf_tools(self):
        """Check for available PDF rendering tools."""
        self.musescore_path = None
        self.lilypond_path = None

        # Check for MuseScore
        for path in [
            "/Applications/MuseScore 4.app/Contents/MacOS/mscore",
            "/Applications/MuseScore 3.app/Contents/MacOS/mscore",
            "/usr/bin/mscore",
            "/usr/local/bin/mscore",
            shutil.which("mscore"),
            shutil.which("musescore"),
        ]:
            if path and Path(str(path)).exists():
                self.musescore_path = path
                logger.info(f"Found MuseScore at: {path}")
                break

        # Check for LilyPond
        lilypond = shutil.which("lilypond")
        if lilypond:
            self.lilypond_path = lilypond
            logger.info(f"Found LilyPond at: {lilypond}")

        if not self.musescore_path and not self.lilypond_path:
            logger.warning(
                "No PDF rendering tools found. " "Install MuseScore or LilyPond for PDF export."
            )

    def from_transcription(
        self,
        result: MusicTranscriptionResult,
        tempo_bpm: Optional[float] = None,
        key_signature: Optional[str] = None,
        time_signature: Optional[str] = None,
        chords: Optional[List[AnalysisChord]] = None,
        title: Optional[str] = None,
        composer: Optional[str] = None,
    ) -> stream.Score:
        """Create a music21 Score from transcription result.

        Args:
            result: MusicTranscriptionResult from transcription engine
            tempo_bpm: Override tempo (BPM)
            key_signature: Override key signature
            time_signature: Override time signature
            chords: List of detected chords to add as chord symbols
            title: Title of the piece for the sheet music header
            composer: Composer/author name for the sheet music header

        Returns:
            music21 Score object
        """
        logger.info(f"Creating score from {result.note_count} notes")

        # Create score
        score = stream.Score()

        # Add metadata (title and composer)
        md = metadata.Metadata()
        md.title = title or "Untitled"
        md.composer = composer or "Unknown"
        score.metadata = md

        part = stream.Part()

        # Add tempo
        current_tempo = tempo_bpm or result.tempo or 120
        tempo_mark = tempo.MetronomeMark(number=current_tempo)
        part.append(tempo_mark)

        # Add time signature
        ts_str = time_signature or result.time_signature or self.default_time_signature
        ts = meter.TimeSignature(ts_str)
        part.append(ts)

        # Add key signature
        key_str = key_signature or result.key or self.default_key
        try:
            ks = key.Key(key_str.replace(" major", "").replace(" minor", "m"))
            part.append(ks)
        except Exception:
            # Default to C major if key parsing fails
            part.append(key.Key("C"))

        # Add clef based on pitch range
        avg_pitch = (result.pitch_range[0] + result.pitch_range[1]) / 2
        if avg_pitch < 55:  # Below G3
            part.append(clef.BassClef())
        else:
            part.append(clef.TrebleClef())

        # Convert notes - note_data.start is in seconds, need to convert to quarter notes
        beats_per_second = current_tempo / 60.0

        # Group notes by their quantized start time
        notes_by_offset = defaultdict(list)

        for note_data in result.notes:
            # Convert start time from seconds to quarter notes (beats)
            offset_in_quarters = note_data.start * beats_per_second
            # Quantize to nearest 16th note for grouping
            quantized_offset = round(offset_in_quarters / 0.25) * 0.25
            notes_by_offset[quantized_offset].append(note_data)

        # Insert notes - for overlapping notes, create a chord (limit to top 4 by velocity)
        for offset, notes_at_offset in sorted(notes_by_offset.items()):
            # Sort by velocity (loudest first) and take top notes
            sorted_notes = sorted(notes_at_offset, key=lambda n: n.velocity, reverse=True)
            # Limit chord size to avoid overly complex notation
            top_notes = sorted_notes[:4]

            if len(top_notes) == 1:
                n = self._create_note(top_notes[0], current_tempo)
                part.insert(offset, n)
            else:
                # Create a chord from the top notes
                pitches = []
                velocities = []
                durations = []
                for note_data in top_notes:
                    n = self._create_note(note_data, current_tempo)
                    pitches.append(n.pitch)
                    velocities.append(n.volume.velocity or 64)
                    durations.append(n.duration.quarterLength)

                c = chord.Chord(pitches)
                c.duration.quarterLength = sum(durations) / len(durations)
                c.volume.velocity = sum(velocities) // len(velocities)
                part.insert(offset, c)

        # Add chord symbols if provided
        if chords:
            self._add_chord_symbols(part, chords, beats_per_second)

        score.append(part)

        if self.quantize:
            score = self._quantize_score(score)

        # Make proper notation (measures, beams, etc.) for clean rendering
        score = score.makeNotation()

        # Flatten to single voice to avoid MuseScore rendering issues with multiple voices
        for p in score.parts:
            for m in p.getElementsByClass('Measure'):
                # Get all notes from all voices
                all_notes = []
                voices_to_remove = []
                for v in m.getElementsByClass('Voice'):
                    all_notes.extend(list(v.notes))
                    voices_to_remove.append(v)

                # Remove all voices
                for v in voices_to_remove:
                    m.remove(v)

                # Re-insert notes directly into measure
                for n in all_notes:
                    m.insert(n.offset, n)

        logger.info("Score created successfully")
        return score

    def _add_chord_symbols(
        self,
        part: stream.Part,
        chords: List[AnalysisChord],
        beats_per_second: float,
    ) -> None:
        """Add chord symbols to a part.

        Args:
            part: music21 Part to add chords to
            chords: List of AnalysisChord objects from audio analysis
            beats_per_second: Conversion factor from seconds to beats
        """
        for chord_data in chords:
            # Skip "N" (no chord) labels
            if chord_data.label == "N":
                continue

            # Convert chord label to music21 format
            chord_symbol = self._convert_chord_label(chord_data.label)
            if chord_symbol:
                try:
                    # Create chord symbol
                    cs = harmony.ChordSymbol(chord_symbol)
                    # Convert start time from seconds to quarter notes
                    offset_in_quarters = chord_data.start * beats_per_second
                    part.insert(offset_in_quarters, cs)
                    logger.debug(f"Added chord {chord_symbol} at {offset_in_quarters:.2f}")
                except Exception as e:
                    logger.warning(f"Could not add chord '{chord_data.label}': {e}")

    def _convert_chord_label(self, label: str) -> Optional[str]:
        """Convert madmom chord label to music21 format.

        Args:
            label: Chord label from madmom (e.g., "C:maj", "A:min", "G:7")

        Returns:
            music21 compatible chord symbol or None if not convertible
        """
        if not label or label == "N":
            return None

        # Handle madmom format: "C:maj", "A:min", "G:7", "D:min7", etc.
        if ":" in label:
            root, quality = label.split(":", 1)
        else:
            # Simple format like "C" or "Am"
            root = label
            quality = ""

        # Normalize root note (handle flats/sharps)
        root = root.replace("b", "-")  # music21 uses - for flat

        # Convert quality to music21 format
        quality_map = {
            "maj": "",
            "min": "m",
            "dim": "dim",
            "aug": "aug",
            "7": "7",
            "maj7": "maj7",
            "min7": "m7",
            "dim7": "dim7",
            "hdim7": "m7b5",
            "sus4": "sus4",
            "sus2": "sus2",
            "": "",
        }

        m21_quality = quality_map.get(quality, quality)
        return f"{root}{m21_quality}"

    def from_midi(
        self,
        midi_path: str | Path,
        tempo_bpm: Optional[float] = None,
        key_signature: Optional[str] = None,
        time_signature: Optional[str] = None,
    ) -> stream.Score:
        """Create a music21 Score from MIDI file.

        Args:
            midi_path: Path to MIDI file
            tempo_bpm: Override tempo
            key_signature: Override key signature
            time_signature: Override time signature

        Returns:
            music21 Score object
        """
        midi_path = Path(midi_path)

        if not midi_path.exists():
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")

        logger.info(f"Loading MIDI file: {midi_path.name}")

        try:
            score = converter.parse(str(midi_path))

            # Override tempo if specified
            if tempo_bpm:
                for el in score.recurse().getElementsByClass(tempo.MetronomeMark):
                    el.number = tempo_bpm

            # Override key if specified
            if key_signature:
                for el in score.recurse().getElementsByClass(key.Key):
                    score.remove(el, recurse=True)
                ks = key.Key(key_signature.replace(" major", "").replace(" minor", "m"))
                score.insert(0, ks)

            # Override time signature if specified
            if time_signature:
                for el in score.recurse().getElementsByClass(meter.TimeSignature):
                    score.remove(el, recurse=True)
                ts = meter.TimeSignature(time_signature)
                score.insert(0, ts)

            if self.quantize:
                score = self._quantize_score(score)

            return score

        except Exception as e:
            error_msg = f"Failed to load MIDI: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _create_note(self, note_data: Note, tempo_bpm: float) -> note.Note:
        """Create a music21 Note from Note data.

        Args:
            note_data: Note object with pitch, timing, velocity
            tempo_bpm: Tempo for duration calculation

        Returns:
            music21 Note object
        """
        n = note.Note(note_data.pitch)
        n.volume.velocity = note_data.velocity

        # Convert duration from seconds to quarter notes
        beats_per_second = tempo_bpm / 60.0
        duration_quarters = note_data.duration * beats_per_second
        n.duration.quarterLength = max(0.25, duration_quarters)  # Minimum 16th note

        return n

    def _quantize_score(self, score: stream.Score) -> stream.Score:
        """Quantize note timings to a grid.

        Args:
            score: music21 Score object

        Returns:
            Quantized Score
        """
        logger.debug(f"Quantizing to {self.quantize_resolution} quarter notes")

        for el in score.recurse().notes:
            # Quantize offset
            offset = el.offset
            quantized_offset = round(offset / self.quantize_resolution) * self.quantize_resolution
            el.offset = quantized_offset

            # Quantize duration
            dur = el.duration.quarterLength
            quantized_dur = round(dur / self.quantize_resolution) * self.quantize_resolution
            el.duration.quarterLength = max(self.quantize_resolution, quantized_dur)

        return score

    def export_musicxml(
        self,
        source: Union[stream.Score, MusicTranscriptionResult, str, Path],
        output_path: str | Path,
        chords: Optional[List[AnalysisChord]] = None,
        title: Optional[str] = None,
        composer: Optional[str] = None,
    ) -> Path:
        """Export to MusicXML format.

        Args:
            source: music21 Score, MusicTranscriptionResult, or MIDI path
            output_path: Output file path
            chords: List of detected chords to add as chord symbols
            title: Title of the piece for the sheet music header
            composer: Composer/author name for the sheet music header

        Returns:
            Path to created MusicXML file
        """
        output_path = Path(output_path)

        # Convert source to Score if needed
        if isinstance(source, MusicTranscriptionResult):
            score = self.from_transcription(source, chords=chords, title=title, composer=composer)
        elif isinstance(source, (str, Path)):
            score = self.from_midi(source)
            # Add chords to MIDI-loaded score if provided
            if chords and score.parts:
                tempo_marks = list(score.recurse().getElementsByClass(tempo.MetronomeMark))
                current_tempo = tempo_marks[0].number if tempo_marks else 120
                beats_per_second = current_tempo / 60.0
                self._add_chord_symbols(score.parts[0], chords, beats_per_second)
            # Add metadata for MIDI-loaded scores
            if title or composer:
                md = metadata.Metadata()
                md.title = title or "Untitled"
                md.composer = composer or "Unknown"
                score.metadata = md
        else:
            score = source

        logger.info(f"Exporting MusicXML to: {output_path}")

        try:
            score.write("musicxml", fp=str(output_path))
            logger.info("MusicXML exported successfully")
            return output_path
        except Exception as e:
            error_msg = f"Failed to export MusicXML: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def export_pdf(
        self,
        source: Union[stream.Score, MusicTranscriptionResult, str, Path],
        output_path: str | Path,
        chords: Optional[List[AnalysisChord]] = None,
        title: Optional[str] = None,
        composer: Optional[str] = None,
    ) -> Path:
        """Export to PDF format.

        Requires MuseScore or LilyPond to be installed.

        Args:
            source: music21 Score, MusicTranscriptionResult, or MIDI path
            output_path: Output file path
            chords: List of detected chords to add as chord symbols
            title: Title of the piece for the sheet music header
            composer: Composer/author name for the sheet music header

        Returns:
            Path to created PDF file

        Raises:
            RuntimeError: If no PDF tools are available
        """
        output_path = Path(output_path)

        if not self.musescore_path and not self.lilypond_path:
            raise RuntimeError(
                "PDF export requires MuseScore or LilyPond. "
                "Please install one of these applications."
            )

        logger.info(f"Exporting PDF to: {output_path}")

        # For MIDI files with MuseScore, we need to add chords via MusicXML
        # if chords are provided, so skip the direct MIDI path
        if isinstance(source, (str, Path)) and self.musescore_path and not chords:
            midi_path = Path(source)
            if midi_path.suffix.lower() in [".mid", ".midi"] and midi_path.exists():
                return self._export_pdf_musescore(midi_path, output_path)

        # Convert source to Score if needed
        if isinstance(source, MusicTranscriptionResult):
            score = self.from_transcription(source, chords=chords, title=title, composer=composer)
        elif isinstance(source, (str, Path)):
            score = self.from_midi(source)
            # Add chords to MIDI-loaded score if provided
            if chords and score.parts:
                tempo_marks = list(score.recurse().getElementsByClass(tempo.MetronomeMark))
                current_tempo = tempo_marks[0].number if tempo_marks else 120
                beats_per_second = current_tempo / 60.0
                self._add_chord_symbols(score.parts[0], chords, beats_per_second)
        else:
            score = source

        try:
            # Try MuseScore first
            if self.musescore_path:
                return self._export_pdf_musescore(score, output_path)
            else:
                return self._export_pdf_lilypond(score, output_path)

        except Exception as e:
            error_msg = f"Failed to export PDF: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _export_pdf_musescore(
        self, score_or_midi: Union[stream.Score, Path], output_path: Path
    ) -> Path:
        """Export PDF using MuseScore.

        Args:
            score_or_midi: music21 Score object or path to MIDI file
            output_path: Output PDF path

        Returns:
            Path to created PDF
        """
        # If it's a Path to a MIDI file, use it directly
        if isinstance(score_or_midi, Path) and score_or_midi.exists():
            input_path = score_or_midi
            cleanup_needed = False
        else:
            # It's a Score object, write to temp MusicXML
            with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as tmp:
                input_path = Path(tmp.name)
            score_or_midi.write("musicxml", fp=str(input_path))
            cleanup_needed = True

        try:
            # Convert to PDF with MuseScore
            result = subprocess.run(
                [self.musescore_path, "-o", str(output_path), str(input_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise RuntimeError(f"MuseScore failed: {result.stderr}")

            logger.info("PDF exported via MuseScore")
            return output_path

        finally:
            # Cleanup temp file if we created one
            if cleanup_needed and input_path.exists():
                input_path.unlink()

    def _export_pdf_lilypond(self, score: stream.Score, output_path: Path) -> Path:
        """Export PDF using LilyPond.

        Args:
            score: music21 Score object
            output_path: Output PDF path

        Returns:
            Path to created PDF
        """
        # Use music21's LilyPond support
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / "score.ly"

            # Write LilyPond file
            score.write("lily", fp=str(tmp_path))

            # Run LilyPond
            result = subprocess.run(
                [
                    self.lilypond_path,
                    "-o",
                    str(output_path.parent / output_path.stem),
                    str(tmp_path),
                ],
                capture_output=True,
                text=True,
                cwd=str(output_path.parent),
            )

            if result.returncode != 0:
                raise RuntimeError(f"LilyPond failed: {result.stderr}")

        logger.info("PDF exported via LilyPond")
        return output_path

    def export_midi(
        self,
        source: Union[stream.Score, MusicTranscriptionResult],
        output_path: str | Path,
    ) -> Path:
        """Export to MIDI format.

        Args:
            source: music21 Score or MusicTranscriptionResult
            output_path: Output file path

        Returns:
            Path to created MIDI file
        """
        output_path = Path(output_path)

        # Convert source to Score if needed
        if isinstance(source, MusicTranscriptionResult):
            # If we have midi_data from Basic Pitch, use that directly
            midi_data = source.metadata.get("midi_data")
            if midi_data:
                midi_data.write(str(output_path))
                logger.info(f"MIDI exported to: {output_path}")
                return output_path
            else:
                score = self.from_transcription(source)
        else:
            score = source

        logger.info(f"Exporting MIDI to: {output_path}")

        try:
            score.write("midi", fp=str(output_path))
            logger.info("MIDI exported successfully")
            return output_path
        except Exception as e:
            error_msg = f"Failed to export MIDI: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def preview(self, source: Union[stream.Score, MusicTranscriptionResult]) -> str:
        """Generate a text preview of the score.

        Args:
            source: music21 Score or MusicTranscriptionResult

        Returns:
            Text representation of the score
        """
        if isinstance(source, MusicTranscriptionResult):
            score = self.from_transcription(source)
        else:
            score = source

        lines = ["=" * 60, "SCORE PREVIEW", "=" * 60, ""]

        # Get metadata
        for el in score.recurse():
            if isinstance(el, tempo.MetronomeMark):
                lines.append(f"Tempo: {el.number} BPM")
            elif isinstance(el, key.Key):
                lines.append(f"Key: {el.name}")
            elif isinstance(el, meter.TimeSignature):
                lines.append(f"Time Signature: {el.ratioString}")

        # Get chord symbols
        chord_symbols = list(score.recurse().getElementsByClass(harmony.ChordSymbol))
        if chord_symbols:
            lines.append("")
            lines.append("-" * 60)
            lines.append(f"Chord Symbols ({len(chord_symbols)} total, first 10):")
            lines.append("-" * 60)
            for cs in chord_symbols[:10]:
                lines.append(f"  {cs.figure:8} | offset: {cs.offset:6.2f}")
            if len(chord_symbols) > 10:
                lines.append(f"  ... and {len(chord_symbols) - 10} more chords")

        lines.append("")
        lines.append("-" * 60)
        lines.append("Notes (first 20):")
        lines.append("-" * 60)

        count = 0
        for el in score.recurse().notes:
            if count >= 20:
                lines.append("...")
                break

            if isinstance(el, note.Note):
                lines.append(
                    f"  {el.nameWithOctave:5} | offset: {el.offset:6.2f} | "
                    f"dur: {el.duration.quarterLength:.2f}q"
                )
            elif isinstance(el, chord.Chord):
                names = ", ".join([n.nameWithOctave for n in el.notes])
                lines.append(
                    f"  [{names}] | offset: {el.offset:6.2f} | "
                    f"dur: {el.duration.quarterLength:.2f}q"
                )
            count += 1

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
