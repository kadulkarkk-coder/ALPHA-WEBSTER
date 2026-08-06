"""
Simple StatusManager for Application
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class StatusManager:
    _running: bool = False
    _started: datetime | None = None

    def set_running(self, value: bool) -> None:
        self._running = bool(value)

        if value and self._started is None:
            self._started = datetime.now()

    @property
    def running(self) -> bool:
        return self._running

    @property
    def started(self) -> datetime | None:
        return self._started

    def __repr__(self) -> str:  # pragma: no cover - tiny repr
        return f"StatusManager(running={self._running})"
