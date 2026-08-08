"""High-level voice manager for Webster."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event, Thread, current_thread

from core.voice.config import VoiceConfig
from core.voice.engine import VoiceEngine


class VoiceManager:
    """Public lifecycle and hands-free voice conversation API."""

    def __init__(self, engine: VoiceEngine | None = None, config: VoiceConfig | None = None) -> None:
        self.config = config or VoiceConfig()
        self.engine = engine or VoiceEngine(config=self.config)
        self._initialized = False
        self._running = False
        self._processor: Callable[[str], str] | None = None
        self._last_input: str | None = None
        self._last_response: str | None = None
        self._last_error: str | None = None
        self._loop_thread: Thread | None = None
        self._stop_event = Event()

    def initialize(self) -> None:
        if self._initialized:
            return
        self.engine.initialize()
        self._initialized = True

    def start(self) -> None:
        if not self._initialized:
            self.initialize()
        if self._running:
            return
        self.engine.start()
        self._running = True

    def stop(self) -> None:
        self._stop_event.set()
        self.engine.stop()
        self._running = False

    def shutdown(self) -> None:
        self.stop_voice_loop()
        if not self._initialized:
            return
        self.engine.shutdown()
        self._initialized = False

    def listen(self) -> str | None:
        if not self._initialized:
            self.initialize()
        text = self.engine.listen()
        self._last_input = text
        return text

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()
        return self.engine.speak(text)

    def set_processor(self, processor: Callable[[str], str] | None) -> None:
        self._processor = processor

    def converse_once(self) -> str | None:
        if not self._initialized:
            self.initialize()
        if self._processor is None:
            self._last_error = "No voice conversation processor is configured."
            return None

        text = self.listen()
        if not text:
            return None

        try:
            response = str(self._processor(text)).strip()
            if not response:
                self._last_error = "AI returned an empty response."
                return None
            self._last_response = response
            if not self.speak(response):
                self._last_error = self.engine.speaker.error or "Voice output failed."
            else:
                self._last_error = None
            return response
        except Exception as error:
            self._last_error = str(error)
            return None

    def start_voice_loop(self) -> bool:
        """Start hands-free mode: wait for speech, answer, then listen again."""
        if self._processor is None:
            self._last_error = "No voice conversation processor is configured."
            return False
        if self._loop_thread is not None and self._loop_thread.is_alive():
            return False
        if not self._initialized:
            self.initialize()
        self._stop_event.clear()
        self.start()
        self._loop_thread = Thread(target=self._voice_loop, name="WebsterVoiceLoop", daemon=True)
        self._loop_thread.start()
        return True

    def stop_voice_loop(self) -> None:
        """Stop hands-free mode and release active voice resources."""
        self._stop_event.set()
        self.engine.stop()
        self._running = False
        thread = self._loop_thread
        if thread is not None and thread.is_alive() and thread is not current_thread():
            thread.join(timeout=1.0)
        self._loop_thread = None

    def _voice_loop(self) -> None:
        """Wait for speech, process it, speak the answer, then wait again."""
        while not self._stop_event.is_set():
            try:
                self.converse_once()
            except Exception as error:
                self._last_error = str(error)
                if self._stop_event.wait(0.2):
                    break

    def health(self) -> dict:
        thread = self._loop_thread
        return {
            "initialized": self._initialized,
            "running": self._running,
            "voice_loop_running": bool(thread and thread.is_alive()),
            "processor_configured": self._processor is not None,
            "last_input": self._last_input,
            "last_response": self._last_response,
            "last_error": self._last_error,
            **self.engine.health(),
        }

    @property
    def ready(self) -> bool:
        return self._initialized and self.engine is not None
