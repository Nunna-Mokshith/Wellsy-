"""
Wellsy Tools — Clipboard Monitor
Watch and interact with the clipboard.
"""
import pyperclip
from langchain_core.tools import tool


@tool
def get_clipboard() -> str:
    """Get the current contents of the clipboard."""
    try:
        content = pyperclip.paste()
        if not content:
            return "Clipboard is empty right now."
        if len(content) > 3000:
            return f"Clipboard contents (showing first 3000 chars):\n\n{content[:3000]}\n\n... ({len(content)} total chars)"
        return f"Here's what's on your clipboard:\n\n{content}"
    except Exception as e:
        return f"Couldn't read clipboard: {e}"


@tool
def set_clipboard(text: str) -> str:
    """Copy text to the clipboard."""
    try:
        pyperclip.copy(text)
        preview = text[:100] + "..." if len(text) > 100 else text
        return f"Copied to clipboard: {preview}"
    except Exception as e:
        return f"Couldn't copy to clipboard: {e}"


CLIPBOARD_TOOLS = [get_clipboard, set_clipboard]
