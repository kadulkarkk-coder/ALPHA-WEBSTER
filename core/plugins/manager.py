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

        self._initialized = False

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

    # =====================================================
    # State
    # =====================================================

    @property
    def initialized(
        self,
    ) -> bool:

        return self._initialized

    # -----------------------------------------------------

    @property
    def ready(
        self,
    ) -> bool:

        return self._initialized

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize the plugin subsystem.

        Plugin discovery/loading remains controlled by the
        existing PluginManager implementation.
        """

        if self._initialized:

            return

        #
        # Ensure existing plugin collections are available.
        #

        if not hasattr(
            self,
            "_plugins",
        ):

            self._plugins = {}

        #
        # Mark the manager as ready.
        #

        self._initialized = True

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown the plugin subsystem.

        Loaded plugin objects are not automatically deleted.
        The existing plugin lifecycle remains responsible
        for unloading individual plugins.
        """

        if not self._initialized:

            return

        self._initialized = False

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:
        """
        Return PluginManager health information.
        """

        plugin_count = 0

        #
        # Detect the existing plugin collection without
        # changing the manager's architecture.
        #

        if hasattr(
            self,
            "_plugins",
        ):

            plugin_count = len(
                self._plugins
            )

        elif hasattr(
            self,
            "_loaded_plugins",
        ):

            plugin_count = len(
                self._loaded_plugins
            )

        return {

            "initialized": self._initialized,

            "healthy": self._initialized,

            "ready": self._initialized,

            "plugins": plugin_count,

        }

    # =====================================================
    # Internal Validation
    # =====================================================

    def _ensure_initialized(
        self,
    ) -> None:
        """
        Ensure the plugin manager is ready.
        """

        if not self._initialized:

            raise RuntimeError(

                "PluginManager has not been initialized. "
                "Call initialize() first."

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