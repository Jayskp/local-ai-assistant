import threading
import time
import subprocess
import sys
import os

# Track popup state to prevent multiple instances
_popup_process = None
_last_trigger_time = 0


def _launch_popup():
    """Launch Flet popup in a subprocess (Flet blocks and needs its own process)"""
    global _popup_process, _last_trigger_time
    
    print("[HOTKEY] Ctrl+Space triggered!")
    
    # Debounce: ignore if triggered within 1 second
    current_time = time.time()
    if current_time - _last_trigger_time < 1.0:
        print("[HOTKEY] Debounced - too soon")
        return
    _last_trigger_time = current_time
    
    # Check if popup is already running
    if _popup_process is not None and _popup_process.poll() is None:
        print("[HOTKEY] Popup already running")
        return
    
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled exe - launch separate popup.exe
            popup_exe = os.path.join(os.path.dirname(sys.executable), "popup.exe")
            
            if not os.path.exists(popup_exe):
                print(f"[HOTKEY] ERROR: popup.exe not found at {popup_exe}")
                return
            
            print(f"[HOTKEY] Launching popup.exe from: {popup_exe}")
            _popup_process = subprocess.Popen(
                [popup_exe],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        else:
            # Running as script - use -m module
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(f"[HOTKEY] Running as script from: {base}")
            _popup_process = subprocess.Popen(
                [sys.executable, "-m", "core.popup_webview"],
                cwd=base
            )
        print(f"[HOTKEY] Popup process started: {_popup_process.pid}")
    except Exception as e:
        print(f"[HOTKEY] Failed to launch popup: {e}")


def start_hotkey():
    def listen():
        try:
            print("[HOTKEY] Waiting 3 seconds before registering hotkey...")
            time.sleep(3)  # Reduced from 10s
            import keyboard
            keyboard.add_hotkey("ctrl+space", _launch_popup)
            print("[HOTKEY] Hotkey registered! Press Ctrl+Space to open assistant.")
            keyboard.wait()
        except Exception as e:
            print(f"[HOTKEY] Error: {e}")

    t = threading.Thread(target=listen, daemon=True)
    t.start()
