"""
Wellsy Tools -- Spotify Controller
Automate Spotify on Windows: play/pause, skip, volume, search, and get current track.
"""
import subprocess
import time
import pyautogui
from langchain_core.tools import tool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_spotify_window():
    """Return the pywinauto wrapper for the main Spotify window, or None."""
    from pywinauto import Desktop
    desktop = Desktop(backend="uia")
    for win in desktop.windows():
        title = win.window_text()
        if title and "Spotify" in title:
            return win
    return None


def _ensure_spotify_running(wait: int = 5) -> bool:
    """Launch Spotify if it is not already running. Returns True if a window was found."""
    win = _find_spotify_window()
    if win is not None:
        return True
    # Try the Microsoft Store / AppX version first, fall back to direct exe
    try:
        subprocess.Popen("start spotify:", shell=True)
    except Exception:
        try:
            subprocess.Popen(
                r"C:\Users\moksh\AppData\Roaming\Spotify\Spotify.exe"
            )
        except FileNotFoundError:
            return False
    time.sleep(wait)
    return _find_spotify_window() is not None


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def open_spotify() -> str:
    """Open the Spotify desktop application. If it is already running, report that."""
    win = _find_spotify_window()
    if win is not None:
        print("[Spotify] Already running.")
        return "Spotify is already open."
    ok = _ensure_spotify_running(wait=6)
    if ok:
        print("[Spotify] Opened successfully.")
        return "Spotify has been opened."
    return "Could not open Spotify. Make sure it is installed."


@tool
def spotify_play_pause() -> str:
    """Toggle play / pause on Spotify using the media play-pause key."""
    pyautogui.press("playpause")
    print("[Spotify] Toggled play/pause.")
    return "Toggled play/pause."


@tool
def spotify_next_track() -> str:
    """Skip to the next track using the media next-track key."""
    pyautogui.press("nexttrack")
    print("[Spotify] Skipped to next track.")
    return "Skipped to the next track."


@tool
def spotify_previous_track() -> str:
    """Go back to the previous track using the media previous-track key."""
    pyautogui.press("prevtrack")
    print("[Spotify] Went to previous track.")
    return "Went back to the previous track."


@tool
def spotify_volume_up(steps: int = 5) -> str:
    """Increase the system volume. Each step is one press of the volume-up key.

    Args:
        steps: Number of volume-up key presses (default 5).
    """
    for _ in range(steps):
        pyautogui.press("volumeup")
    print(f"[Spotify] Volume up x{steps}.")
    return f"Volume increased by {steps} steps."


@tool
def spotify_volume_down(steps: int = 5) -> str:
    """Decrease the system volume. Each step is one press of the volume-down key.

    Args:
        steps: Number of volume-down key presses (default 5).
    """
    for _ in range(steps):
        pyautogui.press("volumedown")
    print(f"[Spotify] Volume down x{steps}.")
    return f"Volume decreased by {steps} steps."


@tool
def spotify_search_and_play(query: str) -> str:
    """Search for a song/artist/album on Spotify and play the first result.

    Steps:
      1. Make sure Spotify is open.
      2. Press Ctrl+L to focus the search bar.
      3. Type the query.
      4. Press Enter to search.
      5. Wait a moment, then press Enter again to play the top result.

    Args:
        query: The song name, artist, or album to search for.
    """
    ok = _ensure_spotify_running(wait=6)
    if not ok:
        return "Could not open Spotify. Is it installed?"

    # Bring Spotify to the foreground
    win = _find_spotify_window()
    if win is not None:
        try:
            win.set_focus()
        except Exception:
            pass
    time.sleep(0.5)

    # Focus the search bar (Ctrl+L works in Spotify desktop)
    pyautogui.hotkey("ctrl", "l")
    time.sleep(0.5)

    # Clear any existing text and type the query
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.typewrite(query, interval=0.03)
    time.sleep(0.8)

    # Press Enter to search
    pyautogui.press("enter")
    time.sleep(1.5)

    # Press Enter again to play the first result
    pyautogui.press("enter")
    time.sleep(0.5)

    print(f"[Spotify] Searched and playing: {query}")
    return f"Searched for '{query}' and started playing the top result."


@tool
def get_current_spotify_track() -> str:
    """Get the currently playing track by reading the Spotify window title.

    The Spotify desktop app sets its window title to 'Artist - Song' when music
    is playing, or just 'Spotify' / 'Spotify Premium' when paused/idle.
    """
    win = _find_spotify_window()
    if win is None:
        return "Spotify does not appear to be running."

    title = win.window_text()
    if not title:
        return "Could not read the Spotify window title."

    # When nothing is playing the title is just "Spotify" or "Spotify Premium"
    if title.strip().lower() in ("spotify", "spotify premium", "spotify free"):
        return "Spotify is open but nothing is currently playing (or playback is paused)."

    print(f"[Spotify] Current track window title: {title}")
    return f"Currently playing: {title}"


# ---------------------------------------------------------------------------
# Export all tools
# ---------------------------------------------------------------------------
SPOTIFY_TOOLS = [
    open_spotify,
    spotify_play_pause,
    spotify_next_track,
    spotify_previous_track,
    spotify_volume_up,
    spotify_volume_down,
    spotify_search_and_play,
    get_current_spotify_track,
]
