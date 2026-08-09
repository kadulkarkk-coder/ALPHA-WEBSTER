"""Configuration for Webster's fully local voice subsystem."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VoiceConfig:
    """Stable defaults for Windows laptop voice interaction."""

    enabled: bool = True
    listen_enabled: bool = True
    speak_enabled: bool = True
    language: str = "en"
    rate: int = 175
    volume: float = 1.0

    # Free/local only. No PyAudio, ElevenLabs, or cloud API is required.
    input_backend: str = "sounddevice_whisper"
    output_backend: str = "pyttsx3"
    whisper_model: str = "tiny.en"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    sample_rate: int = 16_000
    channels: int = 1
    block_ms: int = 30
    input_device: int | None = None

    listen_timeout: float = 8.0
    max_phrase_seconds: float = 12.0
    silence_duration: float = 0.85
    pre_roll_seconds: float = 0.25
    start_blocks: int = 2

    vad_enabled: bool = True
    vad_energy_threshold: float = 0.008
    vad_multiplier: float = 2.2

    wake_word_enabled: bool = True
    wake_word: str = "webster"
    wake_word_similarity: float = 0.72

    # Keep barge-in off until the microphone path is verified. It can then be
    # enabled without changing the rest of the voice architecture.
    barge_in_enabled: bool = False
    barge_in_threshold_multiplier: float = 3.0

    def __post_init__(self) -> None:
        self.rate = max(50, min(int(self.rate), 400))
        self.volume = max(0.0, min(float(self.volume), 1.0))
        self.sample_rate = max(8000, int(self.sample_rate))
        self.channels = max(1, int(self.channels))
        self.block_ms = max(10, int(self.block_ms))
        self.listen_timeout = max(1.0, float(self.listen_timeout))
        self.max_phrase_seconds = max(1.0, float(self.max_phrase_seconds))
        self.silence_duration = max(0.25, float(self.silence_duration))
        self.pre_roll_seconds = max(0.0, float(self.pre_roll_seconds))
        self.start_blocks = max(1, int(self.start_blocks))
        self.vad_energy_threshold = max(0.001, float(self.vad_energy_threshold))
        self.vad_multiplier = max(1.1, float(self.vad_multiplier))
        self.wake_word = self.wake_word.strip().lower() or "webster"
        self.wake_word_similarity = max(0.5, min(float(self.wake_word_similarity), 1.0))
        self.barge_in_threshold_multiplier = max(1.1, float(self.barge_in_threshold_multiplier))
        self.input_backend = self.input_backend.strip().lower() or "sounddevice_whisper"
        self.output_backend = self.output_backend.strip().lower() or "pyttsx3"
        self.whisper_model = self.whisper_model.strip() or "tiny.en"
        self.whisper_device = self.whisper_device.strip().lower() or "cpu"
        self.whisper_compute_type = self.whisper_compute_type.strip().lower() or "int8"
