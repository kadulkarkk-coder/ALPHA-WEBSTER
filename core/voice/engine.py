"""Core coordination layer for Webster voice."""

from __future__ import annotations

from threading import Event, Thread

from core.voice.config import VoiceConfig
from core.voice.listener import VoiceListener
from core.voice.speaker import VoiceSpeaker
from core.voice.stt import SpeechToTextBackend


class VoiceEngine:
    """Coordinates speech input, VAD, wake-word handling and TTS output."""

    def __init__(self, listener: VoiceListener | None = None, speaker: VoiceSpeaker | None = None, config: VoiceConfig | None = None, stt_backend: SpeechToTextBackend | None = None) -> None:
        self.config = config or VoiceConfig()
        self.listener = listener or VoiceListener(config=self.config, backend=stt_backend)
        self.speaker = speaker or VoiceSpeaker(self.config)
        self._initialized = False
        self._barge_in_detected = Event()

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
        self._barge_in_detected.set()
        self.listener.set_speaker_active(False, False)

    def listen(self) -> str | None:
        if not self._initialized:
            self.initialize()
        if self.speaker.speaking:
            return None
        return self.listener.listen()

    def speak(self, text: str) -> bool:
        """Speak a response and optionally allow human speech to interrupt it."""
        if not self._initialized:
            self.initialize()
        if not text.strip():
            return False

        if not self.config.barge_in_enabled:
            self.listener.set_speaker_active(True, False)
            try:
                return self.speaker.speak(text)
            finally:
                self.listener.set_speaker_active(False, False)

        self._barge_in_detected.clear()
        self.listener.set_speaker_active(True, True)
        result = [False]

        def speak_worker() -> None:
            result[0] = self.speaker.speak(text)

        worker = Thread(target=speak_worker, name="WebsterTTS", daemon=True)
        worker.start()

        while worker.is_alive() and not self._barge_in_detected.is_set():
            spoken = self.listener.listen(ignore_wake_word=True)
            if spoken:
                self._barge_in_detected.set()
                self.speaker.stop()
                break
            if self._barge_in_detected.wait(self.config.barge_in_timeout):
                break

        worker.join(timeout=1.0)
        self.listener.set_speaker_active(False, False)
        return result[0]

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
            "barge_in_detected": self._barge_in_detected.is_set(),
            "wake_word_enabled": self.config.wake_word_enabled,
            "wake_word": self.config.wake_word,
            "wake_word_detected": self.listener.wake_word_detected,
            "last_heard": self.listener.last_heard,
            "vad_enabled": self.config.vad_enabled,
            "input_backend": self.listener.backend_name,
            "input_available": self.listener.available,
            "input_error": self.listener.error,
            "output_backend": self.speaker.__class__.__name__,
            "output_available": self.speaker.available,
            "output_error": self.speaker.error,
        }
