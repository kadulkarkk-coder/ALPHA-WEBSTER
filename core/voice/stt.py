"""Speech-to-text and voice-activity backends for Webster Alpha."""

from __future__ import annotations

from abc import ABC, abstractmethod


class SpeechToTextBackend(ABC):
    """Contract implemented by concrete speech-recognition backends."""

    name = "unknown"

    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError


class NullSpeechBackend(SpeechToTextBackend):
    """Safe fallback when no microphone STT backend is installed."""

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
    """SpeechRecognition backend with microphone voice-activity detection."""

    name = "speech_recognition"

    def __init__(self) -> None:
        self._recognizer = None
        self._microphone = None
        self._available = False
        self._listening = False
        self._speaking = False
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
        """Wait for voice activity, capture the utterance, then stop at silence."""
        if not self._available:
            self.initialize()

        if self._recognizer is None or self._microphone is None or self._speaking:
            return None

        try:
            with self._microphone as source:
                self._listening = True

                # Calibrate only once per microphone session when possible.
                self._recognizer.adjust_for_ambient_noise(source, duration=0.25)

                # listen() waits for speech energy and ends when speech stops.
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_timeout,
                )

            text = self._recognizer.recognize_google(audio)
            return text.strip() or None
        except Exception as error:
            # Timeout/no speech is normal in hands-free mode, not a fatal error.
            if error.__class__.__name__ == "WaitTimeoutError":
                return None
            self._error = str(error)
            return None
        finally:
            self._listening = False

    def set_speaking(self, speaking: bool) -> None:
        """Temporarily disable microphone capture while Webster speaks."""
        self._speaking = speaking
        if speaking:
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
        return self._available and not self._speaking

    @property
    def listening(self) -> bool:
        return self._listening

    @property
    def speaking(self) -> bool:
        return self._speaking

    @property
    def error(self) -> str | None:
        return self._error
