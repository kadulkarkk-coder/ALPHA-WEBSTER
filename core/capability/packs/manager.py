"""
Webster Alpha

Capability Pack Manager
Sprint 30.12
"""

from __future__ import annotations

from typing import Iterable

from core.capability.packs.events import CapabilityPackEventBus, PackEventType
from core.capability.packs.manifest import (
    CapabilityPackManifest,
    CapabilityPackManifestRegistry,
)
from core.capability.packs.pack import CapabilityPack
from core.capability.packs.validation import CapabilityPackValidator, PackValidationResult
from core.capability.registry import CapabilityRegistry


class CapabilityPackManager:
    """Manage capability-pack lifecycle with validation, rollback and events."""

    def __init__(
        self,
        registry: CapabilityRegistry,
        manifest_registry: CapabilityPackManifestRegistry | None = None,
        validator: CapabilityPackValidator | None = None,
        event_bus: CapabilityPackEventBus | None = None,
    ) -> None:
        if registry is None:
            raise ValueError("Capability registry cannot be None.")

        self.registry = registry
        self.manifests = manifest_registry or CapabilityPackManifestRegistry()
        self.validator = validator or CapabilityPackValidator()
        self.events = event_bus or CapabilityPackEventBus()
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
        try:
            self._ensure_manifest(pack)
            self.validate_or_raise()
        except Exception:
            del self._packs[key]
            if self.manifests.get(pack.name) is not None:
                self.manifests.remove(pack.name)
            raise
        self.events.emit(PackEventType.REGISTERED, pack.name)
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

        added: list[CapabilityPack] = []
        try:
            for pack in pending:
                self.add(pack)
                added.append(pack)
        except Exception:
            for pack in reversed(added):
                key = self._key(pack)
                self._packs.pop(key, None)
                if self.manifests.get(pack.name) is not None:
                    self.manifests.remove(pack.name)
            raise
        return tuple(added)

    def register_manifest(self, manifest: CapabilityPackManifest) -> CapabilityPackManifest:
        result = self.manifests.add(manifest)
        try:
            self.validate_or_raise()
        except Exception:
            self.manifests.remove(manifest.name)
            raise
        return result

    def register_manifests(self, manifests: Iterable[CapabilityPackManifest]) -> tuple[CapabilityPackManifest, ...]:
        added = self.manifests.add_many(manifests)
        try:
            self.validate_or_raise()
        except Exception:
            for manifest in reversed(added):
                self.manifests.remove(manifest.name)
            raise
        return added

    def validate(self) -> PackValidationResult:
        return self.validator.validate(self.packs, self.manifests)

    def validate_or_raise(self) -> PackValidationResult:
        return self.validator.validate_or_raise(self.packs, self.manifests)

    def load(self, name: str) -> CapabilityPack:
        """Load one pack transactionally and emit lifecycle events."""
        key = self._normalize_name(name)
        pack = self._packs.get(key)
        if pack is None:
            raise KeyError(f"Capability pack '{name}' is not registered.")
        if key in self._loaded:
            return pack

        self.validate_or_raise()
        manifest = self.manifests.get(key)
        if (manifest is not None and not manifest.enabled) or not pack.enabled:
            return pack

        return self._load_transaction((pack,))[0]

    def load_all(self) -> tuple[CapabilityPack, ...]:
        """Load all enabled packs as one validated transaction."""
        result = self.validate_or_raise()
        ordered_names = result.load_order
        if not ordered_names:
            ordered_names = tuple(pack.name for pack in self._packs.values() if pack.enabled)

        packs = tuple(
            self._packs[name.strip().lower()]
            for name in ordered_names
            if name.strip().lower() not in self._loaded
        )
        return self._load_transaction(packs)

    def unload(self, name: str) -> CapabilityPack:
        key = self._normalize_name(name)
        pack = self._packs.get(key)
        if pack is None:
            raise KeyError(f"Capability pack '{name}' is not registered.")
        if key not in self._loaded:
            return pack

        self.events.emit(PackEventType.UNLOAD_STARTED, pack.name)
        try:
            pack.unregister(self.registry)
        except Exception as exc:
            self.events.emit(PackEventType.UNLOAD_FAILED, pack.name, str(exc))
            raise
        self._loaded.remove(key)
        self.events.emit(PackEventType.UNLOADED, pack.name)
        return pack

    def remove(self, name: str) -> CapabilityPack:
        key = self._normalize_name(name)
        pack = self._packs.get(key)
        if pack is None:
            raise KeyError(f"Capability pack '{name}' is not registered.")
        if key in self._loaded:
            self.unload(name)
        del self._packs[key]
        if self.manifests.get(name) is not None:
            self.manifests.remove(name)
        self.events.emit(PackEventType.REMOVED, pack.name)
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

    def _load_transaction(self, packs: tuple[CapabilityPack, ...]) -> tuple[CapabilityPack, ...]:
        if not packs:
            return ()

        registry_before = set(self.registry.names())
        loaded_now: list[CapabilityPack] = []
        current: CapabilityPack | None = None

        try:
            for pack in packs:
                key = self._key(pack)
                if key in self._loaded:
                    continue
                current = pack
                self.events.emit(PackEventType.LOAD_STARTED, pack.name)
                pack.register(self.registry)
                self._loaded.add(key)
                loaded_now.append(pack)
                self.events.emit(PackEventType.LOADED, pack.name)
        except Exception as exc:
            if current is not None:
                self.events.emit(PackEventType.LOAD_FAILED, current.name, str(exc))

            rollback_errors: list[str] = []
            for pack in reversed(loaded_now):
                try:
                    pack.unregister(self.registry)
                except Exception as rollback_exc:
                    rollback_errors.append(f"{pack.name}: {rollback_exc}")
                finally:
                    self._loaded.discard(self._key(pack))

            for capability_name in tuple(self.registry.names()):
                if capability_name not in registry_before:
                    self.registry.unregister(capability_name)

            if rollback_errors:
                raise RuntimeError(
                    "Capability pack load failed and rollback was incomplete: "
                    + "; ".join(rollback_errors)
                ) from exc

            failed_name = current.name if current is not None else packs[0].name
            raise RuntimeError(
                f"Capability pack load failed for '{failed_name}'; transaction rolled back."
            ) from exc

        return tuple(loaded_now)

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
