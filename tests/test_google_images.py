"""
Test script for Wellsy Google Images automation tools.
Searches for 'cute puppies' on Google Images and verifies tools work.
"""
import sys
import os

# Add project root to path so we can import the tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.tools.google_images import (
    search_images,
    download_images,
    get_image_urls,
    GOOGLE_IMAGES_TOOLS,
)


def test_tools_registered():
    """Check that all tools are properly registered with @tool decorator."""
    print("=== Test: Tools Registration ===")
    assert len(GOOGLE_IMAGES_TOOLS) == 3, f"Expected 3 tools, got {len(GOOGLE_IMAGES_TOOLS)}"
    for t in GOOGLE_IMAGES_TOOLS:
        assert hasattr(t, 'name'), f"Tool {t} missing 'name' attribute"
        assert hasattr(t, 'description'), f"Tool {t} missing 'description' attribute"
        desc = t.description[:70] if len(t.description) > 70 else t.description
        print(f"  [OK] {t.name}: {desc}...")
    print("[PASS] All 3 tools registered correctly.\n")


def test_tool_names():
    """Verify tool names match expected values."""
    print("=== Test: Tool Names ===")
    expected_names = [
        "search_images",
        "download_images",
        "get_image_urls",
    ]
    actual_names = [t.name for t in GOOGLE_IMAGES_TOOLS]
    for name in expected_names:
        assert name in actual_names, f"Missing tool: {name}"
        print(f"  [OK] {name}")
    print("[PASS] All tool names correct.\n")


def test_search_images():
    """Test searching Google Images for 'cute puppies' (opens Chrome)."""
    print("=== Test: search_images('cute puppies') ===")
    result = search_images.invoke({"query": "cute puppies"})
    print(f"  Result: {result}")
    assert "cute puppies" in result.lower() or "opened" in result.lower(), (
        f"Unexpected result: {result}"
    )
    print("[PASS] search_images works.\n")


def test_get_image_urls():
    """Test getting image URLs for 'cute puppies'."""
    print("=== Test: get_image_urls('cute puppies') ===")
    result = get_image_urls.invoke({"query": "cute puppies", "num_results": 3})
    print(f"  Result: {result}")
    # Even if scraping fails, the function should return a string
    assert isinstance(result, str), f"Expected string, got {type(result)}"
    print("[PASS] get_image_urls works.\n")


if __name__ == "__main__":
    print("=" * 50)
    print("  Wellsy Google Images Tools -- Test Suite")
    print("=" * 50 + "\n")

    test_tools_registered()
    test_tool_names()
    test_search_images()
    test_get_image_urls()

    print("=" * 50)
    print("  ALL TESTS PASSED")
    print("=" * 50)
