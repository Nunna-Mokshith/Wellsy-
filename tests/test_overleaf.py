"""
Test script for Wellsy Overleaf automation tools.
Opens the Overleaf projects page to verify basic functionality.
"""
import sys
import os

# Add project root to path so we can import the tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.tools.overleaf import (
    open_overleaf,
    create_new_project,
    open_project,
    OVERLEAF_TOOLS,
)


def test_tools_registered():
    """Check that all tools are properly registered with @tool decorator."""
    print("=== Test: Tools Registration ===")
    assert len(OVERLEAF_TOOLS) == 3, f"Expected 3 tools, got {len(OVERLEAF_TOOLS)}"
    for t in OVERLEAF_TOOLS:
        assert hasattr(t, 'name'), f"Tool {t} missing 'name' attribute"
        assert hasattr(t, 'description'), f"Tool {t} missing 'description' attribute"
        print(f"  [OK] {t.name}: {t.description[:60]}...")
    print("[PASS] All 3 tools registered correctly.\n")


def test_tool_names():
    """Verify tool names match expected values."""
    print("=== Test: Tool Names ===")
    expected_names = [
        "open_overleaf",
        "create_new_project",
        "open_project",
    ]
    actual_names = [t.name for t in OVERLEAF_TOOLS]
    for name in expected_names:
        assert name in actual_names, f"Missing tool: {name}"
        print(f"  [OK] {name}")
    print("[PASS] All tool names correct.\n")


def test_open_overleaf():
    """Test opening the Overleaf projects page in Chrome."""
    print("=== Test: open_overleaf() ===")
    result = open_overleaf.invoke({})
    print(f"  Result: {result}")
    assert "overleaf" in result.lower() or "opened" in result.lower(), (
        f"Unexpected result: {result}"
    )
    print("[PASS] open_overleaf works.\n")


if __name__ == "__main__":
    print("=" * 50)
    print("  Wellsy Overleaf Tools -- Test Suite")
    print("=" * 50 + "\n")

    test_tools_registered()
    test_tool_names()
    test_open_overleaf()

    print("=" * 50)
    print("  ALL TESTS PASSED")
    print("=" * 50)
