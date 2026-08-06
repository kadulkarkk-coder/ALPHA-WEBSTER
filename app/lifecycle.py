"""
WEBSTER ALPHA

Application Lifecycle
"""

from __future__ import annotations

from app.runtime import Runtime


class Lifecycle:
    """
    Controls the startup and shutdown
    sequence of Webster.
    """

    def __init__(
        self,
        runtime: Runtime,
    ) -> None:

        self._runtime = runtime

    # ---------------------------------------------------------

    @property
    def runtime(self) -> Runtime:

        return self._runtime

    # ---------------------------------------------------------

    def startup(self) -> None:
        """
        Start all runtime subsystems.
        """

        if self.runtime.capabilities is not None:

            if hasattr(self.runtime.capabilities, "start"):

                self.runtime.capabilities.start()

        if self.runtime.planning is not None:

            if hasattr(self.runtime.planning, "start"):

                self.runtime.planning.start()

    # ---------------------------------------------------------

    def shutdown(self) -> None:
        """
        Shutdown runtime subsystems.
        """

        if self.runtime.planning is not None:

            if hasattr(self.runtime.planning, "stop"):

                self.runtime.planning.stop()

        if self.runtime.capabilities is not None:

            if hasattr(self.runtime.capabilities, "stop"):

                self.runtime.capabilities.stop()