"""
Wellsy Memory & Whitelist Config
Manages watched folders for the passive file scanner.
"""
import json
from pathlib import Path
from typing import List

# Path constants
BACKEND_DIR = Path(__file__).parent.parent
DB_DIR = BACKEND_DIR / "db"
CONFIG_FILE = DB_DIR / "watch_config.json"
SNAPSHOT_FILE = DB_DIR / "file_snapshot.json"
MEMORY_DB_FILE = DB_DIR / "wellsy_memory.db"

# Ensure db directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

# Default watched folders
DEFAULT_WATCHED_FOLDERS = [
    str(Path("D:/Wellsy")),
    str(Path("D:/Projects")),
    str(Path.home() / "Downloads"),
]


def load_watched_folders() -> List[str]:
    """Load list of whitelisted folders to scan."""
    if not CONFIG_FILE.exists():
        save_watched_folders(DEFAULT_WATCHED_FOLDERS)
        return DEFAULT_WATCHED_FOLDERS
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("watched_folders", DEFAULT_WATCHED_FOLDERS)
    except Exception:
        return DEFAULT_WATCHED_FOLDERS


def save_watched_folders(folders: List[str]) -> bool:
    """Save list of whitelisted folders."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"watched_folders": folders}, f, indent=2)
        return True
    except Exception as e:
        print(f"[!] Error saving watch config: {e}")
        return False


def add_watched_folder(folder_path: str) -> bool:
    """Add a new folder to the watch list."""
    folders = load_watched_folders()
    normalized = str(Path(folder_path).resolve())
    if normalized not in folders:
        folders.append(normalized)
        return save_watched_folders(folders)
    return True


def remove_watched_folder(folder_path: str) -> bool:
    """Remove a folder from the watch list."""
    folders = load_watched_folders()
    normalized = str(Path(folder_path).resolve())
    if normalized in folders:
        folders.remove(normalized)
        return save_watched_folders(folders)
    return True
