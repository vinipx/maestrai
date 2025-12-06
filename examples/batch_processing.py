#!/usr/bin/env python3
"""Batch processing example for Maestrai."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transcription_engine import TranscriptionEngine


def main():
    """Demonstrate batch transcription of multiple files."""

    print("Maestrai - Batch Processing Example")
    print("=" * 60)

    # List of audio files to transcribe
    # NOTE: Replace with your actual audio file paths
    audio_files = [
        "path/to/audio1.mp3",
        "path/to/audio2.wav",
        "path/to/audio3.m4a",
    ]

    print(f"\n1. Processing {len(audio_files)} audio files...")

    # Initialize engine
    print("   Initializing transcription engine...")
    engine = TranscriptionEngine(model_name="base")

    # Batch transcribe
    print("\n2. Starting batch transcription...")
    results = engine.transcribe_batch(
        audio_files,
        language=None,  # Auto-detect
        word_timestamps=True,
    )

    print(f"\n3. Batch Results: {len(results)}/{len(audio_files)} successful")

    # Process each result
    for i, result in enumerate(results, 1):
        print(f"\n--- File {i} ---")
        print(f"Language: {result.language}")
        print(f"Duration: {result.duration:.2f}s")
        print(f"Words: {result.word_count}")
        print(f"Preview: {result.text[:100]}...")

        # Export each result
        audio_path = Path(audio_files[i - 1])
        srt_path = audio_path.with_suffix(".srt")
        txt_path = audio_path.with_suffix(".txt")

        try:
            engine.export_srt(result, srt_path)
            engine.export_txt(result, txt_path)
            print(f"Exported: {srt_path.name}, {txt_path.name}")
        except Exception as e:
            print(f"Export failed: {e}")

    print("\n✅ Batch processing completed!")

    # Summary statistics
    total_duration = sum(r.duration for r in results)
    total_words = sum(r.word_count for r in results)

    print("\n4. Summary Statistics:")
    print(f"   Total files processed: {len(results)}")
    print(f"   Total audio duration: {total_duration:.2f}s")
    print(f"   Total words transcribed: {total_words}")
    print(f"   Average words per file: {total_words / len(results):.0f}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("\n⚠️  Please update the 'audio_files' list in this script")
        print("   with paths to your actual audio files.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
