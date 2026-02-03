import re


def parse_fast(text: str):
    t = text.lower()
    actions = []

    # Detect intent words
    wants_open = "open" in t

    # -------- APP ACTIONS --------
    if wants_open and "chrome" in t:
        actions.append({
            "type": "app",
            "action": "open_chrome",
            "params": {}
        })

    if wants_open and ("vscode" in t or "vs code" in t):
        actions.append({
            "type": "app",
            "action": "open_vscode",
            "params": {}
        })

    # -------- FILE ACTIONS --------
    if "organize" in t and "download" in t:
        actions.append({
            "type": "file",
            "action": "organize_downloads",
            "params": {}
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
