#!/usr/bin/env python3
"""Interactive demo script for Maestrai Music Transcription Service.

Converts audio recordings into:
- MIDI files
- MusicXML (sheet music)
- Audio analysis reports
"""

import sys
import logging
from pathlib import Path
import argparse

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
            print(f"Key: {analysis.key}")
            print(f"Time Signature: {analysis.time_signature}")
            print(f"Beats detected: {len(analysis.beats)}")
            print(f"Onsets detected: {len(analysis.onsets)}")

            if analysis.spectral_centroid:
                print(f"Spectral Centroid: {analysis.spectral_centroid:.1f} Hz")
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

            print(f"\nTranscription completed!")
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
            print(f"\nStatistics:")
            print(f"  Notes per second: {stats['notes_per_second']:.2f}")
            print(f"  Average velocity: {stats['average_velocity']:.1f}")
            print(f"  Average note duration: {stats['average_note_duration']:.3f}s")

            # Show first few notes
            print(f"\nFirst 10 notes:")
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

    def export_results(self, result, analysis, original_file: str):
        """Export results to various formats.

        Args:
            result: MusicTranscriptionResult object
            analysis: AudioAnalysis object
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

        # Try PDF export
        pdf_path = self.output_dir / f"{base_name}.pdf"
        try:
            if self.score_gen.musescore_path or self.score_gen.lilypond_path:
                self.score_gen.export_pdf(result, pdf_path)
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

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create demo instance
    demo = MusicTranscriptionDemo()

    try:
        if args.file:
            demo.run_quick(args.file)
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
