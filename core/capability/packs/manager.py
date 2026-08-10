"""
Webster Alpha

Capability Pack Manager
Sprint 30.5
"""

from __future__ import annotations

from typing import Iterable

from core.capability.packs.manifest import CapabilityPackManifest, CapabilityPackManifestRegistry
from core.capability.packs.pack import CapabilityPack
from core.capability.registry import CapabilityRegistry


class CapabilityPackManager:
    """Manage capability-pack lifecycle using optional declarative manifests."""

    def __init__(
        self,
        registry: CapabilityRegistry,
        manifest_registry: CapabilityPackManifestRegistry | None = None,
    ) -> None:
        if registry is None:
            raise ValueError("Capability registry cannot be None.")

        self.registry = registry
        self.manifests = manifest_registry or CapabilityPackManifestRegistry()
        self._packs: dict[str, CapabilityPack] = {}
        self._loaded: set[str] = set()

    @property
    def packs(self) -> tuple[CapabilityPack, ...]:
        return tuple(self._packs.values())

    @property
    def loaded_packs(self) -> tuple[CapabilityPack, ...]:
        return tuple(self._packs[name] for name in self._packs if name in self._loaded)

    def add(self, pack: CapabilityPack) -> CapabilityPack:
        self._validate_pack(pack)
        key = self._key(pack)
        if key in self._packs:
            raise ValueError(f"Capability pack '{pack.name}' is already registered.")
        self._packs[key] = pack
        self._ensure_manifest(pack)
        return pack

    def add_many(self, packs: Iterable[CapabilityPack]) -> tuple[CapabilityPack, ...]:
        pending = list(packs)
        keys: set[str] = set()
        for pack in pending:
            self._validate_pack(pack)
            key = self._key(pack)
            if key in self._packs or key in keys:
                raise ValueError(f"Capability pack '{pack.name}' is already registered.")
            keys.add(key)

        for pack in pending:
            self.add(pack)
        return tuple(pending)

    def register_manifest(self, manifest: CapabilityPackManifest) -> CapabilityPackManifest:
        """Register declarative metadata before its pack is instantiated."""
        return self.manifests.add(manifest)

    def register_manifests(
        self,
        manifests: Iterable[CapabilityPackManifest],
    ) -> tuple[CapabilityPackManifest, ...]:
        return self.manifests.add_many(manifests)

    def load(self, name: str) -> CapabilityPack:
        key = self._normalize_name(name)
        pack = self._packs.get(key)
        if pack is None:
            raise KeyError(f"Capability pack '{name}' is not registered.")
        if key in self._loaded:
            return pack

        manifest = self.manifests.get(key)
        if manifest is not None and not manifest.enabled:
            return pack
        if not pack.enabled:
            return pack

        pack.register(self.registry)
        self._loaded.add(key)
        return pack

    def load_all(self) -> tuple[CapabilityPack, ...]:
        """Load packs in manifest dependency/priority order when available."""
        if self.manifests:
            ordered = self.manifests.load_order()
            loaded: list[CapabilityPack] = []
            for manifest in ordered:
                pack = self._packs.get(manifest.key)
                if pack is None:
                    raise KeyError(
                        f"Manifest '{manifest.name}' has no registered capability pack."
                    )
                loaded.append(self.load(manifest.name))
            return tuple(loaded)

        return tuple(self.load(pack.name) for pack in self._packs.values() if pack.enabled)

    def unload(self, name: str) -> CapabilityPack:
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
        return tuple(pack.metadata() for pack in self._packs.values())

    def manifest_metadata(self) -> tuple[dict[str, object], ...]:
        return self.manifests.metadata()

    def _ensure_manifest(self, pack: CapabilityPack) -> None:
        if self.manifests.get(pack.name) is not None:
            return
        self.manifests.add(
            CapabilityPackManifest(
                name=pack.name,
                module=pack.__class__.__module__,
                class_name=pack.__class__.__qualname__,
                version=pack.version,
                enabled=pack.enabled,
            )
        )

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
        return f"CapabilityPackManager(packs={len(self._packs)}, loaded={len(self._loaded)})"
