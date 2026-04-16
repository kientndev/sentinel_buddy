# Sentinel Buddy - Standalone Desktop Application Build Guide

## Overview

Sentinel Buddy is a high-performance standalone desktop application (.exe) that functions as a "System Operator" AI assistant. It features advanced visual effects, system tray integration, ghost typing, and real-time system logging.

## Features

### Core Capabilities
- **Lightning Aura Effect**: Electric-blue pulsing border animation during AI execution
- **System Tray Integration**: Background operation with hotkey (Ctrl+Shift+S) support
- **Ghost Typing**: Real-time character-by-character text injection using pyautogui
- **System Logs**: Real-time activity logging in the application interface
- **Native Web Opener**: Direct browser integration for quick URL access
- **Always-on-Top Design**: Sidebar-style window that stays above other applications

### Advanced Features
- **Multi-Command Support**: Special commands for system actions
- **Groq AI Integration**: Fast Llama 3.1-8b-instant model responses
- **Error Handling**: Robust retry logic and error management
- **Auto-Connect**: Automatic API key configuration
- **Hotkey Summoning**: Show/hide application with Ctrl+Shift+S

## Prerequisites

### Required Software
- **Python 3.8+**: [Download here](https://www.python.org/downloads/)
- **pip**: Python package manager (included with Python)
- **Windows 10/11**: Desktop application is Windows-specific

### Required Python Packages
All dependencies are listed in `requirements_desktop.txt`:
- `groq>=0.4.1` - Groq AI SDK
- `pyautogui>=0.9.54` - Ghost typing and automation
- `pystray>=0.19.5` - System tray integration
- `Pillow>=10.0.0` - Image processing for icons
- `keyboard>=0.13.5` - Global hotkey support
- `python-dotenv>=1.0.0` - Environment variable management

## Installation

### Step 1: Install Dependencies

Open Command Prompt or PowerShell in the `sentinel_buddy` directory:

```cmd
pip install -r requirements_desktop.txt
```

### Step 2: Set API Key

The application comes with a pre-configured Groq API key. If you need to change it:

**Option A - Environment Variable:**
```cmd
set GROQ_API_KEY=your_groq_api_key_here
```

**Option B - Manual Entry:**
- Launch the application
- Enter your Groq API key in the input field
- Click the ▶ button to connect

Get your free Groq API key: https://console.groq.com/keys

## Building the Standalone EXE

### Automated Build (Recommended)

Run the automated build script:

```cmd
build_exe.bat
```

This script will:
1. Check Python installation
2. Install all dependencies
3. Install PyInstaller if needed
4. Build the standalone EXE
5. Place the executable in the `dist` folder

### Manual Build

If you prefer manual control:

```cmd
# Install PyInstaller
pip install pyinstaller

# Build the EXE using the spec file
pyinstaller sentinel_buddy.spec
```

### Build Configuration

The `sentinel_buddy.spec` file configures:
- **Single File**: `--onefile` - All dependencies bundled into one EXE
- **Windowed Mode**: `--noconsole` - No terminal window appears
- **Hidden Imports**: Groq, pyautogui, pystray, PIL, keyboard
- **Icon**: Custom icon (if `icon.ico` exists)

## Using the Application

### Launching the Application

**Development Mode:**
```cmd
python sentinel_buddy_desktop.py
```

**Standalone EXE:**
```cmd
dist\SentinelBuddy.exe
```

### Special Commands

The application supports special system commands:

1. **"Open Sentinel"** - Opens the SentinelPhish AI dashboard
   ```
   Open Sentinel
   ```

2. **"Dojo Mode"** - Opens Spotify 2010s playlist
   ```
   Dojo Mode
   ```

3. **"Type [text]"** - Ghost types text into the active window
   ```
   Type Hello World
   ```

### System Tray Features

- **Show/Hide**: Right-click the tray icon and select "Show" or "Hide"
- **Hotkey**: Press `Ctrl+Shift+S` to toggle window visibility
- **Quit**: Right-click the tray icon and select "Quit"

### Lightning Aura Effect

The Lightning Aura activates during:
- AI thinking/processing
- System command execution
- Ghost typing operations

The electric-blue border pulses to indicate active processing.

### System Logs

The system log at the bottom shows:
- User messages
- AI thinking states
- System command executions
- Error messages
- Activity timestamps

## Troubleshooting

### Build Issues

**PyInstaller fails to build:**
```cmd
# Try alternative build method
pyinstaller --onefile --windowed --name "SentinelBuddy" --hiddenimports=groq,pyautogui,pystray,PIL,keyboard sentinel_buddy_desktop.py
```

**Missing dependencies:**
```cmd
pip install --upgrade -r requirements_desktop.txt
```

### Runtime Issues

**Hotkey not working:**
- Run as Administrator
- Check if keyboard library is installed
- Verify no other application is using Ctrl+Shift+S

**Ghost typing not working:**
- Ensure the target window has focus
- Run as Administrator
- Check pyautogui installation

**System tray icon not appearing:**
- Check pystray installation
- Verify Pillow is installed
- Run as Administrator

### API Issues

**Invalid API key error:**
- Verify your Groq API key is correct
- Check if the key has expired
- Ensure you have credits on your Groq account

**Rate limit errors:**
- Wait a moment and try again
- The application includes automatic retry logic

## File Structure

```
sentinel_buddy/
├── sentinel_buddy_desktop.py    # Main application file
├── requirements_desktop.txt     # Python dependencies
├── sentinel_buddy.spec          # PyInstaller configuration
├── build_exe.bat                # Automated build script
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
└── dist/                        # Build output folder
    └── SentinelBuddy.exe         # Standalone executable
```

## Advanced Configuration

### Customizing the Application

**Window Position:** Edit `sentinel_buddy_desktop.py`:
```python
SIDEBAR_WIDTH = 300
SIDEBAR_HEIGHT_PERCENT = 0.92
```

**Colors:** Edit the color constants:
```python
BG_PRIMARY = "#0D0F14"
ACCENT_COLOR = "#7C6BFF"
# etc.
```

**System Commands:** Add new commands to `SYSTEM_COMMANDS`:
```python
SYSTEM_COMMANDS = {
    "your command": {
        "type": "url",
        "target": "https://example.com",
        "label": "Opening example...",
    },
}
```

### Adding Custom Icons

Create a 256x256 pixel icon named `icon.ico` in the project root. PyInstaller will automatically use it for the EXE.

## Security Notes

- The API key is embedded in the application code
- For production, use environment variables or secure key storage
- The application requires Administrator privileges for some features
- Ghost typing can type into any active window - use carefully

## Performance Optimization

The standalone EXE is optimized for:
- Fast startup time
- Minimal memory footprint
- Efficient background processing
- Smooth animations

## Distribution

To distribute the application:
1. Build the EXE using the build script
2. Test the standalone EXE thoroughly
3. Package the EXE with a README
4. Optionally create an installer using NSIS or Inno Setup

## Support

For issues and questions:
- Check the troubleshooting section
- Review Groq API documentation
- Verify Python and dependency versions

## License

MIT License - See LICENSE file for details

---

**Built with ❤️ using Python, Groq AI, and PyInstaller**
