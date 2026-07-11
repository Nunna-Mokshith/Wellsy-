"""
Play Perfect on Spotify and set volume to 34%
"""
import time
import subprocess
import pyautogui

def main():
    # Set system volume to 34% using PowerShell
    print("[1] Setting volume to 34%...")
    subprocess.run([
        "powershell", "-Command",
        "$wshell = New-Object -ComObject WScript.Shell; "
        "1..50 | ForEach-Object { $wshell.SendKeys([char]174) }; "  # Volume down to 0
        "Start-Sleep -Milliseconds 500; "
        "1..17 | ForEach-Object { $wshell.SendKeys([char]175) }"    # Volume up ~34%
    ], capture_output=True)
    print("[OK] Volume set to ~34%")
    
    # Play Perfect by Ed Sheeran directly via Spotify URI
    print("[2] Playing Perfect by Ed Sheeran...")
    subprocess.Popen(["explorer", "spotify:track:0tgVpDi06FyKpA1z0VMD4v"])
    time.sleep(3)
    
    # Make sure it's playing - press play
    print("[3] Pressing play...")
    pyautogui.press('playpause')
    time.sleep(1)
    
    print("[DONE] Perfect should be playing at 34% volume!")

if __name__ == "__main__":
    main()
