"""High-level voice manager for Webster."""

from __future__ import annotations

from collections.abc import Callable

from core.voice.config import VoiceConfig
from core.voice.engine import VoiceEngine


class VoiceManager:
    """Public lifecycle and voice-conversation API for Webster."""

    def __init__(
        self,
        engine: VoiceEngine | None = None,
        config: VoiceConfig | None = None,
    ) -> None:
        self.config = config or VoiceConfig()
        self.engine = engine or VoiceEngine(config=self.config)
        self._initialized = False
        self._running = False
        self._processor: Callable[[str], str] | None = None
        self._last_input: str | None = None
        self._last_response: str | None = None
        self._last_error: str | None = None

    def initialize(self) -> None:
        if self._initialized:
            return
        self.engine.initialize()
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            self.initialize()
        if self._running:
            return
        self.engine.start()
        self._running = True

    def stop(self) -> None:
        if not self._running:
            return
        self.engine.stop()
        self._running = False

    def shutdown(self) -> None:
        if not self._initialized:
            return
        self.stop()
        self.engine.shutdown()
        self._initialized = False

    def listen(self) -> str | None:
        if not self._initialized:
            self.initialize()
        text = self.engine.listen()
        self._last_input = text
        return text

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()
        return self.engine.speak(text)

    def set_processor(self, processor: Callable[[str], str] | None) -> None:
        """Set the AI callback used to turn speech into a response."""
        self._processor = processor

    def converse_once(self) -> str | None:
        """Listen once, send the transcript to AI, and speak the reply."""
        if not self._initialized:
            self.initialize()

        if self._processor is None:
            self._last_error = "No voice conversation processor is configured."
            return None

        text = self.listen()
        if not text:
            return None

        try:
            response = str(self._processor(text)).strip()
            if not response:
                self._last_error = "AI returned an empty response."
                return None

            self._last_response = response
            self.speak(response)
            self._last_error = None
            return response
        except Exception as error:
            self._last_error = str(error)
            return None

    def health(self) -> dict:
        return {
            "initialized": self._initialized,
            "running": self._running,
            "processor_configured": self._processor is not None,
            "last_input": self._last_input,
            "last_response": self._last_response,
            "last_error": self._last_error,
            **self.engine.health(),
        }

    @property
    def ready(self) -> bool:
        return self._initialized and self.engine is not None
