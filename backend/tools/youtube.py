"""
Wellsy Tools -- YouTube Automation
Search, play, and control YouTube videos from the desktop.
"""
import subprocess
import time
import pyautogui
from urllib.parse import quote_plus
from langchain_core.tools import tool


# Chrome executable path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Delay after opening Chrome to let the page load (seconds)
PAGE_LOAD_DELAY = 4

# Coordinates for the first video thumbnail on YouTube search results.
# These are approximate and assume a 1920x1080 display at 100% scaling.
# The first result thumbnail is typically around (400, 390) on a fresh search page.
FIRST_RESULT_X = 400
FIRST_RESULT_Y = 390


def _open_chrome_url(url: str) -> None:
    """Open a URL in Chrome (new tab if Chrome is already running)."""
    subprocess.Popen([CHROME_PATH, url])


def _focus_video_area() -> None:
    """Click on the video player area so keyboard shortcuts work."""
    # Click roughly the center of the video player on a YouTube watch page
    # at 1920x1080 resolution. The player center is around (960, 430).
    pyautogui.click(960, 430)
    time.sleep(0.3)


@tool
def search_youtube(query: str) -> str:
    """Search YouTube for a given query. Opens Chrome with YouTube search results for the specified keywords."""
    encoded = quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    try:
        _open_chrome_url(url)
        print(f"[YouTube] Searching for: {query}")
        return f"Opened YouTube search results for '{query}'."
    except FileNotFoundError:
        return "Could not find Chrome. Is Google Chrome installed?"
    except Exception as e:
        return f"Error searching YouTube: {e}"


@tool
def play_first_result() -> str:
    """Click the first video result on a YouTube search results page. Call search_youtube first."""
    try:
        # Give the page time to load if it was just opened
        time.sleep(PAGE_LOAD_DELAY)
        # Click on the first video thumbnail
        pyautogui.click(FIRST_RESULT_X, FIRST_RESULT_Y)
        print("[YouTube] Clicking first video result")
        time.sleep(2)
        return "Clicked the first video result. The video should now be playing."
    except Exception as e:
        return f"Error clicking first result: {e}"


@tool
def pause_resume_video() -> str:
    """Pause or resume the currently playing YouTube video by pressing the K key."""
    try:
        _focus_video_area()
        pyautogui.press('k')
        print("[YouTube] Toggled pause/resume (K key)")
        return "Toggled pause/resume on the YouTube video."
    except Exception as e:
        return f"Error toggling pause/resume: {e}"


@tool
def toggle_fullscreen() -> str:
    """Toggle fullscreen mode on the currently playing YouTube video by pressing the F key."""
    try:
        _focus_video_area()
        pyautogui.press('f')
        print("[YouTube] Toggled fullscreen (F key)")
        return "Toggled fullscreen on the YouTube video."
    except Exception as e:
        return f"Error toggling fullscreen: {e}"


@tool
def volume_up(steps: int = 5) -> str:
    """Increase YouTube video volume. Each step is one Up-arrow press (increases ~5% per step). Default is 5 steps (+25%)."""
    try:
        _focus_video_area()
        for _ in range(steps):
            pyautogui.press('up')
            time.sleep(0.05)
        print(f"[YouTube] Volume up by {steps} steps")
        return f"Increased YouTube volume by {steps} steps (~{steps * 5}%)."
    except Exception as e:
        return f"Error increasing volume: {e}"


@tool
def volume_down(steps: int = 5) -> str:
    """Decrease YouTube video volume. Each step is one Down-arrow press (decreases ~5% per step). Default is 5 steps (-25%)."""
    try:
        _focus_video_area()
        for _ in range(steps):
            pyautogui.press('down')
            time.sleep(0.05)
        print(f"[YouTube] Volume down by {steps} steps")
        return f"Decreased YouTube volume by {steps} steps (~{steps * 5}%)."
    except Exception as e:
        return f"Error decreasing volume: {e}"


@tool
def mute_unmute_video() -> str:
    """Mute or unmute the currently playing YouTube video by pressing the M key."""
    try:
        _focus_video_area()
        pyautogui.press('m')
        print("[YouTube] Toggled mute/unmute (M key)")
        return "Toggled mute/unmute on the YouTube video."
    except Exception as e:
        return f"Error toggling mute: {e}"


# Export all tools
YOUTUBE_TOOLS = [
    search_youtube,
    play_first_result,
    pause_resume_video,
    toggle_fullscreen,
    volume_up,
    volume_down,
    mute_unmute_video,
]
