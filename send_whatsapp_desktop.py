"""
Send Attendance PDF to Teddy via WhatsApp Desktop App
No browser, no QR scan needed!
"""
import time
import subprocess
import pyautogui
import os

PDF_PATH = r"D:\Wellsy\downloads\Attendance_Report.pdf"

def main():
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at {PDF_PATH}")
        return
    
    print(f"[OK] PDF found: {PDF_PATH}")
    
    # Step 1: Open WhatsApp Desktop
    print("[1] Opening WhatsApp...")
    subprocess.Popen(["explorer", "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"])
    time.sleep(6)
    
    # Bring WhatsApp to front
    import pywinauto
    try:
        # Handle multiple WhatsApp windows - find the main one
        desktop = pywinauto.Desktop(backend="uia")
        whatsapp_windows = desktop.windows(title_re=".*WhatsApp.*")
        print(f"[OK] Found {len(whatsapp_windows)} WhatsApp window(s)")
        
        # Pick the largest / main window
        main_win = None
        max_area = 0
        for win in whatsapp_windows:
            try:
                rect = win.rectangle()
                area = (rect.right - rect.left) * (rect.bottom - rect.top)
                if area > max_area:
                    max_area = area
                    main_win = win
            except:
                pass
        
        if main_win:
            main_win.set_focus()
            print("[OK] WhatsApp main window focused")
        else:
            print("[!] Could not find main window, continuing anyway...")
    except Exception as e:
        print(f"[!] pywinauto issue: {e}")
        print("    Continuing anyway...")
    
    time.sleep(2)
    
    # Step 2: Search for Teddy
    print("[2] Searching for 'Teddy'...")
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.typewrite('Teddy', interval=0.15)
    time.sleep(3)
    
    # Step 3: Select Teddy's chat
    print("[3] Selecting Teddy's chat...")
    pyautogui.press('enter')
    time.sleep(3)
    
    # Step 4: Copy file to clipboard and paste
    print("[4] Copying PDF to clipboard...")
    result = os.system(f'powershell -Command "Set-Clipboard -Path \'{PDF_PATH}\'"')
    print(f"    Clipboard copy result: {result}")
    time.sleep(2)
    
    print("[5] Pasting file into chat...")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(5)
    
    # Step 6: Press Enter to send
    print("[6] Pressing Enter to send...")
    pyautogui.press('enter')
    time.sleep(5)
    
    print("")
    print("=" * 50)
    print("[DONE] Attendance PDF sent to Teddy!")
    print("=" * 50)

if __name__ == "__main__":
    main()
