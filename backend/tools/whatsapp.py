"""
Wellsy Tools -- WhatsApp Desktop Automation
Open WhatsApp, send messages, send files, and read recent messages.
Uses pywinauto (UIA backend) + pyautogui for desktop automation.
"""
import subprocess
import time
import os
from pathlib import Path
from langchain_core.tools import tool
import pyautogui
import pywinauto


# WhatsApp UWP shell launch string
WHATSAPP_SHELL = r"shell:AppsFolder\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"

# Timing constants (seconds)
LAUNCH_WAIT = 6
FOCUS_WAIT = 2
SEARCH_WAIT = 1
CHAT_OPEN_WAIT = 3
CLIPBOARD_WAIT = 2
PASTE_WAIT = 5
SEND_WAIT = 5
TYPE_INTERVAL = 0.08


def _find_whatsapp_window():
    """Find and return the main (largest) WhatsApp window via pywinauto UIA backend.

    When WhatsApp is running, there may be multiple windows (notifications, popups).
    We pick the one with the largest area as the main window.

    Returns:
        The pywinauto window wrapper for the main WhatsApp window, or None.
    """
    desktop = pywinauto.Desktop(backend="uia")
    whatsapp_windows = desktop.windows(title_re=".*WhatsApp.*")
    if not whatsapp_windows:
        return None

    main_win = None
    max_area = 0
    for win in whatsapp_windows:
        try:
            rect = win.rectangle()
            area = (rect.right - rect.left) * (rect.bottom - rect.top)
            if area > max_area:
                max_area = area
                main_win = win
        except Exception:
            pass
    return main_win


def _launch_and_focus():
    """Launch WhatsApp Desktop and focus the main window.

    Returns:
        (window, message) tuple. window may be None on failure.
    """
    subprocess.Popen(["explorer", WHATSAPP_SHELL])
    time.sleep(LAUNCH_WAIT)

    win = _find_whatsapp_window()
    if win is None:
        return None, "Could not find any WhatsApp window after launch."

    try:
        win.set_focus()
    except Exception:
        pass  # sometimes set_focus raises but window is still usable
    time.sleep(FOCUS_WAIT)
    return win, "WhatsApp is open and focused."


def _search_contact(contact_name: str):
    """Use Ctrl+F to search for a contact and open the chat."""
    pyautogui.hotkey("ctrl", "f")
    time.sleep(SEARCH_WAIT)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.typewrite(contact_name, interval=TYPE_INTERVAL)
    time.sleep(CHAT_OPEN_WAIT)
    pyautogui.press("enter")
    time.sleep(CHAT_OPEN_WAIT)


@tool
def open_whatsapp() -> str:
    """Open WhatsApp Desktop and bring it to the foreground."""
    try:
        win, msg = _launch_and_focus()
        if win is None:
            return "WhatsApp launched but could not detect window. " + msg
        title = win.window_text()
        return f"WhatsApp is open. Window title: {title}"
    except Exception as e:
        return f"Failed to open WhatsApp: {e}"


@tool
def send_message(contact_name: str, message: str) -> str:
    """Send a text message to a WhatsApp contact by name.

    Opens WhatsApp Desktop, searches for the contact, opens the chat,
    types the message, and presses Enter to send.

    Args:
        contact_name: The display name of the contact (e.g. 'Teddy').
        message: The text message to send.
    """
    try:
        print(f"[whatsapp] Opening WhatsApp to message {contact_name}...")
        win, msg = _launch_and_focus()
        if win is None:
            return f"Could not open WhatsApp: {msg}"

        print(f"[whatsapp] Searching for contact: {contact_name}")
        _search_contact(contact_name)

        # Type the message into the chat input
        print(f"[whatsapp] Typing message...")
        # Use pyperclip-style clipboard paste to support unicode text
        import subprocess as sp
        sp.run(
            ["powershell", "-Command", f"Set-Clipboard -Value '{message}'"],
            capture_output=True,
        )
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)

        # Send
        pyautogui.press("enter")
        time.sleep(SEND_WAIT)

        return f"Message sent to {contact_name}: {message}"
    except Exception as e:
        return f"Failed to send message to {contact_name}: {e}"


@tool
def send_file(contact_name: str, file_path: str) -> str:
    """Send a file (PDF, image, document, etc.) to a WhatsApp contact.

    Opens WhatsApp Desktop, searches for the contact, copies the file
    to the clipboard using PowerShell Set-Clipboard -Path, pastes it
    into the chat, and presses Enter to send.

    Args:
        contact_name: The display name of the contact (e.g. 'Teddy').
        file_path: Absolute path to the file to send.
    """
    try:
        target = Path(file_path).resolve()
        if not target.exists():
            return f"File not found: {file_path}"

        print(f"[whatsapp] Opening WhatsApp to send file to {contact_name}...")
        win, msg = _launch_and_focus()
        if win is None:
            return f"Could not open WhatsApp: {msg}"

        print(f"[whatsapp] Searching for contact: {contact_name}")
        _search_contact(contact_name)

        # Copy file to clipboard via PowerShell
        print(f"[whatsapp] Copying file to clipboard: {target}")
        ps_cmd = f"Set-Clipboard -Path '{target}'"
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return f"Failed to copy file to clipboard: {result.stderr.strip()}"
        time.sleep(CLIPBOARD_WAIT)

        # Paste into chat
        print("[whatsapp] Pasting file into chat...")
        pyautogui.hotkey("ctrl", "v")
        time.sleep(PASTE_WAIT)

        # Press Enter to send the attachment
        print("[whatsapp] Sending...")
        pyautogui.press("enter")
        time.sleep(SEND_WAIT)

        return f"File sent to {contact_name}: {target.name}"
    except Exception as e:
        return f"Failed to send file to {contact_name}: {e}"


@tool
def read_recent_messages(contact_name: str) -> str:
    """Read visible (recent) messages from a WhatsApp chat.

    Opens WhatsApp Desktop, searches for the contact, then uses
    pywinauto to scrape the visible message list items from the chat.

    Args:
        contact_name: The display name of the contact whose chat to read.
    """
    try:
        print(f"[whatsapp] Opening WhatsApp to read messages from {contact_name}...")
        win, msg = _launch_and_focus()
        if win is None:
            return f"Could not open WhatsApp: {msg}"

        print(f"[whatsapp] Searching for contact: {contact_name}")
        _search_contact(contact_name)

        # Give the chat a moment to fully load
        time.sleep(2)

        # Re-acquire the window after navigation
        win = _find_whatsapp_window()
        if win is None:
            return "Lost WhatsApp window while reading messages."

        # Try to find message list items via UIA
        messages = []
        try:
            list_items = win.descendants(control_type="ListItem")
            for item in list_items:
                try:
                    text = item.window_text()
                    if text and len(text.strip()) > 0:
                        messages.append(text.strip())
                except Exception:
                    pass
        except Exception as e:
            return f"Could not read message elements: {e}"

        if not messages:
            return f"Opened chat with {contact_name} but could not extract any messages. The chat may be empty or the UI structure may have changed."

        # Return the last 20 messages to keep it manageable
        recent = messages[-20:]
        header = f"Recent messages from {contact_name}'s chat ({len(recent)} shown):"
        body = "\n".join(f"  - {m}" for m in recent)
        return f"{header}\n{body}"
    except Exception as e:
        return f"Failed to read messages from {contact_name}: {e}"


# Export all tools for Wellsy registration
WHATSAPP_TOOLS = [open_whatsapp, send_message, send_file, read_recent_messages]
