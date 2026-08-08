"""Speech-to-text backends for Webster Alpha."""

from __future__ import annotations

from abc import ABC, abstractmethod


class SpeechToTextBackend(ABC):
    """Contract implemented by concrete speech-recognition backends."""

    name = "unknown"

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the backend."""
        raise NotImplementedError

    @abstractmethod
    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        """Capture and recognize one utterance."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Stop active recognition."""
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """Release backend resources."""
        raise NotImplementedError

    @property
    @abstractmethod
    def available(self) -> bool:
        """Whether this backend is ready to recognize speech."""
        raise NotImplementedError


class NullSpeechBackend(SpeechToTextBackend):
    """Safe fallback used when no real STT backend is available."""

    name = "none"

    def initialize(self) -> None:
        return

    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        return None

    def stop(self) -> None:
        return

    def shutdown(self) -> None:
        return

    @property
    def available(self) -> bool:
        return False


class MicrophoneSpeechBackend(SpeechToTextBackend):
    """Optional microphone backend using SpeechRecognition.

    The dependency is imported lazily so the voice subsystem remains
    optional and Webster can start without microphone support.
    """

    name = "speech_recognition"

    def __init__(self) -> None:
        self._recognizer = None
        self._microphone = None
        self._available = False
        self._listening = False
        self._error: str | None = None

    def initialize(self) -> None:
        if self._available:
            return

        try:
            import speech_recognition as sr

            self._recognizer = sr.Recognizer()
            self._microphone = sr.Microphone()
            self._available = True
            self._error = None
        except Exception as error:
            self._recognizer = None
            self._microphone = None
            self._available = False
            self._error = str(error)

    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        if not self._available:
            self.initialize()

        if self._recognizer is None or self._microphone is None:
            return None

        try:
            with self._microphone as source:
                self._recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5,
                )
                self._listening = True
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_timeout,
                )

            text = self._recognizer.recognize_google(audio)
            return text.strip() or None
        except Exception as error:
            self._error = str(error)
            return None
        finally:
            self._listening = False

    def stop(self) -> None:
        self._listening = False

    def shutdown(self) -> None:
        self.stop()
        self._recognizer = None
        self._microphone = None
        self._available = False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def listening(self) -> bool:
        return self._listening

    @property
    def error(self) -> str | None:
        return self._error
