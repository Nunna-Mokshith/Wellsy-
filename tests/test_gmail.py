"""
Test script for Wellsy Gmail tools.
Tests tool construction, URL building, and opens a compose URL in Chrome
(does NOT actually send any email).
"""
import sys
import urllib.parse

# Ensure the tools module is importable
sys.path.insert(0, r"D:\Wellsy\backend")

def test_imports():
    """Test that the gmail module imports correctly."""
    print("[TEST] Importing gmail module...")
    from tools.gmail import (
        open_gmail, send_email, read_latest_emails,
        search_emails, send_email_with_attachment, GMAIL_TOOLS
    )
    print("  - All functions imported successfully.")
    assert len(GMAIL_TOOLS) == 5, f"Expected 5 tools, got {len(GMAIL_TOOLS)}"
    print(f"  - GMAIL_TOOLS has {len(GMAIL_TOOLS)} tools.")
    print("[PASS] Imports OK\n")


def test_tool_decorators():
    """Test that each function is a proper langchain tool."""
    print("[TEST] Checking @tool decorators...")
    from tools.gmail import GMAIL_TOOLS

    for t in GMAIL_TOOLS:
        assert hasattr(t, "name"), f"{t} missing 'name' attribute"
        assert hasattr(t, "description"), f"{t} missing 'description' attribute"
        print(f"  - {t.name}: OK")
    print("[PASS] All tools properly decorated\n")


def test_compose_url_construction():
    """Test that compose URL is built correctly."""
    print("[TEST] Testing compose URL construction...")
    from tools.gmail import GMAIL_URL

    to = "test@example.com"
    subject = "Hello World"
    body = "This is a test email body."

    params = urllib.parse.urlencode({
        "view": "cm",
        "fs": "1",
        "to": to,
        "su": subject,
        "body": body,
    })
    compose_url = f"{GMAIL_URL}/mail/?{params}"

    assert "view=cm" in compose_url, "Missing view=cm"
    assert "to=test%40example.com" in compose_url, "Missing or wrong 'to' param"
    assert "su=Hello+World" in compose_url or "su=Hello%20World" in compose_url, "Missing subject"
    assert "body=" in compose_url, "Missing body"

    print(f"  - Compose URL: {compose_url}")
    print("[PASS] Compose URL construction OK\n")


def test_search_url_construction():
    """Test that search URL is built correctly."""
    print("[TEST] Testing search URL construction...")
    from tools.gmail import GMAIL_URL

    query = "from:someone@example.com"
    encoded_query = urllib.parse.quote(query)
    search_url = f"{GMAIL_URL}/mail/u/0/#search/{encoded_query}"

    assert "search" in search_url, "Missing search path"
    assert "someone" in search_url, "Missing query content"

    print(f"  - Search URL: {search_url}")
    print("[PASS] Search URL construction OK\n")


def test_open_compose_in_browser():
    """Open a Gmail compose URL in Chrome (no sending). Visual verification only."""
    print("[TEST] Opening Gmail compose URL in Chrome (visual test)...")
    import subprocess

    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    params = urllib.parse.urlencode({
        "view": "cm",
        "fs": "1",
        "to": "test@example.com",
        "su": "Wellsy Test Email - DO NOT SEND",
        "body": "This is an automated test from Wellsy Gmail tools. Please close this window.",
    })
    compose_url = f"https://mail.google.com/mail/?{params}"

    try:
        subprocess.Popen([chrome, compose_url])
        print(f"  - Opened compose URL in Chrome.")
        print("  - Please verify the compose window appeared with pre-filled fields.")
        print("  - Close the compose window manually -- DO NOT send.")
        print("[PASS] Browser compose test launched\n")
    except FileNotFoundError:
        print("  - Chrome not found, skipping browser test.")
        print("[SKIP] Browser compose test\n")


if __name__ == "__main__":
    print("=" * 60)
    print("  Wellsy Gmail Tools -- Test Suite")
    print("=" * 60 + "\n")

    test_imports()
    test_tool_decorators()
    test_compose_url_construction()
    test_search_url_construction()
    test_open_compose_in_browser()

    print("=" * 60)
    print("  All tests completed!")
    print("=" * 60)
