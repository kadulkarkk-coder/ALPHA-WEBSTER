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

    # Voice providers. ElevenLabs avoids the PyAudio dependency and provides
    # cloud STT/TTS; the legacy local backend remains available as a fallback.
    input_backend: str = "elevenlabs"
    output_backend: str = "elevenlabs"
    elevenlabs_voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
    elevenlabs_tts_model: str = "eleven_multilingual_v2"
    elevenlabs_stt_model: str = "scribe_v2"

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
        self.input_backend = self.input_backend.strip().lower() or "elevenlabs"
        self.output_backend = self.output_backend.strip().lower() or "elevenlabs"
        self.elevenlabs_voice_id = self.elevenlabs_voice_id.strip()
        self.elevenlabs_tts_model = self.elevenlabs_tts_model.strip() or "eleven_multilingual_v2"
        self.elevenlabs_stt_model = self.elevenlabs_stt_model.strip() or "scribe_v2"
