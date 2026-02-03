import tkinter as tk
from tkinter import ttk
import threading
from core.commands import parse_fast
from core.llm_parser import parse_with_llm, answer_with_llm
from core.executor import execute_command
from memory.logger import log_command


class ModernPopup:
    def __init__(self):
        self.window_width = 640
        self.window_height = 440
        self.BASE_BG = "#0c1324"  # Solid base to avoid bleed-through
        self.CARD_BG = "#0b1220"
        self.CARD_BORDER = "#1e293b"
        self.PRIMARY_TEXT = "#e2e8f0"
        self.MUTED_TEXT = "#94a3b8"
        self.ACCENT = "#7dd3fc"
        self.ACCENT_STRONG = "#38bdf8"

        self.root = tk.Tk()
        self.root.title("Local AI Assistant")
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # Remove window borders for modern look
        self.root.configure(bg=self.BASE_BG)
        self.root.attributes("-alpha", 1.0)  # Fully opaque to prevent background bleed
        
        # Center window on screen
        self.center_window()
        
        # Create modern UI
        self.create_ui()
        
        # Bind ESC to close
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.window_width
        height = self.window_height
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        """Create the modern UI with a glassy, rounded card"""
        canvas = tk.Canvas(
            self.root,
            bg=self.BASE_BG,
            highlightthickness=0,
            bd=0,
            width=self.window_width,
            height=self.window_height
        )
        canvas.pack(fill="both", expand=True)

        # Soft gradient background behind the card
        for i in range(self.window_height):
            ratio = i / max(1, self.window_height)
            color = self._interpolate_color(self.BASE_BG, "#101a2f", ratio)
            canvas.create_line(0, i, self.window_width, i, fill=color)

        card_margin = 12
        card_radius = 20
        card_x1, card_y1 = card_margin, card_margin
        card_x2, card_y2 = self.window_width - card_margin, self.window_height - card_margin

        # Outer glow
        self._draw_rounded_rect(canvas, card_x1 - 2, card_y1 - 2, card_x2 + 2, card_y2 + 2, card_radius + 2, fill="#0c1a2c")

        # Main glass card
        self._draw_rounded_rect(
            canvas,
            card_x1,
            card_y1,
            card_x2,
            card_y2,
            card_radius,
            fill=self.CARD_BG,
            outline=self.CARD_BORDER,
            width=2
        )

        card_width = card_x2 - card_x1
        card_height = card_y2 - card_y1
        content_frame = tk.Frame(canvas, bg=self.CARD_BG)
        canvas.create_window(
            self.window_width / 2,
            self.window_height / 2,
            window=content_frame,
            width=card_width,
            height=card_height
        )

        # Make the entire card draggable, not just the header
        self._make_draggable(content_frame)

        header = tk.Frame(content_frame, bg=self.CARD_BG)
        header.pack(fill="x", padx=22, pady=(20, 12))

        title = tk.Label(
            header,
            text="✨ Local AI Assistant",
            font=("Segoe UI Variable", 18, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_TEXT
        )
        title.pack(side="left")

        badge = tk.Label(
            header,
            text="Now",
            font=("Segoe UI", 9, "bold"),
            bg=self.ACCENT,
            fg="#0b1220",
            padx=10,
            pady=4
        )
        badge.pack(side="left", padx=(12, 0))

        close_btn = tk.Button(
            header,
            text="✕",
            font=("Segoe UI", 12, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_TEXT,
            activebackground=self.CARD_BG,
            activeforeground=self.ACCENT,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.root.destroy
        )
        close_btn.pack(side="right")

        self._make_draggable(header)

        input_block = tk.Frame(content_frame, bg=self.CARD_BG)
        input_block.pack(fill="x", padx=22, pady=(6, 12))

        prompt_label = tk.Label(
            input_block,
            text="What would you like to do?",
            font=("Segoe UI", 10),
            bg=self.CARD_BG,
            fg=self.MUTED_TEXT
        )
        prompt_label.pack(anchor="w", pady=(0, 8))

        entry_wrap = tk.Frame(input_block, bg=self.CARD_BG, highlightthickness=1, highlightbackground=self.CARD_BORDER)
        entry_wrap.pack(fill="x")

        self.entry = tk.Entry(
            entry_wrap,
            font=("Segoe UI", 13),
            bg="#0f172a",
            fg=self.PRIMARY_TEXT,
            insertbackground=self.ACCENT_STRONG,
            relief="flat",
            highlightthickness=0,
            bd=0
        )
        self.entry.pack(fill="x", ipady=12, padx=12)
        self.entry.focus()
        self.entry.bind("<Return>", self.on_enter)

        self.status_label = tk.Label(
            content_frame,
            text="",
            font=("Segoe UI", 9),
            bg=self.CARD_BG,
            fg=self.ACCENT_STRONG
        )
        self.status_label.pack(pady=(6, 4))

        # Output area for longer messages/results
        output_frame = tk.Frame(content_frame, bg=self.CARD_BG)
        output_frame.pack(fill="both", padx=22, pady=(0, 10))

        output_label = tk.Label(
            output_frame,
            text="Details",
            font=("Segoe UI", 9, "bold"),
            bg=self.CARD_BG,
            fg=self.MUTED_TEXT
        )
        output_label.pack(anchor="w", pady=(0, 4))

        self.output_box = tk.Text(
            output_frame,
            height=5,
            bg="#0f172a",
            fg=self.PRIMARY_TEXT,
            insertbackground=self.ACCENT_STRONG,
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            wrap="word",
            font=("Consolas", 9)
        )
        self.output_box.pack(fill="both", expand=True)
        self.output_box.config(state="disabled")

        quick_frame = tk.Frame(content_frame, bg=self.CARD_BG)
        quick_frame.pack(fill="both", expand=True, padx=22, pady=(10, 12))

        quick_title = tk.Label(
            quick_frame,
            text="Quick Actions",
            font=("Segoe UI", 11, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_TEXT
        )
        quick_title.pack(anchor="w")

        quick_sub = tk.Label(
            quick_frame,
            text="Jump into frequent tasks instantly.",
            font=("Segoe UI", 9),
            bg=self.CARD_BG,
            fg=self.MUTED_TEXT
        )
        quick_sub.pack(anchor="w", pady=(2, 10))

        btn_container = tk.Frame(quick_frame, bg=self.CARD_BG)
        btn_container.pack(fill="x")

        quick_actions = [
            ("🌐 Chrome", "open chrome"),
            ("💻 VS Code", "open vscode"),
            ("📁 Organize Downloads", "organize downloads"),
        ]

        for label, command in quick_actions:
            btn = tk.Button(
                btn_container,
                text=label,
                font=("Segoe UI", 10, "bold"),
                bg="#111d32",
                fg=self.PRIMARY_TEXT,
                activebackground=self.ACCENT_STRONG,
                activeforeground="#0b1220",
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=18,
                pady=12,
                command=lambda cmd=command: self.quick_action(cmd)
            )
            btn.pack(side="left", padx=6, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#111d32"))

        footer = tk.Label(
            content_frame,
            text="💡 Tip: Press Ctrl+Space anytime to summon me | ESC to close",
            font=("Segoe UI", 9),
            bg=self.CARD_BG,
            fg=self.MUTED_TEXT
        )
        footer.pack(side="bottom", pady=10)

        # Accent bar along the bottom edge
        self._draw_rounded_rect(
            canvas,
            card_x1,
            card_y2 - 8,
            card_x2,
            card_y2,
            radius=card_radius,
            fill=self._interpolate_color(self.ACCENT_STRONG, "#2563eb", 0.25),
            outline=""
        )

    def _interpolate_color(self, c1, c2, t):
        """Blend two hex colors."""
        def _hex_to_rgb(c):
            c = c.lstrip('#')
            return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

        def _rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb

        r1, g1, b1 = _hex_to_rgb(c1)
        r2, g2, b2 = _hex_to_rgb(c2)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return _rgb_to_hex((r, g, b))

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius=16, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _make_draggable(self, widget):
        widget.bind("<ButtonPress-1>", self._start_move)
        widget.bind("<B1-Motion>", self._do_move)

    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_move(self, event):
        x = self.root.winfo_pointerx() - self._drag_x
        y = self.root.winfo_pointery() - self._drag_y
        self.root.geometry(f"+{x}+{y}")
        
    def quick_action(self, command):
        """Execute a quick action"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, command)
        self.on_enter()
        
    def on_enter(self, event=None):
        """Handle command submission"""
        command = self.entry.get().strip()
        
        if not command:
            return
        
        # Disable input while processing
        self.entry.config(state="disabled")
        self.status_label.config(text="⏳ Processing...", fg="#5eaaa8")
        self.root.update()
        
        # Process in thread to keep UI responsive
        def process():
            try:
                # Try fast parsing first
                actions = parse_fast(command)

                # Cheap keyword mapping to avoid slow LLM calls
                if actions is None:
                    lowered = command.lower()
                    forced_actions = []
                    if "system info" in lowered or "system information" in lowered or "my system" in lowered:
                        forced_actions.append({"type": "system", "action": "system_info", "params": {}})
                    if "network" in lowered or "internet" in lowered:
                        forced_actions.append({"type": "system", "action": "network_info", "params": {}})
                    if "slow" in lowered or "lag" in lowered or "performance" in lowered:
                        forced_actions.append({"type": "system", "action": "optimize_performance", "params": {"confirm": False}})
                    if "privacy" in lowered:
                        forced_actions.append({"type": "system", "action": "apply_privacy", "params": {"confirm": False}})
                    if "network" in lowered and ("fix" in lowered or "reset" in lowered or "dns" in lowered):
                        forced_actions.append({"type": "system", "action": "fix_network", "params": {"confirm": False}})
                    if "battery" in lowered or "power saver" in lowered or "backup" in lowered:
                        forced_actions.append({"type": "system", "action": "battery_optimize", "params": {"confirm": False}})
                    if "dev mode" in lowered or "developer mode" in lowered or "dev profile" in lowered:
                        forced_actions.append({"type": "system", "action": "dev_mode", "params": {"confirm": False}})
                    if "startup" in lowered:
                        forced_actions.append({"type": "tool", "action": "probe_system", "params": {"probe": "startup"}})

                    if forced_actions:
                        actions = forced_actions

                # If we found actions, execute immediately without LLM thinking state
                if actions:
                    last_result = ""
                    for action in actions:
                        result = execute_command(action)
                        last_result = result
                        print(f"[EXEC] {result}")
                    if last_result:
                        self.status_label.config(text="Done", fg="#7dd3fc")
                        self._set_output(last_result)
                    log_command(command, actions)
                    self.entry.config(state="normal")
                    self.root.update()
                    return

                # If no actions, go straight to concise Q&A (still avoids long LLM tool JSON step)
                self.status_label.config(text="💬 Answering...", fg="#7dd3fc")
                self.root.update()
                answer = answer_with_llm(command)
                self._set_output(answer)
                self.status_label.config(text="Done", fg="#7dd3fc")
                log_command(command, [{"type": "answer", "action": "answer", "params": {"text": answer}}])
                self.entry.config(state="normal")
                self.root.update()
                
            except Exception as e:
                self.status_label.config(text="❌ Error", fg="#e94560")
                self._set_output(str(e))
                self.entry.config(state="normal")
        
        threading.Thread(target=process, daemon=True).start()

    def _set_output(self, text: str):
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text.strip())
        self.output_box.config(state="disabled")
        
    def show(self):
        """Show the popup"""
        self.root.mainloop()


def show_popup():
    """Create and show the modern popup"""
    popup = ModernPopup()
    popup.show()
