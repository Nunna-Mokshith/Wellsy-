"""
1. Find Spotify, play Perfect on repeat
2. Generate voice demos for Wellsy and play them
"""
import time
import subprocess
import pyautogui
import pywinauto
import os

def play_spotify_on_repeat():
    print("=" * 50)
    print("  Step 1: Spotify - Perfect on Repeat")
    print("=" * 50)
    
    # Find any Spotify window
    desktop = pywinauto.Desktop(backend="uia")
    all_wins = desktop.windows()
    spotify_win = None
    for w in all_wins:
        try:
            title = w.window_text()
            if 'spotify' in title.lower() or 'Spotify' in title:
                print(f"  Found window: '{title}'")
                spotify_win = w
                break
        except:
            pass
    
    if not spotify_win:
        print("  Spotify not found by title, opening it...")
        subprocess.Popen(["explorer", "spotify:"])
        time.sleep(5)
        # Try again
        all_wins = desktop.windows()
        for w in all_wins:
            try:
                title = w.window_text()
                if 'spotify' in title.lower():
                    spotify_win = w
                    print(f"  Found: '{title}'")
                    break
            except:
                pass
    
    if spotify_win:
        spotify_win.set_focus()
        time.sleep(1)
        print("  [OK] Spotify focused")
    else:
        print("  [!] Could not find Spotify window, trying anyway...")
    
    # Open Perfect by Ed Sheeran directly
    print("  Opening track...")
    subprocess.Popen(["explorer", "spotify:track:0tgVpDi06FyKpA1z0VMD4v"])
    time.sleep(4)
    
    # Re-focus Spotify
    try:
        all_wins = desktop.windows()
        for w in all_wins:
            try:
                title = w.window_text()
                if 'spotify' in title.lower() or 'perfect' in title.lower() or 'ed sheeran' in title.lower():
                    w.set_focus()
                    print(f"  Re-focused: '{title}'")
                    break
            except:
                pass
    except:
        pass
    
    time.sleep(1)
    
    # Press Space to play
    print("  Pressing Space to play...")
    pyautogui.press('space')
    time.sleep(2)
    
    # Enable repeat - Ctrl+R toggles repeat in Spotify
    print("  Enabling repeat (Ctrl+R)...")
    pyautogui.hotkey('ctrl', 'r')
    time.sleep(0.5)
    # Press again to set to "repeat one" (single track loop)
    pyautogui.hotkey('ctrl', 'r')
    time.sleep(0.5)
    
    print("  [OK] Perfect should be playing on loop!")

if __name__ == "__main__":
    play_spotify_on_repeat()
