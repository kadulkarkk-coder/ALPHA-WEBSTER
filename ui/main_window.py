"""Main Spider-Man inspired Webster Alpha desktop window."""

from __future__ import annotations

import math
import threading
import tkinter as tk
from tkinter import messagebox

from . import theme
from .widgets import WebButton, StatusDot, ScrollableChat


class MainWindow(tk.Tk):
    """Modern dark desktop shell around the existing Webster application."""

    def __init__(self, application=None, launcher=None):
        super().__init__()
        self.application = application
        self.launcher = launcher
        self._busy = False
        self._voice = False
        self.title("WEBSTER ALPHA — SPIDER CORE")
        self.geometry("1280x800")
        self.minsize(980, 650)
        self.configure(bg=theme.BG)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._build()
        self._draw_webs()
        self._refresh_status()
        self.after(700, self._poll_voice)

    def _build(self):
        self.header = tk.Frame(self, bg=theme.PANEL, height=theme.HEADER_H)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        tk.Label(self.header, text="WEBSTER", bg=theme.PANEL, fg=theme.WHITE,
                 font=(theme.FONT, 22, "bold")).pack(side="left", padx=22)
        tk.Label(self.header, text="ALPHA  •  AI OPERATING PLATFORM", bg=theme.PANEL,
                 fg=theme.MUTED, font=(theme.FONT, 9, "bold")).pack(side="left", padx=4)
        self.status_dot = StatusDot(self.header)
        self.status_dot.pack(side="right", padx=(10, 22))
        self.status_label = tk.Label(self.header, text="INITIALIZING", bg=theme.PANEL,
                                     fg=theme.MUTED, font=(theme.FONT, 9, "bold"))
        self.status_label.pack(side="right")

        self.sidebar = tk.Frame(self, bg=theme.PANEL, width=theme.SIDEBAR_W)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="◈", bg=theme.PANEL, fg=theme.RED,
                 font=(theme.FONT, 42, "bold")).pack(pady=(25, 2))
        tk.Label(self.sidebar, text="SPIDER CORE", bg=theme.PANEL, fg=theme.WHITE,
                 font=(theme.FONT, 10, "bold")).pack(pady=(0, 22))
        self._nav("⌂   Dashboard", self._dashboard)
        self._nav("◉   Chat", self._focus_input)
        self._nav("◌   Voice", self._voice_toggle)
        self._nav("▣   Memory", self._memory)
        self._nav("⚙   Settings", self._settings)
        tk.Frame(self.sidebar, bg=theme.BORDER, height=1).pack(fill="x", padx=16, pady=20)
        self.voice_badge = tk.Label(self.sidebar, text="●  VOICE OFF", bg=theme.PANEL,
                                    fg=theme.MUTED, font=(theme.FONT, 9, "bold"))
        self.voice_badge.pack(pady=8)

        self.main = tk.Frame(self, bg=theme.BG)
        self.main.pack(fill="both", expand=True)
        self._build_chat()

    def _nav(self, text, command):
        WebButton(self.sidebar, text=text, command=command, bg=theme.PANEL,
                  activebackground=theme.PANEL_2, anchor="w", justify="left").pack(fill="x", padx=12, pady=3)

    def _build_chat(self):
        top = tk.Frame(self.main, bg=theme.BG)
        top.pack(fill="x", padx=26, pady=(22, 10))
        tk.Label(top, text="MISSION CONTROL", bg=theme.BG, fg=theme.RED,
                 font=(theme.FONT, 9, "bold")).pack(anchor="w")
        tk.Label(top, text="What can I help you with?", bg=theme.BG, fg=theme.WHITE,
                 font=(theme.FONT, 24, "bold")).pack(anchor="w", pady=(2, 0))

        self.chat = ScrollableChat(self.main)
        self.chat.pack(fill="both", expand=True, padx=16)
        self.chat.add("Webster", "Webster Alpha online. Ask me anything or use the voice control.")

        bottom = tk.Frame(self.main, bg=theme.BG)
        bottom.pack(fill="x", padx=26, pady=18)
        self.entry = tk.Entry(bottom, bg=theme.PANEL_2, fg=theme.WHITE, insertbackground=theme.WHITE,
                              relief="flat", bd=0, font=(theme.FONT, 11))
        self.entry.pack(side="left", fill="x", expand=True, ipady=14, padx=(0, 8))
        self.entry.bind("<Return>", lambda _e: self._send())
        WebButton(bottom, "SEND", self._send, accent=True).pack(side="right")
        WebButton(bottom, "MIC", self._voice_toggle).pack(side="right", padx=8)

    def _send(self):
        text = self.entry.get().strip()
        if not text or self._busy or self.application is None:
            return
        self.entry.delete(0, "end")
        self.chat.add("You", text, user=True)
        self._busy = True
        threading.Thread(target=self._chat_worker, args=(text,), daemon=True).start()

    def _chat_worker(self, text):
        try:
            response = self.application.chat(text)
            self.after(0, lambda r=str(response): self.chat.add("Webster", r))
        except Exception as exc:
            self.after(0, lambda e=str(exc): self.chat.add("Webster", f"I hit an error: {e}"))
        finally:
            self.after(0, lambda: setattr(self, "_busy", False))

    def _voice_toggle(self):
        if self.launcher is None:
            return
        try:
            if self._voice:
                self.launcher.stop_voice()
                self._voice = False
            else:
                self.launcher.start_voice()
                self._voice = True
            self._refresh_status()
        except Exception as exc:
            messagebox.showerror("Voice", str(exc))

    def _poll_voice(self):
        self._refresh_status()
        self.after(700, self._poll_voice)

    def _refresh_status(self):
        try:
            health = self.launcher.voice_manager.health() if self.launcher else {}
            running = bool(health.get("voice_loop_running"))
            self._voice = running
            self.status_dot.set(theme.GREEN if running else theme.AMBER)
            self.status_label.configure(text="VOICE ACTIVE" if running else "ONLINE",
                                         fg=theme.GREEN if running else theme.AMBER)
            self.voice_badge.configure(text="●  VOICE ACTIVE" if running else "●  VOICE OFF",
                                       fg=theme.GREEN if running else theme.MUTED)
        except Exception:
            self.status_dot.set(theme.AMBER)

    def _dashboard(self):
        self.chat.add("Webster", "Dashboard is ready. The Spider Core is monitoring the system.")

    def _focus_input(self):
        self.entry.focus_set()

    def _memory(self):
        self.chat.add("Webster", "Memory controls will appear here as the memory UI is connected.")

    def _settings(self):
        self.chat.add("Webster", "Settings panel is ready for the next UI integration pass.")

    def _draw_webs(self):
        overlay = tk.Canvas(self.main, bg=theme.BG, highlightthickness=0)
        overlay.place(relx=0.80, rely=0.08, relwidth=0.20, relheight=0.24)
        c = 130
        for r in (30, 60, 90, 120):
            overlay.create_oval(c-r, c-r, c+r, c+r, outline=theme.RED_DARK, width=1)
        for angle in range(0, 360, 30):
            x = c + 135 * math.cos(math.radians(angle))
            y = c + 135 * math.sin(math.radians(angle))
            overlay.create_line(c, c, x, y, fill=theme.BLUE_DARK, width=1)
        overlay.lower()

    def _close(self):
        self.destroy()
