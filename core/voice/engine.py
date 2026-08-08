"""Core coordination layer for Webster voice."""

from __future__ import annotations

from core.voice.config import VoiceConfig
from core.voice.listener import VoiceListener
from core.voice.speaker import VoiceSpeaker


class VoiceEngine:
    """Coordinates voice input and output without owning an STT/TTS backend."""

    def __init__(
        self,
        listener: VoiceListener | None = None,
        speaker: VoiceSpeaker | None = None,
        config: VoiceConfig | None = None,
    ) -> None:
        self.config = config or VoiceConfig()
        self.listener = listener or VoiceListener(self.config)
        self.speaker = speaker or VoiceSpeaker(self.config)
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        self.listener.initialize()
        self.speaker.initialize()
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            self.initialize()
        self.listener.start()

    def stop(self) -> None:
        self.listener.stop()
        self.speaker.stop()

    def listen(self) -> str | None:
        if not self._initialized:
            self.initialize()
        return self.listener.listen()

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()
        return self.speaker.speak(text)

    def shutdown(self) -> None:
        if not self._initialized:
            return
        self.stop()
        self.listener.shutdown()
        self.speaker.shutdown()
        self._initialized = False

    def health(self) -> dict:
        return {
            "initialized": self._initialized,
            "enabled": self.config.enabled,
            "listening": self.listener.listening,
            "speaking": self.speaker.speaking,
            "input_backend": self.listener.__class__.__name__,
            "output_backend": self.speaker.__class__.__name__,
        }
