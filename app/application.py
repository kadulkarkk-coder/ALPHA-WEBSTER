"""Webster Alpha Application."""

from __future__ import annotations

from datetime import datetime

from app.runtime import Runtime


class Application:
    """Public API for the Webster platform."""

    VERSION = "0.1.0"

    def __init__(self, runtime: Runtime) -> None:
        self.runtime = runtime
        self.started = datetime.now()
        self.running = False

    def initialize(self) -> None:
        if self.running:
            return
        self.runtime.initialize()

    def start(self) -> None:
        if self.running:
            return
        self.initialize()
        self.runtime.start()
        self.running = True

    def shutdown(self) -> None:
        if not self.running:
            return
        self.runtime.shutdown()
        self.running = False

    def restart(self) -> None:
        self.shutdown()
        self.start()

    def chat(self, message: str) -> str:
        return self.runtime.ai.chat(message)

    def execute(self, command: str):
        return self.runtime.ai.chat(command)

    # ---------------------------------------------------------
    # Voice
    # ---------------------------------------------------------

    def start_voice(self) -> bool:
        """Start hands-free voice mode through the shared runtime voice manager."""
        voice = self.runtime.voice
        if voice is None:
            return False
        return voice.start_voice_loop()

    def stop_voice(self) -> None:
        """Stop hands-free voice mode."""
        voice = self.runtime.voice
        if voice is not None:
            voice.stop_voice_loop()

    def voice_chat_once(self) -> str | None:
        """Listen for one utterance, obtain the AI response, and speak it."""
        voice = self.runtime.voice
        if voice is None:
            return None
        return voice.converse_once()

    # ---------------------------------------------------------
    # Files
    # ---------------------------------------------------------

    @property
    def files(self):
        """High-level local filesystem service."""
        service = self.runtime.services.find("file_manager") if self.runtime.services else None
        return service

    def status(self) -> dict:
        runtime_health = self.runtime.health()
        return {
            "running": self.running,
            "started": self.started,
            "version": self.VERSION,
            "healthy": runtime_health.get("healthy", True),
            "voice": runtime_health.get("components", {}).get("voice", False),
            "files": runtime_health.get("components", {}).get("services", False),
        }

    def health(self) -> dict:
        return {
            "application": {
                "running": self.running,
                "started": self.started,
                "version": self.VERSION,
            },
            "runtime": self.runtime.health(),
        }

    @property
    def ai(self):
        return self.runtime.ai

    @property
    def planner(self):
        return self.runtime.planning

    @property
    def capabilities(self):
        return self.runtime.capabilities

    @property
    def providers(self):
        return self.runtime.providers

    @property
    def memory(self):
        return self.runtime.memory

    @property
    def conversation(self):
        return self.runtime.conversation

    @property
    def services(self):
        return self.runtime.services

    @property
    def voice(self):
        return self.runtime.voice

    @property
    def component_count(self) -> int:
        return self.runtime.component_count

    @property
    def provider_count(self) -> int:
        return self.runtime.provider_count

    @property
    def capability_count(self) -> int:
        return self.runtime.capability_count

    @property
    def workflow_count(self) -> int:
        return self.runtime.workflow_count

    def __repr__(self) -> str:
        return f"Application(running={self.running}, version='{self.VERSION}')"
