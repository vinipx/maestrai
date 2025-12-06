#!/usr/bin/env python3
"""Interactive demo script for Maestrai Audio Transcription Service."""

import sys
import logging
from pathlib import Path
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transcription_engine import TranscriptionEngine
from src.audio_processor import AudioProcessor
from src.utils.config import Config


class TranscriptionDemo:
    """Interactive demo for the transcription service."""

    def __init__(self):
        """Initialize the demo."""
        self.engine = None
        self.processor = AudioProcessor()

    def print_header(self):
        """Print demo header."""
        print("\n" + "=" * 80)
        print("  MAESTRAI - Audio Transcription Service Demo")
        print("  Powered by OpenAI Whisper")
        print("=" * 80 + "\n")

    def select_model(self) -> str:
        """Interactive model selection wizard.

        Returns:
            Selected model name
        """
        print("Select a Whisper model:")
        print("-" * 40)

        model_info = {
            "tiny": "Fastest, lowest accuracy (~1GB VRAM)",
            "base": "Fast, good for testing (~1GB VRAM)",
            "small": "Balanced speed/accuracy (~2GB VRAM)",
            "medium": "High accuracy, slower (~5GB VRAM)",
            "large": "Best accuracy, slowest (~10GB VRAM)",
        }

        for i, model in enumerate(Config.AVAILABLE_MODELS, 1):
            print(f"  {i}. {model:8} - {model_info[model]}")

        print()
        while True:
            try:
                choice = input(
                    f"Enter choice (1-{len(Config.AVAILABLE_MODELS)}) [default: 2]: "
                ).strip()

                if not choice:
                    choice = "2"  # Default to base

                choice_num = int(choice)
                if 1 <= choice_num <= len(Config.AVAILABLE_MODELS):
                    selected_model = Config.AVAILABLE_MODELS[choice_num - 1]
                    print(f"\nℹ️  Selected model: {selected_model}")
                    return selected_model
                else:
                    print(f"Please enter a number between 1 and {len(Config.AVAILABLE_MODELS)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nDemo cancelled.")
                sys.exit(0)

    def validate_and_show_info(self, file_path: str) -> bool:
        """Validate audio file and display info.

        Args:
            file_path: Path to audio file

        Returns:
            True if valid, False otherwise
        """
        print("\nValidating audio file...")
        print("-" * 40)

        is_valid, error_msg = self.processor.validate_audio_file(file_path)

        if not is_valid:
            print(f"❌ Validation failed: {error_msg}")
            return False

        print("✅ File validation passed")

        # Get and display audio info
        try:
            info = self.processor.get_audio_info(file_path)
            print("\nℹ️  Audio Information:")
            print(f"   Filename: {info['filename']}")
            print(f"   Format: {info['format']}")
            print(f"   Duration: {info['duration']:.2f} seconds")
            print(f"   Size: {info['size'] / (1024**2):.2f} MB")
            print(f"   Codec: {info['codec']}")
            print(f"   Sample Rate: {info['sample_rate']} Hz")
            print(f"   Channels: {info['channels']}")
            return True
        except Exception as e:
            print(f"⚠️  Could not retrieve audio info: {e}")
            return False

    def run_transcription(self, file_path: str, model_name: str):
        """Run transcription with progress indicators.

        Args:
            file_path: Path to audio file
            model_name: Model to use
        """
        print("\n" + "=" * 80)
        print("TRANSCRIPTION")
        print("=" * 80)

        # Initialize engine
        print(f"\nℹ️  Loading {model_name} model...")
        try:
            self.engine = TranscriptionEngine(model_name=model_name)
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return

        # Run transcription
        print("\nℹ️  Starting transcription...")
        print("   (This may take a while depending on audio length and model size)")
        print()

        try:
            result = self.engine.transcribe(file_path, word_timestamps=True)
            print("✅ Transcription completed!")

            self.display_results(result)
            self.export_results(result, file_path)

        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return

    def display_results(self, result):
        """Display transcription results.

        Args:
            result: TranscriptionResult object
        """
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)

        print(f"\nℹ️  Summary:")
        print(f"   Language: {result.language}")
        print(f"   Duration: {result.duration:.2f} seconds")
        print(f"   Segments: {len(result.segments)}")
        print(f"   Words: {result.word_count}")

        print(f"\n📝 Full Transcription:")
        print("-" * 40)
        print(result.text)
        print("-" * 40)

        # Show first few segments with details
        print(f"\n📊 Segment Details (showing first 3):")
        for i, segment in enumerate(result.segments[:3], 1):
            print(f"\nSegment {i}:")
            print(f"  Time: {segment.start:.2f}s - {segment.end:.2f}s")
            print(f"  Text: {segment.text}")
            if segment.words:
                print(f"  Words: {len(segment.words)}")

        if len(result.segments) > 3:
            print(f"\n... and {len(result.segments) - 3} more segments")

    def export_results(self, result, original_file: str):
        """Export results to SRT and TXT files.

        Args:
            result: TranscriptionResult object
            original_file: Original audio file path
        """
        print("\n" + "=" * 80)
        print("EXPORT")
        print("=" * 80)

        original_path = Path(original_file)
        base_name = original_path.stem

        # Export SRT
        srt_path = original_path.parent / f"{base_name}.srt"
        try:
            self.engine.export_srt(result, srt_path)
            print(f"✅ SRT exported to: {srt_path}")
        except Exception as e:
            print(f"❌ SRT export failed: {e}")

        # Export TXT
        txt_path = original_path.parent / f"{base_name}.txt"
        try:
            self.engine.export_txt(result, txt_path)
            print(f"✅ Text exported to: {txt_path}")
        except Exception as e:
            print(f"❌ Text export failed: {e}")

    def run_interactive(self):
        """Run interactive mode."""
        self.print_header()

        print("Welcome to the Maestrai Demo!")
        print("This interactive tool will guide you through transcribing an audio file.\n")

        # Select model
        model_name = self.select_model()

        # Get audio file path
        print("\n" + "=" * 80)
        print("AUDIO FILE")
        print("=" * 80)

        while True:
            try:
                file_path = input("\nEnter path to audio/video file: ").strip()

                if not file_path:
                    print("Please enter a file path")
                    continue

                # Remove quotes if present
                file_path = file_path.strip("\"'")

                # Expand user home directory (~)
                file_path = str(Path(file_path).expanduser())

                if self.validate_and_show_info(file_path):
                    break
                else:
                    retry = input("\nTry another file? (y/n): ").strip().lower()
                    if retry != "y":
                        print("Demo cancelled.")
                        return

            except KeyboardInterrupt:
                print("\n\nDemo cancelled.")
                return

        # Run transcription
        self.run_transcription(file_path, model_name)

        print("\n" + "=" * 80)
        print("Demo completed successfully!")
        print("=" * 80 + "\n")

    def run_quick(self, file_path: str, model_name: str = "base"):
        """Run quick mode with a single file.

        Args:
            file_path: Path to audio file
            model_name: Model to use (default: base)
        """
        self.print_header()

        # Expand user home directory (~)
        file_path = str(Path(file_path).expanduser())

        print(f"Quick Mode: Transcribing {file_path}")
        print(f"Model: {model_name}\n")

        if not self.validate_and_show_info(file_path):
            print("\n❌ File validation failed. Exiting.")
            sys.exit(1)

        self.run_transcription(file_path, model_name)

        print("\n✅ Quick transcription completed!\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Maestrai Audio Transcription Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python demo.py

  Quick mode:
    python demo.py audio.mp3
    python demo.py video.mp4 --model small
        """,
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Audio/video file to transcribe (optional, triggers quick mode)",
    )

    parser.add_argument(
        "-m",
        "--model",
        default="base",
        choices=Config.AVAILABLE_MODELS,
        help="Whisper model to use (default: base)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create demo instance
    demo = TranscriptionDemo()

    try:
        if args.file:
            # Quick mode
            demo.run_quick(args.file, args.model)
        else:
            # Interactive mode
            demo.run_interactive()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        if hasattr(demo, "processor"):
            demo.processor.cleanup_temp_files()


if __name__ == "__main__":
    main()
