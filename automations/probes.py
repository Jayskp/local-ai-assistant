import subprocess
from core.utils import summarize_output


PROBE_COMMANDS = {
    "systeminfo": "systeminfo",
    "cpu_mem": ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory"],
    "power_plan": ["powercfg", "/getactivescheme"],
    "storage": ["wmic", "logicaldisk", "get", "size,freespace,caption"],
    "disk_usage": [
        "powershell",
        "-Command",
        "Get-PSDrive -PSProvider FileSystem | Select-Object Name,Used,Free | Out-String"
    ],
    "network_basic": "ipconfig",
    "ping": "ping -n 2 8.8.8.8",
    "wifi_status": [
        "powershell",
        "-Command",
        "netsh wlan show interfaces"
    ],
    "windows_update_status": [
        "powershell",
        "-Command",
        "(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search('IsInstalled=0').Updates | Select-Object Title | Out-String"
    ],
    "temp_files_size": [
        "powershell",
        "-Command",
        "$temp = @($env:TEMP, 'C:\\Windows\\Temp'); $temp | ForEach-Object { if (Test-Path $_) { $size = (Get-ChildItem $_ -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB; \"$_: $([math]::Round($size, 2)) MB\" } }"
    ],
    "battery_status": [
        "powershell",
        "-Command",
        "Get-WmiObject -Class Win32_Battery | Select-Object EstimatedChargeRemaining,BatteryStatus | Out-String"
    ],
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
    "clean_temp_files": [
        "powershell",
        "-Command",
        "$temp = @($env:TEMP, 'C:\\Windows\\Temp'); $temp | ForEach-Object { if (Test-Path $_) { Remove-Item -Path \"$_\\*\" -Recurse -Force -ErrorAction SilentlyContinue } }; 'Temp files cleaned'"
    ],
    "wifi_off": [
        "powershell",
        "-Command",
        "netsh interface set interface 'Wi-Fi' disabled"
    ],
    "wifi_on": [
        "powershell",
        "-Command",
        "netsh interface set interface 'Wi-Fi' enabled"
    ],
    "check_windows_updates": [
        "powershell",
        "-Command",
        "Start-Process ms-settings:windowsupdate"
    ],
    "disk_cleanup": [
        "cleanmgr",
        "/sagerun:1"
    ],
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
