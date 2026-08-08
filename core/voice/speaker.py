"""Webster voice output facade."""

from __future__ import annotations

from core.voice.config import VoiceConfig
from core.voice.speaker_pyttsx3 import Pyttsx3Speaker


class VoiceSpeaker:
    """Stable TTS facade backed by the optional pyttsx3 implementation."""

    def __init__(self, config: VoiceConfig | None = None) -> None:
        self.config = config or VoiceConfig()
        self._backend = Pyttsx3Speaker(self.config)
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        self._backend.initialize()
        self._initialized = True

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()

        if not self.config.enabled or not self.config.speak_enabled:
            return False

        return self._backend.speak(str(text))

    def stop(self) -> None:
        self._backend.stop()

    def shutdown(self) -> None:
        if not self._initialized:
            return
        self._backend.shutdown()
        self._initialized = False

    def set_rate(self, rate: int) -> None:
        self.config.rate = max(50, min(int(rate), 400))
        if self._initialized and self._backend.available:
            self._backend.initialize()

    def set_volume(self, volume: float) -> None:
        self.config.volume = max(0.0, min(float(volume), 1.0))
        if self._initialized and self._backend.available:
            self._backend.initialize()

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def speaking(self) -> bool:
        return self._backend.speaking

    @property
    def available(self) -> bool:
        return self._backend.available

    @property
    def error(self) -> str | None:
        return self._backend.error
