import subprocess
import os
from automations.apps import open_chrome, open_vscode
from core.utils import summarize_output


def _requires_confirm(params: dict):
    return not params.get("confirm", False)


def optimize_performance(params: dict) -> str:
    if _requires_confirm(params):
        return "Pending confirmation to optimize performance (disable startup-heavy apps, set high performance plan)."

    outputs = []
    outputs.append(_run_cmd(["powercfg", "/setactive", "SCHEME_MAX"], "Set High Performance plan"))
    outputs.append(_run_cmd([
        "powershell",
        "-Command",
        "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name,CPU,PM | Out-String"
    ], "Top CPU/mem processes (info only)"))
    return "\n".join(outputs)


def apply_privacy(params: dict) -> str:
    if _requires_confirm(params):
        return "Pending confirmation to apply privacy tweaks (reduce telemetry/ads)."

    cmds = [
        (
            ["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo", "/v", "Enabled", "/t", "REG_DWORD", "/d", "0", "/f"],
            "Disable advertising ID"
        ),
        (
            ["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Privacy", "/v", "TailoredExperiencesWithDiagnosticDataEnabled", "/t", "REG_DWORD", "/d", "0", "/f"],
            "Disable tailored experiences"
        ),
        (
            ["reg", "add", "HKLM\\Software\\Policies\\Microsoft\\Windows\\DataCollection", "/v", "AllowTelemetry", "/t", "REG_DWORD", "/d", "1", "/f"],
            "Set telemetry to basic (may require admin)"
        ),
    ]
    outputs = [_run_cmd(cmd, label) for cmd, label in cmds]
    return "\n".join(outputs)


def fix_network(params: dict) -> str:
    if _requires_confirm(params):
        return "Pending confirmation to fix network (flush DNS, reset winsock)."

    cmds = [
        (["ipconfig", "/flushdns"], "Flush DNS"),
        (["netsh", "winsock", "reset"], "Reset winsock (may require reboot)"),
    ]
    outputs = [_run_cmd(cmd, label) for cmd, label in cmds]
    return "\n".join(outputs)


def battery_optimize(params: dict) -> str:
    if _requires_confirm(params):
        return "Pending confirmation to optimize battery (power saver)."

    return _run_cmd(["powercfg", "/setactive", "SCHEME_MIN"], "Set Power Saver plan")


def dev_mode(params: dict) -> str:
    if _requires_confirm(params):
        return "Pending confirmation to start dev mode (launch tools, set performance)."

    profile = params.get("profile") or "default"
    outputs = []
    outputs.append(_run_cmd(["powercfg", "/setactive", "SCHEME_MAX"], "Set High Performance plan"))

    # Launch common dev apps (best-effort)
    try:
        open_vscode()
        outputs.append("Launched VS Code")
    except Exception as e:
        outputs.append(f"VS Code launch failed: {e}")
    try:
        open_chrome()
        outputs.append("Launched Chrome")
    except Exception as e:
        outputs.append(f"Chrome launch failed: {e}")

    outputs.append(f"Dev mode profile: {profile}")
    return "\n".join(outputs)


def _run_cmd(cmd, label: str) -> str:
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            shell=False
        )
    except FileNotFoundError:
        return f"{label}: tool not found ({cmd[0]})."
    except subprocess.TimeoutExpired:
        return f"{label}: timed out."
    except Exception as e:
        return f"{label}: failed ({e})."

    summary = summarize_output(completed.stdout, completed.stderr)
    status = "ok" if completed.returncode == 0 else f"exit {completed.returncode}"
    return f"{label}: {status}. Output: {summary}"
