"""
Test script for Wellsy YouTube automation tools.
Searches for 'lofi beats' on YouTube and verifies tools work.
"""
import sys
import os

# Add project root to path so we can import the tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.tools.youtube import (
    search_youtube,
    play_first_result,
    pause_resume_video,
    toggle_fullscreen,
    volume_up,
    volume_down,
    mute_unmute_video,
    YOUTUBE_TOOLS,
)


def test_tools_registered():
    """Check that all tools are properly registered with @tool decorator."""
    print("=== Test: Tools Registration ===")
    assert len(YOUTUBE_TOOLS) == 7, f"Expected 7 tools, got {len(YOUTUBE_TOOLS)}"
    for t in YOUTUBE_TOOLS:
        assert hasattr(t, 'name'), f"Tool {t} missing 'name' attribute"
        assert hasattr(t, 'description'), f"Tool {t} missing 'description' attribute"
        print(f"  [OK] {t.name}: {t.description[:60]}...")
    print("[PASS] All 7 tools registered correctly.\n")


def test_search_youtube():
    """Test searching YouTube for 'lofi beats'."""
    print("=== Test: search_youtube('lofi beats') ===")
    result = search_youtube.invoke({"query": "lofi beats"})
    print(f"  Result: {result}")
    assert "lofi beats" in result.lower() or "opened" in result.lower(), f"Unexpected result: {result}"
    print("[PASS] search_youtube works.\n")


def test_tool_names():
    """Verify tool names match expected values."""
    print("=== Test: Tool Names ===")
    expected_names = [
        "search_youtube",
        "play_first_result",
        "pause_resume_video",
        "toggle_fullscreen",
        "volume_up",
        "volume_down",
        "mute_unmute_video",
    ]
    actual_names = [t.name for t in YOUTUBE_TOOLS]
    for name in expected_names:
        assert name in actual_names, f"Missing tool: {name}"
        print(f"  [OK] {name}")
    print("[PASS] All tool names correct.\n")


if __name__ == "__main__":
    print("=" * 50)
    print("  Wellsy YouTube Tools -- Test Suite")
    print("=" * 50 + "\n")

    test_tools_registered()
    test_tool_names()
    test_search_youtube()

    print("=" * 50)
    print("  ALL TESTS PASSED")
    print("=" * 50)
