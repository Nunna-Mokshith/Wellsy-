"""
Wellsy Test: Play Perfect from Liked Songs on Spotify
"""
import sys
import time
sys.path.insert(0, r"D:\Wellsy\backend")

import pyautogui
import subprocess

def main():
    print("=" * 50)
    print("  Playing Perfect from Liked Songs on Spotify")
    print("=" * 50)
    
    # Step 1: Open Spotify
    print("\n[1] Opening Spotify...")
    subprocess.Popen(["explorer", "spotify:"])
    time.sleep(5)
    
    # Step 2: Focus Spotify window
    import pywinauto
    try:
        desktop = pywinauto.Desktop(backend="uia")
        wins = desktop.windows(title_re=".*Spotify.*")
        if wins:
            main_win = max(wins, key=lambda w: (w.rectangle().right - w.rectangle().left) * (w.rectangle().bottom - w.rectangle().top))
            main_win.set_focus()
            print("[OK] Spotify focused")
        time.sleep(1)
    except Exception as e:
        print(f"[!] Focus issue: {e}")
    
    # Step 3: Go to Liked Songs (Spotify shortcut or navigate)
    # Open Liked Songs via URI
    print("\n[2] Opening Liked Songs...")
    subprocess.Popen(["explorer", "spotify:collection:tracks"])
    time.sleep(4)
    
    # Step 4: Search within Liked Songs for "Perfect"
    print("\n[3] Searching for 'Perfect' in Liked Songs...")
    # Use Ctrl+Shift+F for filter in liked songs, or Ctrl+F
    pyautogui.hotkey('ctrl', 'shift', 'f')
    time.sleep(1)
    pyautogui.typewrite('Perfect', interval=0.1)
    time.sleep(2)
    
    # Step 5: Press Enter to play the first result
    print("\n[4] Playing the song...")
    pyautogui.press('enter')
    time.sleep(2)
    
    print("\n[DONE] Perfect should be playing from Liked Songs!")

if __name__ == "__main__":
    main()
