import subprocess
import time
import requests
from core.config import load_server_config

# ===============================
# LLAMA SERVER CONFIG
# ===============================
SERVER_CFG = load_server_config()


def is_server_running():
    """
    Check if llama-server is already running.
    """
    try:
        requests.get(f"{SERVER_CFG.base_url}/health", timeout=1)
        return True
    except Exception:
        return False


def start_server():
    """
    Start llama-server silently in the background.
    """
    print("[SYSTEM] Starting llama-server in background...")

    subprocess.Popen(
        [
            SERVER_CFG.exe_path,
            "-m", SERVER_CFG.model_path,
            "--port", str(SERVER_CFG.port)
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def wait_for_server(timeout=30):
    """
    Wait until llama-server becomes available.
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        if is_server_running():
            print("[SYSTEM] llama-server is ready")
            return
        time.sleep(1)

    raise RuntimeError("llama-server failed to start within timeout")
