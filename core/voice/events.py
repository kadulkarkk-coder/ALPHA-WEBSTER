"""Typed events emitted by the WEBSTER voice subsystem."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VoiceEventType(str, Enum):
    LISTENING_STARTED = "listening_started"
    SPEECH_DETECTED = "speech_detected"
    TRANSCRIPT_READY = "transcript_ready"
    WAKE_WORD_DETECTED = "wake_word_detected"
    SPEAKING_STARTED = "speaking_started"
    SPEAKING_FINISHED = "speaking_finished"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class VoiceEvent:
    type: VoiceEventType
    text: str | None = None
    confidence: float = 0.0
    error: str | None = None
