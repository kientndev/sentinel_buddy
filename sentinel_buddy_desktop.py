"""
Sentinel Buddy - Full-Screen Pro AI Dashboard with System Automation
=====================================================================
A modular AI assistant with Brain (AI) and Body (UI + Automation Tools)

Tech Stack: Python + tkinter + Groq API + pyautogui
UI Style: Full-screen dashboard with collapsible sidebar, centered chat
Features: Intent Detection, Web Search, Ghost Typing, App Launching, Lightning Aura

HOW TO USE:
-----------
1. Install dependencies:
   pip install groq pyautogui pystray Pillow keyboard python-dotenv

2. Run:
   python sentinel_buddy_desktop.py

3. Intent Commands (auto-detected from AI responses):
   - "Open [website]"      -> Opens website in browser
   - "Type this: [text]"   -> Ghost types text with delay
   - "Launch [app.exe]"    -> Launches local application

Architecture:
- Brain: AI processing with Groq API
- Body: UI components and Automation Tools layer
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import webbrowser
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import time
import pyautogui
import pystray
from PIL import Image, ImageDraw
import keyboard
from dotenv import load_dotenv
import difflib
import urllib.parse

# Configuration - Full-Screen Pro Dashboard
APP_TITLE = "Sentinel Buddy Pro"
SIDEBAR_EXPANDED = 200          # Expanded sidebar width
SIDEBAR_COLLAPSED = 50          # Collapsed sidebar width
CHAT_MAX_WIDTH = 800            # Max width for centered chat (ChatGPT style)

# Colors - Lightning Aura Theme
BG_PRIMARY = "#0A0A0A"          # Deep black background
BG_SECONDARY = "#1E1E1E"        # Sidebar/cards (dark mode)
BG_SIDEBAR = "#f0f2f5"          # Light grey sidebar (Gemini style)
BG_INPUT = "#2D2D2D"            # Input field
BG_CHAT = "#121212"             # Chat area background
ACCENT_COLOR = "#7C6BFF"        # Neon purple accent
ACCENT_GLOW = "#00D4FF"         # Lightning blue glow
TEXT_PRIMARY = "#FFFFFF"        # White main text
TEXT_SECONDARY = "#A0A0A0"      # Grey subtext
TEXT_SYSTEM = "#888888"         # System message grey
TEXT_SIDEBAR = "#1a1a1a"        # Dark text for light sidebar
ACTIVE_CHAT = "#cce5ff"         # Active chat blue bubble

# Bubble Colors
BUBBLE_USER = "#2A1F4E"         # Deep purple for user
BUBBLE_AI = "#1A1A1A"           # Stealth grey for AI
BUBBLE_SYSTEM = "#1E1E1E"       # System messages

# System Commands
SYSTEM_COMMANDS = {
    "open sentinel": {
        "type": "url",
        "target": "https://sentinelphishai.vercel.app",
        "label": "Opening SentinelPhish AI Dashboard...",
    },
    "dojo mode": {
        "type": "url",
        "target": "https://open.spotify.com/playlist/37i9dQZF1DX5Ejj0EkURtP",
        "label": "Activating Dojo Mode \ud83c\udfb5 Opening Spotify...",
    },
    "type": {
        "type": "ghost_type",
        "label": "Ghost typing: ",
    },
}

# Load API key from .env file (with path-aware loading)
try:
    # This finds the actual folder where your script lives
    script_dir = Path(__file__).parent.absolute()
    env_path = script_dir / ".env"
    
    # Load the specific path
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        DEFAULT_API_KEY = api_key.strip()
    else:
        DEFAULT_API_KEY = ""
except Exception:
    DEFAULT_API_KEY = ""


# ============================================================================
# BRAIN - AI Processing Layer
# ============================================================================
class Brain:
    """Handles all AI processing with Groq API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Groq client."""
        try:
            import groq
            self.client = groq.Groq(api_key=self.api_key)
        except Exception as e:
            print(f"Failed to initialize Groq client: {e}")
    
    def process_message(self, user_message: str) -> dict:
        """Process user message and return response with intent detection."""
        if not self.client:
            return {"error": "AI client not initialized", "content": None, "intent": None}
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": """You are Sentinel Buddy Pro, an advanced AI assistant with system automation capabilities.
                        
When you want to perform actions, use these formats:
- To open a website: say "Open [URL or website name]"
- To type text: say "Type this: [text to type]"
- To launch an app: say "Launch [application name or path]"

Example responses:
"I'll open Google for you. Open google.com"
"Let me type that for you. Type this: Hello World"
"Launching Calculator. Launch calc.exe"

