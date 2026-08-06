"""
Webster Alpha

Application
"""

from __future__ import annotations

from datetime import datetime

from app.runtime import Runtime


class Application:
    """
    Webster Application.

    This class exposes the public API for the
    entire Webster platform.

    The console, GUI, voice assistant, REST API,
    mobile app, and plugins should interact only
    with this class.
    """

    VERSION = "0.1.0"

    # ---------------------------------------------------------
    # Construction
    # ---------------------------------------------------------

    def __init__(
        self,
        runtime: Runtime,
    ) -> None:
        """
        Create the Webster application.
        """

        self.runtime = runtime

        self.started = datetime.now()

        self.running = False

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(
        self,
    ) -> None:
        """
        Initialize Webster.
        """

        if self.running:

            return

        self.runtime.initialize()

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def start(
        self,
    ) -> None:
        """
        Start Webster.
        """

        if self.running:

            return

        self.initialize()

        self.runtime.start()

        self.running = True

    # ---------------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown Webster.
        """

        if not self.running:

            return

        self.runtime.shutdown()

        self.running = False

    # ---------------------------------------------------------

    def restart(
        self,
    ) -> None:
        """
        Restart Webster.
        """

        self.shutdown()

        self.start()

    # ---------------------------------------------------------
    # AI
    # ---------------------------------------------------------

    def chat(
        self,
        message: str,
    ) -> str:
        """
        Send a message to Webster.
        """

        return self.runtime.ai.chat(
            message
        )

    # ---------------------------------------------------------

    def execute(
        self,
        command: str,
    ):
        """
        Execute a natural language command.
        """

        return self.runtime.ai.chat(
            command
        )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def status(
        self,
    ) -> dict:
        """
        Return the current runtime status.
        """

        return {

            "running": self.running,

            "started": self.started,

            "version": self.VERSION,

            "healthy": self.runtime.health().get(

                "healthy",

                True,

            ),

        }

    # ---------------------------------------------------------

    def health(
        self,
    ) -> dict:
        """
        Return complete application health.
        """

        return {

            "application": {

                "running": self.running,

                "started": self.started,

                "version": self.VERSION,

            },

            "runtime": self.runtime.health(),

        }

    # ---------------------------------------------------------
    # Convenience Properties
    # ---------------------------------------------------------

    @property
    def ai(
        self,
    ):

        return self.runtime.ai

    @property
    def planner(
        self,
    ):

        return self.runtime.planning

    @property
    def capabilities(
        self,
    ):

        return self.runtime.capabilities

    @property
    def providers(
        self,
    ):

        return self.runtime.providers

    @property
    def memory(
        self,
    ):

        return self.runtime.memory

    @property
    def conversation(
        self,
    ):

        return self.runtime.conversation

    @property
    def services(
        self,
    ):

        return self.runtime.services

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    @property
    def component_count(
        self,
    ) -> int:

        return self.runtime.component_count

    @property
    def provider_count(
        self,
    ) -> int:

        return self.runtime.provider_count

    @property
    def capability_count(
        self,
    ) -> int:

        return self.runtime.capability_count

    @property
    def workflow_count(
        self,
    ) -> int:

        return self.runtime.workflow_count

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            "Application("

            f"running={self.running}, "

            f"version='{self.VERSION}'"

            ")"

        )
