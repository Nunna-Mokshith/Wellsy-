"""
Wellsy Background Daemon & System Tray Service
Runs Wellsy silently in the background on Windows startup with optional System Tray icon.
"""
import sys
import os
import asyncio
import threading
import webbrowser
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from main import app, FRONTEND_DIR

# Tray icon support
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


def create_tray_icon():
    """Create a simple cyan orb icon for system tray."""
    image = Image.new('RGB', (64, 64), color=(10, 14, 26))
    draw = ImageDraw.Draw(image)
    # Draw cyan glowing circle
    draw.ellipse((8, 8, 56, 56), fill=(0, 212, 255), outline=(59, 139, 255))
    draw.ellipse((20, 20, 44, 44), fill=(255, 255, 255))
    return image


def open_dashboard(icon=None, item=None):
    """Open Wellsy dashboard in default web browser."""
    webbrowser.open("http://localhost:8765")


def stop_daemon(icon=None, item=None):
    """Stop the Wellsy tray icon and exit daemon process."""
    print("  [-] Stopping Wellsy Daemon...")
    if icon:
        icon.stop()
    os._exit(0)


def run_tray():
    """Run system tray icon in main thread."""
    if not TRAY_AVAILABLE:
        print("  [!] pystray not installed — running daemon headlessly.")
        return

    icon_image = create_tray_icon()
    menu = pystray.Menu(
        pystray.MenuItem("Open Command Center", open_dashboard, default=True),
        pystray.MenuItem("System Status: ONLINE", lambda icon, item: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit Wellsy", stop_daemon)
    )
    icon = pystray.Icon("Wellsy", icon_image, "Wellsy Command Center", menu)
    icon.run()


def start_server():
    """Run uvicorn server in a daemon thread."""
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="warning")


if __name__ == "__main__":
    print("========================================")
    print("   WELLSY BACKGROUND DAEMON STARTING")
    print("========================================")
    print("  [+] Command Center Dashboard : http://localhost:8765")
    print("  [+] WebSocket API            : ws://localhost:8765/ws")
    
    # Start server thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Open dashboard automatically
    open_dashboard()

    # Run system tray icon if available, else keep thread alive
    if TRAY_AVAILABLE:
        run_tray()
    else:
        try:
            while True:
                threading.Event().wait(1000)
        except KeyboardInterrupt:
            print("\n  [-] Wellsy Daemon stopped.")
