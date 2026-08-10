"""
Webster Alpha

Capability Pack Discovery
Sprint 30.3
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Iterable

from core.capability.packs.manager import CapabilityPackManager
from core.capability.packs.pack import CapabilityPack


class CapabilityPackDiscovery:
    """Discover CapabilityPack implementations from a Python package."""

    def __init__(self, package: str = "core.capability.packs") -> None:
        self.package = package

    def discover(self) -> tuple[type[CapabilityPack], ...]:
        """Find concrete CapabilityPack subclasses in the pack package."""
        package_module = importlib.import_module(self.package)
        classes: dict[str, type[CapabilityPack]] = {}

        for module_info in pkgutil.iter_modules(package_module.__path__):
            name = module_info.name
            if name.startswith("_") or name in {"pack", "manager", "discovery"}:
                continue

            module = importlib.import_module(f"{self.package}.{name}")
            self._collect(module, classes)

        return tuple(classes[key] for key in sorted(classes))

    def instantiate(self) -> tuple[CapabilityPack, ...]:
        """Discover packs and instantiate them using their default constructor."""
        packs: list[CapabilityPack] = []
        for pack_class in self.discover():
            try:
                packs.append(pack_class())
            except TypeError as exc:
                raise TypeError(
                    f"Capability pack '{pack_class.__name__}' must support "
                    "a no-argument constructor for automatic discovery."
                ) from exc
        return tuple(packs)

    def register_with_manager(
        self,
        manager: CapabilityPackManager,
    ) -> tuple[CapabilityPack, ...]:
        """Discover packs, add them to a manager, and load enabled packs."""
        if manager is None:
            raise ValueError("Capability pack manager cannot be None.")

        packs = self.instantiate()
        manager.add_many(packs)
        manager.load_all()
        return packs

    @classmethod
    def _collect(
        cls,
        module: ModuleType,
        classes: dict[str, type[CapabilityPack]],
    ) -> None:
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if candidate is CapabilityPack:
                continue
            if not issubclass(candidate, CapabilityPack):
                continue
            if inspect.isabstract(candidate):
                continue
            if candidate.__module__ != module.__name__:
                continue

            key = f"{candidate.__module__}.{candidate.__qualname__}"
            classes[key] = candidate

    def __repr__(self) -> str:
        return f"CapabilityPackDiscovery(package='{self.package}')"
