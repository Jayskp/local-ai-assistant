import subprocess
from core.utils import summarize_output


PROBE_COMMANDS = {
    "systeminfo": "systeminfo",
    "cpu_mem": ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory"],
    "power_plan": ["powercfg", "/getactivescheme"],
    "storage": ["wmic", "logicaldisk", "get", "size,freespace,caption"],
    "network_basic": "ipconfig",
    "ping": "ping -n 2 8.8.8.8",
    "top_processes": [
        "powershell",
        "-Command",
        "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name,CPU,PM | Out-String"
    ],
    "startup": [
        "powershell",
        "-Command",
        "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command | Out-String"
    ],
}


CHANGE_COMMANDS = {
    "flush_dns": ["ipconfig", "/flushdns"],
    "winsock_reset": ["netsh", "winsock", "reset"],
    "power_plan_high": ["powercfg", "/setactive", "SCHEME_MAX"],
    "power_plan_balanced": ["powercfg", "/setactive", "SCHEME_BALANCED"],
    "power_plan_low": ["powercfg", "/setactive", "SCHEME_MIN"],
}


def run_probe(name: str) -> str:
    cmd = PROBE_COMMANDS.get(name)
    if not cmd:
        return f"Probe '{name}' not supported."
    return _run(cmd, f"probe {name}", timeout=40)


def apply_change(name: str) -> str:
    cmd = CHANGE_COMMANDS.get(name)
    if not cmd:
        return f"Change '{name}' not supported."
    return _run(cmd, f"change {name}", timeout=40)


def _run(cmd, label: str, timeout: int) -> str:
    try:
        completed = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return f"{label}: timed out."
    except FileNotFoundError:
        return f"{label}: command not found."
    except Exception as e:
        return f"{label}: failed ({e})."

    summary = summarize_output(completed.stdout, completed.stderr)
    status = "ok" if completed.returncode == 0 else f"exit {completed.returncode}"
    return f"{label}: {status}. Output: {summary}"
