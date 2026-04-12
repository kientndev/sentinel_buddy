"""
╔══════════════════════════════════════════════════════════════╗
║                      SENTINEL BUDDY                          ║
║              Windows Desktop AI Assistant Sidebar            ║
║                                                              ║
║  Tech Stack  : Python + customtkinter + OpenAI GPT-4o-mini   ║
║  UI Style    : Narrow 300px sidebar, always-on-top, dark     ║
║  Features    : AI Chat, System Executor commands             ║
╚══════════════════════════════════════════════════════════════╝

HOW TO USE:
-----------
1. Install dependencies:
   pip install customtkinter openai python-dotenv

2. Add your key to .env in the same folder:
   OPENAI_API_KEY=sk-...

3. Run:
   python sentinel_buddy.py

3. Enter your OpenAI API key in the sidebar header.

4. Special Commands (System Executor):
   - "Open Sentinel"  → Opens your SentinelPhish Vercel dashboard
   - "Dojo Mode"      → Opens Spotify 2010s playlist

5. To expand later:
   - Add more commands in the SYSTEM_COMMANDS dict below.
   - Add new AI system prompts in SYSTEM_PROMPT.
   - Hook into OS features via the subprocess module.
"""

import tkinter as tk
import customtkinter as ctk
import threading
import webbrowser
import subprocess
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# ── Load .env from the same directory as this script ──
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=_ENV_PATH)
from openai import OpenAI

# ─────────────────────────────────────────────────────────────
#  CONFIGURATION — Edit these to customize Sentinel Buddy
# ─────────────────────────────────────────────────────────────

APP_TITLE = "Sentinel Buddy"
SIDEBAR_WIDTH = 300
SIDEBAR_HEIGHT_PERCENT = 0.92   # 92% of screen height
BG_COLOR_PRIMARY = "#0D0F14"    # Deep dark background
BG_COLOR_SECONDARY = "#13161E"  # Card/panel background
BG_COLOR_INPUT = "#1A1D27"      # Input field background
ACCENT_COLOR = "#7C6BFF"        # Purple accent (brand color)
ACCENT_GLOW = "#5B4CE0"         # Darker accent for pressed states
TEXT_PRIMARY = "#E8E8F0"        # Main text
TEXT_SECONDARY = "#8888A8"      # Muted/subtext
TEXT_USER = "#A8D8FF"           # User bubble text color
TEXT_AI = "#C8FFD4"             # AI bubble text color
BUBBLE_USER = "#1E2A4A"         # User message bubble bg
BUBBLE_AI = "#141E1A"           # AI message bubble bg
BUBBLE_SYSTEM = "#1A1520"       # System/executor message bubble bg
FONT_FAMILY = "Segoe UI"        # Windows-native modern font
FONT_SIZE_BASE = 12
FONT_SIZE_SMALL = 10
FONT_SIZE_TITLE = 14

# ── OpenAI Model ──
AI_MODEL = "gpt-4o-mini"

# ── AI Personality (System Prompt) ──
SYSTEM_PROMPT = """You are Sentinel Buddy, a sharp, resourceful AI assistant embedded 
directly into the user's Windows desktop sidebar. You are an expert in:
- Cybersecurity, phishing analysis, and threat intelligence
- Coding (Python, JavaScript, TypeScript, Next.js)
- Productivity and system automation

Keep responses concise and actionable. Use markdown sparingly (bold key terms). 
When asked about security topics, be direct and technical.
You are the user's always-on-top AI co-pilot."""

