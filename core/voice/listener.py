"""Voice input abstraction for Webster."""

from __future__ import annotations

from core.voice.config import VoiceConfig


class VoiceListener:
    """Backend-neutral speech input interface.

    Sprint 36.1 intentionally does not require a microphone or STT package.
    Concrete speech-recognition backends can be attached later.
    """

    def __init__(self, config: VoiceConfig | None = None) -> None:
        self.config = config or VoiceConfig()
        self._initialized = False
        self._listening = False

    def initialize(self) -> None:
        if self._initialized:
            return
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            self.initialize()
        if not self.config.enabled or not self.config.listen_enabled:
            return
        self._listening = True

    def stop(self) -> None:
        self._listening = False

    def listen(self) -> str | None:
        """Return recognized text when a backend is installed.

        The base implementation deliberately returns ``None`` rather than
        pretending that speech was recognized.
        """
        if not self._initialized:
            self.initialize()
        return None

    def shutdown(self) -> None:
        self.stop()
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def listening(self) -> bool:
        return self._listening
