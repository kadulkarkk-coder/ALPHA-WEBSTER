"""Speech input coordinator for Webster Alpha."""

from __future__ import annotations

from core.voice.config import VoiceConfig
from core.voice.stt import ElevenLabsSpeechBackend, MicrophoneSpeechBackend, NullSpeechBackend, SpeechToTextBackend


class VoiceListener:
    """Coordinates microphone/STT backends and wake-word filtering."""

    def __init__(self, config: VoiceConfig | None = None, backend: SpeechToTextBackend | None = None) -> None:
        self.config = config or VoiceConfig()
        self._backend = backend or self._build_backend()
        self._initialized = False
        self._listening = False
        self._error: str | None = None
        self._wake_word_detected = False

    def _build_backend(self) -> SpeechToTextBackend:
        if self.config.input_backend == "elevenlabs":
            return ElevenLabsSpeechBackend(self.config)
        if self.config.input_backend == "speech_recognition":
            return MicrophoneSpeechBackend()
        return NullSpeechBackend()

    def initialize(self) -> None:
        if self._initialized:
            return
        self._error = None
        if not self.config.enabled or not self.config.listen_enabled:
            self._backend = NullSpeechBackend()
        try:
            self._backend.initialize()
            if hasattr(self._backend, "configure_vad") and self.config.vad_enabled:
                self._backend.configure_vad(self.config.vad_energy_threshold, self.config.vad_pause_threshold)
        except Exception as error:
            self._error = str(error)
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            self.initialize()
        if self.config.enabled and self.config.listen_enabled:
            self._listening = True

    def stop(self) -> None:
        try:
            self._backend.stop()
        except Exception as error:
            self._error = str(error)
        finally:
            self._listening = False

    def listen(self, ignore_wake_word: bool = False) -> str | None:
        """Wait for voice activity and return a command when accepted."""
        if not self._initialized:
            self.initialize()
        if not self.config.enabled or not self.config.listen_enabled or not self._backend.available:
            return None

        try:
            self._listening = True
            timeout = self.config.input_timeout
            if self.config.wake_word_enabled and not ignore_wake_word:
                timeout = self.config.wake_word_timeout

            text = self._backend.listen(timeout=timeout, phrase_timeout=self.config.phrase_timeout)
            if not text:
                self._wake_word_detected = False
                return None

            text = text.strip()
            if ignore_wake_word or not self.config.wake_word_enabled:
                self._wake_word_detected = True
                return text

            command = self._extract_wake_command(text)
            if command is None:
                self._wake_word_detected = False
                return None

            self._wake_word_detected = True
            return command if command else None
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
        prefix = wake + " "
        if normalized.startswith(prefix):
            return text[len(wake):].strip()
        return None

    def set_speaker_active(self, active: bool, allow_barge_in: bool = False) -> None:
        setter = getattr(self._backend, "set_speaking", None)
        if callable(setter):
            setter(active, allow_barge_in)

    def shutdown(self) -> None:
        self.stop()
        try:
            self._backend.shutdown()
        except Exception as error:
            self._error = str(error)
        finally:
            self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def listening(self) -> bool:
        return self._listening

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
    def error(self) -> str | None:
        return self._error or getattr(self._backend, "error", None)
