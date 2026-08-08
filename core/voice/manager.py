"""High-level voice manager for Webster."""

from __future__ import annotations

from core.voice.config import VoiceConfig
from core.voice.engine import VoiceEngine


class VoiceManager:
    """Public lifecycle and access API for Webster voice."""

    def __init__(
        self,
        engine: VoiceEngine | None = None,
        config: VoiceConfig | None = None,
    ) -> None:
        self.config = config or VoiceConfig()
        self.engine = engine or VoiceEngine(config=self.config)
        self._initialized = False
        self._running = False

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
        return self.engine.listen()

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()
        return self.engine.speak(text)

    def health(self) -> dict:
        return {
            "initialized": self._initialized,
            "running": self._running,
            **self.engine.health(),
        }

    @property
    def ready(self) -> bool:
        return self._initialized and self.engine is not None
