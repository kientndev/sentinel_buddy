@echo off
title Sentinel Buddy Desktop Launcher
echo ========================================
echo   Sentinel Buddy Desktop - Starting up...
echo ========================================
echo.

:: Try to find Python in common locations
set PYTHON_CMD=
set PIP_CMD=

:: Check if python is in PATH
python --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=python
    set PIP_CMD=pip
    echo Found Python in PATH
    goto :found
)

:: Check common Python installation paths
if exist "C:\Python39\python.exe" (
    set PYTHON_CMD=C:\Python39\python.exe
    set PIP_CMD=C:\Python39\Scripts\pip.exe
    echo Found Python 3.9 in C:\Python39
    goto :found
)

if exist "C:\Python310\python.exe" (
    set PYTHON_CMD=C:\Python310\python.exe
    set PIP_CMD=C:\Python310\Scripts\pip.exe
    echo Found Python 3.10 in C:\Python310
    goto :found
)

if exist "C:\Python311\python.exe" (
    set PYTHON_CMD=C:\Python311\python.exe
    set PIP_CMD=C:\Python311\Scripts\pip.exe
    echo Found Python 3.11 in C:\Python311
    goto :found
)

if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    set PIP_CMD=C:\Python312\Scripts\pip.exe
    echo Found Python 3.12 in C:\Python312
    goto :found
)

:: Check AppData\Local\Programs\Python
if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python39\python.exe
    set PIP_CMD=%LOCALAPPDATA%\Programs\Python\Python39\Scripts\pip.exe
    echo Found Python 3.9 in AppData
    goto :found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
    set PIP_CMD=%LOCALAPPDATA%\Programs\Python\Python310\Scripts\pip.exe
    echo Found Python 3.10 in AppData
    goto :found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    set PIP_CMD=%LOCALAPPDATA%\Programs\Python\Python311\Scripts\pip.exe
    echo Found Python 3.11 in AppData
    goto :found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    set PIP_CMD=%LOCALAPPDATA%\Programs\Python\Python312\Scripts\pip.exe
    echo Found Python 3.12 in AppData
    goto :found
)

:: Try py launcher (Windows Python launcher)
py --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=py
    set PIP_CMD=py -m pip
    echo Found Python launcher (py)
    goto :found
)

echo Python not found! Please install Python first.
echo Download from: https://www.python.org/downloads/
pause
exit /b 1

:found
echo Using Python: %PYTHON_CMD%
echo Using pip: %PIP_CMD%

:: Install dependencies if not present
echo Installing dependencies...
%PIP_CMD% install -r requirements_desktop.txt

:: Launch the desktop app
echo Starting Sentinel Buddy...
%PYTHON_CMD% sentinel_buddy_desktop.py

pause
