import tkinter as tk
from core.commands import parse_fast
from core.llm_parser import parse_with_llm
from core.executor import execute_command


def show_popup():
    root = tk.Tk()
    root.title("Local AI Assistant")
    root.geometry("420x60")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    entry = tk.Entry(root, font=("Segoe UI", 12))
    entry.pack(fill="both", expand=True, padx=10, pady=10)
    entry.focus()

    def on_enter(event=None):
        command = entry.get().strip()
        root.destroy()

        if not command:
            return

        actions = parse_fast(command)
        if actions is None:
            actions = parse_with_llm(command)

        if not actions:
            return

        for action in actions:
            execute_command(action)

    entry.bind("<Return>", on_enter)
    root.mainloop()
