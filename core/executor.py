import os
import subprocess
from automations.apps import open_chrome, open_vscode
from automations.files import organize_downloads
from automations.tweaks import (
    optimize_performance,
    apply_privacy,
    fix_network,
    battery_optimize,
    dev_mode,
)
from automations.probes import run_probe, apply_change
from core.utils import summarize_output


def execute_command(command: dict):
    command_type = command["type"]
    action = command["action"]
    params = command.get("params", {})

    if command_type == "app":
        if action == "open_chrome":
            open_chrome()
            return "✅ Chrome opened."

        if action == "open_vscode":
            open_vscode()
            return "✅ VS Code opened."

    if command_type == "file":
        if action == "organize_downloads":
            organize_downloads()
            return "📁 Downloads organized."

    if command_type == "system":
        if action == "run_command":
            return _run_shell_command(
                cmd=params.get("cmd"),
                cwd=params.get("cwd")
            )

        if action == "git_clone":
            return _git_clone(
                repo=params.get("repo"),
                folder=params.get("folder")
            )

        if action == "optimize_performance":
            return optimize_performance(params)

        if action == "apply_privacy":
            return apply_privacy(params)

        if action == "fix_network":
            return fix_network(params)

        if action == "battery_optimize":
            return battery_optimize(params)

        if action == "dev_mode":
            return dev_mode(params)

        if action == "system_info":
            return _system_info()

        if action == "network_info":
            return _network_info()

    if command_type == "tool":
        if action == "probe_system":
            probe = params.get("probe") if isinstance(params, dict) else None
            if not probe:
                return "⚠️ No probe specified."
            return run_probe(probe)

        if action == "apply_change":
            change = params.get("change") if isinstance(params, dict) else None
            if not change:
                return "⚠️ No change specified."
            if params.get("confirm") is not True:
                return "Pending confirmation to apply change."
            return apply_change(change)

    return "⚠️ Command recognized but not implemented."


def _run_shell_command(cmd: str, cwd: str | None) -> str:
    if not cmd:
        return "⚠️ No command provided."

    home = os.path.expanduser("~")
    target_cwd = _resolve_folder(cwd, home, default_to_base=True)
    if not target_cwd:
        return "⚠️ Target folder not found under your user directory."

    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            cwd=target_cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
    except subprocess.TimeoutExpired:
        return f"⏱️ Timeout after 60s running '{cmd}' in {target_cwd}."
    except Exception as e:
        return f"❌ Failed to run '{cmd}' in {target_cwd}: {e}"

    output = summarize_output(completed.stdout, completed.stderr)
    return (
        f"✅ Ran '{cmd}' in {target_cwd} (exit {completed.returncode})." +
        (f" Output: {output}" if output else "")
    )


def _git_clone(repo: str | None, folder: str | None) -> str:
    if not repo:
        return "⚠️ No repo URL provided."

    base = os.path.expanduser("~")
    target_dir = _resolve_folder(folder, base) if folder else base

    if not target_dir:
        return "⚠️ Target folder not found under your user directory."

    try:
        completed = subprocess.run(
            ["git", "clone", repo],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
    except subprocess.TimeoutExpired:
        return f"⏱️ Timeout cloning {repo} into {target_dir}."
    except FileNotFoundError:
        return "❌ Git not found in PATH."
    except Exception as e:
        return f"❌ Failed to clone {repo} into {target_dir}: {e}"

    output = summarize_output(completed.stdout, completed.stderr)
    if completed.returncode == 0:
        return f"✅ Cloned {repo} into {target_dir}. Output: {output}"
    return f"❌ Git clone failed (exit {completed.returncode}) into {target_dir}. Output: {output}"


def _resolve_folder(folder: str | None, base: str, default_to_base: bool = False) -> str | None:
    if not folder:
        return base if default_to_base else None

    cleaned = folder.strip().strip('"').strip()
    if not cleaned:
        return base if default_to_base else None

    # If absolute, ensure under base and exists
    if os.path.isabs(cleaned):
        abs_path = os.path.abspath(cleaned)
        try:
            common = os.path.commonpath([base, abs_path])
        except ValueError:
            common = ""
        if common != base:
            return None
        return abs_path if os.path.isdir(abs_path) else None

    # Search by folder name under base (limited depth)
    target = _find_folder_by_name(cleaned, base)
    if target:
        return target

    # Fallback: treat as subfolder directly under base
    fallback = os.path.join(base, cleaned)
    return fallback if os.path.isdir(fallback) else None


def _find_folder_by_name(name: str, base: str, max_depth: int = 10) -> str | None:
    name_lower = name.lower()
    stack = [(base, 0)]

    while stack:
        path, depth = stack.pop()
        if depth > max_depth:
            continue
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name.lower() == name_lower:
                            return entry.path
                        stack.append((entry.path, depth + 1))
        except (PermissionError, FileNotFoundError):
            continue
    return None


def _system_info() -> str:
    cmds = [
        ("systeminfo", "System info"),
        (["wmic", "cpu", "get", "name"], "CPU name"),
        (["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory"], "Memory"),
    ]
    outputs = []
    for cmd, label in cmds:
        outputs.append(_run_simple_cmd(cmd, label, timeout=20))
    return "\n".join(outputs)


def _network_info() -> str:
    cmds = [
        ("ipconfig", "IP config"),
        ("ping -n 2 8.8.8.8", "Ping 8.8.8.8"),
    ]
    outputs = []
    for cmd, label in cmds:
        outputs.append(_run_simple_cmd(cmd, label, timeout=20))
    return "\n".join(outputs)


def _run_simple_cmd(cmd, label: str, timeout: int = 30) -> str:
    try:
        completed = subprocess.run(
            cmd,
            shell=True,
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


    # summarize_output now in core.utils
