"""Voice output abstraction for Webster."""

from __future__ import annotations

from core.voice.config import VoiceConfig


class VoiceSpeaker:
    """Backend-neutral text-to-speech interface."""

    def __init__(self, config: VoiceConfig | None = None) -> None:
        self.config = config or VoiceConfig()
        self._initialized = False
        self._speaking = False

    def initialize(self) -> None:
        if self._initialized:
            return
        self._initialized = True

    def speak(self, text: str) -> bool:
        """Speak text when a concrete TTS backend is attached."""
        if not self._initialized:
            self.initialize()

        text = str(text).strip()
        if not text or not self.config.enabled or not self.config.speak_enabled:
            return False

        # Sprint 36.1 is backend-neutral. pyttsx3 integration belongs to 36.2.
        return False

    def stop(self) -> None:
        self._speaking = False

    def shutdown(self) -> None:
        self.stop()
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def speaking(self) -> bool:
        return self._speaking
