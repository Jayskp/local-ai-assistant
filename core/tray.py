import threading
import sys
import os
import time
import traceback
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw


# Get log path (same as main.py)
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    APPLICATION_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_FILE = os.path.join(APPLICATION_PATH, "startup_error.log")

def log_error(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - [TRAY] {msg}\n")
    except:
        pass


def create_image():
    """Create a simple tray icon dynamically"""
    image = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="white")
    return image


def on_exit(icon, item):
    log_error("Exit clicked by user")
    icon.stop()
    sys.exit(0)


def run_tray():
    max_retries = 5
    retry_delay = 10  # seconds
    
    for attempt in range(max_retries):
        try:
            log_error(f"Creating tray icon (attempt {attempt + 1}/{max_retries})...")
            icon = Icon(
                "LocalAI",
                create_image(),
                "Local AI Assistant",
                menu=Menu(
                    MenuItem("Exit", on_exit)
                )
            )
            log_error("Tray icon created, calling icon.run()...")
            icon.run()
            log_error("icon.run() returned (tray closed normally)")
            return  # Normal exit
        except Exception as e:
            log_error(f"Tray error on attempt {attempt + 1}: {str(e)}\n{traceback.format_exc()}")
            if attempt < max_retries - 1:
                log_error(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                log_error("Max retries reached, tray thread exiting")
    
    # Keep thread alive even if tray fails (prevents app from exiting)
    log_error("Tray failed, entering keep-alive loop...")
    while True:
        time.sleep(60)



def start_tray():
    # Non-daemon thread keeps the app alive
    tray_thread = threading.Thread(target=run_tray, daemon=False)
    tray_thread.start()
    return tray_thread
