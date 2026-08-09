"""Desktop UI bootstrap for Webster Alpha."""

from __future__ import annotations

from .main_window import MainWindow


def run(application, launcher) -> None:
    """Start the desktop interface using the already initialized runtime."""
    window = MainWindow(application=application, launcher=launcher)
    window.mainloop()
