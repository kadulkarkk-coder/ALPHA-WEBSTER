"""
Webster Alpha

Capability Pack Dependency Validation
Sprint 30.6
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.capability.packs.manifest import (
    CapabilityPackManifest,
    CapabilityPackManifestRegistry,
)
from core.capability.packs.pack import CapabilityPack


@dataclass(frozen=True, slots=True)
class PackValidationResult:
    """Result of validating the pack set before loading."""

    valid: bool
    errors: tuple[str, ...] = ()
    load_order: tuple[str, ...] = ()


class CapabilityPackValidator:
    """Validate pack instances and manifests before lifecycle operations."""

    def validate(
        self,
        packs: Iterable[CapabilityPack],
        manifests: CapabilityPackManifestRegistry,
    ) -> PackValidationResult:
        pack_list = tuple(packs)
        errors: list[str] = []
        pack_keys: set[str] = set()

        for pack in pack_list:
            if not isinstance(pack, CapabilityPack):
                errors.append("Expected CapabilityPack instances.")
                continue

            key = str(pack.name).strip().lower()
            if not key:
                errors.append("Capability pack has an empty name.")
            elif key in pack_keys:
                errors.append(f"Duplicate capability pack '{pack.name}'.")
            pack_keys.add(key)

        manifest_keys = {manifest.key for manifest in manifests.manifests}

        for manifest in manifests.manifests:
            if manifest.enabled and manifest.key not in pack_keys:
                errors.append(
                    f"Enabled manifest '{manifest.name}' has no registered pack."
                )

            for dependency in manifest.dependencies:
                if dependency == manifest.key:
                    errors.append(
                        f"Pack '{manifest.name}' cannot depend on itself."
                    )
                elif dependency not in manifest_keys:
                    errors.append(
                        f"Pack '{manifest.name}' depends on unknown pack '{dependency}'."
                    )
                else:
                    dependency_manifest = manifests.get(dependency)
                    if manifest.enabled and dependency_manifest is not None and not dependency_manifest.enabled:
                        errors.append(
                            f"Pack '{manifest.name}' depends on disabled pack '{dependency}'."
                        )

        order: tuple[str, ...] = ()
        if not errors:
            try:
                order = tuple(manifest.name for manifest in manifests.load_order())
            except ValueError as exc:
                errors.append(str(exc))

        return PackValidationResult(
            valid=not errors,
            errors=tuple(dict.fromkeys(errors)),
            load_order=order,
        )

    def validate_or_raise(
        self,
        packs: Iterable[CapabilityPack],
        manifests: CapabilityPackManifestRegistry,
    ) -> PackValidationResult:
        result = self.validate(packs, manifests)
        if not result.valid:
            raise ValueError(
                "Capability pack validation failed: " + "; ".join(result.errors)
            )
        return result
