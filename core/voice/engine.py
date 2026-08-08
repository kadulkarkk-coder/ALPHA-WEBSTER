"""Core coordination layer for Webster voice."""

from __future__ import annotations

from core.voice.config import VoiceConfig
from core.voice.listener import VoiceListener
from core.voice.speaker import VoiceSpeaker
from core.voice.stt import SpeechToTextBackend


class VoiceEngine:
    """Coordinates speech input, voice activity, and text-to-speech output."""

    def __init__(
        self,
        listener: VoiceListener | None = None,
        speaker: VoiceSpeaker | None = None,
        config: VoiceConfig | None = None,
        stt_backend: SpeechToTextBackend | None = None,
    ) -> None:
        self.config = config or VoiceConfig()
        self.listener = listener or VoiceListener(
            config=self.config,
            backend=stt_backend,
        )
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
        self._set_input_suppressed(False)

    def listen(self) -> str | None:
        if not self._initialized:
            self.initialize()
        if self.speaker.speaking:
            return None
        return self.listener.listen()

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()

        # Prevent Webster from transcribing its own TTS output.
        self._set_input_suppressed(True)
        try:
            return self.speaker.speak(text)
        finally:
            self._set_input_suppressed(False)

    def _set_input_suppressed(self, suppressed: bool) -> None:
        backend = getattr(self.listener, "_backend", None)
        setter = getattr(backend, "set_speaking", None)
        if callable(setter):
            setter(suppressed)

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
            "input_backend": self.listener.backend_name,
            "input_available": self.listener.available,
            "input_error": self.listener.error,
            "output_backend": self.speaker.__class__.__name__,
            "output_available": self.speaker.available,
            "output_error": self.speaker.error,
        }
