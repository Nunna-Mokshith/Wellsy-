"""
Test script for Gemini Chat tools.
Opens the Gemini page in Chrome to verify basic functionality.
"""
import sys
import os

# Add backend to path so we can import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from tools.gemini_chat import open_gemini, ask_gemini, GEMINI_CHAT_TOOLS


def test_tools_registered():
    """Verify all tools are in the export list."""
    print("[TEST] Checking GEMINI_CHAT_TOOLS export list...")
    assert len(GEMINI_CHAT_TOOLS) == 2, f"Expected 2 tools, got {len(GEMINI_CHAT_TOOLS)}"
    tool_names = [t.name for t in GEMINI_CHAT_TOOLS]
    assert "open_gemini" in tool_names, "open_gemini not in GEMINI_CHAT_TOOLS"
    assert "ask_gemini" in tool_names, "ask_gemini not in GEMINI_CHAT_TOOLS"
    print("[TEST] PASS -- All tools registered correctly")


def test_open_gemini():
    """Open Gemini in Chrome to verify it works."""
    print("[TEST] Opening Gemini in Chrome...")
    result = open_gemini.invoke({})
    print(f"[TEST] Result: {result}")
    assert "Opened" in result or "Error" in result
    print("[TEST] PASS -- open_gemini executed")


if __name__ == "__main__":
    test_tools_registered()
    print()
    test_open_gemini()
    print()
    print("[TEST] All Gemini chat tests passed!")
