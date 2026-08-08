"""Speech-to-text backend abstraction for Webster Alpha."""

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
    """Safe fallback used until a real STT backend is installed."""

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
