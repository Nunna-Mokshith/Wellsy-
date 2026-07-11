"""
Wellsy Tools -- Overleaf Automation
Open, create, and navigate Overleaf LaTeX projects from the desktop.
"""
import subprocess
import time
import pyautogui
from langchain_core.tools import tool


# Chrome executable path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Overleaf base URLs
OVERLEAF_PROJECTS_URL = "https://www.overleaf.com/project"

# Delay after opening Chrome to let the page fully load (seconds)
PAGE_LOAD_DELAY = 5

# Delay after clicking UI elements (seconds)
CLICK_DELAY = 1.5


def _open_chrome_url(url: str) -> None:
    """Open a URL in Chrome (new tab if Chrome is already running)."""
    subprocess.Popen([CHROME_PATH, url])


@tool
def open_overleaf() -> str:
    """Open the Overleaf projects page in Chrome. Shows all projects for the logged-in user."""
    try:
        _open_chrome_url(OVERLEAF_PROJECTS_URL)
        print("[Overleaf] Opening projects page...")
        time.sleep(PAGE_LOAD_DELAY)
        print("[Overleaf] Projects page opened.")
        return "Opened Overleaf projects page at https://www.overleaf.com/project"
    except FileNotFoundError:
        return "Could not find Chrome. Is Google Chrome installed?"
    except Exception as e:
        return f"Error opening Overleaf: {e}"


@tool
def create_new_project(project_name: str) -> str:
    """Create a new blank project on Overleaf.

    Steps:
      1. Open the Overleaf projects page.
      2. Click the 'New Project' button.
      3. Select 'Blank Project' from the dropdown.
      4. Type the project name in the dialog.
      5. Press Enter to confirm.

    Args:
        project_name: The name for the new Overleaf project.
    """
    try:
        # Step 1: Open Overleaf projects page
        _open_chrome_url(OVERLEAF_PROJECTS_URL)
        print("[Overleaf] Opening projects page...")
        time.sleep(PAGE_LOAD_DELAY)

        # Step 2: Click 'New Project' button (top-left area of the projects page)
        # On a 1920x1080 display, the green 'New Project' button is near (175, 185)
        pyautogui.click(175, 185)
        print("[Overleaf] Clicked 'New Project' button.")
        time.sleep(CLICK_DELAY)

        # Step 3: Select 'Blank Project' from the dropdown
        # 'Blank Project' is the first option, roughly at (175, 225)
        pyautogui.click(175, 225)
        print("[Overleaf] Selected 'Blank Project'.")
        time.sleep(CLICK_DELAY)

        # Step 4: A modal dialog appears asking for the project name.
        # Clear any default text and type the project name.
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.typewrite(project_name, interval=0.03)
        print(f"[Overleaf] Typed project name: {project_name}")
        time.sleep(0.5)

        # Step 5: Press Enter to create the project
        pyautogui.press("enter")
        print("[Overleaf] Pressed Enter to create project.")
        time.sleep(PAGE_LOAD_DELAY)

        print(f"[Overleaf] Project '{project_name}' created successfully.")
        return f"Created new Overleaf project: '{project_name}'"
    except FileNotFoundError:
        return "Could not find Chrome. Is Google Chrome installed?"
    except Exception as e:
        return f"Error creating Overleaf project: {e}"


@tool
def open_project(project_name: str) -> str:
    """Open an existing Overleaf project by name.

    Steps:
      1. Open the Overleaf projects page.
      2. Use Ctrl+F to search for the project name on the page.
      3. Press Escape to close the find bar.
      4. Click on the highlighted project link.

    Args:
        project_name: The name of the project to open.
    """
    try:
        # Step 1: Open projects page
        _open_chrome_url(OVERLEAF_PROJECTS_URL)
        print("[Overleaf] Opening projects page...")
        time.sleep(PAGE_LOAD_DELAY)

        # Step 2: Use browser find (Ctrl+F) to locate the project
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.8)

        # Type the project name in the find bar
        pyautogui.typewrite(project_name, interval=0.03)
        print(f"[Overleaf] Searching for project: {project_name}")
        time.sleep(1.0)

        # Step 3: Press Escape to close the find bar
        pyautogui.press("escape")
        time.sleep(0.5)

        # Step 4: Press Enter on the highlighted result to navigate to it
        # The found text should be highlighted; click on it
        pyautogui.press("enter")
        time.sleep(PAGE_LOAD_DELAY)

        print(f"[Overleaf] Opened project: {project_name}")
        return f"Opened Overleaf project: '{project_name}'"
    except FileNotFoundError:
        return "Could not find Chrome. Is Google Chrome installed?"
    except Exception as e:
        return f"Error opening Overleaf project: {e}"


# ---------------------------------------------------------------------------
# Export all tools
# ---------------------------------------------------------------------------
OVERLEAF_TOOLS = [
    open_overleaf,
    create_new_project,
    open_project,
]
