"""
Sentinel Buddy - Automation Engine
==================================
Dual-Engine Architecture for Web and OS Automation

Web Agent: Playwright-based browser automation
OS Agent: PyAutoGUI-based desktop automation
Safety: Kill Switch (Ctrl+Shift+Q) + FAILSAFE
"""

import threading
import queue
import time
import random
import keyboard
import pyautogui
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

# Safety Configuration
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Small delay between actions for safety


class EngineType(Enum):
    """Automation engine types."""
    WEB = "web"
    OS = "os"


class ActionType(Enum):
    """Supported automation action types."""
    # Web Actions
    WEB_NAVIGATE = "web_navigate"
    WEB_CLICK = "web_click"
    WEB_TYPE = "web_type"
    WEB_SCRAPE = "web_scrape"
    WEB_WAIT = "web_wait"
    
    # OS Actions
    OS_MOUSE_MOVE = "os_mouse_move"
    OS_MOUSE_CLICK = "os_mouse_click"
    OS_TYPE = "os_type"
    OS_HOTKEY = "os_hotkey"
    OS_PIXEL_CHECK = "os_pixel_check"
    OS_SCREENSHOT = "os_screenshot"
    
    # Control Actions
    DELAY = "delay"
    CHAIN_START = "chain_start"
    CHAIN_END = "chain_end"


class AutomationError(Exception):
    """Custom exception for automation errors."""
    pass


class SafetyKillSwitch:
    """Emergency kill switch for terminating all automation."""
    
    def __init__(self):
        self._enabled = True
        self._kill_signal = threading.Event()
        self._thread = None
        
    def enable(self):
        """Enable the kill switch."""
        if not self._enabled:
            self._enabled = True
            self._thread = threading.Thread(target=self._listen, daemon=True)
            self._thread.start()
    
    def disable(self):
        """Disable the kill switch."""
        self._enabled = False
        if self._thread:
            keyboard.unhook_all()
    
    def _listen(self):
        """Listen for kill switch key combination (Ctrl+Shift+Q)."""
        keyboard.add_hotkey('ctrl+shift+q', self._trigger)
        keyboard.wait()
    
    def _trigger(self):
        """Trigger the kill signal."""
        print("[KILL SWITCH] Emergency termination triggered!")
        self._kill_signal.set()
    
    def is_triggered(self) -> bool:
        """Check if kill switch was triggered."""
        return self._kill_signal.is_set()
    
    def reset(self):
        """Reset the kill signal."""
        self._kill_signal.clear()


