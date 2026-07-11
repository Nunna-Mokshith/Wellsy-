"""
Test script for Wellsy Outlook tools.
Tests imports, tool decorators, and opens Outlook in Chrome (no email sent).
"""
import sys

# Ensure the tools module is importable
sys.path.insert(0, r"D:\Wellsy\backend")


def test_imports():
    """Test that the outlook module imports correctly."""
    print("[TEST] Importing outlook module...")
    from tools.outlook import (
        open_outlook, send_outlook_email, read_outlook_inbox, OUTLOOK_TOOLS
    )
    print("  - All functions imported successfully.")
    assert len(OUTLOOK_TOOLS) == 3, f"Expected 3 tools, got {len(OUTLOOK_TOOLS)}"
    print(f"  - OUTLOOK_TOOLS has {len(OUTLOOK_TOOLS)} tools.")
    print("[PASS] Imports OK\n")


def test_tool_decorators():
    """Test that each function is a proper langchain tool."""
    print("[TEST] Checking @tool decorators...")
    from tools.outlook import OUTLOOK_TOOLS

    for t in OUTLOOK_TOOLS:
        assert hasattr(t, "name"), f"{t} missing 'name' attribute"
        assert hasattr(t, "description"), f"{t} missing 'description' attribute"
        print(f"  - {t.name}: OK")
    print("[PASS] All tools properly decorated\n")


def test_tool_schemas():
    """Test that tool argument schemas are correctly defined."""
    print("[TEST] Checking tool argument schemas...")
    from tools.outlook import send_outlook_email

    schema = send_outlook_email.args_schema.schema()
    props = schema.get("properties", {})
    assert "to" in props, "send_outlook_email missing 'to' arg"
    assert "subject" in props, "send_outlook_email missing 'subject' arg"
    assert "body" in props, "send_outlook_email missing 'body' arg"
    print("  - send_outlook_email schema: to, subject, body -- OK")
    print("[PASS] Tool schemas OK\n")


def test_open_outlook_in_browser():
    """Open Outlook in Chrome (visual verification only, no email sent)."""
    print("[TEST] Opening Outlook in Chrome (visual test)...")
    import subprocess

    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    url = "https://outlook.live.com/mail/"

    try:
        subprocess.Popen([chrome, url])
        print("  - Opened Outlook in Chrome.")
        print("  - Please verify the Outlook inbox appeared in the browser.")
        print("[PASS] Browser test launched\n")
    except FileNotFoundError:
        print("  - Chrome not found, skipping browser test.")
        print("[SKIP] Browser test\n")


if __name__ == "__main__":
    print("=" * 60)
    print("  Wellsy Outlook Tools -- Test Suite")
    print("=" * 60 + "\n")

    test_imports()
    test_tool_decorators()
    test_tool_schemas()
    test_open_outlook_in_browser()

    print("=" * 60)
    print("  All tests completed!")
    print("=" * 60)
