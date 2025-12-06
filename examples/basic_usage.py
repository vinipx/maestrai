#!/usr/bin/env python3
"""Basic usage example for Maestrai."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transcription_engine import TranscriptionEngine


def main():
    """Demonstrate basic transcription usage."""

    print("Maestrai - Basic Usage Example")
    print("=" * 60)

    # Initialize the transcription engine with base model
    print("\n1. Initializing transcription engine...")
    engine = TranscriptionEngine(model_name="base")
    print("   Engine initialized successfully!")

    # Check model info
    print("\n2. Model Information:")
    info = engine.get_model_info()
    print(f"   Model: {info['model_name']}")
    print(f"   Device: {info['device']}")
    print(f"   CUDA Available: {info['cuda_available']}")
    print(f"   Supported Languages: {info['supported_languages']}")

    # Transcribe an audio file
    # NOTE: Replace with your actual audio file path
    audio_file = "path/to/your/audio.mp3"

    print(f"\n3. Transcribing audio file: {audio_file}")
    print("   (This may take a while...)")

    try:
        result = engine.transcribe(
            audio_file,
            language=None,  # Auto-detect language
            word_timestamps=True,
        )

        print("\n4. Transcription Results:")
        print(f"   Language: {result.language}")
        print(f"   Duration: {result.duration:.2f}s")
        print(f"   Segments: {len(result.segments)}")
        print(f"   Words: {result.word_count}")

        print("\n5. Transcribed Text:")
        print("-" * 60)
        print(result.text)
        print("-" * 60)

        # Export to SRT and TXT
        print("\n6. Exporting results...")
        srt_path = Path(audio_file).with_suffix(".srt")
        txt_path = Path(audio_file).with_suffix(".txt")

        engine.export_srt(result, srt_path)
        print(f"   SRT saved to: {srt_path}")

        engine.export_txt(result, txt_path)
        print(f"   TXT saved to: {txt_path}")

        print("\n✅ Transcription completed successfully!")

    except FileNotFoundError:
        print("\n⚠️  Please update the 'audio_file' path in this script")
        print("   with the path to your actual audio file.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
