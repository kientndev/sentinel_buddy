@echo off
REM Sentinel Buddy - Build Script for Standalone EXE
REM This script builds the standalone executable using PyInstaller

echo ========================================
echo   Sentinel Buddy - Building Standalone EXE
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements_desktop.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully
echo.

REM Install PyInstaller if not already installed
echo Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
) else (
    echo PyInstaller already installed
)

echo.
echo ========================================
echo   Building Standalone EXE
echo ========================================
echo.

REM Build the executable using the spec file
echo Building with PyInstaller...
pyinstaller sentinel_buddy.spec
if %ERRORLEVEL% neq 0 (
    echo ERROR: PyInstaller build failed
    echo Trying alternative build method...
    pyinstaller --onefile --windowed --name "SentinelBuddy" --hiddenimports=groq,pyautogui,pystray,PIL,keyboard sentinel_buddy_desktop.py
    if %ERRORLEVEL% neq 0 (
        echo ERROR: PyInstaller build failed again
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo The standalone EXE should be in the 'dist' folder
echo Location: dist\SentinelBuddy.exe
echo.
echo To test the application:
echo   1. Navigate to the dist folder
echo   2. Run SentinelBuddy.exe
echo.
pause
