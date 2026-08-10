"""
Webster Alpha

Capability Pack Manager
Sprint 30.2
"""

from __future__ import annotations

from typing import Iterable

from core.capability.packs.pack import CapabilityPack
from core.capability.registry import CapabilityRegistry


class CapabilityPackManager:
    """Manage the lifecycle of Webster capability packs.

    The manager owns pack lifecycle only. Capability registration remains
    delegated to each pack and the registry remains the source of truth for
    individual capabilities.
    """

    def __init__(self, registry: CapabilityRegistry) -> None:
        if registry is None:
            raise ValueError("Capability registry cannot be None.")

        self.registry = registry
        self._packs: dict[str, CapabilityPack] = {}
        self._loaded: set[str] = set()

    @property
    def packs(self) -> tuple[CapabilityPack, ...]:
        """Return all known packs in registration order."""
        return tuple(self._packs.values())

    @property
    def loaded_packs(self) -> tuple[CapabilityPack, ...]:
        """Return currently loaded packs."""
        return tuple(
            self._packs[name]
            for name in self._packs
            if name in self._loaded
        )

    def add(self, pack: CapabilityPack) -> CapabilityPack:
        """Add a pack without loading it."""
        self._validate_pack(pack)
        key = self._key(pack)

        if key in self._packs:
            raise ValueError(f"Capability pack '{pack.name}' is already registered.")

        self._packs[key] = pack
        return pack

    def add_many(self, packs: Iterable[CapabilityPack]) -> tuple[CapabilityPack, ...]:
        """Add multiple packs atomically with respect to duplicate names."""
        added: list[CapabilityPack] = []
        pending: set[str] = set()

        for pack in packs:
            self._validate_pack(pack)
            key = self._key(pack)
            if key in self._packs or key in pending:
                raise ValueError(f"Capability pack '{pack.name}' is already registered.")
            pending.add(key)
            added.append(pack)

        for pack in added:
            self._packs[self._key(pack)] = pack

        return tuple(added)

    def load(self, name: str) -> CapabilityPack:
        """Load and register a pack by name."""
        key = self._normalize_name(name)
        pack = self._packs.get(key)

        if pack is None:
            raise KeyError(f"Capability pack '{name}' is not registered.")

        if key in self._loaded:
            return pack

        if not pack.enabled:
            return pack

        pack.register(self.registry)
        self._loaded.add(key)
        return pack

    def load_all(self) -> tuple[CapabilityPack, ...]:
        """Load every enabled pack."""
        loaded: list[CapabilityPack] = []
        for pack in self._packs.values():
            if pack.enabled:
                loaded.append(self.load(pack.name))
        return tuple(loaded)

    def unload(self, name: str) -> CapabilityPack:
        """Unload a loaded pack using its optional cleanup hook."""
        key = self._normalize_name(name)
        pack = self._packs.get(key)

        if pack is None:
            raise KeyError(f"Capability pack '{name}' is not registered.")

        if key not in self._loaded:
            return pack

        pack.unregister(self.registry)
        self._loaded.remove(key)
        return pack

    def remove(self, name: str) -> CapabilityPack:
        """Unload and forget a pack."""
        key = self._normalize_name(name)
        pack = self._packs.get(key)

        if pack is None:
            raise KeyError(f"Capability pack '{name}' is not registered.")

        if key in self._loaded:
            self.unload(name)

        del self._packs[key]
        return pack

    def is_registered(self, name: str) -> bool:
        return self._normalize_name(name) in self._packs

    def is_loaded(self, name: str) -> bool:
        return self._normalize_name(name) in self._loaded

    def get(self, name: str) -> CapabilityPack | None:
        return self._packs.get(self._normalize_name(name))

    def metadata(self) -> tuple[dict[str, object], ...]:
        """Return metadata for all known packs."""
        return tuple(pack.metadata() for pack in self._packs.values())

    @staticmethod
    def _validate_pack(pack: CapabilityPack) -> None:
        if not isinstance(pack, CapabilityPack):
            raise TypeError("Expected a CapabilityPack instance.")

        if not str(pack.name).strip():
            raise ValueError("Capability pack name cannot be empty.")

    @staticmethod
    def _normalize_name(name: str) -> str:
        value = str(name).strip().lower()
        if not value:
            raise ValueError("Capability pack name cannot be empty.")
        return value

    @classmethod
    def _key(cls, pack: CapabilityPack) -> str:
        return cls._normalize_name(pack.name)

    def __contains__(self, name: str) -> bool:
        return self.is_registered(name)

    def __len__(self) -> int:
        return len(self._packs)

    def __repr__(self) -> str:
        return (
            f"CapabilityPackManager(packs={len(self._packs)}, "
            f"loaded={len(self._loaded)})"
        )
