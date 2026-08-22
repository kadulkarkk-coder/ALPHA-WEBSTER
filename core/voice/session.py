"""Stateful voice session abstraction."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VoiceSession:
    """Tracks one conversational voice session without owning audio resources."""

    active: bool = False
    turns: int = 0
    last_transcript: str | None = None
    last_error: str | None = None

    def begin(self) -> None:
        self.active = True
        self.turns = 0
        self.last_error = None

    def record_turn(self, transcript: str | None) -> None:
        self.turns += 1
        self.last_transcript = transcript

    def fail(self, error: str) -> None:
        self.last_error = str(error)

    def end(self) -> None:
        self.active = False
