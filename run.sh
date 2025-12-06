#!/bin/bash
# Maestrai - AI-Powered Music & Audio Transcription
# Usage: ./run.sh [music|speech] <audio_file> [options]

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║           MAESTRAI - Music & Audio Transcription         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print usage
print_usage() {
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./run.sh music <audio_file>      Convert audio to sheet music (MIDI, MusicXML, PDF)"
    echo "  ./run.sh speech <audio_file>     Convert speech to text (SRT, TXT)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./run.sh music ~/Music/song.mp3"
    echo "  ./run.sh speech ~/Downloads/podcast.mp3"
    echo "  ./run.sh music recording.wav"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Enable verbose output"
    echo ""
    echo -e "${YELLOW}Output:${NC}"
    echo "  All generated files are saved to: ${SCRIPT_DIR}/output/"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        echo -e "${RED}Error: Virtual environment not found.${NC}"
        echo -e "Please run ${GREEN}./setup.sh${NC} first to set up the environment."
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    source "$SCRIPT_DIR/venv/bin/activate"
}

# Main logic
main() {
    print_banner

    # Check for help flag
    if [[ "$1" == "-h" || "$1" == "--help" || -z "$1" ]]; then
        print_usage
        exit 0
    fi

    # Check virtual environment
    check_venv
    activate_venv

    # Parse mode
    MODE="$1"
    shift

    case "$MODE" in
        music)
            if [ -z "$1" ]; then
                echo -e "${RED}Error: Please provide an audio file.${NC}"
                echo ""
                print_usage
                exit 1
            fi
            echo -e "${GREEN}Starting music transcription...${NC}"
            python "$SCRIPT_DIR/scripts/music_demo.py" "$@"
            ;;
        speech)
            if [ -z "$1" ]; then
                echo -e "${RED}Error: Please provide an audio file.${NC}"
                echo ""
                print_usage
                exit 1
            fi
            echo -e "${GREEN}Starting speech transcription...${NC}"
            python "$SCRIPT_DIR/scripts/demo.py" "$@"
            ;;
        *)
            echo -e "${RED}Error: Unknown mode '$MODE'${NC}"
            echo ""
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