class WebAgent:
    """Playwright-based web automation agent."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize Playwright browser."""
        if self._initialized:
            return True
        
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = self.context.new_page()
            self._initialized = True
            return True
        except Exception as e:
            raise AutomationError(f"Failed to initialize WebAgent: {str(e)}")
    
    def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        if not self._initialized:
            self.initialize()
        
        try:
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            return True
        except Exception as e:
            raise AutomationError(f"Navigation failed: {str(e)}")
    
    def click_element(self, selector: str, timeout: int = 5000) -> bool:
        """Click an element by CSS selector."""
        if not self._initialized:
            raise AutomationError("WebAgent not initialized")
        
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.page.click(selector)
            return True
        except Exception as e:
            raise AutomationError(f"Click failed: {str(e)}")
    
    def type_text(self, selector: str, text: str, clear_first: bool = True) -> bool:
        """Type text into an element."""
        if not self._initialized:
            raise AutomationError("WebAgent not initialized")
        
        try:
            if clear_first:
                self.page.fill(selector, "")
            self.page.type(selector, text, delay=random.uniform(50, 150))
            return True
        except Exception as e:
            raise AutomationError(f"Type failed: {str(e)}")
    
    def scrape_text(self, selector: str = None) -> str:
        """Scrape text from page or specific element."""
        if not self._initialized:
            raise AutomationError("WebAgent not initialized")
        
        try:
            if selector:
                element = self.page.wait_for_selector(selector, timeout=5000)
                return element.inner_text() if element else ""
            return self.page.inner_text('body')
        except Exception as e:
            raise AutomationError(f"Scrape failed: {str(e)}")
    
    def wait(self, milliseconds: int):
        """Wait for specified milliseconds."""
        time.sleep(milliseconds / 1000)
    
    def close(self):
        """Close browser and cleanup."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self._initialized = False


class OSAgent:
    """PyAutoGUI-based OS automation agent."""
    
    def __init__(self):
        self._initialized = True
    
    def mouse_move(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Move mouse to coordinates with human-like motion."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            raise AutomationError(f"Mouse move failed: {str(e)}")
    
    def mouse_click(self, button: str = 'left', clicks: int = 1) -> bool:
        """Click mouse button."""
        try:
            pyautogui.click(button=button, clicks=clicks)
            return True
        except Exception as e:
            raise AutomationError(f"Mouse click failed: {str(e)}")
    
    def type_text(self, text: str, human_like: bool = True) -> bool:
        """Type text with human-like speed randomization."""
        try:
            if human_like:
                # Type each character with random delay
                for char in text:
                    delay = random.uniform(0.05, 0.15)
                    pyautogui.typewrite(char, interval=delay)
            else:
                pyautogui.typewrite(text, interval=0.01)
            return True
        except Exception as e:
            raise AutomationError(f"Type failed: {str(e)}")
    
    def press_hotkey(self, *keys) -> bool:
        """Press hotkey combination."""
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            raise AutomationError(f"Hotkey failed: {str(e)}")
    
    def pixel_check(self, x: int, y: int, expected_color: tuple, tolerance: int = 10) -> bool:
        """Check if pixel at coordinates matches expected color."""
        try:
            actual_color = pyautogui.pixel(x, y)
            # Check if colors are within tolerance
            r_diff = abs(actual_color[0] - expected_color[0])
            g_diff = abs(actual_color[1] - expected_color[1])
            b_diff = abs(actual_color[2] - expected_color[2])
            return (r_diff <= tolerance and g_diff <= tolerance and b_diff <= tolerance)
        except Exception as e:
            raise AutomationError(f"Pixel check failed: {str(e)}")
    
    def screenshot(self, filename: str = None) -> str:
        """Take screenshot and save to file."""
        try:
            if filename:
                return pyautogui.screenshot(filename)
            else:
                return pyautogui.screenshot()
        except Exception as e:
            raise AutomationError(f"Screenshot failed: {str(e)}")
    
    def get_screen_size(self) -> tuple:
        """Get screen dimensions."""
        return pyautogui.size()
    
    def get_mouse_position(self) -> tuple:
        """Get current mouse position."""
        return pyautogui.position()


class Task:
    """Single automation task."""
    
    def __init__(self, action_type: ActionType, params: Dict[str, Any], callback: Callable = None):
        self.action_type = action_type
        self.params = params
        self.callback = callback
        self.result = None
        self.error = None
        self.completed = False
    
    def execute(self, web_agent: WebAgent, os_agent: OSAgent) -> Any:
        """Execute the task."""
        try:
            if self.action_type == ActionType.WEB_NAVIGATE:
                self.result = web_agent.navigate(self.params['url'])
            
            elif self.action_type == ActionType.WEB_CLICK:
                self.result = web_agent.click_element(
                    self.params['selector'],
                    self.params.get('timeout', 5000)
                )
            
            elif self.action_type == ActionType.WEB_TYPE:
                self.result = web_agent.type_text(
                    self.params['selector'],
                    self.params['text'],
                    self.params.get('clear_first', True)
                )
            
            elif self.action_type == ActionType.WEB_SCRAPE:
                self.result = web_agent.scrape_text(self.params.get('selector'))
            
            elif self.action_type == ActionType.WEB_WAIT:
                web_agent.wait(self.params['milliseconds'])
                self.result = True
            
            elif self.action_type == ActionType.OS_MOUSE_MOVE:
                self.result = os_agent.mouse_move(
                    self.params['x'],
                    self.params['y'],
                    self.params.get('duration', 0.5)
                )
            
            elif self.action_type == ActionType.OS_MOUSE_CLICK:
                self.result = os_agent.mouse_click(
                    self.params.get('button', 'left'),
                    self.params.get('clicks', 1)
                )
            
            elif self.action_type == ActionType.OS_TYPE:
                self.result = os_agent.type_text(
                    self.params['text'],
                    self.params.get('human_like', True)
                )
            
            elif self.action_type == ActionType.OS_HOTKEY:
                self.result = os_agent.press_hotkey(*self.params['keys'])
            
            elif self.action_type == ActionType.OS_PIXEL_CHECK:
                self.result = os_agent.pixel_check(
                    self.params['x'],
                    self.params['y'],
                    self.params['color'],
                    self.params.get('tolerance', 10)
                )
            
            elif self.action_type == ActionType.OS_SCREENSHOT:
                self.result = os_agent.screenshot(self.params.get('filename'))
            
            elif self.action_type == ActionType.DELAY:
                time.sleep(self.params['milliseconds'] / 1000)
                self.result = True
            
            else:
                raise AutomationError(f"Unknown action type: {self.action_type}")
            
            self.completed = True
            
            if self.callback:
                self.callback(self.result)
            
            return self.result
            
        except Exception as e:
            self.error = str(e)
            self.completed = True
            raise AutomationError(f"Task execution failed: {str(e)}")


class TaskRunner:
    """Task runner with queue and chaining support."""
    
    def __init__(self, headless_browser: bool = True):
        self.web_agent = WebAgent(headless=headless_browser)
        self.os_agent = OSAgent()
        self.task_queue = queue.Queue()
        self.current_chain: List[Task] = []
        self.is_running = False
        self.worker_thread = None
        self.kill_switch = SafetyKillSwitch()
        self.kill_switch.enable()
        self.on_task_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
    
    def add_task(self, task: Task):
        """Add a single task to the queue."""
        self.task_queue.put(task)
    
    def add_chain(self, tasks: List[Task]):
        """Add a chain of tasks to the queue."""
        for task in tasks:
            self.add_task(task)
    
    def start(self):
        """Start the task runner worker thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
    
    def stop(self):
        """Stop the task runner."""
        self.is_running = False
        self.kill_switch.disable()
    
    def _worker(self):
        """Worker thread that processes tasks."""
        while self.is_running and not self.kill_switch.is_triggered():
            try:
                task = self.task_queue.get(timeout=0.1)
                
                # Check kill switch before executing
                if self.kill_switch.is_triggered():
                    break
                
                task.execute(self.web_agent, self.os_agent)
                
                if self.on_task_complete:
                    self.on_task_complete(task)
                
            except queue.Empty:
                continue
            except Exception as e:
                if self.on_error:
                    self.on_error(e)
                print(f"[TaskRunner] Error: {str(e)}")
    
    def emergency_stop(self):
        """Emergency stop - terminate all operations."""
        self.kill_switch._trigger()
        self.stop()
        self.web_agent.close()
    
    def clear_queue(self):
        """Clear all pending tasks."""
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except queue.Empty:
                break
    
    def get_queue_size(self) -> int:
        """Get the number of pending tasks."""
        return self.task_queue.qsize()
    
    def is_idle(self) -> bool:
        """Check if the runner is idle (no tasks in queue)."""
        return self.task_queue.empty()


