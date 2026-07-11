"""
Wellsy Tools — App Launcher & Controller
Open, close, and manage applications on Windows.
"""
import subprocess
import os
from pathlib import Path
from langchain_core.tools import tool
import psutil


# Common app paths on Windows
COMMON_APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "microsoft edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
    "powershell": "powershell.exe",
    "task manager": "taskmgr.exe",
    "paint": "mspaint.exe",
    "snipping tool": "SnippingTool.exe",
    "settings": "ms-settings:",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
}


@tool
def open_application(app_name: str) -> str:
    """Open an application by name (e.g., 'Chrome', 'VS Code', 'File Explorer') or by full path."""
    name_lower = app_name.lower().strip()

    # Check if it's a known app
    if name_lower in COMMON_APPS:
        app_path = COMMON_APPS[name_lower]
        try:
            if app_path.startswith("ms-"):
                os.startfile(app_path)
            else:
                subprocess.Popen(app_path, shell=True)
            return f"Opening {app_name}! 🚀"
        except FileNotFoundError:
            return f"Hmm, couldn't find {app_name} at the usual spot. Is it installed?"
        except Exception as e:
            return f"Ran into an issue opening {app_name}: {e}"

    # Try as a direct path
    if Path(app_name).exists():
        try:
            os.startfile(app_name)
            return f"Opening {Path(app_name).name}!"
        except Exception as e:
            return f"Couldn't open that: {e}"

    # Try Windows 'start' command as fallback
    try:
        subprocess.Popen(f"start {app_name}", shell=True)
        return f"Trying to open {app_name}..."
    except Exception:
        return f"I don't know how to open '{app_name}'. Can you give me the full path?"


@tool
def close_application(app_name: str) -> str:
    """Close a running application by name. Tries graceful close first."""
    name_lower = app_name.lower().strip()

    # Map common names to process names
    process_names = {
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "notepad": "notepad.exe",
        "vscode": "Code.exe",
        "vs code": "Code.exe",
        "explorer": "explorer.exe",
        "whatsapp": "WhatsApp.exe",
    }

    target_process = process_names.get(name_lower, f"{name_lower}.exe")

    killed = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == target_process.lower():
                proc.terminate()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed > 0:
        return f"Closed {app_name}. ✅"
    else:
        return f"Doesn't look like {app_name} is running right now."


@tool
def list_running_apps() -> str:
    """List all currently running applications (visible windows)."""
    seen = set()
    apps = []

    for proc in psutil.process_iter(['name', 'memory_info']):
        try:
            name = proc.info['name']
            if name and name not in seen and not name.startswith('svchost'):
                mem = proc.info['memory_info']
                if mem and mem.rss > 10 * 1024 * 1024:  # Only show apps using >10MB RAM
                    mem_mb = mem.rss / (1024 * 1024)
                    apps.append((name, mem_mb))
                    seen.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    apps.sort(key=lambda x: x[1], reverse=True)
    lines = [f"🟢 {name} ({mem:.0f} MB)" for name, mem in apps[:20]]

    return f"Running apps (top 20 by memory):\n" + "\n".join(lines)


@tool
def open_url(url: str) -> str:
    """Open a URL in the default browser."""
    import webbrowser
    try:
        webbrowser.open(url)
        return f"Opened {url} in your browser! 🌐"
    except Exception as e:
        return f"Couldn't open that URL: {e}"


@tool
def open_file_in_default_app(file_path: str) -> str:
    """Open a file with its default application (e.g., PDF in Adobe, .docx in Word)."""
    target = Path(file_path).expanduser()
    if not target.exists():
        return f"File not found: {file_path}"
    try:
        os.startfile(str(target))
        return f"Opened {target.name} with its default app!"
    except Exception as e:
        return f"Couldn't open {target.name}: {e}"


# Export all tools
APP_TOOLS = [open_application, close_application, list_running_apps, open_url, open_file_in_default_app]
