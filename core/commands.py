import re


def parse_fast(text: str):
    t = text.lower()
    actions = []

    # Detect intent words
    wants_open = "open" in t

    # -------- APP ACTIONS --------
    # Specific apps (for speed)
    if wants_open and "chrome" in t:
        actions.append({
            "type": "app",
            "action": "open_chrome",
            "params": {}
        })

    elif wants_open and ("vscode" in t or "vs code" in t):
        actions.append({
            "type": "app",
            "action": "open_vscode",
            "params": {}
        })
    
    # Universal app/file opener - catches "open <anything>"
    elif wants_open:
        # Extract app name after "open"
        open_match = re.search(r"open\s+(.+)", text, flags=re.IGNORECASE)
        if open_match:
            app_name = open_match.group(1).strip().strip('"')
            if app_name:
                actions.append({
                    "type": "app",
                    "action": "open_any",
                    "params": {"name": app_name}
                })

    # -------- FILE ACTIONS --------
    if "organize" in t and "download" in t:
        actions.append({
            "type": "file",
            "action": "organize_downloads",
            "params": {}
        })

    # -------- SYSTEM CHANGES (with confirmation) --------
    # Temp file cleanup
    if ("clean" in t or "delete" in t or "remove" in t) and ("temp" in t or "temporary" in t):
        actions.append({
            "type": "tool",
            "action": "apply_change",
            "params": {"change": "clean_temp_files", "confirm": False}
        })
    
    # Wi-Fi control
    if ("turn off" in t or "disable" in t or "switch off" in t) and ("wifi" in t or "wi-fi" in t):
        actions.append({
            "type": "tool",
            "action": "apply_change",
            "params": {"change": "wifi_off", "confirm": False}
        })
    
    if ("turn on" in t or "enable" in t or "switch on" in t) and ("wifi" in t or "wi-fi" in t):
        actions.append({
            "type": "tool",
            "action": "apply_change",
            "params": {"change": "wifi_on", "confirm": False}
        })
    
    # DNS flush
    if ("flush" in t or "clear" in t or "reset" in t) and "dns" in t:
        actions.append({
            "type": "tool",
            "action": "apply_change",
            "params": {"change": "flush_dns", "confirm": False}
        })
    
    # Windows Update
    if ("check" in t or "open" in t) and ("update" in t or "windows update" in t):
        actions.append({
            "type": "tool",
            "action": "apply_change",
            "params": {"change": "check_windows_updates", "confirm": False}
        })
    
    # Disk cleanup
    if ("disk cleanup" in t or ("clean" in t and "disk" in t)):
        actions.append({
            "type": "tool",
            "action": "apply_change",
            "params": {"change": "disk_cleanup", "confirm": False}
        })

    # -------- SHELL COMMAND --------
    # Pattern: "run <cmd> in <path>" or "run <cmd>"
    run_in_match = re.search(r"run\s+(.+?)\s+in\s+(.+)", text, flags=re.IGNORECASE)
    if run_in_match:
        cmd = run_in_match.group(1).strip().strip('"')
        cwd = run_in_match.group(2).strip().strip('"')
        if cmd:
            actions.append({
                "type": "system",
                "action": "run_command",
                "params": {"cmd": cmd, "cwd": cwd}
            })
    else:
        run_match = re.search(r"run\s+(.+)", text, flags=re.IGNORECASE)
        if run_match:
            cmd = run_match.group(1).strip().strip('"')
            if cmd:
                actions.append({
                    "type": "system",
                    "action": "run_command",
                    "params": {"cmd": cmd}
                })

    if actions:
        return actions

    return None
