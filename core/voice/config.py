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

    # Hands-free voice controls.
    wake_word_enabled: bool = True
    wake_word: str = "webster"
    wake_word_timeout: float = 4.0
    vad_enabled: bool = True
    vad_energy_threshold: int = 300
    vad_pause_threshold: float = 0.8
    barge_in_enabled: bool = True
    barge_in_timeout: float = 0.8

    def __post_init__(self) -> None:
        self.rate = max(50, min(self.rate, 400))
        self.volume = max(0.0, min(self.volume, 1.0))
        self.input_timeout = max(0.1, self.input_timeout)
        self.phrase_timeout = max(0.1, self.phrase_timeout)
        self.wake_word = self.wake_word.strip().lower() or "webster"
        self.wake_word_timeout = max(0.5, self.wake_word_timeout)
        self.vad_energy_threshold = max(0, int(self.vad_energy_threshold))
        self.vad_pause_threshold = max(0.1, self.vad_pause_threshold)
        self.barge_in_timeout = max(0.1, self.barge_in_timeout)
