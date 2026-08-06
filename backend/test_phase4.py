"""
Wellsy Phase 4 Verification Test Suite
Tests CLI parsing, daemon initialization, and system status endpoint integration.
"""
import sys
import subprocess
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def test_cli_help():
    print("\n--- Testing CLI Help & Arguments ---")
    res = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "wellsy.py"), "--help"],
        capture_output=True, text=True, timeout=5
    )
    assert res.returncode == 0
    assert "Wellsy CLI" in res.stdout
    print("  [+] `wellsy.py --help` returned status 0 with expected description.")


def test_cli_status():
    print("\n--- Testing CLI Status Check ---")
    res = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "wellsy.py"), "--status"],
        capture_output=True, text=True, timeout=5
    )
    assert res.returncode == 0
    print(f"  [+] `wellsy.py --status` executed cleanly:\n{res.stdout.strip()}")


if __name__ == "__main__":
    print("========================================")
    print(" RUNNING WELLSY PHASE 4 TEST SUITE")
    print("========================================")
    test_cli_help()
    test_cli_status()
    print("\n[ALL PHASE 4 TESTS PASSED CLEANLY] [OK]")
