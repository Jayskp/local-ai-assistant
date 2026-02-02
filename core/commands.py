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

    if actions:
        return actions

    return None
