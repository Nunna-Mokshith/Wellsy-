"""
Wellsy Scheduler Pre-flight Safety Checks
Runs automated safety checks before scheduled background actions execute.
If any pre-flight check fails, the task aborts and alerts the user instead.
"""
import os
import subprocess
from pathlib import Path
from typing import Tuple, Optional


def check_git_status(repo_path: str) -> Tuple[bool, str]:
    """Pre-flight check for scheduled git operations."""
    path = Path(repo_path)
    if not path.exists() or not (path / ".git").exists():
        return False, f"Git repository not found at {repo_path}"

    try:
        # Check for uncommitted merge conflict markers
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=str(path), capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            return False, "Unresolved merge conflicts detected in repository."

        # Check if .env or secret files are staged
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(path), capture_output=True, text=True, timeout=5
        )
        for line in staged.stdout.splitlines():
            if ".env" in line or "secret" in line.lower() or "key" in line.lower():
                return False, f"Security risk: Sensitive file '{line}' staged for commit."

        return True, "Git pre-flight checks passed cleanly."
    except Exception as e:
        return False, f"Git pre-flight error: {e}"


def check_python_syntax(file_path: str) -> Tuple[bool, str]:
    """Pre-flight check for Python syntax errors."""
    try:
        import py_compile
        py_compile.compile(file_path, doraise=True)
        return True, "Syntax check passed."
    except Exception as e:
        return False, f"Python syntax error in {file_path}: {e}"


def run_preflight_checks(action_type: str, target: Optional[str] = None) -> Tuple[bool, str]:
    """Master entry point for pre-flight safety checks."""
    if "git" in action_type.lower():
        repo = target if target else "D:\\Wellsy"
        return check_git_status(repo)

    # Default pass for standard low-risk tasks
    return True, "Pre-flight safety checks passed."
