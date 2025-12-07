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
    echo -e "${YELLOW}Music Options:${NC}"
    echo "  --input, -i <file>        Input audio file (positional may be used instead)"
    echo "  --output, -o <dir>        Output directory (default: ./output)"
    echo "  --format <musicxml|midi>  Preferred export format"
    echo "  --midi                   Export MIDI"
    echo "  --pdf                    Export PDF (requires MuseScore or LilyPond)"
    echo "  --model <name>           Select transcription model (e.g. basic-pitch)"
    echo "  --sample-rate <hz>       Resample input to given sample rate"
    echo "  --musescore-path <path>  Path to MuseScore binary for PDF export"
    echo "  -v, --verbose            Enable verbose output"
    echo "  -h, --help               Show this help message"
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

# Normalize and forward args to Python script for music mode
forward_music_args() {
    # Accept positional input as first arg if present
    local INPUT=""
    local OUTPUT=""
    local FORMAT=""
    local MODEL=""
    local SR=""
    local MUSESCORE=""
    local MIDI=false
    local PDF=false
    local VERBOSE=false

    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            --input|-i)
                INPUT="$2"; shift 2;;
            --output|-o)
                OUTPUT="$2"; shift 2;;
            --format)
                FORMAT="$2"; shift 2;;
            --midi)
                MIDI=true; shift;;
            --pdf)
                PDF=true; shift;;
            --model)
                MODEL="$2"; shift 2;;
            --sample-rate)
                SR="$2"; shift 2;;
            --musescore-path)
                MUSESCORE="$2"; shift 2;;
            -v|--verbose)
                VERBOSE=true; shift;;
            -h|--help)
                print_usage; exit 0;;
            *)
                # treat first unknown as input file (positional)
                if [ -z "$INPUT" ]; then
                    INPUT="$1"
                    shift
                else
                    echo -e "${RED}Unknown argument: $1${NC}";
                    print_usage; exit 1
                fi
                ;;
        esac
    done

    # Build python args array
    PY_ARGS=()
    if [ -n "$INPUT" ]; then PY_ARGS+=("$INPUT"); fi
    if [ -n "$OUTPUT" ]; then PY_ARGS+=("--output" "$OUTPUT"); fi
    if [ -n "$FORMAT" ]; then PY_ARGS+=("--format" "$FORMAT"); fi
    if [ "$MIDI" = true ]; then PY_ARGS+=("--midi"); fi
    if [ "$PDF" = true ]; then PY_ARGS+=("--pdf"); fi
    if [ -n "$MODEL" ]; then PY_ARGS+=("--model" "$MODEL"); fi
    if [ -n "$SR" ]; then PY_ARGS+=("--sample-rate" "$SR"); fi
    if [ -n "$MUSESCORE" ]; then PY_ARGS+=("--musescore-path" "$MUSESCORE"); fi
    if [ "$VERBOSE" = true ]; then PY_ARGS+=("--verbose"); fi

    # Call python demo with normalized args
    python "$SCRIPT_DIR/scripts/music_demo.py" "${PY_ARGS[@]}"
}

# Main logic
main() {
    print_banner

    # Check for help flag or no args
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
                echo -e "${RED}Error: Please provide an audio file or options.${NC}"
                echo ""
                print_usage
                exit 1
            fi
            echo -e "${GREEN}Starting music transcription...${NC}"
            forward_music_args "$@"
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
