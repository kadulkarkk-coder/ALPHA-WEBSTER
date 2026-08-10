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


@dataclass(frozen=True, slots=True)
class PackValidationResult:
    """Result of validating a capability-pack manifest registry."""

    valid: bool
    errors: tuple[str, ...] = ()
    load_order: tuple[str, ...] = ()


class CapabilityPackValidator:
    """Validate pack manifests before packs are loaded."""

    def validate(
        self,
        manifests: CapabilityPackManifestRegistry | Iterable[CapabilityPackManifest],
    ) -> PackValidationResult:
        registry = (
            manifests
            if isinstance(manifests, CapabilityPackManifestRegistry)
            else CapabilityPackManifestRegistry(manifests)
        )

        errors: list[str] = []
        enabled = {manifest.key: manifest for manifest in registry.enabled()}

        for manifest in registry.manifests:
            for dependency in manifest.dependencies:
                dependency_manifest = registry.get(dependency)
                if dependency_manifest is None:
                    errors.append(
                        f"Pack '{manifest.name}' depends on unknown pack '{dependency}'."
                    )
                elif manifest.enabled and not dependency_manifest.enabled:
                    errors.append(
                        f"Pack '{manifest.name}' depends on disabled pack '{dependency}'."
                    )

        order: tuple[str, ...] = ()
        if not errors:
            try:
                order = tuple(manifest.name for manifest in registry.load_order())
            except ValueError as exc:
                errors.append(str(exc))

        # A dependency must not silently resolve to a disabled pack through an
        # unrelated disabled branch.
        if not errors:
            for key, manifest in enabled.items():
                if key in manifest.dependencies:
                    errors.append(
                        f"Pack '{manifest.name}' cannot depend on itself."
                    )

        return PackValidationResult(
            valid=not errors,
            errors=tuple(dict.fromkeys(errors)),
            load_order=order,
        )

    def validate_or_raise(
        self,
        manifests: CapabilityPackManifestRegistry | Iterable[CapabilityPackManifest],
    ) -> PackValidationResult:
        result = self.validate(manifests)
        if not result.valid:
            raise ValueError(
                "Capability pack validation failed: " + "; ".join(result.errors)
            )
        return result
