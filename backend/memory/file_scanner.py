"""
Wellsy Passive File Scanner
Monitors whitelisted folders for file metadata changes between sessions.
Never reads file contents — only tracks name, size, and modified timestamps.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

from memory.config import load_watched_folders, SNAPSHOT_FILE
from memory.memory_db import memory_db

# Folders / files to ignore during scan
IGNORE_DIRS = {
    "venv", ".git", "__pycache__", "node_modules", ".vscode", ".idea",
    "voice_cache", "downloads", "models", "storage", "dist", "build"
}
IGNORE_EXTENSIONS = {".pyc", ".pyo", ".log", ".tmp", ".bak", ".db"}


class FileScanner:
    def __init__(self):
        self.watched_folders = load_watched_folders()

    def _should_ignore(self, path: Path) -> bool:
        """Check if path or parent should be ignored."""
        parts = set(path.parts)
        if parts.intersection(IGNORE_DIRS):
            return True
        if path.suffix in IGNORE_EXTENSIONS:
            return True
        return False

    def scan_current_state(self) -> Dict[str, Dict[str, Any]]:
        """Scan all whitelisted folders and build a state dictionary."""
        current_state = {}
        folders = load_watched_folders()

        for folder_str in folders:
            folder = Path(folder_str)
            if not folder.exists() or not folder.is_dir():
                continue

            try:
                for root, dirs, files in os.walk(folder):
                    # Filter out ignored directories in-place
                    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

                    for f in files:
                        file_path = Path(root) / f
                        if self._should_ignore(file_path):
                            continue

                        try:
                            stat = file_path.stat()
                            current_state[str(file_path)] = {
                                "name": f,
                                "size": stat.st_size,
                                "mtime": stat.st_mtime,
                                "folder": str(folder)
                            }
                        except Exception:
                            continue
            except Exception as e:
                print(f"[!] FileScanner error scanning {folder}: {e}")

        return current_state

    def load_last_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Load the snapshot from the previous session."""
        if not SNAPSHOT_FILE.exists():
            return {}
        try:
            with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_snapshot(self, state: Dict[str, Dict[str, Any]]) -> bool:
        """Save the current state as the snapshot for next session."""
        try:
            with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            print(f"[!] Error saving file snapshot: {e}")
            return False

    def detect_changes(self) -> Tuple[List[str], List[str], List[str]]:
        """Compare current state with last snapshot to find new, modified, deleted files."""
        last_state = self.load_last_snapshot()
        current_state = self.scan_current_state()

        new_files = []
        modified_files = []
        deleted_files = []

        # Find new and modified
        for path, info in current_state.items():
            if path not in last_state:
                new_files.append(info["name"])
            else:
                last_info = last_state[path]
                if abs(info["mtime"] - last_info.get("mtime", 0)) > 2.0 or info["size"] != last_info.get("size", 0):
                    modified_files.append(info["name"])

        # Find deleted
        for path, info in last_state.items():
            if path not in current_state:
                deleted_files.append(info["name"])

        # Save new snapshot
        self.save_snapshot(current_state)

        # Log change event to memory DB if any changes detected
        if new_files or modified_files or deleted_files:
            content = f"File Scanner session update: {len(new_files)} new, {len(modified_files)} modified, {len(deleted_files)} deleted."
            memory_db.store_memory("FILE_EVENT", content, {
                "new": new_files[:10],
                "modified": modified_files[:10],
                "deleted": deleted_files[:10]
            })

        return new_files, modified_files, deleted_files

    def generate_greeting_summary(self) -> str:
        """Generate a natural language greeting summary of changes since last session."""
        new_files, modified_files, deleted_files = self.detect_changes()

        if not new_files and not modified_files and not deleted_files:
            return ""

        parts = []
        if new_files:
            sample = ", ".join(new_files[:3])
            more = f" and {len(new_files) - 3} others" if len(new_files) > 3 else ""
            parts.append(f"{len(new_files)} new file(s) ({sample}{more})")

        if modified_files:
            sample = ", ".join(modified_files[:3])
            more = f" and {len(modified_files) - 3} others" if len(modified_files) > 3 else ""
            parts.append(f"{len(modified_files)} modified file(s) ({sample}{more})")

        if deleted_files:
            parts.append(f"{len(deleted_files)} removed file(s)")

        summary = "I noticed some activity since last session: " + ", ".join(parts) + ". Want to fill me in on what's new?"
        return summary


file_scanner = FileScanner()
