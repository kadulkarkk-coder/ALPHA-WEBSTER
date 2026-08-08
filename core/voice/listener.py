"""Speech input coordinator for Webster Alpha."""

from __future__ import annotations

from core.voice.config import VoiceConfig
from core.voice.stt import MicrophoneSpeechBackend, NullSpeechBackend, SpeechToTextBackend


class VoiceListener:
    """Coordinates microphone/STT backends without coupling Webster to one."""

    def __init__(
        self,
        config: VoiceConfig | None = None,
        backend: SpeechToTextBackend | None = None,
    ) -> None:
        self.config = config or VoiceConfig()
        self._backend = backend or MicrophoneSpeechBackend()
        self._initialized = False
        self._listening = False
        self._error: str | None = None

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
        if not self.config.enabled or not self.config.listen_enabled:
            return
        self._listening = True

    def stop(self) -> None:
        try:
            self._backend.stop()
        except Exception as error:
            self._error = str(error)
        finally:
            self._listening = False

    def listen(self) -> str | None:
        if not self._initialized:
            self.initialize()

        if not self.config.enabled or not self.config.listen_enabled:
            return None
        if not self._backend.available:
            return None

        try:
            self._listening = True
            result = self._backend.listen(
                timeout=self.config.input_timeout,
                phrase_timeout=self.config.phrase_timeout,
            )
            return result.strip() if result else None
        except Exception as error:
            self._error = str(error)
            return None
        finally:
            self._listening = False

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
    def error(self) -> str | None:
        return self._error or getattr(self._backend, "error", None)
