"""Core voice conversation pipeline for Webster Alpha."""
from __future__ import annotations

import re
from threading import Event, Thread

from core.voice.config import VoiceConfig
from core.voice.listener import VoiceListener
from core.voice.speaker import VoiceSpeaker
from core.voice.stt import SpeechToTextBackend


class VoiceEngine:
    """Coordinates natural turn-taking, wake-word follow-up and barge-in."""

    _SENTENCE_RE = re.compile(r".+?(?:[.!?]+(?=\s|$)|$)", re.DOTALL)

    def __init__(self, listener: VoiceListener | None = None, speaker: VoiceSpeaker | None = None, config: VoiceConfig | None = None, stt_backend: SpeechToTextBackend | None = None) -> None:
        self.config = config or VoiceConfig()
        self.listener = listener or VoiceListener(config=self.config, backend=stt_backend)
        self.speaker = speaker or VoiceSpeaker(self.config)
        self._initialized = False
        self._sentence_barge_ready = False
        self._sentences_spoken = 0
        self._barge_stop = Event()
        self._barge_thread: Thread | None = None
        self._conversation_active = False
        self._turns = 0
        self._last_interrupted = False

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
        self._stop_barge_monitor()
        self.listener.stop()
        self.speaker.stop()
        self._sentence_barge_ready = False
        self._conversation_active = False
        self.listener.set_speaker_active(False, False)

    def listen(self, ignore_wake_word: bool = False) -> str | None:
        if not self._initialized:
            self.initialize()
        return self.listener.listen(ignore_wake_word=ignore_wake_word)

    def listen_turn(self) -> str | None:
        """Listen naturally after Webster has already established a conversation.

        The wake word is not required during the short active-conversation
        window; after the window expires the normal listener requires wake-up
        again. This makes follow-up questions feel conversational without
        leaving Webster permanently attentive to unrelated speech.
        """
        self._conversation_active = True
        return self.listen(ignore_wake_word=True)

    @classmethod
    def _split_sentences(cls, text: str) -> list[str]:
        parts = [part.strip() for part in cls._SENTENCE_RE.findall(text) if part.strip()]
        return parts or [text.strip()]

    def _stop_barge_monitor(self) -> None:
        self._barge_stop.set()
        thread = self._barge_thread
        self._barge_thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=0.35)

    def _start_barge_monitor(self) -> None:
        method = getattr(self.listener, "listen_for_barge_in", None)
        if not callable(method) or self._barge_thread is not None:
            return
        self._barge_stop.clear()

        def monitor() -> None:
            try:
                if method(self._barge_stop):
                    self._last_interrupted = True
                    self.speaker.stop()
            except Exception:
                pass

        self._barge_thread = Thread(target=monitor, name="WebsterBargeIn", daemon=True)
        self._barge_thread.start()

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()
        if not self.config.speak_enabled or not text.strip():
            return False

        sentences = self._split_sentences(text)
        self._sentence_barge_ready = False
        self._sentences_spoken = 0
        self._last_interrupted = False
        success = True

        try:
            for index, sentence in enumerate(sentences):
                allow_barge = self.config.barge_in_enabled and index > 0 and self._sentence_barge_ready
                self.listener.set_speaker_active(True, allow_barge)
                if allow_barge:
                    self._start_barge_monitor()

                if not self.speaker.speak(sentence):
                    success = False
                    break

                self._stop_barge_monitor()
                if self._last_interrupted:
                    success = False
                    break

                self._sentences_spoken += 1
                if self._sentences_spoken >= 1:
                    self._sentence_barge_ready = True

            return success
        finally:
            self._stop_barge_monitor()
            self._sentence_barge_ready = False
            self.listener.set_speaker_active(False, False)

    def begin_conversation(self) -> None:
        self._conversation_active = True
        self._turns = 0

    def end_conversation(self) -> None:
        self._conversation_active = False
        self._turns = 0
        self._sentence_barge_ready = False

    @property
    def conversation_active(self) -> bool:
        return self._conversation_active

    @property
    def turns(self) -> int:
        return self._turns

    @property
    def sentence_barge_ready(self) -> bool:
        return self._sentence_barge_ready

    @property
    def sentences_spoken(self) -> int:
        return self._sentences_spoken

    @property
    def last_interrupted(self) -> bool:
        return self._last_interrupted

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
            "conversation_active": self._conversation_active,
            "turns": self._turns,
            "barge_in_enabled": self.config.barge_in_enabled,
            "sentence_barge_ready": self._sentence_barge_ready,
            "sentences_spoken": self._sentences_spoken,
            "last_interrupted": self._last_interrupted,
            "wake_word_enabled": self.config.wake_word_enabled,
            "wake_word": self.config.wake_word,
            "wake_word_detected": self.listener.wake_word_detected,
            "wake_word_score": self.listener.wake_word_score,
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
