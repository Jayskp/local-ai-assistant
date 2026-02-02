# Local AI Assistant

A privacy-first, modular LLM orchestrator for Windows.

## Project Structure

```
local-ai-assistant/
│
├── core/
│   ├── main.py          # Main entry point
│   ├── commands.py      # Command definitions and parsing
│   └── executor.py      # Command execution engine
│
├── automations/
│   ├── files.py         # File automation utilities
│   ├── apps.py          # Application automation utilities
│   └── system.py        # System automation utilities
│
├── memory/
│   └── memory.json      # Persistent memory storage
│
└── README.md
```

## Features

- **Privacy-First**: All processing happens locally
- **Modular Design**: Easy to extend with new automations
- **Memory System**: Persistent storage for preferences and context

## Getting Started

1. Run the assistant:
   ```bash
   python core/main.py
   ```

## Modules

### Core
- `main.py` - Initialize and run the assistant
- `commands.py` - Define and register commands
- `executor.py` - Execute tasks and manage queue

### Automations
- `files.py` - Create, delete, move, copy files
- `apps.py` - Open/close applications, launch URLs
- `system.py` - System controls (shutdown, restart, sleep, lock)

### Memory
- `memory.json` - Store user preferences and conversation history
