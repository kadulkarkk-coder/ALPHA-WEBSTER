"""Configuration for the Webster voice subsystem."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VoiceConfig:
    """Runtime-independent voice settings."""

    enabled: bool = True
    listen_enabled: bool = True
    speak_enabled: bool = True
    language: str = "en-US"
    rate: int = 175
    volume: float = 1.0
    input_timeout: float = 5.0
    phrase_timeout: float = 2.0

    def __post_init__(self) -> None:
        self.rate = max(50, min(self.rate, 400))
        self.volume = max(0.0, min(self.volume, 1.0))
        self.input_timeout = max(0.1, self.input_timeout)
        self.phrase_timeout = max(0.1, self.phrase_timeout)
