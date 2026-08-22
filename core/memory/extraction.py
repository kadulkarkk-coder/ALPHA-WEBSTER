"""Deterministic memory extraction helpers for WEBSTER."""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.memory.types import MemoryType


@dataclass(frozen=True, slots=True)
class MemoryCandidate:
    """A candidate memory identified from user text."""

    memory_type: MemoryType
    topic: str
    value: str
    confidence: float
    reason: str


class MemoryExtractor:
    """Extracts conservative, explicit memories from natural language."""

    _preference = re.compile(r"\b(?:i|my)\s+(?:prefer|like|love|use|want)\s+(?P<value>.+)", re.I)
    _remember = re.compile(r"\bremember(?: that)?\s+(?P<value>.+)", re.I)
    _name = re.compile(r"\bmy name is\s+(?P<value>[A-Za-z][A-Za-z .'-]{1,80})\b", re.I)

    def extract(self, text: str) -> list[MemoryCandidate]:
        text = str(text).strip()
        if not text:
            return []

        candidates: list[MemoryCandidate] = []

        match = self._name.search(text)
        if match:
            value = match.group("value").strip(" .")
            candidates.append(MemoryCandidate(
                MemoryType.PROFILE, "user_name", value, 0.98, "explicit identity statement"
            ))

        match = self._preference.search(text)
        if match:
            value = match.group("value").strip(" .")
            candidates.append(MemoryCandidate(
                MemoryType.PREFERENCE, "user_preference", value, 0.90, "explicit preference statement"
            ))

        match = self._remember.search(text)
        if match:
            value = match.group("value").strip(" .")
            candidates.append(MemoryCandidate(
                MemoryType.LONG_TERM, "explicit_memory", value, 0.95, "explicit remember request"
            ))

        return candidates
