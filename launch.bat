@echo off
title Sentinel Buddy Launcher
echo ========================================
echo   Sentinel Buddy — Starting up...
echo ========================================
echo.

:: Install dependencies silently if not present
pip install -r requirements.txt --quiet

:: Launch the app
python sentinel_buddy.py

pause
