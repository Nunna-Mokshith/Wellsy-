"""
Test WhatsApp tool -- SAFE: only opens WhatsApp and prints window info.
Does NOT send any messages or files.
"""
import sys
import os

# Add backend to path so we can import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from tools.whatsapp import _launch_and_focus, _find_whatsapp_window


def main():
    print("=" * 50)
    print("WhatsApp Tool - Safe Open Test")
    print("=" * 50)

    print("\n[1] Launching WhatsApp Desktop...")
    win, msg = _launch_and_focus()
    print(f"    Result: {msg}")

    if win is None:
        print("[FAIL] Could not find WhatsApp window.")
        print("       Make sure WhatsApp Desktop is installed.")
        return

    title = win.window_text()
    print(f"[OK] Window title: {title}")

    rect = win.rectangle()
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    print(f"[OK] Window size: {width} x {height}")

    # Try finding it again to confirm helper works independently
    print("\n[2] Re-finding WhatsApp window with helper...")
    win2 = _find_whatsapp_window()
    if win2:
        print(f"[OK] Re-found window: {win2.window_text()}")
    else:
        print("[WARN] Could not re-find window.")

    print("\n" + "=" * 50)
    print("[DONE] WhatsApp tool basic test passed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
