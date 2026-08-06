"""
Plugin Loader
"""

from importlib import import_module

from core.plugins.plugin import Plugin


class PluginLoader:
    """
    Loads plugins dynamically.
    """

    def load(
        self,
        module_name: str,
        class_name: str
    ) -> Plugin:

        module = import_module(
            module_name
        )

        plugin_class = getattr(
            module,
            class_name
        )

        plugin = plugin_class()

        if not isinstance(
            plugin,
            Plugin
        ):

            raise TypeError(
                "Invalid plugin type."
            )

        return plugin