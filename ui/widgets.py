"""Reusable Tk widgets for the Webster desktop interface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import theme


class WebButton(tk.Button):
    def __init__(self, master, text, command=None, accent=False, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            bg=theme.RED if accent else theme.PANEL_2,
            fg=theme.WHITE,
            activebackground=theme.RED_DARK if accent else theme.BLUE_DARK,
            activeforeground=theme.WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(theme.FONT, 10, "bold"),
            padx=14,
            pady=10,
            **kwargs,
        )


class StatusDot(tk.Canvas):
    def __init__(self, master, size=12, **kwargs):
        super().__init__(master, width=size, height=size, bg=theme.BG, highlightthickness=0, **kwargs)
        self.size = size
        self.dot = self.create_oval(2, 2, size - 2, size - 2, fill=theme.MUTED, outline="")

    def set(self, color):
        self.itemconfigure(self.dot, fill=color)


class ChatBubble(tk.Frame):
    def __init__(self, master, speaker, text, user=False):
        super().__init__(master, bg=theme.BG)
        bubble_color = theme.RED_DARK if user else theme.PANEL_2
        label_color = theme.WHITE
        tk.Label(
            self,
            text=speaker.upper(),
            bg=theme.BG,
            fg=theme.RED if user else theme.BLUE,
            font=(theme.FONT, 8, "bold"),
        ).pack(anchor="e" if user else "w", padx=10)
        tk.Label(
            self,
            text=text,
            bg=bubble_color,
            fg=label_color,
            justify="left",
            wraplength=680,
            padx=14,
            pady=10,
            font=(theme.FONT, 10),
        ).pack(anchor="e" if user else "w", padx=8, pady=(2, 10))


class ScrollableChat(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=theme.BG)
        self.canvas = tk.Canvas(self, bg=theme.BG, highlightthickness=0)
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=theme.BG)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._update)
        self.canvas.bind("<Configure>", self._resize)

    def _update(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    def _resize(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def add(self, speaker, text, user=False):
        bubble = ChatBubble(self.inner, speaker, text, user=user)
        bubble.pack(fill="x", padx=20, pady=3)
        self.after_idle(self._update)
