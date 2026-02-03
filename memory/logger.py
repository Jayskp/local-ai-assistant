import json
import os
from datetime import datetime


def _memory_file():
    base = os.environ.get("LOCAL_AI_ASSISTANT_DATA")
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".local_ai_assistant")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "memory.json")


def log_command(text, result):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "command": text,
        "result": result
    }

    memory_file = _memory_file()

    # Load existing memory or start fresh
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memory = {}

    # Ensure a list exists to hold command entries
    history = memory.setdefault("command_history", [])
    history.append(entry)

    # Write back safely (overwrite)
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def get_recent_history(limit: int = 5):
    memory_file = _memory_file()
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    history = memory.get("command_history", [])
    return history[-limit:]