import subprocess
import time
import requests

# ===============================
# LLAMA SERVER CONFIG
# ===============================
LLAMA_SERVER_URL = "http://127.0.0.1:8080"
LLAMA_SERVER_EXE = r"C:\Users\Admin\llma.cpp\llama-server.exe"
MODEL_PATH = r"C:\Users\Admin\llma.cpp\models\phi3.gguf"


def is_server_running():
    """
    Check if llama-server is already running.
    """
    try:
        requests.get(f"{LLAMA_SERVER_URL}/health", timeout=1)
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
            LLAMA_SERVER_EXE,
            "-m", MODEL_PATH,
            "--port", "8080"
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