Keep responses concise and actionable. Use markdown sparingly."""
                    },
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1024,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            intent = self._detect_intent(content)
            
            return {"content": content, "intent": intent, "error": None}
            
        except Exception as e:
            return {"error": str(e), "content": None, "intent": None}
    
    def _detect_intent(self, text: str) -> dict:
        """Detect automation intents from AI response."""
        text_lower = text.lower()
        intent = {"type": None, "action": None, "params": {}}
        
        # Check for Clean Mind Filter first
        if not AutomationTools.is_safe_query(text):
            return {
                "type": "blocked",
                "action": "block",
                "params": {
                    "response": "I don't do that kind of content. Let's get back to work."
                }
            }
        
        # Check for search intent ("search for...", "look up...", "what is...", "find...", "google...")
        if any(trigger in text_lower for trigger in ["search for", "look up", "what is", "who is", "where is", "how to", "find", "google"]):
            # Strip the trigger words for clean query extraction
            clean_query = text_lower.replace('search for', '').replace('look up', '').replace('what is', '').replace('who is', '').replace('where is', '').replace('how to', '').replace('find', '').replace('google', '').strip()
            query = clean_query if clean_query else text_lower
            
            # Check for lyrics queries to prioritize high-authority sites
            if "lyrics" in text_lower:
                priority_site = "genius" if "genius" in text_lower else "azlyrics"
                intent = {
                    "type": "web_search",
                    "action": "search_google",
                    "params": {
                        "query": query,
                        "safe_search": True,
                        "priority_site": priority_site
                    }
                }
                return intent
            
            intent = {
                "type": "web_search",
                "action": "search_google",
                "params": {
                    "query": query,
                    "safe_search": True
                }
            }
            return intent
        
        # Check for Dojo Timer intent
        if "dojo timer" in text_lower or "timer" in text_lower:
            # Extract minutes
            parts = text_lower.split()
            for part in parts:
                if part.isdigit():
                    minutes = int(part)
                    intent = {
                        "type": "dojo_timer",
                        "action": "start_timer",
                        "params": {
                            "minutes": minutes
                        }
                    }
                    return intent
        
        # Check for combined commands (automation chain)
        if " and " in text_lower:
            # Detect combined commands like "Open Spotify and type: Godzilla"
            actions = []
            
            # Check for web/app launch
            for app_name in list(AutomationTools.APP_MAPPING.keys()) + list(AutomationTools.WEB_MAPPING.keys()):
                if f"open {app_name}" in text_lower:
                    if app_name in AutomationTools.WEB_MAPPING:
                        actions.append({"type": "web_open", "params": {"site": app_name}})
                    else:
                        actions.append({"type": "app_launch", "params": {"app": app_name}})
                    break
            
            # Check for ghost typing
            if "type:" in text_lower or "type this:" in text_lower:
                parts = text.split("type", 1)
                if len(parts) > 1:
                    text_to_type = parts[1].split(":", 1)[1].strip() if ":" in parts[1] else parts[1].strip()
                    actions.append({"type": "ghost_type", "params": {"text": text_to_type}})
            
            if len(actions) > 1:
                intent = {"type": "automation_chain", "action": "chain", "params": {"actions": actions}}
                return intent
        
        # App Launch Intent (check against APP_MAPPING first)
        for app_name in AutomationTools.APP_MAPPING.keys():
            if f"open {app_name}" in text_lower or f"launch {app_name}" in text_lower:
                intent = {"type": "app_launch", "action": "launch_app", "params": {"app": app_name}}
                return intent
        
        # Web Search Intent (check WEB_MAPPING first)
        for site_name in AutomationTools.WEB_MAPPING.keys():
            if f"open {site_name}" in text_lower:
                intent = {"type": "web_open", "action": "open_url", "params": {"site": site_name}}
                return intent
        
        # Generic web open
        if "open " in text_lower:
            parts = text_lower.split("open ")
            if len(parts) > 1:
                site_part = parts[1].split()[0]
                intent = {"type": "web_open", "action": "open_url", "params": {"site": site_part}}
        
        # Ghost Typing Intent
        elif "type this:" in text_lower or "type:" in text_lower:
            parts = text.split("type", 1)
            if len(parts) > 1:
                text_to_type = parts[1].split(":", 1)[1].strip() if ":" in parts[1] else parts[1].strip()
                intent = {"type": "ghost_type", "action": "type_text", "params": {"text": text_to_type}}
        
        return intent


# ============================================================================
# AUTOMATION TOOLS - System Action Layer
# ============================================================================
class AutomationTools:
    """Handles all system automation tasks."""
    
    # Natural Language App Mapping (no .exe needed)
    # For full paths, use double backslashes: "C:\\Program Files\\Spotify\\Spotify.exe"
    APP_MAPPING = {
        "chrome": "chrome",
        "notepad": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "edge": "msedge",
        "explorer": "explorer",
        "cmd": "cmd",
        "powershell": "powershell",
        "vscode": "code",
        "spotify": "spotify",  # Or use full path: "C:\\Users\\YourName\\AppData\\Roaming\\Spotify\\Spotify.exe"
        "discord": "discord",  # Or use full path: "C:\\Users\\YourName\\AppData\\Local\\Discord\\Update.exe"
        "slack": "slack",
        "teams": "ms-teams",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "outlook": "outlook",
        # Example of full path format:
        # "zalo": "C:\\Program Files\\Zalo\\Zalo.exe",
    }
    
    # Web Mapping Dictionary for common sites
    WEB_MAPPING = {
        "spotify": "https://open.spotify.com",
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com",
        "discord": "https://discord.com/app",
        "twitter": "https://twitter.com",
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com",
        "linkedin": "https://linkedin.com",
        "reddit": "https://reddit.com",
        "amazon": "https://amazon.com",
        "netflix": "https://netflix.com",
        "chatgpt": "https://chat.openai.com",
        "openai": "https://openai.com",
        "genius": "https://genius.com",
        "azlyrics": "https://azlyrics.com",
    }
    
    # Forbidden keywords for Clean Mind Filter
    FORBIDDEN_KEYWORDS = [
        "porn", "xxx", "adult", "nude", "sex", "nsfw", 
        "erotic", "hentai", "xxx", "pornography"
    ]
    
    @staticmethod
    def is_safe_query(query: str) -> bool:
        """Check if query contains forbidden keywords."""
        query_lower = query.lower()
        for keyword in AutomationTools.FORBIDDEN_KEYWORDS:
            if keyword in query_lower:
                return False
        return True
    
    # App cache file
    APP_CACHE_FILE = "paths.json"
    
    @staticmethod
    def _load_app_cache():
        """Load app paths from cache file."""
        try:
            if os.path.exists(AutomationTools.APP_CACHE_FILE):
                with open(AutomationTools.APP_CACHE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load app cache: {e}")
        return {}
    
    @staticmethod
    def _save_app_cache(cache):
        """Save app paths to cache file."""
        try:
            with open(AutomationTools.APP_CACHE_FILE, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Failed to save app cache: {e}")
    
    @staticmethod
    def find_app_path(app_name: str, callback=None):
        """Find app path by scanning common directories and using fuzzy matching."""
        # Load cache
        cache = AutomationTools._load_app_cache()
        app_lower = app_name.lower()
        
        # Check cache first
        if app_lower in cache:
            return cache[app_lower]
        
        # Common install directories
        search_dirs = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.join(os.environ.get('LOCALAPPDATA', ''), ''),
        ]
        
        # Scan directories for .exe files
        found_apps = {}
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            try:
                for root, dirs, files in os.walk(search_dir):
                    for file in files:
                        if file.lower().endswith('.exe'):
                            # Remove .exe extension for matching
                            name_key = file[:-4].lower()
                            found_apps[name_key] = os.path.join(root, file)
            except Exception as e:
                print(f"Error scanning {search_dir}: {e}")
                continue
        
        # Registry scanning (optional but pro)
        try:
            import winreg
            uninstall_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                         r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            for i in range(winreg.QueryInfoKey(uninstall_key)[0]):
                try:
                    subkey_name = winreg.EnumKey(uninstall_key, i)
                    subkey = winreg.OpenKey(uninstall_key, subkey_name)
                    try:
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        if install_location:
                            # Scan install location for .exe
                            if os.path.exists(install_location):
                                for root, dirs, files in os.walk(install_location):
                                    for file in files:
                                        if file.lower().endswith('.exe'):
                                            name_key = file[:-4].lower()
                                            found_apps[name_key] = os.path.join(root, file)
                                            # Also store by display name
                                            found_apps[display_name.lower()] = os.path.join(root, file)
                    except FileNotFoundError:
                        pass
                    winreg.CloseKey(subkey)
                except Exception as e:
                    pass
            winreg.CloseKey(uninstall_key)
        except Exception as e:
            print(f"Registry scanning failed: {e}")
        
        # Fuzzy matching
        app_names = list(found_apps.keys())
        matches = difflib.get_close_matches(app_lower, app_names, n=1, cutoff=0.6)
        
        if matches:
            best_match = matches[0]
            app_path = found_apps[best_match]
            
            # Log the find
            if callback:
                callback(f"[ACTION] Found {app_name} at: {app_path}")
            
            # Cache the result
            cache[app_lower] = app_path
            AutomationTools._save_app_cache(cache)
            
            return app_path
        
        if callback:
            callback(f"[ERROR] Could not find app: {app_name}")
        return None
    
    @staticmethod
    def open_website(site: str, callback=None) -> bool:
        """Open a website with smart mapping, fuzzy matching, and auto-completion."""
        try:
            # Sanitize input: remove quotes and spaces
            site = site.strip().strip("'").strip('"')
            
            # Check web mapping first
            site_lower = site.lower()
            if site_lower in AutomationTools.WEB_MAPPING:
                url = AutomationTools.WEB_MAPPING[site_lower]
            else:
                # Fuzzy matching for typos
                site_names = list(AutomationTools.WEB_MAPPING.keys())
                matches = difflib.get_close_matches(site_lower, site_names, n=1, cutoff=0.6)
                if matches:
                    url = AutomationTools.WEB_MAPPING[matches[0]]
                else:
                    # Smart web logic: assume .com if not mapped
                    if not site.startswith("http"):
                        if "." not in site:
                            url = f"https://{site.lower()}.com"
                        else:
                            url = f"https://{site}" if not site.startswith("http") else site
                    else:
                        url = site
            
            # Debug log
            print(f"[DEBUG] Opening URL: {url}")
            if callback:
                callback(f"[SYSTEM] Opening: {url}")
            
            # Print debug statement before execution
            print(f"[LAUNCHING] Website: {url}")
            
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"Failed to open website: {e}")
            if callback:
                callback(f"[ERROR] Failed to open: {site}")
            return False
    
    @staticmethod
    def ghost_type(text: str, callback=None) -> bool:
        """Type text with fast realistic typing using pyautogui."""
        try:
            if callback:
                callback(f"[ACTION] Typing: {text[:30]}{'...' if len(text) > 30 else ''}")
            pyautogui.write(text, interval=0.01)
            return True
        except Exception as e:
            print(f"Ghost typing failed: {e}")
            if callback:
                callback(f"[ERROR] Ghost typing failed: {str(e)}")
            return False
    
    @staticmethod
    def launch_application(app_name: str, callback=None) -> bool:
        """Launch an application using dynamic system scanner with subprocess.Popen to prevent blocking."""
        try:
            # Try dynamic app search first
            app_path = AutomationTools.find_app_path(app_name, callback)
            if app_path:
                # Special log for Zalo/Roblox (apps with background processes)
                if any(special in app_name.lower() for special in ["zalo", "roblox"]):
                    if callback:
                        callback(f"[SYSTEM] Handing execution to Windows Shell for: {app_name}")
                else:
                    if callback:
                        callback(f"[ACTION] Launching: {app_path}")
                
                # Use abspath to ensure the .exe sees the real drive path
                absolute_path = os.path.abspath(app_path)
                print(f"[LAUNCHING] Application: {absolute_path}")
                # Use subprocess.Popen with shell=True to prevent waiting
                subprocess.Popen(absolute_path, shell=True)
                print(f"SUCCESS: Launched {absolute_path}")
                return True
            
            # Fallback to app mapping
            app_lower = app_name.lower()
            if app_lower in AutomationTools.APP_MAPPING:
                exe_path = AutomationTools.APP_MAPPING[app_lower]
                if callback:
                    callback(f"[ACTION] Launching: {app_name}")
                
                # Use abspath to ensure the .exe sees the real drive path
                absolute_path = os.path.abspath(exe_path)
                print(f"[LAUNCHING] Application: {absolute_path}")
                # Use subprocess.Popen with shell=True to prevent waiting
                subprocess.Popen(absolute_path, shell=True)
                print(f"SUCCESS: Launched {absolute_path}")
                return True
            
            # Try to launch directly with quote protection
            if not app_name.endswith('.exe'):
                app_name += '.exe'
            
            # Use abspath to ensure the .exe sees the real drive path
            absolute_path = os.path.abspath(app_name)
            print(f"[LAUNCHING] Application: {absolute_path}")
            # Use subprocess.Popen with shell=True to prevent waiting
            subprocess.Popen(absolute_path, shell=True)
            print(f"SUCCESS: Launched {absolute_path}")
            if callback:
                callback(f"[ACTION] Launching: {app_name}")
            return True
        except Exception as e:
            error_msg = f"ERROR: Could not launch {app_name}. {str(e)}"
            print(error_msg)
            if callback:
                callback(f"[ERROR] {error_msg}")
            return False
    
    @staticmethod
    def execute_automation_chain(actions: list, callback=None):
        """Execute a chain of automation actions with delays."""
        def execute_chain():
            for i, action in enumerate(actions):
                action_type = action.get("type")
                params = action.get("params", {})
                
                if action_type == "web_open":
                    site = params.get("site", params.get("url", ""))
                    AutomationTools.open_website(site, callback)
                    time.sleep(2)  # Wait for page to load
                
                elif action_type == "app_launch":
                    app = params.get("app", "")
                    AutomationTools.launch_application(app, callback)
                    time.sleep(1)  # Wait for app to launch
                
                elif action_type == "ghost_type":
                    text = params.get("text", "")
                    AutomationTools.ghost_type(text, callback)
        
        # Run in background thread
        threading.Thread(target=execute_chain, daemon=True).start()
    
    @staticmethod
    def quick_search(query: str):
        """Quick Google search for fast response (110 WPM input speed)."""
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        # Play click sound effect
        try:
            import winsound
            winsound.Beep(1000, 50)  # 1000Hz frequency, 50ms duration
        except Exception:
            pass  # Fallback silently if winsound is not available
        webbrowser.open(search_url)
    
    @staticmethod
    def execute_intent(intent: dict, callback=None) -> str:
        """Execute detected intent and return result message."""
        if not intent or not intent.get("type"):
            return None
        
        action_type = intent.get("type")
        params = intent.get("params", {})
        result = None
        
        # Handle blocked intent (Clean Mind Filter)
        if action_type == "blocked":
            response = params.get("response", "I don't do that kind of content. Let's get back to work.")
            if callback:
                callback(f"[BLOCKED] Safety Filter Triggered")
            return response
        
        # Handle web_search intent with SafeSearch
        elif action_type == "web_search":
            query = params.get("query", "")
            safe_search = params.get("safe_search", True)
            priority_site = params.get("priority_site")
            
            # URL-encode the query
            encoded_query = urllib.parse.quote(query)
            
            # Build Google search URL with SafeSearch
            search_url = f"https://www.google.com/search?q={encoded_query}"
            if safe_search:
                search_url += "&safe=active"
            
            # If priority site specified, try to use it
            if priority_site == "genius" and "genius" in AutomationTools.WEB_MAPPING:
                search_url = f"{AutomationTools.WEB_MAPPING['genius']}/search?q={encoded_query}"
            elif priority_site == "azlyrics" and "azlyrics" in AutomationTools.WEB_MAPPING:
                search_url = f"{AutomationTools.WEB_MAPPING['azlyrics']}/search?q={encoded_query}"
            
            if callback:
                callback(f"[SYSTEM] Searching: {query}")
            webbrowser.open(search_url)
            result = f"🔍 Searching for: {query}"
        
        # Handle Dojo Timer intent
        elif action_type == "dojo_timer":
            minutes = params.get("minutes", 5)
            if callback:
                callback(f"[SYSTEM] Dojo Timer started: {minutes} minutes")
            result = f"⏱️ Dojo Timer: {minutes} minutes"
        
        elif action_type == "web_open":
            site = params.get("site", params.get("url", ""))
            if AutomationTools.open_website(site, callback):
                result = f"🔗 Opened: {site}"
        
        elif action_type == "ghost_type":
            text = params.get("text", "")
            if AutomationTools.ghost_type(text, callback):
                result = f"⌨️ Typed: {text[:30]}{'...' if len(text) > 30 else ''}"
        
        elif action_type == "app_launch":
            app = params.get("app", "")
            # Wrap in background thread to prevent blocking main Tkinter loop
            # Don't pass callback to avoid UI thread-safety issues
            threading.Thread(target=AutomationTools.launch_application, args=(app, None), daemon=True).start()
            result = f"🚀 Launched: {app}"
        
        elif action_type == "automation_chain":
            actions = params.get("actions", [])
            AutomationTools.execute_automation_chain(actions, callback)
            result = "🔗 Executing automation chain..."
        
        if callback and result:
            callback(result)
        
        return result


# ============================================================================
# BODY - UI and Main Application
# ============================================================================
class SentinelBuddyDesktop:
    """Main application window - Full-Screen Pro AI Dashboard."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.api_key = DEFAULT_API_KEY
        self.chat_history = []
        self.is_thinking = False
        self.is_executing = False
        self.system_logs = []
        
        # Sidebar state
        self.sidebar_expanded = True
        self.sidebar_width = SIDEBAR_EXPANDED
        
        # Key visibility state
        self.key_visible = False
        
        # Lightning Aura animation variables
        self.aura_active = False
        self.aura_frame = None
        self.aura_pulse = 0
        
        # Initialize Brain (AI)
        self.brain = Brain(self.api_key)
        
        # Setup window (full-screen)
        self._setup_window()
        
        # Build UI
        self._build_ui()
        
        # Setup global hotkey (Ctrl + Space)
        self._setup_global_hotkey()
        
        # Auto-connect with default API key
        self._auto_connect_api()
    
    def _setup_window(self):
        """Configure window: full-screen mode."""
        self.root.title(APP_TITLE)
        self.root.state('zoomed')  # Full-screen mode
        self.root.configure(bg=BG_PRIMARY)
        
        # Set window icon
        icon_path = Path(__file__).parent / "assets" / "icon2.png"
        try:
            if icon_path.exists():
                self.root.iconphoto(False, tk.PhotoImage(file=str(icon_path)))
        except Exception as e:
            # Icon not found or error loading, continue without icon
            pass
    
    def _setup_global_hotkey(self):
        """Setup global hotkey (Ctrl + Space) for toggle minimize/restore."""
        try:
            keyboard.add_hotkey('ctrl+space', self._toggle_window_visibility)
        except Exception as e:
            self._add_system_log(f"Failed to setup global hotkey: {e}")
    
    def _toggle_window_visibility(self):
        """Toggle window between minimized and restored state."""
        if self.root.state() == 'iconic' or not self.root.focus_displayof():
            # Restore and focus
            self.root.deiconify()
            self.root.state('zoomed')
            self.root.lift()
            self.root.focus_force()
        else:
            # Minimize
            self.root.iconify()
    
    def _build_lightning_aura(self):
        """Create Lightning Aura border effect frame."""
        self.aura_frame = tk.Frame(self.root, bg=BG_PRIMARY, highlightbackground="#00D4FF", highlightthickness=0)
        self.aura_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.aura_frame.lower()  # Put behind all other widgets
        self.aura_frame.grid_remove()  # Initially hidden
    
    def _start_lightning_aura(self):
        """Start the Lightning Aura animation."""
        self.aura_active = True
        self.aura_frame.grid()
        self.aura_frame.lift()  # Bring to front for border effect
        self._animate_lightning()
    
    def _stop_lightning_aura(self):
        """Stop the Lightning Aura animation."""
        self.aura_active = False
        self.aura_frame.grid_remove()
    
    def _animate_lightning(self):
        """Animate the Lightning Aura border effect."""
        if not self.aura_active:
            return
        
        # Pulse effect
        self.aura_pulse = (self.aura_pulse + 1) % 20
        thickness = 2 if self.aura_pulse < 10 else 4
        self.aura_frame.configure(highlightthickness=thickness)
        
        # Schedule next animation frame
        self.root.after(100, self._animate_lightning)
    
    def _setup_system_tray(self):
        """Setup system tray icon with menu."""
        # Load icon from assets folder
        icon_path = Path(__file__).parent / "assets" / "icon2.png"
        try:
            image = Image.open(icon_path)
            # Resize to 64x64 for system tray
            image = image.resize((64, 64), Image.Resampling.LANCZOS)
        except Exception as e:
            # Fallback to programmatic icon if image not found
            image = Image.new('RGB', (64, 64), color=(124, 107, 255))
            draw = ImageDraw.Draw(image)
            draw.text((20, 20), "S", fill=(255, 255, 255))
        
        menu = pystray.Menu(
            pystray.MenuItem("Show", self._show_window),
            pystray.MenuItem("Hide", self._hide_window),
            pystray.MenuItem("Quit", self._quit_app)
        )
        
        self.icon = pystray.Icon("sentinel_buddy", image, "Sentinel Buddy", menu)
        
        # Run system tray in separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()
    
    def _setup_hotkey(self):
        """Setup global hotkey for showing/hiding the window."""
        try:
            keyboard.add_hotkey('ctrl+shift+s', self._toggle_window)
            self._add_system_log("Hotkey registered: Ctrl+Shift+S")
        except Exception as e:
            self._add_system_log(f"Failed to register hotkey: {str(e)}")
    
    def _show_window(self):
        """Show the application window."""
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self._add_system_log("Window shown")
    
    def _hide_window(self):
        """Hide the application window."""
        self.root.withdraw()
        self._add_system_log("Window hidden")
    
    def _toggle_window(self):
        """Toggle window visibility."""
        if self.root.state() == 'withdrawn':
            self._show_window()
        else:
            self._hide_window()
    
    def _quit_app(self):
        """Quit the application."""
        self.icon.stop()
        self.root.quit()
        self.root.destroy()
    
    def _build_ui(self):
        """Build all UI sections: Sidebar + Centered Chat."""
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create Lightning Aura frame (border effect)
        self._build_lightning_aura()
        
        # Build Sidebar
        self._build_sidebar()
        
        # Build Main Content Area (centered chat)
        self._build_main_content()
    
    def _build_sidebar(self):
        """Build functional Navigation & History sidebar (Gemini/ChatGPT style)."""
        self.sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=self.sidebar_width)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        
        # Sidebar content
        self.sidebar_content = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        self.sidebar_content.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Top bar with hamburger and search
        top_bar = tk.Frame(self.sidebar_content, bg=BG_SIDEBAR)
        top_bar.pack(fill="x", padx=10, pady=10)
        
        toggle_btn = tk.Button(top_bar, text="☰", font=("Segoe UI", 14),
                              bg=BG_SIDEBAR, fg=TEXT_SIDEBAR, relief="flat",
                              command=self._toggle_sidebar, width=2)
        toggle_btn.pack(side="left", padx=(0, 10))
        
        search_btn = tk.Button(top_bar, text="🔍", font=("Segoe UI", 14),
                              bg=BG_SIDEBAR, fg=TEXT_SIDEBAR, relief="flat", width=2)
        search_btn.pack(side="left")
        
        # Primary Actions
        actions_frame = tk.Frame(self.sidebar_content, bg=BG_SIDEBAR)
        actions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        new_chat_btn = tk.Button(actions_frame, text="+ New Chat", font=("Segoe UI", 10, "bold"),
                                bg=BG_SIDEBAR, fg=TEXT_SIDEBAR, relief="flat",
                                command=self._new_chat, anchor="w")
        new_chat_btn.pack(fill="x", pady=(0, 5))
        
        mystuff_btn = tk.Button(actions_frame, text="⭐ My Stuff", font=("Segoe UI", 10),
                               bg=BG_SIDEBAR, fg=TEXT_SIDEBAR, relief="flat", anchor="w")
        mystuff_btn.pack(fill="x")
        
        # Chats History Section
        chats_header = tk.Label(self.sidebar_content, text="Chats", bg=BG_SIDEBAR,
                               fg=TEXT_SIDEBAR, font=("Segoe UI", 11, "bold"), anchor="w")
        chats_header.pack(fill="x", padx=10, pady=(15, 5))
        
        # Chat history listbox
        self.chat_history_listbox = tk.Listbox(self.sidebar_content, bg=BG_SIDEBAR,
                                              fg=TEXT_SIDEBAR, font=("Segoe UI", 9),
                                              borderwidth=0, highlightthickness=0,
                                              selectbackground=ACTIVE_CHAT,
                                              activestyle="none")
        self.chat_history_listbox.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        self.chat_history_listbox.bind("<Button-1>", self._on_chat_select)
        
        # Gems expandable section
        gems_frame = tk.Frame(self.sidebar_content, bg=BG_SIDEBAR)
        gems_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        gems_btn = tk.Button(gems_frame, text="> Gems", font=("Segoe UI", 10),
                            bg=BG_SIDEBAR, fg=TEXT_SIDEBAR, relief="flat", anchor="w")
        gems_btn.pack(fill="x")
        
        # Bottom Settings & Help
        bottom_frame = tk.Frame(self.sidebar_content, bg=BG_SIDEBAR)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        settings_btn = tk.Button(bottom_frame, text="⚙️ Settings & Help", font=("Segoe UI", 10),
                                bg=BG_SIDEBAR, fg=TEXT_SIDEBAR, relief="flat", anchor="w",
                                command=self._open_settings)
        settings_btn.pack(fill="x")
        
        # Notification dot
        notification_dot = tk.Label(settings_btn, text="●", fg="#2196F3", bg=BG_SIDEBAR,
                                   font=("Segoe UI", 8))
        notification_dot.place(relx=0.95, rely=0.5, anchor="e")
        
        # Initialize chat history storage
        self.chat_history_data = {}  # {title: [messages]}
        self.current_chat_title = None
        self.current_messages = []   # Current conversation messages
        
        # Store canvas width for consistent bubble sizing
        self.stored_canvas_width = None
    
    def _new_chat(self):
        """Start a new chat conversation."""
        # Clear current messages
        self.current_messages = []
        self.current_chat_title = None
        
        # Clear chat canvas
        for widget in self.chat_inner.winfo_children():
            widget.destroy()
        
        # Clear system log
        self.system_logs = []
        self._add_system_log("New chat started")
        
        # Add welcome message with app examples
        self._add_system_bubble(
            "⚡ Sentinel Buddy Pro\n"
            "Ready to assist!\n\n"
            "Automation Examples:\n"
            "  → Open Spotify\n"
            "  → Open Calculator\n"
            "  → Open Spotify and type: Godzilla\n"
            "  → Open youtube.com\n\n"
            "Try saying something!"
        )
    
    def _open_settings(self):
        """Open Settings window with Toplevel."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings & Help")
        settings_window.geometry("600x500")
        settings_window.configure(bg=BG_SECONDARY)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings Tab
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        settings_tab = tk.Frame(notebook, bg=BG_SECONDARY)
        help_tab = tk.Frame(notebook, bg=BG_SECONDARY)
        
        notebook.add(settings_tab, text="Settings")
        notebook.add(help_tab, text="Help")
        
        # Settings Content
        tk.Label(settings_tab, text="AI Personality", bg=BG_SECONDARY, fg=TEXT_PRIMARY, 
                font=("Segoe UI", 12, "bold")).pack(pady=(20, 10))
        
        personality_var = tk.StringVar(value="Pro Mode")
        personalities = ["Pro Mode", "Rap God Mode", "Creative Mode"]
        
        for p in personalities:
            tk.Radiobutton(settings_tab, text=p, variable=personality_var, value=p,
                          bg=BG_SECONDARY, fg=TEXT_PRIMARY, selectcolor=BG_INPUT,
                          font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=5)
        
        tk.Label(settings_tab, text="Theme", bg=BG_SECONDARY, fg=TEXT_PRIMARY,
                font=("Segoe UI", 12, "bold")).pack(pady=(20, 10))
        
        theme_var = tk.StringVar(value="Dark Mode")
        themes = ["Dark Mode", "Light Mode"]
        
        for t in themes:
            tk.Radiobutton(settings_tab, text=t, variable=theme_var, value=t,
                          bg=BG_SECONDARY, fg=TEXT_PRIMARY, selectcolor=BG_INPUT,
                          font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=5)
        
        # Help Content
        tk.Label(help_tab, text="Available Commands", bg=BG_SECONDARY, fg=TEXT_PRIMARY,
                font=("Segoe UI", 12, "bold")).pack(pady=(20, 10))
        
        commands = [
            "Open [website] - Opens website in browser",
            "Open [app] - Launches application",
            "Type this: [text] - Ghost types text",
            "Launch [app.exe] - Launches local executable",
            "Ctrl+Space - Toggle window minimize/restore"
        ]
        
        for cmd in commands:
            tk.Label(help_tab, text=f"  → {cmd}", bg=BG_SECONDARY, fg=TEXT_SECONDARY,
                    font=("Segoe UI", 10), anchor="w").pack(fill="x", padx=20, pady=3)
        
        # Close button
        tk.Button(settings_window, text="Close", bg=ACCENT_COLOR, fg="white",
                 font=("Segoe UI", 10), command=settings_window.destroy).pack(pady=10)
    
    def _on_chat_select(self, event):
        """Handle chat selection from history."""
        selection = self.chat_history_listbox.curselection()
        if not selection:
            return
        
        title = self.chat_history_listbox.get(selection[0])
        
        # Load conversation
        if title in self.chat_history_data:
            self.current_chat_title = title
            self.current_messages = self.chat_history_data[title]
            
            # Clear and reload chat
            for widget in self.chat_inner.winfo_children():
                widget.destroy()
            
            for msg in self.current_messages:
                if msg["type"] == "user":
                    self._add_user_bubble(msg["text"])
                elif msg["type"] == "ai":
                    self._add_ai_bubble(msg["text"])
                elif msg["type"] == "system":
                    self._add_system_bubble(msg["text"])
    
    def _save_conversation(self, first_message: str):
        """Save conversation with first 5 words as title."""
        if not self.current_chat_title:
            # Generate title from first 5 words
            words = first_message.split()[:5]
            title = " ".join(words)
            
            # Add number if title exists
            base_title = title
            counter = 1
            while title in self.chat_history_data:
                title = f"{base_title} ({counter})"
                counter += 1
            
            self.current_chat_title = title
            self.chat_history_listbox.insert(tk.END, title)
            self.chat_history_data[title] = self.current_messages
    
    def _toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed."""
        if self.sidebar_expanded:
            self.sidebar_width = SIDEBAR_COLLAPSED
            self.sidebar_expanded = False
            # Hide content, keep only toggle button
            self.sidebar_content.pack_forget()
            toggle_btn = tk.Button(self.sidebar, text="☰", font=("Segoe UI", 16),
                                  bg=BG_SIDEBAR, fg=TEXT_SIDEBAR, relief="flat",
                                  command=self._toggle_sidebar)
            toggle_btn.pack(pady=10, padx=5)
        else:
            self.sidebar_width = SIDEBAR_EXPANDED
            self.sidebar_expanded = True
            # Rebuild full sidebar
            for widget in self.sidebar.winfo_children():
                widget.destroy()
            self._build_sidebar()
        
        self.sidebar.configure(width=self.sidebar_width)
    
    def _build_main_content(self):
        """Build main content area with centered chat (ChatGPT style)."""
        main_container = tk.Frame(self.root, bg=BG_PRIMARY)
        main_container.grid(row=0, column=1, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Center frame for chat (max width 800px)
        center_frame = tk.Frame(main_container, bg=BG_PRIMARY)
        center_frame.grid(row=0, column=0, sticky="nsew")
        
        # Header
        self._build_header(center_frame)
        
        # Chat area
        self._build_chat_area(center_frame)
        
        # Input area
        self._build_input_area(center_frame)
        
        # System log
        self._build_system_log(center_frame)
    
    def _build_header(self, parent):
        """Top section: logo, title, API key input."""
        header_frame = tk.Frame(parent, bg=BG_SECONDARY, highlightbackground=ACCENT_COLOR, highlightthickness=1)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Logo row
        logo_row = tk.Frame(header_frame, bg=BG_SECONDARY)
        logo_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        
        # Colored accent dot
        dot = tk.Label(logo_row, text="⚡", fg=ACCENT_GLOW, bg=BG_SECONDARY, 
                      font=("Segoe UI", 18, "bold"))
        dot.pack(side="left", padx=(0, 6))
        
        # App title
        title_lbl = tk.Label(logo_row, text=APP_TITLE, fg=TEXT_PRIMARY, bg=BG_SECONDARY,
                           font=("Segoe UI", 14, "bold"))
        title_lbl.pack(side="left")
        
        # Model badge (top-right)
        model_badge = tk.Label(logo_row, text="llama-3.1-8b-instant", fg=TEXT_SECONDARY, bg=BG_SECONDARY,
                             font=("Segoe UI", 9))
        model_badge.pack(side="right")
        
        # API Key section
        key_label = tk.Label(header_frame, text="Groq API Key", fg=TEXT_SECONDARY, bg=BG_SECONDARY,
                           font=("Segoe UI", 10), anchor="w")
        key_label.grid(row=1, column=0, sticky="w", padx=14, pady=(4, 2))
        
        key_row = tk.Frame(header_frame, bg=BG_SECONDARY)
        key_row.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
        key_row.grid_columnconfigure(0, weight=1)
        
        self.key_entry = tk.Entry(key_row, show="*", bg=BG_INPUT, fg=TEXT_PRIMARY,
                                 font=("Segoe UI", 10), relief="solid", bd=1)
        self.key_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        
        # Disable copy functionality for key entry
        self.key_entry.bind("<Control-c>", lambda e: "break")
        self.key_entry.bind("<Button-3>", lambda e: "break")  # Disable right-click
        
        # Show/Hide toggle button
        self.show_key_btn = tk.Button(key_row, text="👁", width=3, height=1,
                                     bg=BG_INPUT, fg=TEXT_SECONDARY, font=("Segoe UI", 10),
                                     command=self._toggle_key_visibility, relief="flat", bd=0)
        self.show_key_btn.grid(row=0, column=1, padx=(0, 4))
        
        # Save Key button
        save_btn = tk.Button(key_row, text="💾", width=3, height=1,
                           bg=BG_INPUT, fg=TEXT_SECONDARY, font=("Segoe UI", 10),
                           command=self._save_key_from_ui, relief="flat", bd=0)
        save_btn.grid(row=0, column=2, padx=(0, 4))
        
        connect_btn = tk.Button(key_row, text="▶", width=3, height=1,
                              bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
                              command=self._connect_api, relief="flat", bd=0)
        connect_btn.grid(row=0, column=3)
        
        # Connected indicator
        self.connection_indicator = tk.Label(header_frame, text="● Not connected",
                                          fg="#FF6B6B", bg=BG_SECONDARY,
                                          font=("Segoe UI", 9), anchor="w")
        self.connection_indicator.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 10))
    
    def _build_chat_area(self, parent):
        """Scrollable middle section that displays conversation bubbles with rounded frames."""
        chat_outer = tk.Frame(parent, bg=BG_CHAT)
        chat_outer.pack(fill="both", expand=True, padx=20, pady=10)
        chat_outer.grid_rowconfigure(0, weight=1)
        chat_outer.grid_columnconfigure(0, weight=1)
        
        # Create canvas for bubble layout
        self.chat_canvas = tk.Canvas(
            chat_outer,
            bg=BG_CHAT,
            highlightthickness=0,
            relief="flat"
        )
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Create scrollable frame inside canvas
        self.chat_scrollbar = tk.Scrollbar(chat_outer, orient="vertical", command=self.chat_canvas.yview)
        self.chat_scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        
        # Create inner frame for bubbles
        self.chat_inner = tk.Frame(self.chat_canvas, bg=BG_CHAT)
        self.chat_canvas.create_window((0, 0), window=self.chat_inner, anchor="nw", width=self.chat_canvas.winfo_width())
        
        # Configure canvas scroll to match width
        def update_scroll_region(event=None):
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
            # Update window width to match canvas
            canvas_width = self.chat_canvas.winfo_width()
            self.chat_canvas.itemconfigure(1, width=canvas_width)
        
        self.chat_inner.bind("<Configure>", update_scroll_region)
        
        # Store bubble references for auto-scroll
        self.bubble_count = 0
        
        # Store thinking animation reference
        self.thinking_bubble = None
        
        # Dojo Timer variables
        self.dojo_timer_active = False
        self.dojo_timer_label = None
        self.dojo_timer_seconds = 0
        
        # Welcome message (will be updated after auto-connect)
        self._add_system_bubble(
            "\ud83e\udd16 Sentinel Buddy Pro starting...\n"
            "Connecting to Groq API...\n\n"
            "Automation capabilities:\n"
            "  \u2192 'Open [website]'    \u2014 Opens in browser\n"
            "  \u2192 'Type this: [text]' \u2014 Ghost types text\n"
            "  \u2192 'Launch [app.exe]'  \u2014 Launches application"
        )
    
    def _build_input_area(self, parent):
        """Bottom text input + send button."""
        input_frame = tk.Frame(parent, bg=BG_SECONDARY, highlightbackground=ACCENT_COLOR, highlightthickness=1)
        input_frame.pack(fill="x", padx=20, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Multi-line text input
        self.input_box = tk.Text(input_frame, height=3, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                font=("Segoe UI", 12), relief="solid", bd=1)
        self.input_box.grid(row=0, column=0, sticky="ew", padx=(10, 6), pady=(10, 6))
        
        # Circular Send button
        send_btn = tk.Button(input_frame, text="▶", width=3, height=1,
                           bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
                           command=self._on_send, relief="flat", bd=0, padx=8, pady=8)
        send_btn.grid(row=0, column=1, padx=(0, 10), pady=(10, 6))
        
        # Bind Enter to send
        self.input_box.bind("<Return>", self._on_enter_key)
    
    def _build_system_log(self, parent):
        """System log display area at the bottom."""
        log_frame = tk.Frame(parent, bg="#0A0C11", height=80)
        log_frame.pack(fill="x", padx=20, pady=(0, 10))
        log_frame.pack_propagate(False)
        log_frame.grid_columnconfigure(0, weight=1)
        
        # Log header
        log_header = tk.Label(log_frame, text="SYSTEM LOG", fg=ACCENT_GLOW, bg="#0A0C11",
                           font=("Segoe UI", 8, "bold"), anchor="w")
        log_header.grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=4,
            bg="#0A0C11",
            fg="#8888A8",
            font=("Consolas", 8),
            relief="flat",
            bd=0,
            padx=5,
            pady=2
        )
        self.log_text.grid(row=1, column=0, sticky="nsew")
        self.log_text.configure(state="disabled")
    
    def _add_system_log(self, message: str):
        """Add a message to the system log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.system_logs.append(log_entry)
        
        # Keep only last 50 log entries
        if len(self.system_logs) > 50:
            self.system_logs = self.system_logs[-50:]
        
        # Update log display
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        for log in self.system_logs:
            self.log_text.insert(tk.END, log)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
    
    def _add_user_bubble(self, text: str):
        self.current_messages.append({"type": "user", "text": text})
        self._save_conversation(text)
        self._render_bubble_frame(text, "user")
    
    def _add_ai_bubble(self, text: str):
        self.current_messages.append({"type": "ai", "text": text})
        self._type_ai_bubble(text)
    
    def _type_ai_bubble(self, text: str):
        """Type AI response character-by-character with Ghost Pulse effect."""
        # Create bubble frame
        bubble_frame = tk.Frame(self.chat_inner, bg=BG_CHAT)
        bubble_frame.pack(fill="x", padx=10, pady=8)
        
        # Use screen width minus sidebar for consistent full-width sizing
        if self.stored_canvas_width is None:
            screen_width = self.root.winfo_screenwidth()
            self.stored_canvas_width = screen_width - SIDEBAR_EXPANDED - 60
        
        max_bubble_width = self.stored_canvas_width
        
        # AI Bubbles - Left aligned, dark grey with rounded corners
        inner = tk.Frame(bubble_frame, bg="#2a2a2a", relief="solid", bd=0, 
                       highlightbackground="#404040", highlightthickness=1)
        inner.pack(side="left", anchor="w")
        
        # Create label for typing effect
        lbl = tk.Label(inner, text="", bg="#2a2a2a", fg="#FFFFFF", 
                      font=("Segoe UI", 11), wraplength=max_bubble_width, justify="left", padx=16, pady=12, anchor="w")
        lbl.pack(anchor="w")
        
        # Character-by-character typing
        self._type_text_character_by_character(lbl, text, 0)
    
    def _type_text_character_by_character(self, label, text: str, index: int):
        """Type text character by character with auto-scroll."""
        if index < len(text):
            # Append next character
            current_text = label.cget("text")
            label.configure(text=current_text + text[index])
            
            # Auto-scroll to bottom
            self._auto_scroll()
            
            # Schedule next character (0.02s for fast but natural feel)
            self.root.after(20, lambda: self._type_text_character_by_character(label, text, index + 1))
    
    def _add_system_bubble(self, text: str):
        self.current_messages.append({"type": "system", "text": text})
        self._render_bubble_frame(text, "system")
    
    def _add_system_message(self, text: str):
        self.current_messages.append({"type": "system", "text": text})
        self._render_bubble_frame(text, "system")
    
    def _add_automation_log(self, message: str):
        """Add automation log as special system message (centered, small, italicized)."""
        self._render_bubble_frame(f"⚡ {message}", "automation")
    
    def _show_thinking_animation(self):
        """Show animated thinking bubble while AI is responding."""
        if self.thinking_bubble:
            return  # Already showing
        
        bubble_frame = tk.Frame(self.chat_inner, bg=BG_CHAT)
        bubble_frame.pack(fill="x", padx=10, pady=8)
        
        inner = tk.Frame(bubble_frame, bg="#2a2a2a", relief="solid", bd=0, 
                       highlightbackground="#404040", highlightthickness=1)
        inner.pack(side="left", anchor="w")
        
        self.thinking_label = tk.Label(inner, text="Sentinel is thinking", bg="#2a2a2a", fg="#FFFFFF", 
                                      font=("Segoe UI", 10), padx=16, pady=12)
        self.thinking_label.pack(anchor="w")
        
        self.thinking_bubble = bubble_frame
        self.thinking_dots = 0
        self._animate_thinking_dots()
        self._auto_scroll()
    
    def _hide_thinking_animation(self):
        """Hide the thinking animation bubble."""
        if self.thinking_bubble:
            self.thinking_bubble.destroy()
            self.thinking_bubble = None
            self.thinking_label = None
    
    def _animate_thinking_dots(self):
        """Animate the thinking dots with pulsing effect."""
        if not self.thinking_bubble:
            return
        
        dots = "." * (self.thinking_dots % 4)
        if self.thinking_label:
            self.thinking_label.configure(text=f"Sentinel is thinking{dots}")
            self.thinking_dots += 1
            self.root.after(500, self._animate_thinking_dots)
    
    def _start_dojo_timer(self, minutes: int):
        """Start Dojo Timer countdown in sidebar."""
        if self.dojo_timer_active:
            return
        
        self.dojo_timer_active = True
        self.dojo_timer_seconds = minutes * 60
        
        # Create timer label in sidebar
        if self.sidebar_content:
            timer_frame = tk.Frame(self.sidebar_content, bg=BG_SIDEBAR)
            timer_frame.pack(fill="x", padx=10, pady=10)
            
            tk.Label(timer_frame, text="⏱️ Dojo Timer", bg=BG_SIDEBAR, fg=TEXT_SIDEBAR,
                    font=("Segoe UI", 10, "bold")).pack(anchor="w")
            
            self.dojo_timer_label = tk.Label(timer_frame, text=f"{minutes}:00", bg=BG_SIDEBAR, fg=ACCENT_COLOR,
                                           font=("Segoe UI", 24, "bold"))
            self.dojo_timer_label.pack(anchor="w", pady=5)
            
            tk.Button(timer_frame, text="Stop", bg=BG_INPUT, fg=TEXT_SIDEBAR,
                     font=("Segoe UI", 9), command=self._stop_dojo_timer).pack(anchor="w")
        
        self._update_dojo_timer()
    
    def _update_dojo_timer(self):
        """Update Dojo Timer countdown."""
        if not self.dojo_timer_active:
            return
        
        if self.dojo_timer_seconds > 0:
            minutes = self.dojo_timer_seconds // 60
            seconds = self.dojo_timer_seconds % 60
            if self.dojo_timer_label:
                self.dojo_timer_label.configure(text=f"{minutes}:{seconds:02d}")
            self.dojo_timer_seconds -= 1
            self.root.after(1000, self._update_dojo_timer)
        else:
            # Timer complete
            self._dojo_timer_complete()
    
    def _dojo_timer_complete(self):
        """Handle Dojo Timer completion."""
        self.dojo_timer_active = False
        if self.dojo_timer_label:
            self.dojo_timer_label.configure(text="Time's Up!", fg="#FF6B6B")
        
        # Bring window to front
        self.root.deiconify()
        self.root.state('zoomed')
        self.root.lift()
        self.root.focus_force()
        
        # Show completion message
        self._add_system_bubble("⏱️ Lab Closed. Time to Spar!")
    
    def _stop_dojo_timer(self):
        """Stop Dojo Timer."""
        self.dojo_timer_active = False
    
    def _render_bubble_frame(self, text: str, sender_type: str):
        bubble_frame = tk.Frame(self.chat_inner, bg=BG_CHAT)
        bubble_frame.pack(fill="x", padx=10, pady=8)
        
        # Use screen width minus sidebar for consistent full-width sizing
        if self.stored_canvas_width is None:
            screen_width = self.root.winfo_screenwidth()
            self.stored_canvas_width = screen_width - SIDEBAR_EXPANDED - 60
        
        max_bubble_width = self.stored_canvas_width
        
        if sender_type == "user":
            # User Bubbles - Right aligned, bright purple border
            inner = tk.Frame(bubble_frame, bg=BUBBLE_USER, relief="solid", bd=0, 
                           highlightbackground="#00D4FF", highlightthickness=2)
            inner.pack(side="right", anchor="e")
            lbl = tk.Label(inner, text=text, bg=BUBBLE_USER, fg="#FFFFFF", 
                          font=("Segoe UI", 11), wraplength=max_bubble_width, justify="right", padx=12, pady=8, anchor="e")
            lbl.pack()
        elif sender_type == "ai":
            # AI Bubbles - Left aligned, dark grey with rounded corners
            inner = tk.Frame(bubble_frame, bg="#2a2a2a", relief="solid", bd=0, 
                           highlightbackground="#404040", highlightthickness=1)
            inner.pack(side="left", anchor="w")
            lbl = tk.Label(inner, text=text, bg="#2a2a2a", fg="#FFFFFF", 
                          font=("Segoe UI", 11), wraplength=max_bubble_width, justify="left", padx=16, pady=12, anchor="w")
            lbl.pack()
        elif sender_type == "automation":
            inner = tk.Frame(bubble_frame, bg=BUBBLE_SYSTEM, relief="flat", bd=0)
            inner.pack(fill="x")
            lbl = tk.Label(inner, text=text, bg=BUBBLE_SYSTEM, fg=ACCENT_GLOW, 
                          font=("Segoe UI", 9, "italic"), wraplength=250, justify="center", padx=12, pady=4)
            lbl.pack()
        else:
            inner = tk.Frame(bubble_frame, bg=BUBBLE_SYSTEM, relief="flat", bd=0)
            inner.pack(fill="x")
            lbl = tk.Label(inner, text=text, bg=BUBBLE_SYSTEM, fg=TEXT_SYSTEM, 
                          font=("Segoe UI", 10), wraplength=250, justify="center", padx=12, pady=6)
            lbl.pack()
        
        self._auto_scroll()
    
    def _auto_scroll(self):
        """Auto-scroll to bottom immediately when new message appears."""
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
        self.chat_canvas.after(100, self.chat_canvas.yview_moveto, 1.0)  # Ensure scroll
    
    def _on_enter_key(self, event):
        """Send message on Enter (without Shift)."""
        if not event.state & 0x1:  # Not Shift key
            self._on_send()
            return "break"  # Prevent newline insertion
    
    def _on_send(self):
        """Handle send button click - route to System Executor or AI."""
        if self.is_thinking:
            return  # Prevent double-send while AI is responding
        
        raw_text = self.input_box.get("1.0", tk.END).strip()
        if not raw_text:
            return
        
        # Clear input immediately
        self.input_box.delete("1.0", tk.END)
        
        # Display user's message immediately
        self._add_user_bubble(raw_text)
        self._add_system_log(f"[SYSTEM] User message: {raw_text[:50]}...")
        
        # System Executor check FIRST
        lower_text = raw_text.lower().strip()
        
        # Check for quick search triggers (google, search, find) for fast 110 WPM response
        if any(trigger in lower_text for trigger in ["google", "search", "find"]):
            # Determine which trigger was used
            for trigger in ["google", "search", "find"]:
                if trigger in lower_text:
                    search_query = lower_text.split(trigger)[-1].strip()
                    if search_query:
                        # Show bright cyan pulse message
                        self._add_system_bubble(f"🎯 TARGET ACQUIRED: SEARCHING THE WEB...")
                        self._add_system_log(f"[SYSTEM] Quick search: {search_query}")
                        # Execute search
                        AutomationTools.quick_search(search_query)
                        return
        
        # Check for ghost typing command
        if "type" in lower_text:
            type_index = lower_text.find("type")
            text_to_type = raw_text[type_index + 4:].strip()
            if text_to_type:
                self._execute_system_command(SYSTEM_COMMANDS["type"], text_to_type)
                self.root.after(2500, lambda: setattr(self, 'is_thinking', False))
                return
        
        for trigger, config in SYSTEM_COMMANDS.items():
            if trigger in lower_text and trigger != "type":
                self._execute_system_command(config)
                self.root.after(2500, lambda: setattr(self, 'is_thinking', False))
                return
        
        # Otherwise, call AI
        if not self.api_key:
            self._add_system_bubble("⚠️ No API key connected.\nSet GROQ_API_KEY environment variable or enter key above and click ▶")
            return
        
        # Run AI call in background thread (keeps UI responsive)
        self.is_thinking = True
        self._start_lightning_aura()
        self._show_thinking_animation()
        self._add_system_log("[SYSTEM] AI is thinking...")
        threading.Thread(target=self._call_ai, args=(raw_text,), daemon=True).start()
    
    def _execute_system_command(self, config: dict, text_to_type: str = ""):
        """System Executor: Runs actions triggered by special keywords."""
        label = config.get("label", "Executing command...")
        cmd_type = config.get("type", "url")
        target = config.get("target", "")
        
        # Start Lightning Aura
        self._start_lightning_aura()
        self.is_executing = True
        
        # Show action feedback
        self._add_system_message(f"\u26a1 {label}")
        self._add_system_log(f"Executing: {label}")
        
        if cmd_type == "url":
            webbrowser.open(target)
            self._add_system_log(f"Opened URL: {target}")
        elif cmd_type == "shell":
            subprocess.Popen(target, shell=True)
            self._add_system_log(f"Executed shell command: {target}")
        elif cmd_type == "ghost_type":
            self._ghost_type(text_to_type)
        
        # Stop Lightning Aura after execution
        self.root.after(2000, self._stop_lightning_aura)
        self.is_executing = False
    
    def _ghost_type(self, text: str):
        """Ghost type text character by character using pyautogui."""
        self._add_system_log(f"Ghost typing: {text}")
        self._add_system_message(f"\ud83d\udd30 Ghost typing: {text}")
        
        try:
            pyautogui.write(text, interval=0.05)
            self._add_system_log("Ghost typing completed")
        except Exception as e:
            self._add_system_log(f"Ghost typing failed: {str(e)}")
            self._add_system_message(f"\u26a0 Ghost typing failed: {str(e)}")
    
    def _call_ai(self, user_message: str):
        """Background thread: uses Brain class to process message and execute intents."""
        try:
            # Use Brain class for AI processing
            result = self.brain.process_message(user_message)
            
            if result.get("error"):
                # Handle error
                error_msg = f"Error: {result['error']}"
                self.root.after(0, self._add_system_bubble, f"⚠️ {error_msg}")
                self.root.after(0, lambda: setattr(self, 'is_thinking', False))
                self.root.after(0, self._stop_lightning_aura)
                return
            
            # Display AI response
            ai_reply = result.get("content", "")
            intent = result.get("intent", {})
            
            # Update UI on main thread
            self.root.after(0, self._add_ai_bubble, ai_reply)
            self.root.after(0, self._add_system_log, "[SYSTEM] Response received")
            
            # Execute intent if detected (keep animation active during scan)
            if intent and intent.get("type"):
                # Check if blocked intent
                if intent.get("type") == "blocked":
                    response = intent.get("params", {}).get("response", "I don't do that kind of content. Let's get back to work.")
                    self.root.after(0, self._add_system_bubble, f"⚠️ {response}")
                    self.root.after(0, self._hide_thinking_animation)
                # Check if Dojo Timer intent
                elif intent.get("type") == "dojo_timer":
                    minutes = intent.get("params", {}).get("minutes", 5)
                    self.root.after(0, self._start_dojo_timer, minutes)
                    self.root.after(0, self._hide_thinking_animation)
                else:
                    # Keep animation active for app scanning
                    self.root.after(0, lambda: AutomationTools.execute_intent(intent, self._add_automation_log))
                    # Hide animation after a delay to allow scanning to complete
                    self.root.after(2000, self._hide_thinking_animation)
            else:
                # Hide animation immediately if no intent
                self.root.after(0, self._hide_thinking_animation)
            
            # Reset thinking flag
            self.root.after(0, lambda: setattr(self, 'is_thinking', False))
            self.root.after(0, self._stop_lightning_aura)
            
        except Exception as e:
            error_msg = f"AI Error: {str(e)}"
            self.root.after(0, self._add_system_bubble, f"⚠️ {error_msg}")
            self.root.after(0, self._add_system_log, f"[SYSTEM] Error: {str(e)}")
            self.root.after(0, lambda: setattr(self, 'is_thinking', False))
            self.root.after(0, self._stop_lightning_aura)
    
    def _auto_connect_api(self):
        """Auto-connect with environment variable API key on startup."""
        if DEFAULT_API_KEY:
            # Set API key in entry field
            self.key_entry.insert(0, DEFAULT_API_KEY)
            
            # Make entry read-only to prevent modification
            self.key_entry.configure(state="readonly")
            
            # Auto-connect immediately
            self.api_key = DEFAULT_API_KEY
            self.brain = Brain(self.api_key)
            self._save_key(DEFAULT_API_KEY)
            
            self.connection_indicator.configure(text="● Connected", fg="#6BFF9E")
            self._add_system_log("Groq API connected. Ready to chat!")
            
            # Clear existing bubbles and add welcome message
            for widget in self.chat_inner.winfo_children():
                widget.destroy()
            
            self._add_system_bubble(
                "⚡ Sentinel Buddy Pro online!\n"
                "Groq API connected automatically.\n\n"
                "Ready to assist!\n\n"
                "Automation Examples:\n"
                "  → Open Spotify\n"
                "  → Open Calculator\n"
                "  → Open Spotify and type: Godzilla\n"
                "  → Open youtube.com"
            )
        else:
            # No API key found
            self.connection_indicator.configure(text="● Not connected", fg="#FF6B6B")
            self._add_system_log("No API key found.")
            
            self._add_system_message(
                "⚡ Sentinel Buddy Pro online!\n"
                "No Groq API key found in .env file.\n\n"
                "Please add your API key to .env file:\n"
                "  GROQ_API_KEY=your_key_here\n"
                "  Or enter key manually above and click ▶\n\n"
                "Get your free key from: https://console.groq.com/keys"
            )
    
    def _connect_api(self):
        """Validate and store the Groq API key."""
        key = self.key_entry.get().strip()
        if not key:
            self.connection_indicator.configure(text="● No key provided", fg="#FF6B6B")
            return
        
        # Store API key
        self.api_key = key
        self.brain = Brain(self.api_key)  # Reinitialize Brain with new key
        self._save_key(key)
        
        self.connection_indicator.configure(text="● Connected", fg="#6BFF9E")
        self._add_system_log("API key connected. Ready to chat!")
        self._add_system_bubble(
            "✅ API key accepted. Sentinel Buddy Pro is fully online.\n"
            "Ask me anything or use automation commands!"
        )
    
    def _toggle_key_visibility(self):
        """Toggle between showing and hiding the API key."""
        self.key_visible = not self.key_visible
        if self.key_visible:
            self.key_entry.configure(show="")
            self.show_key_btn.configure(text="🙈")
        else:
            self.key_entry.configure(show="*")
            self.show_key_btn.configure(text="👁")
    
    def _save_key_from_ui(self):
        """Save API key from UI entry to .env file."""
        key = self.key_entry.get().strip()
        if not key:
            self._add_system_bubble("⚠️ No key to save.")
            return
        
        try:
            env_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), ".env"
            )
            with open(env_path, "w") as f:
                f.write(f"GROQ_API_KEY={key}\n")
            self._add_system_bubble("✅ API key saved to .env file.")
            self._add_system_log("[SYSTEM] API key saved securely")
        except Exception as e:
            self._add_system_bubble(f"⚠️ Failed to save key: {str(e)}")
    
    def _save_key(self, key: str):
        """Save API key to .env file (legacy method)."""
        env_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ".env"
        )
        with open(env_path, "w") as f:
            f.write(f"GROQ_API_KEY={key}\n")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

def main():
    """Entry point for Sentinel Buddy Desktop."""
    try:
        app = SentinelBuddyDesktop()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Sentinel Buddy: {str(e)}")

if __name__ == "__main__":
    main()
