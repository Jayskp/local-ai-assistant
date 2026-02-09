import sys
import os
import time 
import traceback


# Handle PyInstaller bundled exe paths correctly
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    # Running as script
    APPLICATION_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = APPLICATION_PATH
sys.path.append(PROJECT_ROOT)

# Log file in same directory as exe
LOG_FILE = os.path.join(APPLICATION_PATH, "startup_error.log")

def log_error(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    except:
        pass

# Log startup attempt
log_error("=== Application starting ===")

try:
    from core.commands import parse_fast
    from core.llm_parser import parse_with_llm
    from core.executor import execute_command
    from memory.logger import log_command
    from core.llm_manager import is_server_running, start_server, wait_for_server
    from core.tray import start_tray
    from core.hotkey import start_hotkey
    log_error("Imports successful")
except Exception as e:
    log_error(f"Import error: {str(e)}\n{traceback.format_exc()}")
    raise


def main():
    try:
        log_error("main() started")
        
        # Start LLM server FIRST so it's ready when user opens popup
        if not is_server_running():
            log_error("Starting LLM server...")
            start_server()
            log_error("Waiting for server to be ready...")
            if not wait_for_server(timeout=60):
                log_error("Server failed to start, but continuing...")
            else:
                log_error("LLM server is ready!")
        else:
            log_error("LLM server already running")
        
        log_error("Starting tray...")
        tray_thread = start_tray()
        log_error("Tray started")
        
        log_error("Starting hotkey...")
        start_hotkey()
        log_error("Hotkey started")

        log_error("Waiting for tray thread to finish (app running)...")
        # Wait for tray thread to finish (keeps app alive)
        tray_thread.join()
        log_error("Tray thread ended, application exiting")
    except Exception as e:
        log_error(f"Error in main(): {str(e)}\\n{traceback.format_exc()}")
        # Keep running anyway with fallback loop
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()

