import threading
import time
from core.popup import show_popup

def start_hotkey():
    def listen():
        try:
            time.sleep(10)  # wait for Windows + Explorer
            import keyboard
            keyboard.add_hotkey("ctrl+space", show_popup)
            keyboard.wait()
        except Exception as e:
            # Silently ignore hotkey failure at startup
            # App should continue running
            pass

    t = threading.Thread(target=listen, daemon=True)
    t.start()
