"""
Webster Alpha

Capability Pack Lifecycle Events
Sprint 30.11
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from typing import Callable


class PackEventType(str, Enum):
    """Lifecycle events emitted by the capability-pack system."""

    REGISTERED = "registered"
    LOAD_STARTED = "load_started"
    LOADED = "loaded"
    LOAD_FAILED = "load_failed"
    UNLOAD_STARTED = "unload_started"
    UNLOADED = "unloaded"
    UNLOAD_FAILED = "unload_failed"
    REMOVED = "removed"


@dataclass(frozen=True, slots=True)
class CapabilityPackEvent:
    """Immutable snapshot of a pack lifecycle event."""

    event_type: PackEventType
    pack_name: str
    timestamp: str
    error: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "event": self.event_type.value,
            "pack": self.pack_name,
            "timestamp": self.timestamp,
            "error": self.error,
        }


PackEventListener = Callable[[CapabilityPackEvent], None]


class CapabilityPackEventBus:
    """Thread-safe event bus for pack lifecycle notifications."""

    def __init__(self) -> None:
        self._listeners: dict[PackEventType, list[PackEventListener]] = {
            event_type: [] for event_type in PackEventType
        }
        self._lock = RLock()

    def subscribe(
        self,
        listener: PackEventListener,
        event_type: PackEventType | None = None,
    ) -> None:
        if not callable(listener):
            raise TypeError("Pack event listener must be callable.")

        with self._lock:
            targets = (
                (event_type,)
                if event_type is not None
                else tuple(PackEventType)
            )
            for target in targets:
                if listener not in self._listeners[target]:
                    self._listeners[target].append(listener)

    def unsubscribe(
        self,
        listener: PackEventListener,
        event_type: PackEventType | None = None,
    ) -> None:
        with self._lock:
            targets = (
                (event_type,)
                if event_type is not None
                else tuple(PackEventType)
            )
            for target in targets:
                if listener in self._listeners[target]:
                    self._listeners[target].remove(listener)

    def emit(
        self,
        event_type: PackEventType,
        pack_name: str,
        error: str | None = None,
    ) -> CapabilityPackEvent:
        event = CapabilityPackEvent(
            event_type=event_type,
            pack_name=str(pack_name),
            timestamp=datetime.now(timezone.utc).isoformat(),
            error=error,
        )

        with self._lock:
            listeners = tuple(self._listeners[event_type])

        for listener in listeners:
            try:
                listener(event)
            except Exception:
                # Observers must never break pack lifecycle operations.
                continue

        return event

    def listener_count(self, event_type: PackEventType | None = None) -> int:
        with self._lock:
            if event_type is not None:
                return len(self._listeners[event_type])
            return sum(len(items) for items in self._listeners.values())

    def clear(self) -> None:
        with self._lock:
            for listeners in self._listeners.values():
                listeners.clear()

    def __repr__(self) -> str:
        return f"CapabilityPackEventBus(listeners={self.listener_count()})"
