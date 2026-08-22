"""Voice-to-AI pipeline contract."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.voice.controller import VoiceController


class VoiceResponder(Protocol):
    def __call__(self, text: str) -> str: ...


@dataclass(slots=True)
class VoicePipeline:
    """Connects voice input/output to an injected AI responder.

    The responder is deliberately injected so the voice layer remains independent
    from a particular model provider or UI implementation.
    """

    controller: VoiceController
    responder: VoiceResponder

    def run_turn(self) -> tuple[str | None, str | None]:
        transcript = self.controller.listen_turn(ignore_wake_word=True)
        if not transcript:
            return None, None
        response = self.responder(transcript)
        if response:
            self.controller.speak(response)
        return transcript, response
