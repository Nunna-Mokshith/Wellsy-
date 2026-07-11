"""
Test script for Wellsy Spotify tools.
Opens Spotify and reads the current window title.
"""
import sys
import os
import time

# Make sure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from tools.spotify import (
    open_spotify,
    get_current_spotify_track,
    spotify_play_pause,
    spotify_next_track,
    spotify_previous_track,
    _find_spotify_window,
)


def test_open_spotify():
    print("=" * 50)
    print("TEST 1: Open Spotify")
    print("=" * 50)
    result = open_spotify.invoke({})
    print(f"Result: {result}")
    assert "Spotify" in result, f"Unexpected result: {result}"
    print("[PASS] open_spotify works.\n")


def test_get_current_track():
    print("=" * 50)
    print("TEST 2: Get current Spotify track")
    print("=" * 50)
    # Give Spotify a moment to fully load
    time.sleep(2)
    result = get_current_spotify_track.invoke({})
    print(f"Result: {result}")
    assert isinstance(result, str) and len(result) > 0, "Empty result"
    print("[PASS] get_current_spotify_track works.\n")


def test_find_window():
    print("=" * 50)
    print("TEST 3: Verify Spotify window is detectable")
    print("=" * 50)
    win = _find_spotify_window()
    if win is not None:
        title = win.window_text()
        print(f"Window title: {title}")
        print("[PASS] Spotify window found.\n")
    else:
        print("[WARN] Spotify window not found (may still be loading).\n")


if __name__ == "__main__":
    print("Wellsy Spotify Tools -- Test Suite")
    print("-" * 50)
    test_open_spotify()
    test_find_window()
    test_get_current_track()
    print("=" * 50)
    print("All tests completed.")
    print("=" * 50)
