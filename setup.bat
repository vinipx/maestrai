@echo off
REM Maestrai Setup Script for Windows
REM This script sets up all dependencies and verifies the installation

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo   MAESTRAI - Audio Transcription Service Setup
echo   Powered by OpenAI Whisper
echo ================================================================================
echo.

REM Step 1: Check Python version
echo Step 1: Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [✓] Python %PYTHON_VERSION% found
echo.

REM Step 2: Check FFmpeg
echo Step 2: Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [!] FFmpeg not found
    echo.
    echo Installing FFmpeg via Chocolatey...
    echo.
    choco --version >nul 2>&1
    if errorlevel 1 (
        echo [!] Chocolatey not found
        echo.
        echo Please install FFmpeg manually:
        echo   1. Using Chocolatey ^(recommended^):
        echo      - Install Chocolatey from https://chocolatey.org/install
        echo      - Run: choco install ffmpeg
        echo.
        echo   2. Manual installation:
        echo      - Download from https://ffmpeg.org/download.html
        echo      - Extract to C:\ffmpeg
        echo      - Add C:\ffmpeg\bin to PATH
        echo.
        pause
        exit /b 1
    ) else (
        echo Installing FFmpeg...
        choco install ffmpeg -y
        if errorlevel 1 (
            echo [X] FFmpeg installation failed
            pause
            exit /b 1
        )
        echo [✓] FFmpeg installed successfully
    )
) else (
    for /f "tokens=3" %%i in ('ffmpeg -version ^| findstr /C:"ffmpeg version"') do set FFMPEG_VERSION=%%i
    echo [✓] FFmpeg !FFMPEG_VERSION! found
)
echo.

REM Step 3: Create virtual environment
echo Step 3: Setting up Python virtual environment...
if exist venv (
    echo [!] Virtual environment already exists
    set /p RECREATE="Recreate it? (y/n): "
    if /i "!RECREATE!"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
        python -m venv venv
        echo [✓] Virtual environment recreated
    ) else (
        echo [i] Using existing virtual environment
    )
) else (
    python -m venv venv
    echo [✓] Virtual environment created
)
echo.

REM Step 4: Activate virtual environment and install dependencies
echo Step 4: Installing Python dependencies...
call venv\Scripts\activate.bat

echo [i] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo [i] Installing project dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [X] Failed to install dependencies
    pause
    exit /b 1
)

if exist requirements-dev.txt (
    set /p INSTALL_DEV="Install development dependencies? (y/n): "
    if /i "!INSTALL_DEV!"=="y" (
        pip install -r requirements-dev.txt --quiet
        echo [✓] Development dependencies installed
    )
)

echo [✓] All dependencies installed
echo.

REM Step 5: Verify installation
echo Step 5: Verifying installation...

echo [i] Testing imports...
python -c "from src.utils.config import Config; from src.audio_processor import AudioProcessor; from src.transcription_engine import TranscriptionEngine; print('[✓] All imports successful')"
if errorlevel 1 (
    echo [X] Import test failed
    pause
    exit /b 1
)
echo.

REM Step 6: Run tests
echo Step 6: Running test suite...
python -m pytest tests/ -v --tb=short
if errorlevel 1 (
    echo [!] Some tests may have failed ^(check above^)
) else (
    echo [✓] All tests passed
)
echo.

REM Step 7: Display summary
echo ================================================================================
echo   SETUP COMPLETE!
echo ================================================================================
echo.
echo [✓] Maestrai is ready to use!
echo.
echo Next steps:
echo.
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Run the interactive demo:
echo      python scripts\demo.py
echo.
echo   3. Quick transcription:
echo      python scripts\demo.py path\to\audio.mp3 --model tiny
echo.
echo   4. View documentation:
echo      type README.md
echo      type QUICK_REFERENCE.md
echo.
echo   5. Run tests:
echo      pytest tests\
echo.
echo ================================================================================
echo.

echo [i] For help, run: python scripts\demo.py --help
echo [i] Documentation: README.md, SETUP.md, QUICK_REFERENCE.md
echo.

pause
