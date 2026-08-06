"""
Extension Manager
"""

from core.extensions.loader import ExtensionLoader
from core.extensions.registry import ExtensionRegistry
from core.extensions.extension import Extension


class ExtensionManager:
    """
    Controls Webster extensions.
    """

    def __init__(
        self
    ) -> None:

        self._loader = ExtensionLoader()

        self._registry = ExtensionRegistry()

    @property
    def count(
        self
    ) -> int:

        return self._registry.count

    def register(
        self,
        extension: Extension
    ) -> None:

        self._registry.register(
            extension
        )

    def load(
        self,
        module_name: str,
        class_name: str
    ) -> Extension:

        extension = self._loader.load(
            module_name,
            class_name
        )

        extension.load()

        extension.initialize()

        self.register(
            extension
        )

        return extension

    def unload(
        self,
        name: str
    ) -> None:

        extension = self._registry.get(
            name
        )

        extension.shutdown()

        extension.unload()

        self._registry.unregister(
            name
        )

    def get(
        self,
        name: str
    ) -> Extension:

        return self._registry.get(
            name
        )

    def all(
        self
    ) -> list[Extension]:

        return self._registry.all()