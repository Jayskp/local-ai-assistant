from automations.apps import open_chrome, open_vscode
from automations.files import organize_downloads
    
def execute_command(command: dict):
    command_type = command["type"]
    action = command["action"]

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

    return "⚠️ Command recognized but not implemented."
