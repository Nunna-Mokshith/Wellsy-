"""
Wellsy Tools -- Outlook Automation
Open, compose, send, and read emails on Outlook.live.com using Chrome browser
automation with subprocess and pyautogui.
"""
import subprocess
import time
import pyautogui
from langchain_core.tools import tool


# Chrome path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTLOOK_URL = "https://outlook.live.com/mail/"
USER_EMAIL = "mokshithnunna31@gmail.com"

# pyautogui safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


def _open_chrome_url(url: str) -> None:
    """Open a URL in Chrome."""
    subprocess.Popen([CHROME_PATH, url])


def _wait_for_page_load(seconds: float = 3.0) -> None:
    """Wait for the page to load."""
    time.sleep(seconds)


@tool
def open_outlook() -> str:
    """Open Outlook inbox in Chrome. The user should already be logged into their
    Microsoft account (mokshithnunna31@gmail.com)."""
    try:
        _open_chrome_url(OUTLOOK_URL)
        _wait_for_page_load(5)
        print("[Wellsy] Outlook inbox opened in Chrome.")
        return "Outlook inbox is now open in Chrome."
    except FileNotFoundError:
        return "Chrome not found. Is Google Chrome installed at the default location?"
    except Exception as e:
        return f"Failed to open Outlook: {e}"


@tool
def send_outlook_email(to: str, subject: str, body: str) -> str:
    """Send an email via Outlook Web by opening Chrome, clicking New Mail,
    filling in To/Subject/Body fields, and clicking Send.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body text.
    """
    try:
        # Step 1: Open Outlook in Chrome
        _open_chrome_url(OUTLOOK_URL)
        _wait_for_page_load(6)
        print("[Wellsy] Outlook loaded, starting compose flow...")

        # Step 2: Click 'New mail' button using keyboard shortcut
        # Outlook Web shortcut for New Message: N (when not focused in a text field)
        # First click somewhere neutral to ensure focus is on the page
        screen_w, screen_h = pyautogui.size()
        pyautogui.click(screen_w // 2, screen_h // 2)
        time.sleep(1)

        # Press 'N' to open new message (Outlook keyboard shortcut)
        pyautogui.press("n")
        time.sleep(3)  # Wait for compose pane to open

        print("[Wellsy] Compose pane opened, filling fields...")

        # Step 3: Fill the To field
        # After pressing N, the cursor should be in the To field
        pyautogui.typewrite(to, interval=0.03)
        time.sleep(0.5)
        # Press Tab to move to the next field (this may trigger auto-complete)
        pyautogui.press("tab")
        time.sleep(1)

        # Step 4: Fill the Subject field
        # Depending on Outlook layout, we may need an extra Tab to skip CC/BCC
        # Typically: To -> Tab -> Subject in Outlook Web
        pyautogui.typewrite(subject, interval=0.03)
        time.sleep(0.5)

        # Step 5: Tab into the Body field
        pyautogui.press("tab")
        time.sleep(0.5)
        pyautogui.typewrite(body, interval=0.02)
        time.sleep(0.5)

        print("[Wellsy] Fields filled, sending email...")

        # Step 6: Send the email with Ctrl+Enter
        pyautogui.hotkey("ctrl", "Return")
        time.sleep(2)

        print(f"[Wellsy] Email sent to {to}.")
        return f"Email sent to {to} with subject '{subject}'."
    except Exception as e:
        return f"Failed to send Outlook email: {e}"


@tool
def read_outlook_inbox() -> str:
    """Open Outlook inbox and read visible email subjects by selecting and
    copying page text to the clipboard."""
    try:
        # Open Outlook inbox
        _open_chrome_url(OUTLOOK_URL)
        _wait_for_page_load(6)

        print("[Wellsy] Outlook inbox loaded, reading visible emails...")

        # Click on the message list area to set focus
        screen_w, screen_h = pyautogui.size()
        pyautogui.click(screen_w // 3, screen_h // 2)
        time.sleep(1)

        # Select all visible text
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.5)

        # Copy to clipboard
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.5)

        # Read clipboard content via PowerShell
        result = subprocess.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True, text=True, timeout=5
        )
        clipboard_text = result.stdout.strip()

        if clipboard_text:
            # Filter and trim to readable content
            lines = clipboard_text.split("\n")
            meaningful = [line.strip() for line in lines if line.strip()]
            preview = "\n".join(meaningful[:50])
            print("[Wellsy] Inbox content captured.")
            return f"Outlook inbox content (visible text):\n\n{preview}"
        else:
            return ("Outlook is open but could not read inbox content. "
                    "Please check the browser.")

    except Exception as e:
        return f"Failed to read Outlook inbox: {e}"


# Export all tools
OUTLOOK_TOOLS = [open_outlook, send_outlook_email, read_outlook_inbox]
