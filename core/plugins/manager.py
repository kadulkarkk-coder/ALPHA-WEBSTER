"""
Plugin Manager
"""

from core.plugins.plugin import Plugin


class PluginManager:
    """
    Manages Webster plugins.
    """

    def __init__(
        self
    ) -> None:

        self._plugins: dict[
            str,
            Plugin
        ] = {}

    @property
    def count(
        self
    ) -> int:

        return len(
            self._plugins
        )

    def register(
        self,
        plugin: Plugin
    ) -> None:

        self._plugins[
            plugin.name
        ] = plugin

    def get(
        self,
        name: str
    ) -> Plugin:

        return self._plugins[
            name
        ]

    def enable(
        self,
        name: str
    ) -> None:

        plugin = self.get(
            name
        )

        plugin.enable()

        plugin.start()

    def disable(
        self,
        name: str
    ) -> None:

        plugin = self.get(
            name
        )

        plugin.stop()

        plugin.disable()

    def remove(
        self,
        name: str
    ) -> None:

        if name in self._plugins:

            self.disable(
                name
            )

            del self._plugins[
                name
            ]

    def all(
        self
    ) -> list[Plugin]:

        return list(
            self._plugins.values()
        )