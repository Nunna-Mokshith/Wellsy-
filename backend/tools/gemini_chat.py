"""
Wellsy Tools -- Gemini AI Chat
Open and interact with Google Gemini AI in the browser.
"""
import subprocess
import time
import pyperclip
import pyautogui
from langchain_core.tools import tool


# Chrome executable path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Gemini URL
GEMINI_URL = "https://gemini.google.com/"

# How long to wait for the Gemini page to load (seconds)
PAGE_LOAD_DELAY = 5


def _open_chrome_url(url: str) -> None:
    """Open a URL in Chrome (new tab if Chrome is already running)."""
    subprocess.Popen([CHROME_PATH, url])


@tool
def open_gemini() -> str:
    """Open Google Gemini AI in Chrome. The user should already be logged in as mokshithnunna31@gmail.com."""
    try:
        _open_chrome_url(GEMINI_URL)
        print("[Gemini] Opening Gemini AI in Chrome")
        time.sleep(PAGE_LOAD_DELAY)
        return "Opened Google Gemini AI in Chrome."
    except FileNotFoundError:
        return "Could not find Chrome. Is Google Chrome installed?"
    except Exception as e:
        return f"Error opening Gemini: {e}"


@tool
def ask_gemini(prompt: str) -> str:
    """Open Google Gemini AI and send a prompt. Opens Gemini in Chrome, waits for the page to load, pastes the prompt into the text area using clipboard (supports unicode), and presses Enter to submit."""
    try:
        # Open Gemini
        _open_chrome_url(GEMINI_URL)
        print("[Gemini] Opening Gemini AI in Chrome")
        time.sleep(PAGE_LOAD_DELAY)

        # Click on the text input area -- it is typically near the bottom-center
        # of the page on a 1920x1080 display at 100% scaling.
        # The rich text editor / prompt box is around (960, 880).
        pyautogui.click(960, 880)
        time.sleep(0.5)

        # Use clipboard paste to support unicode characters
        old_clipboard = None
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            pass

        pyperclip.copy(prompt)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)

        # Restore old clipboard
        if old_clipboard is not None:
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass

        # Press Enter to submit
        pyautogui.press('enter')
        print(f"[Gemini] Sent prompt: {prompt[:80]}")
        return f"Sent prompt to Gemini: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'"

    except FileNotFoundError:
        return "Could not find Chrome. Is Google Chrome installed?"
    except Exception as e:
        return f"Error asking Gemini: {e}"


# Export all tools
GEMINI_CHAT_TOOLS = [
    open_gemini,
    ask_gemini,
]
