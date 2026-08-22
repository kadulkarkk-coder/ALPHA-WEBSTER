"""Microphone service data models."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MicrophoneState(str, Enum):
    UNINITIALIZED = "uninitialized"
    READY = "ready"
    CAPTURING = "capturing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass(frozen=True, slots=True)
class MicrophoneDevice:
    """Describes an available input device without exposing backend details."""

    index: int
    name: str
    channels: int = 0
    sample_rate: float = 0.0
    default: bool = False


@dataclass(frozen=True, slots=True)
class MicrophoneSnapshot:
    """Safe diagnostic snapshot of microphone service state."""

    state: MicrophoneState
    available: bool
    device: MicrophoneDevice | None
    error: str | None = None
    sample_rate: float = 0.0
    channels: int = 0
