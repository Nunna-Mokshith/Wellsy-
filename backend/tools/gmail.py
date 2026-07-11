"""
Wellsy Tools -- Gmail Automation
Send, read, and search emails using browser automation with Chrome.
Uses Gmail URLs with pre-filled parameters and pyautogui for interactions.
"""
import subprocess
import time
import urllib.parse
import os
from pathlib import Path
from langchain_core.tools import tool
import pyautogui


# Chrome path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
GMAIL_URL = "https://mail.google.com"
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
def open_gmail() -> str:
    """Open Gmail inbox in Chrome. The user should already be logged into their Google account."""
    try:
        _open_chrome_url(GMAIL_URL)
        _wait_for_page_load(4)
        return "Gmail inbox is now open in Chrome."
    except FileNotFoundError:
        return "Chrome not found. Is Google Chrome installed at the default location?"
    except Exception as e:
        return f"Failed to open Gmail: {e}"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail by opening Chrome with a pre-filled compose URL.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body text.
    """
    try:
        # URL-encode the parameters
        params = urllib.parse.urlencode({
            "view": "cm",
            "fs": "1",
            "to": to,
            "su": subject,
            "body": body,
        })
        compose_url = f"{GMAIL_URL}/mail/?{params}"

        _open_chrome_url(compose_url)
        _wait_for_page_load(5)

        # Send the email with Ctrl+Enter
        pyautogui.hotkey("ctrl", "Return")
        time.sleep(2)

        return f"Email sent to {to} with subject '{subject}'."
    except Exception as e:
        return f"Failed to send email: {e}"


@tool
def read_latest_emails(count: int = 5) -> str:
    """Open Gmail inbox and read visible email subjects using keyboard navigation.

    Args:
        count: Number of recent emails to try to read (default 5).
    """
    try:
        _open_chrome_url(GMAIL_URL)
        _wait_for_page_load(5)

        # Use Gmail keyboard shortcuts to navigate
        # First, make sure keyboard shortcuts are active by clicking on the page
        pyautogui.click(x=pyautogui.size()[0] // 2, y=pyautogui.size()[1] // 2)
        time.sleep(1)

        # Select all visible text using Ctrl+A then copy
        # A better approach: use the Gmail API URL to get a simpler view
        # Navigate to the basic HTML view for easier reading
        basic_url = f"{GMAIL_URL}/mail/u/0/#inbox"
        _open_chrome_url(basic_url)
        _wait_for_page_load(4)

        # Use Ctrl+A to select all, Ctrl+C to copy
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.5)

        # Read from clipboard
        import subprocess as sp
        result = sp.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True, text=True, timeout=5
        )
        clipboard_text = result.stdout.strip()

        if clipboard_text:
            # Truncate to reasonable length
            lines = clipboard_text.split("\n")
            # Filter out empty lines and get meaningful content
            meaningful = [l.strip() for l in lines if l.strip()]
            preview = "\n".join(meaningful[:50])
            return f"Gmail inbox content (visible text):\n\n{preview}"
        else:
            return "Gmail is open but could not read inbox content. Please check the browser."

    except Exception as e:
        return f"Failed to read emails: {e}"


@tool
def search_emails(query: str) -> str:
    """Search for emails in Gmail by opening the search URL.

    Args:
        query: Search query (e.g., 'from:someone@example.com', 'subject:meeting', 'is:unread').
    """
    try:
        # Use Gmail search URL directly
        encoded_query = urllib.parse.quote(query)
        search_url = f"{GMAIL_URL}/mail/u/0/#search/{encoded_query}"

        _open_chrome_url(search_url)
        _wait_for_page_load(5)

        # Read visible results
        pyautogui.click(x=pyautogui.size()[0] // 2, y=pyautogui.size()[1] // 2)
        time.sleep(1)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.5)

        import subprocess as sp
        result = sp.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True, text=True, timeout=5
        )
        clipboard_text = result.stdout.strip()

        if clipboard_text:
            lines = clipboard_text.split("\n")
            meaningful = [l.strip() for l in lines if l.strip()]
            preview = "\n".join(meaningful[:50])
            return f"Search results for '{query}':\n\n{preview}"
        else:
            return f"Search opened for '{query}' but could not read results. Check the browser."

    except Exception as e:
        return f"Failed to search emails: {e}"


@tool
def send_email_with_attachment(to: str, subject: str, body: str, file_path: str) -> str:
    """Send an email via Gmail with a file attachment.

    Opens a compose window with pre-filled fields, then attaches a file using the
    file dialog.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body text.
        file_path: Absolute path to the file to attach.
    """
    try:
        # Verify the file exists
        target = Path(file_path).expanduser()
        if not target.exists():
            return f"Attachment file not found: {file_path}"

        # Open compose URL with pre-filled fields
        params = urllib.parse.urlencode({
            "view": "cm",
            "fs": "1",
            "to": to,
            "su": subject,
            "body": body,
        })
        compose_url = f"{GMAIL_URL}/mail/?{params}"

        _open_chrome_url(compose_url)
        _wait_for_page_load(5)

        # Click the attach button (paperclip icon) -- we can use the keyboard shortcut
        # Gmail doesn't have a keyboard shortcut for attach, so we click the attach area
        # A more reliable approach: use Tab to navigate to attach or find the button
        # The attach file button is usually at the bottom of the compose window

        # Press Tab a few times to get focus into the compose window, then use
        # the attach files shortcut: there is no standard one, so we locate and click it.
        # We'll look for the attach icon by pressing the paperclip area at bottom of compose.

        # Alternative approach: just open file dialog via the attach button coordinates
        # Since compose window positions can vary, use pyautogui to find the attach icon
        # Fallback: use Ctrl+Shift+A if available (not standard Gmail)

        # Most reliable: click on the bottom toolbar of compose, near the attach icon
        # The compose window is typically at bottom-right
        screen_w, screen_h = pyautogui.size()

        # Look for the attach button image, or use a heuristic position
        # In Gmail, the compose toolbar with attach is at the bottom of the compose popup
        # Typical position: bottom-right area of screen, about 30-40% from right, near bottom

        # Click the attach button area (approximate position in compose toolbar)
        # This is the paperclip/attach icon in the compose toolbar
        attach_x = int(screen_w * 0.62)
        attach_y = int(screen_h * 0.88)
        pyautogui.click(attach_x, attach_y)
        time.sleep(2)

        # The file dialog should be open now -- type the file path and press Enter
        abs_path = str(target.resolve())
        pyautogui.typewrite(abs_path, interval=0.02) if abs_path.isascii() else pyautogui.write(abs_path)
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(3)  # Wait for upload

        # Now send the email
        pyautogui.hotkey("ctrl", "Return")
        time.sleep(2)

        return f"Email sent to {to} with subject '{subject}' and attachment '{target.name}'."
    except Exception as e:
        return f"Failed to send email with attachment: {e}"


# Export all tools
GMAIL_TOOLS = [open_gmail, send_email, read_latest_emails, search_emails, send_email_with_attachment]
