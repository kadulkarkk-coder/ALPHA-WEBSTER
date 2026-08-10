"""
Webster Alpha

Capability Pack Event Audit Trail
Sprint 30.13
"""

from __future__ import annotations

from collections import deque
from threading import RLock

from core.capability.packs.events import CapabilityPackEvent, PackEventType


class CapabilityPackAuditTrail:
    """Thread-safe, bounded in-memory history of pack lifecycle events."""

    def __init__(self, max_events: int = 500) -> None:
        if max_events < 1:
            raise ValueError("max_events must be at least 1.")
        self._events: deque[CapabilityPackEvent] = deque(maxlen=max_events)
        self._max_events = max_events
        self._lock = RLock()

    @property
    def max_events(self) -> int:
        return self._max_events

    def record(self, event: CapabilityPackEvent) -> CapabilityPackEvent:
        if not isinstance(event, CapabilityPackEvent):
            raise TypeError("Audit trail accepts CapabilityPackEvent instances only.")
        with self._lock:
            self._events.append(event)
        return event

    def events(
        self,
        *,
        pack_name: str | None = None,
        event_type: PackEventType | None = None,
        limit: int | None = None,
    ) -> tuple[CapabilityPackEvent, ...]:
        if limit is not None and limit < 1:
            return ()

        normalized = pack_name.strip().lower() if pack_name is not None else None
        with self._lock:
            result = tuple(
                event
                for event in self._events
                if (normalized is None or event.pack_name.strip().lower() == normalized)
                and (event_type is None or event.event_type == event_type)
            )

        if limit is not None:
            return result[-limit:]
        return result

    def latest(self, pack_name: str | None = None) -> CapabilityPackEvent | None:
        result = self.events(pack_name=pack_name, limit=1)
        return result[0] if result else None

    def count(self, event_type: PackEventType | None = None) -> int:
        return len(self.events(event_type=event_type))

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def as_dicts(self, limit: int | None = None) -> tuple[dict[str, object], ...]:
        return tuple(event.as_dict() for event in self.events(limit=limit))

    def summary(self) -> dict[str, object]:
        events = self.events()
        counts = {event_type.value: 0 for event_type in PackEventType}
        for event in events:
            counts[event.event_type.value] += 1
        return {
            "total_events": len(events),
            "max_events": self._max_events,
            "event_counts": counts,
        }

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)

    def __repr__(self) -> str:
        return f"CapabilityPackAuditTrail(events={len(self)}, max_events={self._max_events})"
