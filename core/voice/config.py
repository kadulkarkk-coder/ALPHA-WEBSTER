"""Configuration for the free, local Webster voice subsystem."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VoiceConfig:
    enabled: bool = True
    listen_enabled: bool = True
    speak_enabled: bool = True
    language: str = "en"
    rate: int = 175
    volume: float = 1.0

    # Fully local backends. No PyAudio, API key, or cloud service is required.
    input_backend: str = "faster_whisper"
    output_backend: str = "pyttsx3"
    whisper_model: str = "tiny.en"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    sample_rate: int = 16_000
    channels: int = 1
    block_ms: int = 30
    max_phrase_seconds: float = 12.0
    input_timeout: float = 5.0
    phrase_timeout: float = 2.0

    # Hands-free controls.
    wake_word_enabled: bool = True
    wake_word: str = "webster"
    wake_word_timeout: float = 4.0
    vad_enabled: bool = True
    vad_energy_threshold: float = 0.015
    vad_pause_threshold: float = 0.8
    barge_in_enabled: bool = True
    barge_in_timeout: float = 0.8

    def __post_init__(self) -> None:
        self.rate = max(50, min(int(self.rate), 400))
        self.volume = max(0.0, min(float(self.volume), 1.0))
        self.input_timeout = max(0.1, float(self.input_timeout))
        self.phrase_timeout = max(0.1, float(self.phrase_timeout))
        self.sample_rate = max(8000, int(self.sample_rate))
        self.channels = max(1, int(self.channels))
        self.block_ms = max(10, int(self.block_ms))
        self.max_phrase_seconds = max(1.0, float(self.max_phrase_seconds))
        self.wake_word = self.wake_word.strip().lower() or "webster"
        self.wake_word_timeout = max(0.5, float(self.wake_word_timeout))
        self.vad_energy_threshold = max(0.001, float(self.vad_energy_threshold))
        self.vad_pause_threshold = max(0.2, float(self.vad_pause_threshold))
        self.barge_in_timeout = max(0.1, float(self.barge_in_timeout))
        self.input_backend = self.input_backend.strip().lower() or "faster_whisper"
        self.output_backend = self.output_backend.strip().lower() or "pyttsx3"
        self.whisper_model = self.whisper_model.strip() or "tiny.en"
        self.whisper_device = self.whisper_device.strip().lower() or "cpu"
        self.whisper_compute_type = self.whisper_compute_type.strip().lower() or "int8"
