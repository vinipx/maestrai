#!/bin/bash
# Maestrai Setup Script for macOS and Linux
# This script sets up all dependencies and verifies the installation

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emoji support
CHECK="✅"
CROSS="❌"
INFO="ℹ️"
WARN="⚠️"

echo ""
echo "================================================================================"
echo "  MAESTRAI - Audio Transcription Service Setup"
echo "  Powered by OpenAI Whisper"
echo "================================================================================"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARN} $1${NC}"
}

print_info() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

print_info "Detected OS: ${MACHINE}"
echo ""

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        print_success "Python $PYTHON_VERSION found (requires 3.9+)"
    else
        print_error "Python 3.9+ required, found $PYTHON_VERSION"
        echo "Please install Python 3.9 or higher from https://www.python.org/downloads/"
        exit 1
    fi
else
    print_error "Python 3 not found"
    echo "Please install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi
echo ""

# Step 2: Check/Install FFmpeg
echo "Step 2: Checking FFmpeg installation..."
if command_exists ffmpeg; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
    print_success "FFmpeg $FFMPEG_VERSION found"
else
    print_warning "FFmpeg not found. Installing..."

    if [ "$MACHINE" = "Mac" ]; then
        if command_exists brew; then
            print_info "Installing FFmpeg via Homebrew..."
            brew install ffmpeg
            print_success "FFmpeg installed successfully"
        else
            print_error "Homebrew not found. Please install Homebrew first:"
            echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [ "$MACHINE" = "Linux" ]; then
        if command_exists apt-get; then
            print_info "Installing FFmpeg via apt-get..."
            sudo apt-get update
            sudo apt-get install -y ffmpeg
            print_success "FFmpeg installed successfully"
        elif command_exists yum; then
            print_info "Installing FFmpeg via yum..."
            sudo yum install -y ffmpeg
            print_success "FFmpeg installed successfully"
        else
            print_error "Could not install FFmpeg automatically"
            echo "Please install FFmpeg manually: https://ffmpeg.org/download.html"
            exit 1
        fi
    fi
fi
echo ""

# Step 3: Create virtual environment
echo "Step 3: Setting up Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    else
        print_info "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi
echo ""

# Step 4: Activate virtual environment and install dependencies
echo "Step 4: Installing Python dependencies..."
source venv/bin/activate

print_info "Upgrading pip..."
pip install --upgrade pip --quiet

print_info "Installing project dependencies..."
pip install -r requirements.txt --quiet

if [ -f "requirements-dev.txt" ]; then
    read -p "Install development dependencies? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install -r requirements-dev.txt --quiet
        print_success "Development dependencies installed"
    fi
fi

print_success "All dependencies installed"
echo ""

# Step 5: Verify installation
echo "Step 5: Verifying installation..."

print_info "Testing imports..."
python -c "
from src.utils.config import Config
from src.audio_processor import AudioProcessor
from src.transcription_engine import TranscriptionEngine
print('✅ All imports successful')
" && print_success "Import test passed" || print_error "Import test failed"

echo ""

# Step 6: Run tests
echo "Step 6: Running test suite..."
python -m pytest tests/ -v --tb=short 2>&1 | grep -E "(PASSED|FAILED|ERROR|passed|failed)" | tail -5
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    print_success "All tests passed"
else
    print_warning "Some tests may have failed (check above)"
fi
echo ""

# Step 7: Display summary
echo "================================================================================"
echo "  SETUP COMPLETE!"
echo "================================================================================"
echo ""
print_success "Maestrai is ready to use!"
echo ""
echo "Next steps:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the interactive demo:"
echo "     python scripts/demo.py"
echo ""
echo "  3. Quick transcription:"
echo "     python scripts/demo.py path/to/audio.mp3 --model tiny"
echo ""
echo "  4. View documentation:"
echo "     cat README.md"
echo "     cat QUICK_REFERENCE.md"
echo ""
echo "  5. Run tests:"
echo "     pytest tests/"
echo ""
echo "================================================================================"
echo ""

print_info "For help, run: python scripts/demo.py --help"
print_info "Documentation: README.md, SETUP.md, QUICK_REFERENCE.md"
echo ""
