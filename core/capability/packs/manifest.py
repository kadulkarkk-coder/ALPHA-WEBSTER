"""
Webster Alpha

Capability Pack Manifest
Sprint 30.4
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True, slots=True)
class CapabilityPackManifest:
    """Declarative metadata describing a capability pack.

    The manifest deliberately contains metadata only. It does not import or
    instantiate packs, keeping discovery and lifecycle management separate.
    """

    name: str
    module: str
    class_name: str
    version: str = "1.0.0"
    enabled: bool = True
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    priority: int = 100

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Pack manifest name cannot be empty.")
        if not self.module.strip():
            raise ValueError("Pack manifest module cannot be empty.")
        if not self.class_name.strip():
            raise ValueError("Pack manifest class_name cannot be empty.")

        normalized = tuple(
            dependency.strip().lower()
            for dependency in self.dependencies
            if dependency.strip()
        )
        object.__setattr__(self, "dependencies", normalized)

    @property
    def key(self) -> str:
        return self.name.strip().lower()

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "module": self.module,
            "class_name": self.class_name,
            "version": self.version,
            "enabled": self.enabled,
            "dependencies": self.dependencies,
            "priority": self.priority,
        }


class CapabilityPackManifestRegistry:
    """Registry for declarative capability-pack manifests."""

    def __init__(self, manifests: Iterable[CapabilityPackManifest] = ()) -> None:
        self._manifests: dict[str, CapabilityPackManifest] = {}
        self.add_many(manifests)

    @property
    def manifests(self) -> tuple[CapabilityPackManifest, ...]:
        return tuple(self._manifests.values())

    def add(self, manifest: CapabilityPackManifest) -> CapabilityPackManifest:
        if not isinstance(manifest, CapabilityPackManifest):
            raise TypeError("Expected a CapabilityPackManifest instance.")
        if manifest.key in self._manifests:
            raise ValueError(f"Pack manifest '{manifest.name}' is already registered.")
        self._manifests[manifest.key] = manifest
        return manifest

    def add_many(
        self,
        manifests: Iterable[CapabilityPackManifest],
    ) -> tuple[CapabilityPackManifest, ...]:
        pending: list[CapabilityPackManifest] = []
        keys: set[str] = set()

        for manifest in manifests:
            if not isinstance(manifest, CapabilityPackManifest):
                raise TypeError("Expected CapabilityPackManifest instances.")
            if manifest.key in self._manifests or manifest.key in keys:
                raise ValueError(
                    f"Pack manifest '{manifest.name}' is already registered."
                )
            keys.add(manifest.key)
            pending.append(manifest)

        for manifest in pending:
            self._manifests[manifest.key] = manifest
        return tuple(pending)

    def get(self, name: str) -> CapabilityPackManifest | None:
        return self._manifests.get(name.strip().lower())

    def remove(self, name: str) -> CapabilityPackManifest:
        key = name.strip().lower()
        if key not in self._manifests:
            raise KeyError(f"Pack manifest '{name}' is not registered.")
        return self._manifests.pop(key)

    def enabled(self) -> tuple[CapabilityPackManifest, ...]:
        return tuple(manifest for manifest in self._manifests.values() if manifest.enabled)

    def load_order(self) -> tuple[CapabilityPackManifest, ...]:
        """Return enabled manifests in deterministic dependency-friendly order."""
        manifests = {manifest.key: manifest for manifest in self.enabled()}
        result: list[CapabilityPackManifest] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(key: str) -> None:
            if key in visited:
                return
            if key in visiting:
                raise ValueError(f"Cyclic capability-pack dependency involving '{key}'.")

            manifest = manifests.get(key)
            if manifest is None:
                raise ValueError(f"Missing enabled dependency '{key}'.")

            visiting.add(key)
            for dependency in manifest.dependencies:
                if dependency in manifests:
                    visit(dependency)
                else:
                    dependency_manifest = self.get(dependency)
                    if dependency_manifest is None:
                        raise ValueError(
                            f"Pack '{manifest.name}' depends on unknown pack '{dependency}'."
                        )
                    if dependency_manifest.enabled:
                        visit(dependency)
                    else:
                        raise ValueError(
                            f"Pack '{manifest.name}' depends on disabled pack '{dependency}'."
                        )

            visiting.remove(key)
            visited.add(key)
            result.append(manifest)

        for key in sorted(manifests, key=lambda item: (manifests[item].priority, item)):
            visit(key)

        return tuple(result)

    def metadata(self) -> tuple[dict[str, object], ...]:
        return tuple(manifest.as_dict() for manifest in self._manifests.values())

    def __contains__(self, name: str) -> bool:
        return name.strip().lower() in self._manifests

    def __len__(self) -> int:
        return len(self._manifests)
