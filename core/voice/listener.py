"""Speech input coordinator for Webster Alpha."""

from __future__ import annotations

from difflib import SequenceMatcher

from core.voice.config import VoiceConfig
from core.voice.stt import FasterWhisperSpeechBackend, NullSpeechBackend, SpeechToTextBackend


class VoiceListener:
    """Owns the speech-to-text input path and wake-word policy."""

    def __init__(self, config: VoiceConfig | None = None, backend: SpeechToTextBackend | None = None) -> None:
        self.config = config or VoiceConfig()
        self._backend = backend or self._build_backend()
        self._initialized = False
        self._listening = False
        self._error: str | None = None
        self._wake_word_detected = False
        self._last_heard: str | None = None

    def _build_backend(self) -> SpeechToTextBackend:
        if self.config.input_backend in {"sounddevice_whisper", "faster_whisper", "microphone"}:
            return FasterWhisperSpeechBackend(self.config)
        return NullSpeechBackend()

    def initialize(self) -> None:
        if self._initialized:
            return
        self._error = None
        if not self.config.enabled or not self.config.listen_enabled:
            self._backend = NullSpeechBackend()
        try:
            self._backend.initialize()
        except Exception as error:
            self._error = str(error)
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            self.initialize()
        self._listening = False

    def stop(self) -> None:
        try:
            self._backend.stop()
        except Exception as error:
            self._error = str(error)
        finally:
            self._listening = False

    def listen(self, ignore_wake_word: bool = False) -> str | None:
        """Record one utterance and return a command if the wake policy allows it."""
        if not self._initialized:
            self.initialize()
        if not self.config.enabled or not self.config.listen_enabled or not self._backend.available:
            return None

        try:
            self._listening = True
            text = self._backend.listen(
                timeout=self.config.listen_timeout,
                phrase_timeout=self.config.max_phrase_seconds,
            )
            if not text:
                self._wake_word_detected = False
                return None

            text = " ".join(text.strip().split())
            if not text:
                return None
            self._last_heard = text

            if ignore_wake_word or not self.config.wake_word_enabled:
                self._wake_word_detected = True
                return text

            command = self._extract_wake_command(text)
            if command is None:
                self._wake_word_detected = False
                return None

            self._wake_word_detected = True
            if command:
                return command

            # A wake-word-only utterance activates Webster and opens a second
            # short listening window for the actual command.
            follow_up = self._backend.listen(
                timeout=6.0,
                phrase_timeout=self.config.max_phrase_seconds,
            )
            if follow_up:
                self._last_heard = " ".join(follow_up.strip().split())
                return self._last_heard or None
            return None
        except Exception as error:
            self._error = str(error)
            return None
        finally:
            self._listening = False

    def _extract_wake_command(self, text: str) -> str | None:
        normalized = " ".join(text.lower().split())
        wake = self.config.wake_word
        if normalized == wake:
            return ""
        if normalized.startswith(wake + " "):
            return text[len(wake):].strip()

        words = normalized.split(maxsplit=1)
        if not words:
            return None
        similarity = SequenceMatcher(None, words[0], wake).ratio()
        if similarity >= self.config.wake_word_similarity:
            return text.split(maxsplit=1)[1].strip() if len(words) > 1 else ""
        return None

    def set_speaker_active(self, active: bool, allow_barge_in: bool = False) -> None:
        setter = getattr(self._backend, "set_speaking", None)
        if callable(setter):
            setter(active, allow_barge_in)

    def devices(self) -> list[dict]:
        method = getattr(self._backend, "devices", None)
        if callable(method):
            return method()
        return []

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def listening(self) -> bool:
        return self._listening or bool(getattr(self._backend, "listening", False))

    @property
    def available(self) -> bool:
        return self._backend.available

    @property
    def backend_name(self) -> str:
        return self._backend.name

    @property
    def wake_word_detected(self) -> bool:
        return self._wake_word_detected

    @property
    def last_heard(self) -> str | None:
        return self._last_heard

    @property
    def error(self) -> str | None:
        return self._error or getattr(self._backend, "error", None)

    @property
    def device_name(self) -> str | None:
        return getattr(self._backend, "device_name", None)

    @property
    def last_rms(self) -> float:
        return float(getattr(self._backend, "last_rms", 0.0))

    @property
    def last_threshold(self) -> float:
        return float(getattr(self._backend, "last_threshold", 0.0))

    def shutdown(self) -> None:
        self.stop()
        try:
            self._backend.shutdown()
        except Exception as error:
            self._error = str(error)
        finally:
            self._initialized = False
