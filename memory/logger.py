import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), 'memory.json')

def log_command(text, result):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "command": text,
        "result": result
    }

    # Load existing memory or start fresh
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memory = {}

    # Ensure a list exists to hold command entries
    history = memory.setdefault("command_history", [])
    history.append(entry)

    # Write back safely (overwrite)
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)