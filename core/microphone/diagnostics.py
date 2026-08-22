"""Microphone diagnostics helpers."""
from __future__ import annotations

from core.microphone.manager import MicrophoneManager


def microphone_health(manager: MicrophoneManager) -> dict[str, object]:
    """Return UI- and logging-safe microphone health information."""
    snapshot = manager.snapshot()
    return {
        "state": snapshot.state.value,
        "available": snapshot.available,
        "device": snapshot.device.name if snapshot.device else None,
        "device_index": snapshot.device.index if snapshot.device else None,
        "sample_rate": snapshot.sample_rate,
        "channels": snapshot.channels,
        "error": snapshot.error,
        "backend": manager.backend.name,
    }
