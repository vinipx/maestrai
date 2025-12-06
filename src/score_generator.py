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

from music21 import converter, stream, note, chord, meter, key, tempo, clef
from music21 import environment as m21env
import pretty_midi

from .music_transcription_engine import MusicTranscriptionResult, Note

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
    ) -> stream.Score:
        """Create a music21 Score from transcription result.

        Args:
            result: MusicTranscriptionResult from transcription engine
            tempo_bpm: Override tempo (BPM)
            key_signature: Override key signature
            time_signature: Override time signature

        Returns:
            music21 Score object
        """
        logger.info(f"Creating score from {result.note_count} notes")

        # Create score
        score = stream.Score()
        part = stream.Part()

        # Add tempo
        if tempo_bpm or result.tempo:
            tempo_mark = tempo.MetronomeMark(number=tempo_bpm or result.tempo or 120)
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

        # Convert notes
        for note_data in result.notes:
            n = self._create_note(note_data, tempo_bpm or result.tempo or 120)
            part.insert(note_data.start, n)

        score.append(part)

        if self.quantize:
            score = self._quantize_score(score)

        logger.info("Score created successfully")
        return score

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
    ) -> Path:
        """Export to MusicXML format.

        Args:
            source: music21 Score, MusicTranscriptionResult, or MIDI path
            output_path: Output file path

        Returns:
            Path to created MusicXML file
        """
        output_path = Path(output_path)

        # Convert source to Score if needed
        if isinstance(source, MusicTranscriptionResult):
            score = self.from_transcription(source)
        elif isinstance(source, (str, Path)):
            score = self.from_midi(source)
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
    ) -> Path:
        """Export to PDF format.

        Requires MuseScore or LilyPond to be installed.

        Args:
            source: music21 Score, MusicTranscriptionResult, or MIDI path
            output_path: Output file path

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

        # Convert source to Score if needed
        if isinstance(source, MusicTranscriptionResult):
            score = self.from_transcription(source)
        elif isinstance(source, (str, Path)):
            score = self.from_midi(source)
        else:
            score = source

        logger.info(f"Exporting PDF to: {output_path}")

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

    def _export_pdf_musescore(self, score: stream.Score, output_path: Path) -> Path:
        """Export PDF using MuseScore.

        Args:
            score: music21 Score object
            output_path: Output PDF path

        Returns:
            Path to created PDF
        """
        with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Write MusicXML first
            score.write("musicxml", fp=str(tmp_path))

            # Convert to PDF with MuseScore
            result = subprocess.run(
                [self.musescore_path, "-o", str(output_path), str(tmp_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise RuntimeError(f"MuseScore failed: {result.stderr}")

            logger.info("PDF exported via MuseScore")
            return output_path

        finally:
            # Cleanup temp file
            if tmp_path.exists():
                tmp_path.unlink()

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
