"""High-level voice manager for Webster Alpha."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event, Thread, current_thread

from core.voice.config import VoiceConfig
from core.voice.engine import VoiceEngine


class VoiceManager:
    """Lifecycle, diagnostics and hands-free conversation controller."""

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
        if not self.engine.listener.available:
            self._last_error = self.engine.listener.error or "No usable microphone/STT backend is available."

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
        if self._initialized:
            self.engine.shutdown()
            self._initialized = False

    def listen(self, ignore_wake_word: bool = False) -> str | None:
        if not self._initialized:
            self.initialize()
        text = self.engine.listen(ignore_wake_word=ignore_wake_word)
        if text:
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
        if not self.engine.listener.available:
            self._last_error = self.engine.listener.error or "Voice input is unavailable."
            return None

        text = self.listen()
        if not text:
            return None

        try:
            print(f"\n[VOICE] You: {text}")
            response = str(self._processor(text)).strip()
            if not response:
                self._last_error = "AI returned an empty response."
                return None
            self._last_response = response
            print(f"[VOICE] Webster: {response}\n")
            if not self.speak(response):
                self._last_error = self.engine.speaker.error or "Voice output failed."
            else:
                self._last_error = None
            return response
        except Exception as error:
            self._last_error = str(error)
            print(f"[VOICE] Error: {error}")
            return None

    def start_voice_loop(self) -> bool:
        """Start the persistent local voice conversation loop."""
        if self._processor is None:
            self._last_error = "No voice conversation processor is configured."
            return False
        if self._loop_thread is not None and self._loop_thread.is_alive():
            return True
        if not self._initialized:
            self.initialize()
        if not self.engine.listener.available:
            self._last_error = self.engine.listener.error or "Voice input is unavailable."
            return False

        self._stop_event.clear()
        self.start()
        self._loop_thread = Thread(target=self._voice_loop, name="WebsterVoiceLoop", daemon=True)
        self._loop_thread.start()
        return True

    def stop_voice_loop(self) -> None:
        self._stop_event.set()
        self.engine.stop()
        self._running = False
        thread = self._loop_thread
        if thread is not None and thread.is_alive() and thread is not current_thread():
            thread.join(timeout=1.5)
        self._loop_thread = None

    def _voice_loop(self) -> None:
        print("[VOICE] Hands-free voice mode active. Say 'Webster' to wake me.")
        while not self._stop_event.is_set():
            try:
                result = self.converse_once()
                if result is None and self._last_error:
                    # Avoid a tight failure loop while still allowing the
                    # listener to recover from transient microphone errors.
                    self._stop_event.wait(0.25)
            except Exception as error:
                self._last_error = str(error)
                self._stop_event.wait(0.25)

    def devices(self) -> list[dict]:
        if not self._initialized:
            self.initialize()
        return self.engine.devices()

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
        return self._initialized and self.engine.listener.available
