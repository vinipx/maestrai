#!/usr/bin/env python3
"""Interactive demo script for Maestrai Music Transcription Service.

Converts audio recordings into:
- MIDI files
- MusicXML (sheet music)
- Audio analysis reports
"""

import sys
import os
import logging
import warnings
from pathlib import Path
import argparse

# Suppress noisy warnings from dependencies BEFORE importing them
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TensorFlow logging
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*beam.*")  # music21 beam warnings
warnings.filterwarnings("ignore", message=".*scikit-learn.*")
warnings.filterwarnings("ignore", message=".*TensorFlow.*")
warnings.filterwarnings("ignore", message=".*Torch.*")
warnings.filterwarnings("ignore", message=".*tflite.*")
warnings.filterwarnings("ignore", message=".*onnxruntime.*")

# Suppress root logger warnings
logging.getLogger("root").setLevel(logging.ERROR)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.music_transcription_engine import MusicTranscriptionEngine
from src.audio_analyzer import AudioAnalyzer
from src.score_generator import ScoreGenerator


class MusicTranscriptionDemo:
    """Interactive demo for the music transcription service."""

    def __init__(self):
        """Initialize the demo."""
        self.engine = None
        self.analyzer = None
        self.score_gen = None
        # Output directory relative to project root
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)

    def print_header(self):
        """Print demo header."""
        print("\n" + "=" * 80)
        print("  MAESTRAI - Music Transcription Service Demo")
        print("  Audio to Sheet Music powered by Spotify Basic Pitch")
        print("=" * 80 + "\n")

    def initialize_engines(self):
        """Initialize transcription engines."""
        print("Initializing music transcription engines...")
        print("-" * 40)

        try:
            print("  Loading Basic Pitch model...")
            self.engine = MusicTranscriptionEngine()
            print("  Basic Pitch model loaded")

            print("  Initializing audio analyzer...")
            self.analyzer = AudioAnalyzer()
            print("  Audio analyzer ready")

            print("  Initializing score generator...")
            self.score_gen = ScoreGenerator()
            print("  Score generator ready")

            print("-" * 40)
            print("All engines initialized successfully")
            return True

        except Exception as e:
            print(f"Failed to initialize engines: {e}")
            return False

    def analyze_audio(self, file_path: str):
        """Analyze audio file and display info.

        Args:
            file_path: Path to audio file
        """
        print("\n" + "=" * 80)
        print("AUDIO ANALYSIS")
        print("=" * 80)

        try:
            analysis = self.analyzer.analyze(file_path)

            print(f"\nFile: {Path(file_path).name}")
            print(f"Duration: {analysis.duration:.2f} seconds")
            print(f"Sample Rate: {analysis.sample_rate} Hz")
            print("-" * 40)
            print(f"Tempo: {analysis.tempo:.1f} BPM")
            if analysis.tempo_strengths and len(analysis.tempo_strengths) > 1:
                alt_tempos = ", ".join(
                    f"{t:.1f} ({s:.2f})" for t, s in analysis.tempo_strengths[:3]
                )
                print(f"  Alternative tempos: {alt_tempos}")
            print(f"Key: {analysis.key}")
            if analysis.key_confidence > 0:
                print(f"  Key confidence: {analysis.key_confidence:.2f}")
            print(f"Time Signature: {analysis.time_signature}")
            print(f"Beats detected: {len(analysis.beats)}")
            print(f"Downbeats detected: {len(analysis.downbeats)}")
            print(f"Onsets detected: {len(analysis.onsets)}")

            # Display chord progression
            if analysis.chords:
                print(f"Chords detected: {len(analysis.chords)}")
                print("\nChord Progression (first 10):")
                print("-" * 40)
                for chord in analysis.chords[:10]:
                    print(f"  {chord.start:6.2f}s - {chord.end:6.2f}s: {chord.label}")
                if len(analysis.chords) > 10:
                    print(f"  ... and {len(analysis.chords) - 10} more chords")

            if analysis.spectral_centroid:
                print(f"\nSpectral Centroid: {analysis.spectral_centroid:.1f} Hz")
            if analysis.rms_energy:
                print(f"RMS Energy: {analysis.rms_energy:.4f}")

            return analysis

        except Exception as e:
            print(f"Analysis failed: {e}")
            return None

    def transcribe_music(self, file_path: str, analysis=None):
        """Transcribe audio to musical notes.

        Args:
            file_path: Path to audio file
            analysis: Optional AudioAnalysis from previous step
        """
        print("\n" + "=" * 80)
        print("MUSIC TRANSCRIPTION")
        print("=" * 80)

        print("\nTranscribing audio to musical notes...")
        print("(This may take a moment depending on file length)")

        try:
            result = self.engine.transcribe(file_path)

            # Update result with analysis data if available
            if analysis:
                result.tempo = analysis.tempo
                result.key = analysis.key
                result.time_signature = analysis.time_signature

            print("\nTranscription completed!")
            print("-" * 40)
            print(f"Notes detected: {result.note_count}")
            print(f"Duration: {result.duration:.2f} seconds")
            print(f"Pitch range: {result.pitch_range_names[0]} - {result.pitch_range_names[1]}")

            if result.tempo:
                print(f"Tempo: {result.tempo:.1f} BPM")
            if result.key:
                print(f"Key: {result.key}")

            # Show statistics
            stats = self.engine.get_statistics(result)
            print("\nStatistics:")
            print(f"  Notes per second: {stats['notes_per_second']:.2f}")
            print(f"  Average velocity: {stats['average_velocity']:.1f}")
            print(f"  Average note duration: {stats['average_note_duration']:.3f}s")

            # Show first few notes
            print("\nFirst 10 notes:")
            print("-" * 40)
            for note in result.notes[:10]:
                print(f"  {note}")

            if len(result.notes) > 10:
                print(f"  ... and {len(result.notes) - 10} more notes")

            return result

        except Exception as e:
            print(f"Transcription failed: {e}")
            import traceback

            traceback.print_exc()
            return None

    def export_results(self, result, _analysis, original_file: str):
        """Export results to various formats.

        Args:
            result: MusicTranscriptionResult object
            _analysis: (unused) AudioAnalysis object (kept for compatibility)
            original_file: Original audio file path
        """
        print("\n" + "=" * 80)
        print("EXPORT")
        print("=" * 80)

        original_path = Path(original_file)
        base_name = original_path.stem

        print(f"\nOutput directory: {self.output_dir}")

        # Export MIDI
        midi_path = self.output_dir / f"{base_name}.mid"
        try:
            self.engine.export_midi(result, midi_path)
            print(f"MIDI exported to: {midi_path}")
        except Exception as e:
            print(f"MIDI export failed: {e}")

        # Export MusicXML
        musicxml_path = self.output_dir / f"{base_name}.musicxml"
        try:
            self.score_gen.export_musicxml(
                result,
                musicxml_path,
            )
            print(f"MusicXML exported to: {musicxml_path}")
        except Exception as e:
            print(f"MusicXML export failed: {e}")

        # Try PDF export - use MIDI file directly for better results
        pdf_path = self.output_dir / f"{base_name}.pdf"
        try:
            if self.score_gen.musescore_path or self.score_gen.lilypond_path:
                # Use MIDI file directly for PDF generation (more reliable)
                self.score_gen.export_pdf(midi_path, pdf_path)
                print(f"PDF exported to: {pdf_path}")
            else:
                print("PDF export skipped (MuseScore or LilyPond not installed)")
        except Exception as e:
            print(f"PDF export failed: {e}")

        # Show score preview
        print("\n" + "=" * 80)
        print("SCORE PREVIEW")
        print("=" * 80)
        preview = self.score_gen.preview(result)
        print(preview)

    def run_interactive(self):
        """Run interactive mode."""
        self.print_header()

        print("Welcome to the Maestrai Music Transcription Demo!")
        print("This tool will convert your audio recording into sheet music.\n")

        if not self.initialize_engines():
            print("\nFailed to initialize. Exiting.")
            sys.exit(1)

        # Get audio file path
        print("\n" + "=" * 80)
        print("AUDIO FILE")
        print("=" * 80)

        while True:
            try:
                file_path = input("\nEnter path to audio file: ").strip()

                if not file_path:
                    print("Please enter a file path")
                    continue

                # Remove quotes and expand path
                file_path = file_path.strip("\"'")
                file_path = str(Path(file_path).expanduser())

                if not Path(file_path).exists():
                    print(f"File not found: {file_path}")
                    continue

                break

            except KeyboardInterrupt:
                print("\n\nDemo cancelled.")
                return

        # Analyze audio
        analysis = self.analyze_audio(file_path)

        # Transcribe music
        result = self.transcribe_music(file_path, analysis)

        if result:
            # Export results
            self.export_results(result, analysis, file_path)

        print("\n" + "=" * 80)
        print("Demo completed!")
        print("=" * 80 + "\n")

    def run_quick(self, file_path: str):
        """Run quick mode with a single file.

        Args:
            file_path: Path to audio file
        """
        self.print_header()

        # Expand path
        file_path = str(Path(file_path).expanduser())

        print(f"Quick Mode: Transcribing {file_path}\n")

        if not Path(file_path).exists():
            print(f"File not found: {file_path}")
            sys.exit(1)

        if not self.initialize_engines():
            print("\nFailed to initialize. Exiting.")
            sys.exit(1)

        # Analyze
        analysis = self.analyze_audio(file_path)

        # Transcribe
        result = self.transcribe_music(file_path, analysis)

        if result:
            # Export
            self.export_results(result, analysis, file_path)

        print("\nQuick transcription completed!\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Maestrai Music Transcription Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python music_demo.py

  Quick mode:
    python music_demo.py song.mp3
    python music_demo.py piano.wav
        """,
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Audio file to transcribe (optional, triggers quick mode)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output directory to write results (default: ./output)",
    )

    parser.add_argument(
        "--format",
        help="Preferred export format (musicxml, midi)",
    )

    parser.add_argument(
        "--midi",
        action="store_true",
        help="Export MIDI file",
    )

    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Export PDF (requires MuseScore or LilyPond)",
    )

    parser.add_argument(
        "--model",
        help="Model name to use for transcription (e.g. basic-pitch)",
    )

    parser.add_argument(
        "--sample-rate",
        type=int,
        help="Resample input to this sample rate (Hz)",
    )

    parser.add_argument(
        "--musescore-path",
        help="Path to MuseScore binary for PDF export",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create demo instance
    demo = MusicTranscriptionDemo()

    # Set optional runtime config from CLI
    if args.output:
        demo.output_dir = Path(args.output)
        demo.output_dir.mkdir(parents=True, exist_ok=True)

    # Pass model selection via environment or attribute if supported
    if args.model:
        # Some engine versions accept a model name; set attribute for backward compatibility
        demo.engine = None
        MusicTranscriptionEngine.default_model = args.model

    # Configure ScoreGenerator musescore path if provided
    if args.musescore_path:
        # Ensure score generator instance gets the musescore path on initialization
        ScoreGenerator.default_musescore_path = args.musescore_path

    try:
        if args.file:
            # Quick mode: respect export flags
            # Initialize engines and override export behavior accordingly
            if not demo.initialize_engines():
                print(FAILED_INIT_MSG)
                sys.exit(1)

            analysis = demo.analyze_audio(args.file)
            result = demo.transcribe_music(args.file, analysis)

            if result:
                # Export only requested formats; default to all if none specified
                export_midi = args.midi or (not args.midi and not args.pdf and not args.format)
                export_pdf = args.pdf or (not args.midi and not args.pdf and not args.format)

                # If --format is specified, interpret it
                if args.format:
                    fmt = args.format.lower()
                    export_midi = fmt in ("midi", "all") or export_midi
                    export_pdf = fmt in ("musicxml", "all") or export_pdf

                # Use existing export_results but control behavior
                demo.initialize_engines()
                # adjust score generator musescore path if attribute exists
                try:
                    if hasattr(demo.score_gen, 'musescore_path') and args.musescore_path:
                        demo.score_gen.musescore_path = args.musescore_path
                except Exception:
                    pass

                # Perform exports manually to control which ones run
                base = Path(args.file).stem
                # always define midi_path variable to avoid uninitialized reference
                midi_path = demo.output_dir / f"{base}.mid"

                # Ensure engines are initialized
                if demo.engine is None or demo.score_gen is None:
                    raise RuntimeError("Engines not initialized; cannot export results")

                if export_midi:
                    demo.engine.export_midi(result, midi_path)
                    print(f"MIDI exported to: {midi_path}")

                musicxml_path = demo.output_dir / f"{base}.musicxml"
                demo.score_gen.export_musicxml(result, musicxml_path)
                print(f"MusicXML exported to: {musicxml_path}")

                if export_pdf:
                    pdf_path = demo.output_dir / f"{base}.pdf"
                    try:
                        if demo.score_gen.musescore_path or demo.score_gen.lilypond_path:
                            demo.score_gen.export_pdf(midi_path, pdf_path)
                            print(f"PDF exported to: {pdf_path}")
                        else:
                            print("PDF export skipped (MuseScore or LilyPond not installed)")
                    except Exception as e:
                        print(f"PDF export failed: {e}")

            print("\nQuick transcription completed!\n")
        else:
            demo.run_interactive()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
