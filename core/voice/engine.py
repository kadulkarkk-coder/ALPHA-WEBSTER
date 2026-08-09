"""Core voice pipeline for Webster Alpha."""

from __future__ import annotations

from core.voice.config import VoiceConfig
from core.voice.listener import VoiceListener
from core.voice.speaker import VoiceSpeaker
from core.voice.stt import SpeechToTextBackend


class VoiceEngine:
    """Coordinates local STT, wake-word filtering and local TTS."""

    def __init__(
        self,
        listener: VoiceListener | None = None,
        speaker: VoiceSpeaker | None = None,
        config: VoiceConfig | None = None,
        stt_backend: SpeechToTextBackend | None = None,
    ) -> None:
        self.config = config or VoiceConfig()
        self.listener = listener or VoiceListener(config=self.config, backend=stt_backend)
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
        self.listener.set_speaker_active(False, False)

    def listen(self, ignore_wake_word: bool = False) -> str | None:
        if not self._initialized:
            self.initialize()
        return self.listener.listen(ignore_wake_word=ignore_wake_word)

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()
        if not self.config.speak_enabled or not text.strip():
            return False

        # The stable default is full-duplex-safe: don't listen through the
        # laptop speakers while TTS is playing. Barge-in remains an explicit
        # configuration switch for a later microphone-tested mode.
        self.listener.set_speaker_active(True, self.config.barge_in_enabled)
        try:
            return self.speaker.speak(text)
        finally:
            self.listener.set_speaker_active(False, False)

    def devices(self) -> list[dict]:
        return self.listener.devices()

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
            "barge_in_enabled": self.config.barge_in_enabled,
            "wake_word_enabled": self.config.wake_word_enabled,
            "wake_word": self.config.wake_word,
            "wake_word_detected": self.listener.wake_word_detected,
            "last_heard": self.listener.last_heard,
            "vad_enabled": self.config.vad_enabled,
            "input_backend": self.listener.backend_name,
            "input_available": self.listener.available,
            "input_error": self.listener.error,
            "input_device": self.listener.device_name,
            "input_rms": self.listener.last_rms,
            "input_threshold": self.listener.last_threshold,
            "output_backend": self.speaker.__class__.__name__,
            "output_available": self.speaker.available,
            "output_error": self.speaker.error,
        }
