#!/usr/bin/env python3
"""Video transcription example for Maestrai."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transcription_engine import TranscriptionEngine
from src.audio_processor import AudioProcessor


def main():
    """Demonstrate video audio extraction and transcription."""

    print("Maestrai - Video Transcription Example")
    print("=" * 60)

    # Video file to process
    # NOTE: Replace with your actual video file path
    video_file = "path/to/your/video.mp4"

    print(f"\n1. Processing video file: {video_file}")

    # Initialize components
    print("\n2. Initializing components...")
    processor = AudioProcessor()
    engine = TranscriptionEngine(model_name="base")

    # Validate video file
    print("\n3. Validating video file...")
    is_valid, error = processor.validate_audio_file(video_file)

    if not is_valid:
        print(f"   ❌ Validation failed: {error}")
        return

    print("   ✅ Video file is valid")

    # Get video info
    print("\n4. Video Information:")
    try:
        info = processor.get_audio_info(video_file)
        print(f"   Format: {info['format']}")
        print(f"   Duration: {info['duration']:.2f}s")
        print(f"   Size: {info['size'] / (1024**2):.2f} MB")
        print(f"   Audio Codec: {info['codec']}")
        print(f"   Sample Rate: {info['sample_rate']} Hz")
        print(f"   Channels: {info['channels']}")
    except Exception as e:
        print(f"   ⚠️  Could not retrieve info: {e}")

    # Extract and transcribe
    print("\n5. Extracting audio and transcribing...")
    print("   (This may take a while...)")

    try:
        # The transcription engine will automatically extract audio from video
        result = engine.transcribe(
            video_file,
            language=None,  # Auto-detect
            word_timestamps=True,
        )

        print("\n6. Transcription Results:")
        print(f"   Language: {result.language}")
        print(f"   Duration: {result.duration:.2f}s")
        print(f"   Segments: {len(result.segments)}")
        print(f"   Words: {result.word_count}")

        print("\n7. Transcribed Text:")
        print("-" * 60)
        print(result.text)
        print("-" * 60)

        # Show segment details with timestamps
        print("\n8. Segments with Timestamps:")
        for i, segment in enumerate(result.segments[:5], 1):  # Show first 5
            timestamp = f"[{segment.start:.2f}s - {segment.end:.2f}s]"
            print(f"   {i}. {timestamp} {segment.text}")

        if len(result.segments) > 5:
            print(f"   ... and {len(result.segments) - 5} more segments")

        # Export subtitle file (SRT) - perfect for videos!
        print("\n9. Exporting subtitle file...")
        video_path = Path(video_file)
        srt_path = video_path.with_suffix(".srt")
        txt_path = video_path.with_suffix(".txt")

        engine.export_srt(result, srt_path)
        print(f"   ✅ Subtitles saved to: {srt_path}")
        print("      (Can be used with video players!)")

        engine.export_txt(result, txt_path)
        print(f"   ✅ Transcript saved to: {txt_path}")

        print("\n✅ Video transcription completed successfully!")

        print("\n💡 Tip: You can use the .srt file with your video player")
        print("   to display synchronized subtitles!")

    except FileNotFoundError:
        print("\n⚠️  Please update the 'video_file' path in this script")
        print("   with the path to your actual video file.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup temporary files
        processor.cleanup_temp_files()


if __name__ == "__main__":
    main()
