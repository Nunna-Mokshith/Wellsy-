"""
Wellsy Tools — File Operations
Browse, search, read, create, move, and delete files.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from langchain_core.tools import tool


@tool
def list_directory(path: str) -> str:
    """List all files and folders in a directory. Shows names, sizes, and types."""
    target = Path(path).expanduser()
    if not target.exists():
        return f"Hmm, that path doesn't exist: {path}"
    if not target.is_dir():
        return f"That's a file, not a folder! Try read_file instead."

    items = []
    try:
        for item in sorted(target.iterdir()):
            if item.name.startswith('.'):
                continue
            if item.is_dir():
                count = sum(1 for _ in item.iterdir()) if item.exists() else 0
                items.append(f"📁 {item.name}/ ({count} items)")
            else:
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                elif size < 1024 * 1024 * 1024:
                    size_str = f"{size / (1024*1024):.1f} MB"
                else:
                    size_str = f"{size / (1024*1024*1024):.1f} GB"
                items.append(f"📄 {item.name} ({size_str})")
    except PermissionError:
        return f"I don't have permission to access {path}."

    if not items:
        return f"The folder {target.name} is empty."

    header = f"Contents of {target.name}/ ({len(items)} items):\n"
    return header + "\n".join(items)


@tool
def read_file(path: str) -> str:
    """Read the text contents of a file."""
    target = Path(path).expanduser()
    if not target.exists():
        return f"Can't find that file: {path}"
    if not target.is_file():
        return f"That's a folder, not a file. Try list_directory instead."

    try:
        text = target.read_text(encoding="utf-8", errors="replace")
        if len(text) > 5000:
            return f"File: {target.name} (showing first 5000 chars):\n\n{text[:5000]}\n\n... (truncated, {len(text)} total chars)"
        return f"File: {target.name}:\n\n{text}"
    except Exception as e:
        return f"Couldn't read that file: {e}"


@tool
def search_files(directory: str, pattern: str) -> str:
    """Search for files matching a pattern (e.g., '*.pdf', '*.py') in a directory and subdirectories."""
    target = Path(directory).expanduser()
    if not target.exists():
        return f"Directory not found: {directory}"

    matches = list(target.rglob(pattern))
    if not matches:
        return f"No files matching '{pattern}' found in {target.name}/."

    results = []
    for m in matches[:30]:  # Cap at 30 results
        size = m.stat().st_size
        if size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024*1024):.1f} MB"
        modified = datetime.fromtimestamp(m.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        results.append(f"📄 {m.relative_to(target)} ({size_str}, modified {modified})")

    header = f"Found {len(matches)} files matching '{pattern}':\n"
    if len(matches) > 30:
        header += f"(showing first 30)\n"
    return header + "\n".join(results)


@tool
def create_file(path: str, content: str) -> str:
    """Create a new file with the given content. Creates parent directories if needed."""
    target = Path(path).expanduser()
    if target.exists():
        return f"File already exists: {path}. I don't want to overwrite it without you confirming."

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Created {target.name} ✨"
    except Exception as e:
        return f"Couldn't create the file: {e}"


@tool
def move_file(source: str, destination: str) -> str:
    """Move or rename a file from source to destination."""
    src = Path(source).expanduser()
    dst = Path(destination).expanduser()

    if not src.exists():
        return f"Source not found: {source}"

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return f"Moved {src.name} → {dst.name} ✅"
    except Exception as e:
        return f"Couldn't move the file: {e}"


@tool
def delete_file(path: str) -> str:
    """Delete a file. WARNING: This is permanent! Only use when explicitly asked."""
    target = Path(path).expanduser()
    if not target.exists():
        return f"File not found: {path}"

    try:
        if target.is_dir():
            shutil.rmtree(target)
            return f"Deleted folder {target.name} and all its contents."
        else:
            target.unlink()
            return f"Deleted {target.name}."
    except Exception as e:
        return f"Couldn't delete: {e}"


@tool
def get_file_info(path: str) -> str:
    """Get detailed info about a file (size, type, modified date)."""
    target = Path(path).expanduser()
    if not target.exists():
        return f"Not found: {path}"

    stat = target.stat()
    size = stat.st_size
    if size < 1024:
        size_str = f"{size} bytes"
    elif size < 1024 * 1024:
        size_str = f"{size / 1024:.1f} KB"
    else:
        size_str = f"{size / (1024*1024):.1f} MB"

    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"{'📁 Folder' if target.is_dir() else '📄 File'}: {target.name}\n"
        f"Path: {target.absolute()}\n"
        f"Size: {size_str}\n"
        f"Modified: {modified}\n"
        f"Created: {created}\n"
        f"Extension: {target.suffix or 'none'}"
    )


# Export all tools
FILE_TOOLS = [list_directory, read_file, search_files, create_file, move_file, delete_file, get_file_info]
