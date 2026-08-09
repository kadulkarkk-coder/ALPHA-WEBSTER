"""Core voice pipeline for Webster Alpha."""

from __future__ import annotations

import re

from core.voice.config import VoiceConfig
from core.voice.listener import VoiceListener
from core.voice.speaker import VoiceSpeaker
from core.voice.stt import SpeechToTextBackend


class VoiceEngine:
    """Coordinates local STT, wake-word filtering and local TTS.

    Barge-in is deliberately sentence-gated: microphone interruption is not
    enabled until Webster has completed at least the first sentence of a
    response. This prevents immediate noise, coughs, or accidental input from
    cutting off the beginning of a response.
    """

    _SENTENCE_RE = re.compile(r".+?(?:[.!?]+(?=\s|$)|$)", re.DOTALL)

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
        self._sentence_barge_ready = False
        self._sentences_spoken = 0

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
        self._sentence_barge_ready = False
        self._sentences_spoken = 0
        self.listener.set_speaker_active(False, False)

    def listen(self, ignore_wake_word: bool = False) -> str | None:
        if not self._initialized:
            self.initialize()
        return self.listener.listen(ignore_wake_word=ignore_wake_word)

    @classmethod
    def _split_sentences(cls, text: str) -> list[str]:
        parts = [part.strip() for part in cls._SENTENCE_RE.findall(text) if part.strip()]
        return parts or [text.strip()]

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()
        if not self.config.speak_enabled or not text.strip():
            return False

        sentences = self._split_sentences(text)
        self._sentence_barge_ready = False
        self._sentences_spoken = 0
        success = True

        try:
            for index, sentence in enumerate(sentences):
                # The first sentence is protected. Barge-in becomes eligible
                # only after this sentence has actually returned from TTS.
                allow_barge = (
                    self.config.barge_in_enabled
                    and self._sentence_barge_ready
                    and index > 0
                )
                self.listener.set_speaker_active(True, allow_barge)
                if not self.speaker.speak(sentence):
                    success = False
                    break

                self._sentences_spoken += 1
                if self._sentences_spoken >= 1:
                    self._sentence_barge_ready = True

            return success
        finally:
            self.listener.set_speaker_active(False, False)

    @property
    def sentence_barge_ready(self) -> bool:
        return self._sentence_barge_ready

    @property
    def sentences_spoken(self) -> int:
        return self._sentences_spoken

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
            "sentence_barge_ready": self._sentence_barge_ready,
            "sentences_spoken": self._sentences_spoken,
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
