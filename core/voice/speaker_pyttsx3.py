"""Optional pyttsx3 backend for Webster voice output."""

from __future__ import annotations

from core.voice.config import VoiceConfig


class Pyttsx3Speaker:
    """Offline Windows-friendly TTS backend.

    This backend is optional. Importing this module does not require
    pyttsx3; the dependency is loaded only during initialization.
    """

    def __init__(self, config: VoiceConfig | None = None) -> None:
        self.config = config or VoiceConfig()
        self._engine = None
        self._error: str | None = None
        self._speaking = False

    def initialize(self) -> None:
        if self._engine is not None:
            return
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.config.rate)
            self._engine.setProperty("volume", self.config.volume)
            self._error = None
        except Exception as error:
            self._engine = None
            self._error = str(error)

    def speak(self, text: str) -> bool:
        self.initialize()
        if self._engine is None or not text.strip():
            return False
        try:
            self._speaking = True
            self._engine.say(text.strip())
            self._engine.runAndWait()
            return True
        except Exception as error:
            self._error = str(error)
            return False
        finally:
            self._speaking = False

    def stop(self) -> None:
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass
        self._speaking = False

    def shutdown(self) -> None:
        self.stop()
        self._engine = None

    @property
    def available(self) -> bool:
        return self._engine is not None

    @property
    def speaking(self) -> bool:
        return self._speaking

    @property
    def error(self) -> str | None:
        return self._error
