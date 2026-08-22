"""High-level voice controller for WEBSTER."""
from __future__ import annotations

from collections.abc import Callable

from core.voice.engine import VoiceEngine
from core.voice.events import VoiceEvent, VoiceEventType
from core.voice.session import VoiceSession


class VoiceController:
    """Coordinates listening, wake-word handling, speech output and session state."""

    def __init__(self, engine: VoiceEngine | None = None) -> None:
        self.engine = engine or VoiceEngine()
        self.session = VoiceSession()
        self._listeners: list[Callable[[VoiceEvent], None]] = []

    def subscribe(self, callback: Callable[[VoiceEvent], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def _emit(self, event: VoiceEvent) -> None:
        for callback in tuple(self._listeners):
            try:
                callback(event)
            except Exception:
                continue

    def initialize(self) -> None:
        self.engine.initialize()

    def start_session(self) -> None:
        self.initialize()
        self.session.begin()
        self.engine.begin_conversation()
        self.engine.start()

    def listen_turn(self, ignore_wake_word: bool = True) -> str | None:
        self.initialize()
        self._emit(VoiceEvent(VoiceEventType.LISTENING_STARTED))
        try:
            text = self.engine.listen(ignore_wake_word=ignore_wake_word)
            if text:
                self.session.record_turn(text)
                self._emit(VoiceEvent(VoiceEventType.SPEECH_DETECTED, text=text))
                self._emit(VoiceEvent(VoiceEventType.TRANSCRIPT_READY, text=text))
            return text
        except Exception as exc:
            self.session.fail(str(exc))
            self._emit(VoiceEvent(VoiceEventType.ERROR, error=str(exc)))
            return None

    def speak(self, text: str) -> bool:
        self.initialize()
        self._emit(VoiceEvent(VoiceEventType.SPEAKING_STARTED, text=text))
        try:
            ok = self.engine.speak(text)
            if ok:
                self._emit(VoiceEvent(VoiceEventType.SPEAKING_FINISHED, text=text))
            return ok
        except Exception as exc:
            self.session.fail(str(exc))
            self._emit(VoiceEvent(VoiceEventType.ERROR, error=str(exc)))
            return False

    def stop_session(self) -> None:
        self.engine.end_conversation()
        self.engine.stop()
        self.session.end()

    def health(self) -> dict:
        return {"session": self.session.__dict__ if hasattr(self.session, "__dict__") else {"active": self.session.active, "turns": self.session.turns, "last_transcript": self.session.last_transcript, "last_error": self.session.last_error}, "engine": self.engine.health()}

    def shutdown(self) -> None:
        self.session.end()
        self.engine.shutdown()