# ── System Executor Commands ──
# Add more commands here as key-value dicts.
# Each entry: "trigger phrase (lowercase)" → action config
SYSTEM_COMMANDS = {
    "open sentinel": {
        "type": "url",
        "target": "https://sentinel-phish.vercel.app",  # ← Your Vercel URL
        "label": "Opening SentinelPhish Dashboard...",
    },
    "dojo mode": {
        "type": "url",
        # Spotify 2010s playlist — replace with your actual playlist link
        "target": "https://open.spotify.com/playlist/37i9dQZF1DX5Ejj0EkURtP",
        "label": "Activating Dojo Mode 🎵 Opening Spotify...",
    },
    # ── EXAMPLES: Add your own commands ──
    # "open github": {
    #     "type": "url",
    #     "target": "https://github.com",
    #     "label": "Opening GitHub...",
    # },
    # "run terminal": {
    #     "type": "shell",
    #     "target": "start cmd",
    #     "label": "Launching terminal...",
    # },
}

# ─────────────────────────────────────────────────────────────
#  APPLICATION CLASS
# ─────────────────────────────────────────────────────────────

class SentinelBuddy(ctk.CTk):
    """Main application window — a narrow sidebar assistant."""

    def __init__(self):
        super().__init__()

        # ── CustomTkinter appearance ──
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Window setup ──
        self._setup_window()

        # ── State ──
        self.api_client: OpenAI | None = None
        self.chat_history: list[dict] = []  # Maintains conversation context
        self.is_thinking: bool = False

        # ── Build UI ──
        self._build_ui()

        # ── Load saved API key if it exists ──
        self._load_saved_key()

    # ──────────────────────────────────────────────
    #  WINDOW POSITIONING
    # ──────────────────────────────────────────────

    def _setup_window(self):
        """Configure window: always-on-top, snapped to right edge."""
        self.title(APP_TITLE)
        self.overrideredirect(False)   # Keep titlebar for drag/minimize

        # Compute position — right edge of screen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        win_h = int(screen_h * SIDEBAR_HEIGHT_PERCENT)
        win_y = int((screen_h - win_h) / 2)  # Vertically centered
        win_x = screen_w - SIDEBAR_WIDTH - 8  # 8px margin from right edge

        self.geometry(f"{SIDEBAR_WIDTH}x{win_h}+{win_x}+{win_y}")
        self.resizable(False, True)  # Allow vertical resize only

        # Always on top of other windows
        self.attributes("-topmost", True)

        # Background color
        self.configure(fg_color=BG_COLOR_PRIMARY)

        # Keep on top even when focus changes
        self.bind("<FocusOut>", lambda e: self.attributes("-topmost", True))

    # ──────────────────────────────────────────────
    #  UI CONSTRUCTION
    # ──────────────────────────────────────────────

    def _build_ui(self):
        """Build all UI sections top-to-bottom."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Chat area expands

        self._build_header()       # Row 0: Branding + API Key
        self._build_chat_area()    # Row 1: Scrollable chat
        self._build_input_area()   # Row 2: Text input + send button
        self._build_status_bar()   # Row 3: Status / token count

    # ── HEADER ──────────────────────────────────

    def _build_header(self):
        """Top section: logo, title, API key input."""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=BG_COLOR_SECONDARY,
            corner_radius=0,
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)

        # ── Logo row ──
        logo_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))

        # Colored accent dot
        dot = ctk.CTkLabel(
            logo_row,
            text="◈",
            text_color=ACCENT_COLOR,
            font=(FONT_FAMILY, 18, "bold"),
        )
        dot.pack(side="left", padx=(0, 6))

        # App title
        title_lbl = ctk.CTkLabel(
            logo_row,
            text=APP_TITLE,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"),
        )
        title_lbl.pack(side="left")

        # Model badge (top-right)
        model_badge = ctk.CTkLabel(
            logo_row,
            text=AI_MODEL,
            text_color=TEXT_SECONDARY,
            font=(FONT_FAMILY, FONT_SIZE_SMALL - 1),
        )
        model_badge.pack(side="right")

        # ── API Key section ──
        key_label = ctk.CTkLabel(
            header_frame,
            text="OpenAI API Key",
            text_color=TEXT_SECONDARY,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            anchor="w",
        )
        key_label.grid(row=1, column=0, sticky="w", padx=14, pady=(4, 2))

        key_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        key_row.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
        key_row.grid_columnconfigure(0, weight=1)

        self.key_entry = ctk.CTkEntry(
            key_row,
            placeholder_text="sk-...",
            show="•",  # Masked by default
            fg_color=BG_COLOR_INPUT,
            border_color=ACCENT_COLOR,
            border_width=1,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            height=30,
        )
        self.key_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        connect_btn = ctk.CTkButton(
            key_row,
            text="▶",
            width=30,
            height=30,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_GLOW,
            font=(FONT_FAMILY, 12, "bold"),
            command=self._connect_api,
        )
        connect_btn.grid(row=0, column=1)

        # Connected indicator
        self.connection_indicator = ctk.CTkLabel(
            header_frame,
            text="● Not connected",
            text_color="#FF6B6B",
            font=(FONT_FAMILY, FONT_SIZE_SMALL - 1),
            anchor="w",
        )
        self.connection_indicator.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 10))

    # ── CHAT AREA ──────────────────────────────

    def _build_chat_area(self):
        """Scrollable middle section that displays conversation bubbles."""
        chat_outer = ctk.CTkFrame(
            self,
            fg_color=BG_COLOR_PRIMARY,
            corner_radius=0,
        )
        chat_outer.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        chat_outer.grid_rowconfigure(0, weight=1)
        chat_outer.grid_columnconfigure(0, weight=1)

        # CTkScrollableFrame handles overflow automatically
        self.chat_frame = ctk.CTkScrollableFrame(
            chat_outer,
            fg_color=BG_COLOR_PRIMARY,
            scrollbar_button_color=ACCENT_COLOR,
            scrollbar_button_hover_color=ACCENT_GLOW,
            corner_radius=0,
        )
        self.chat_frame.grid(row=0, column=0, sticky="nsew")
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Welcome message
        self._add_system_message(
            f"👾 Sentinel Buddy online.\n"
            f"Add your API key above and start chatting.\n\n"
            f"Quick commands:\n"
            f"  → 'Open Sentinel'  — Launch dashboard\n"
            f"  → 'Dojo Mode'      — Open Spotify playlist"
        )

    # ── INPUT AREA ──────────────────────────────

    def _build_input_area(self):
        """Bottom text input + send button."""
        input_frame = ctk.CTkFrame(
            self,
            fg_color=BG_COLOR_SECONDARY,
            corner_radius=0,
        )
        input_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        input_frame.grid_columnconfigure(0, weight=1)

        # Multi-line text input
        self.input_box = ctk.CTkTextbox(
            input_frame,
            height=70,
            fg_color=BG_COLOR_INPUT,
            border_color=ACCENT_COLOR,
            border_width=1,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, FONT_SIZE_BASE),
            wrap="word",
            corner_radius=8,
        )
        self.input_box.grid(row=0, column=0, sticky="ew", padx=(10, 6), pady=(10, 6))

        # Send button
        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=60,
            height=70,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_GLOW,
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            command=self._on_send,
            corner_radius=8,
        )
        send_btn.grid(row=0, column=1, padx=(0, 10), pady=(10, 6))

        # Bind Enter to send, Shift+Enter for new line
        self.input_box.bind("<Return>", self._on_enter_key)
        self.input_box.bind("<Shift-Return>", lambda e: None)  # Allow newlines

    # ── STATUS BAR ──────────────────────────────

    def _build_status_bar(self):
        """Thin bottom bar: shows thinking indicator & message count."""
        status_frame = ctk.CTkFrame(
            self,
            fg_color="#0A0C11",
            corner_radius=0,
            height=24,
        )
        status_frame.grid(row=3, column=0, sticky="ew")
        status_frame.grid_propagate(False)
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            text_color=TEXT_SECONDARY,
            font=(FONT_FAMILY, FONT_SIZE_SMALL - 1),
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=10)

        self.time_label = ctk.CTkLabel(
            status_frame,
            text="",
            text_color=TEXT_SECONDARY,
            font=(FONT_FAMILY, FONT_SIZE_SMALL - 1),
            anchor="e",
        )
        self.time_label.grid(row=0, column=1, sticky="e", padx=10)
        self._update_clock()

    # ──────────────────────────────────────────────
    #  CHAT BUBBLE HELPERS
    # ──────────────────────────────────────────────

    def _add_user_bubble(self, text: str):
        """Render a user message bubble."""
        self._render_bubble(
            sender="You",
            text=text,
            bg=BUBBLE_USER,
            fg=TEXT_USER,
            sender_color=ACCENT_COLOR,
        )

    def _add_ai_bubble(self, text: str):
        """Render an AI response bubble."""
        self._render_bubble(
            sender="Sentinel",
            text=text,
            bg=BUBBLE_AI,
            fg=TEXT_AI,
            sender_color="#6BFF9E",  # Neon green for AI
        )

    def _add_system_message(self, text: str):
        """Render a system/info message bubble."""
        self._render_bubble(
            sender="System",
            text=text,
            bg=BUBBLE_SYSTEM,
            fg=TEXT_SECONDARY,
            sender_color="#FF9F6B",  # Orange for system
        )

    def _render_bubble(
        self,
        sender: str,
        text: str,
        bg: str,
        fg: str,
        sender_color: str,
    ):
        """
        Generic bubble renderer.

        Creates a card-style frame with:
        - Colored sender label (top-left)
        - Wrapped message text
        - Light border accent matching sender color
        """
        row_idx = len(self.chat_frame.winfo_children())

        bubble = ctk.CTkFrame(
            self.chat_frame,
            fg_color=bg,
            corner_radius=10,
            border_width=1,
            border_color=sender_color + "40",  # 25% opacity border
        )
        bubble.grid(
            row=row_idx,
            column=0,
            sticky="ew",
            padx=8,
            pady=(0, 8),
        )
        bubble.grid_columnconfigure(0, weight=1)

        # Sender label
        sender_lbl = ctk.CTkLabel(
            bubble,
            text=sender,
            text_color=sender_color,
            font=(FONT_FAMILY, FONT_SIZE_SMALL - 1, "bold"),
            anchor="w",
        )
        sender_lbl.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        # Message text
        msg_lbl = ctk.CTkLabel(
            bubble,
            text=text,
            text_color=fg,
            font=(FONT_FAMILY, FONT_SIZE_BASE),
            anchor="w",
            justify="left",
            wraplength=SIDEBAR_WIDTH - 60,  # Wrap to sidebar width
        )
        msg_lbl.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Auto-scroll to bottom
        self.after(50, self._scroll_to_bottom)

    # ──────────────────────────────────────────────
    #  CORE LOGIC
    # ──────────────────────────────────────────────

    def _on_enter_key(self, event):
        """Send message on Enter (without Shift)."""
        if not event.state & 0x1:  # Not Shift key
            self._on_send()
            return "break"  # Prevent newline insertion

    def _on_send(self):
        """Handle send button click — route to System Executor or AI."""
        if self.is_thinking:
            return  # Prevent double-send while AI is responding

        raw_text = self.input_box.get("1.0", "end").strip()
        if not raw_text:
            return

        # Clear input immediately
        self.input_box.delete("1.0", "end")

        # Display user's message
        self._add_user_bubble(raw_text)

        # ── System Executor check FIRST ──
        # Match against known commands (case-insensitive)
        lower_text = raw_text.lower().strip()
        for trigger, config in SYSTEM_COMMANDS.items():
            if trigger in lower_text:
                self._execute_system_command(config)
                return  # Don't call AI for system commands

        # ── Otherwise, call AI ──
        if not self.api_client:
            self._add_system_message(
                "⚠ No API key connected.\n"
                "Enter your OpenAI API key above and click ▶"
            )
            return

        # Run AI call in background thread (keeps UI responsive)
        self.is_thinking = True
        self._set_status("Sentinel is thinking...")
        threading.Thread(
            target=self._call_ai,
            args=(raw_text,),
            daemon=True,
        ).start()

    def _execute_system_command(self, config: dict):
        """
        System Executor: Runs actions triggered by special keywords.

        Supports:
          - "url"   → opens URL in default browser
          - "shell" → runs a shell command via subprocess
        """
        label = config.get("label", "Executing command...")
        cmd_type = config.get("type", "url")
        target = config.get("target", "")

        # Show action feedback
        self._add_system_message(f"⚡ {label}")
        self._set_status("System command executed.")

        if cmd_type == "url":
            webbrowser.open(target)
        elif cmd_type == "shell":
            # Run shell commands (e.g., open apps)
            subprocess.Popen(target, shell=True)

    def _call_ai(self, user_message: str):
        """
        Background thread: sends message to OpenAI and streams the reply.

        Maintains conversation history for multi-turn context.
        """
        # Add to history
        self.chat_history.append({
            "role": "user",
            "content": user_message,
        })

        try:
            response = self.api_client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *self.chat_history,  # Full conversation context
                ],
                max_tokens=1024,
                temperature=0.7,
            )

            ai_reply = response.choices[0].message.content.strip()

            # Add AI response to history
            self.chat_history.append({
                "role": "assistant",
                "content": ai_reply,
            })

            # Update UI on main thread
            self.after(0, self._add_ai_bubble, ai_reply)
            self.after(0, self._set_status,
                f"Tokens used: {response.usage.total_tokens}")

        except Exception as e:
            error_msg = f"API Error: {str(e)}"
            self.after(0, self._add_system_message, f"⚠ {error_msg}")
            self.after(0, self._set_status, "Error — check API key or network.")

        finally:
            self.is_thinking = False

    # ──────────────────────────────────────────────
    #  API KEY MANAGEMENT
    # ──────────────────────────────────────────────

    def _connect_api(self):
        """Validate and store the OpenAI API key."""
        key = self.key_entry.get().strip()
        if not key:
            self.connection_indicator.configure(
                text="● No key provided",
                text_color="#FF6B6B",
            )
            return

        # Initialize OpenAI client
        self.api_client = OpenAI(api_key=key)

        # Save key locally for next session (only if not already in .env)
        if not os.getenv("OPENAI_API_KEY"):
            self._save_key(key)

        self.connection_indicator.configure(
            text="● Connected",
            text_color="#6BFF9E",
        )
        self._set_status("API key connected. Ready to chat!")
        self._add_system_message(
            "✅ API key accepted. Sentinel Buddy is fully online.\n"
            "Ask me anything or use a quick command!"
        )

    def _save_key(self, key: str):
        """Save API key to local config file (fallback when no .env key exists)."""
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ".sentinel_config.json"
        )
        with open(config_path, "w") as f:
            json.dump({"api_key": key}, f)

    def _load_saved_key(self):
        """
        Key resolution priority:
          1. OPENAI_API_KEY in .env  (highest priority)
          2. .sentinel_config.json   (manual entry fallback)
        """
        # ── Priority 1: .env variable ──
        env_key = os.getenv("OPENAI_API_KEY", "").strip()
        if env_key:
            self.key_entry.insert(0, env_key)
            self._connect_api()  # Auto-connect silently
            return

        # ── Priority 2: saved config JSON ──
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ".sentinel_config.json"
        )
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    saved_key = data.get("api_key", "")
                if saved_key:
                    self.key_entry.insert(0, saved_key)
                    self._connect_api()  # Auto-connect on launch
            except Exception:
                pass  # Silently ignore corrupt config

    # ──────────────────────────────────────────────
    #  UTILITIES
    # ──────────────────────────────────────────────

    def _scroll_to_bottom(self):
        """Force scroll the chat to the latest message."""
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _set_status(self, text: str):
        """Update the bottom status bar label."""
        self.status_label.configure(text=text)

    def _update_clock(self):
        """Show live clock in status bar."""
        now = datetime.now().strftime("%H:%M")
        self.time_label.configure(text=now)
        self.after(30_000, self._update_clock)  # Update every 30s


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = SentinelBuddy()
    app.mainloop()