# Convenience functions for creating tasks
def create_web_navigate_task(url: str, callback: Callable = None) -> Task:
    """Create a web navigation task."""
    return Task(ActionType.WEB_NAVIGATE, {'url': url}, callback)


def create_web_click_task(selector: str, timeout: int = 5000, callback: Callable = None) -> Task:
    """Create a web click task."""
    return Task(ActionType.WEB_CLICK, {'selector': selector, 'timeout': timeout}, callback)


def create_web_type_task(selector: str, text: str, clear_first: bool = True, callback: Callable = None) -> Task:
    """Create a web type task."""
    return Task(ActionType.WEB_TYPE, {'selector': selector, 'text': text, 'clear_first': clear_first}, callback)


def create_web_scrape_task(selector: str = None, callback: Callable = None) -> Task:
    """Create a web scrape task."""
    return Task(ActionType.WEB_SCRAPE, {'selector': selector}, callback)


def create_os_mouse_move_task(x: int, y: int, duration: float = 0.5, callback: Callable = None) -> Task:
    """Create an OS mouse move task."""
    return Task(ActionType.OS_MOUSE_MOVE, {'x': x, 'y': y, 'duration': duration}, callback)


def create_os_mouse_click_task(button: str = 'left', clicks: int = 1, callback: Callable = None) -> Task:
    """Create an OS mouse click task."""
    return Task(ActionType.OS_MOUSE_CLICK, {'button': button, 'clicks': clicks}, callback)


def create_os_type_task(text: str, human_like: bool = True, callback: Callable = None) -> Task:
    """Create an OS type task."""
    return Task(ActionType.OS_TYPE, {'text': text, 'human_like': human_like}, callback)


def create_os_hotkey_task(*keys, callback: Callable = None) -> Task:
    """Create an OS hotkey task."""
    return Task(ActionType.OS_HOTKEY, {'keys': keys}, callback)


def create_delay_task(milliseconds: int, callback: Callable = None) -> Task:
    """Create a delay task."""
    return Task(ActionType.DELAY, {'milliseconds': milliseconds}, callback)


# Example usage
if __name__ == "__main__":
    # Create task runner
    runner = TaskRunner(headless_browser=False)
    
    # Define callback for task completion
    def on_complete(task: Task):
        print(f"Task completed: {task.action_type.value}, Result: {task.result}")
    
    # Define callback for errors
    def on_error(error):
        print(f"Error occurred: {error}")
    
    runner.on_task_complete = on_complete
    runner.on_error = on_error
    
    # Example: Chain actions - Open Chrome -> Go to URL -> Type credentials
    task_chain = [
        create_web_navigate_task("https://example.com"),
        create_delay_task(1000),
        create_web_click_task("#username"),
        create_web_type_task("#username", "test@example.com"),
        create_delay_task(500),
        create_web_click_task("#password"),
        create_web_type_task("#password", "password123"),
        create_delay_task(500),
        create_web_click_task("#login-button"),
    ]
    
    # Add chain to queue
    runner.add_chain(task_chain)
    
    # Start runner
    runner.start()
    
    # Wait for completion (in real app, you'd handle this differently)
    time.sleep(10)
    
    # Stop runner
    runner.stop()
    runner.web_agent.close()
    
    print("Automation complete!")
