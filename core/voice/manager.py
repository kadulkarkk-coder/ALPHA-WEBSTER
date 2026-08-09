"""High-level voice manager for Webster Alpha."""
from __future__ import annotations
from collections.abc import Callable
from threading import Event, Thread, current_thread
import time
from core.voice.config import VoiceConfig
from core.voice.engine import VoiceEngine

class VoiceManager:
    """Persistent hands-free voice controller.

    After startup, voice mode stays active continuously. The microphone is
    reopened for every utterance, and a failed/empty capture never terminates
    the voice loop. Audio-only barge-in remains disabled.
    """
    def __init__(self, engine: VoiceEngine | None = None, config: VoiceConfig | None = None) -> None:
        self.config=config or VoiceConfig(); self.engine=engine or VoiceEngine(config=self.config); self._initialized=False; self._running=False; self._processor: Callable[[str], str] | None=None; self._last_input=None; self._last_response=None; self._last_error=None; self._loop_thread=None; self._stop_event=Event(); self._voice_ready=Event(); self._muted=False

    def initialize(self):
        if self._initialized: return
        self.engine.initialize(); self._initialized=True
        if not self.engine.listener.available: self._last_error=self.engine.listener.error or "No usable microphone/STT backend is available."

    def start(self):
        if not self._initialized: self.initialize()
        if self._running: return
        self.engine.start(); self._running=True

    def stop(self):
        self._stop_event.set(); self._voice_ready.clear(); self.engine.stop(); self._running=False

    def shutdown(self):
        self.stop_voice_loop()
        if self._initialized: self.engine.shutdown(); self._initialized=False

    def listen(self, ignore_wake_word=True):
        if not self._initialized: self.initialize()
        text=self.engine.listen(ignore_wake_word=ignore_wake_word)
        if text: self._last_input=text
        return text

    def speak(self,text):
        if not self._initialized: self.initialize()
        return self.engine.speak(text)

    def set_processor(self,processor): self._processor=processor

    def _process(self,text):
        self._last_input=text; print(f"\n[VOICE] You: {text}", flush=True)
        response=str(self._processor(text)).strip()
        if not response: raise RuntimeError("AI returned an empty response.")
        self._last_response=response; print(f"[VOICE] Webster: {response}\n", flush=True)
        if not self.speak(response): raise RuntimeError(self.engine.speaker.error or "Voice output failed.")
        self._last_error=None; return response

    def start_voice_loop(self):
        if self._processor is None: self._last_error="No voice conversation processor is configured."; return False
        if self._loop_thread is not None and self._loop_thread.is_alive(): return True
        if not self._initialized: self.initialize()
        if not self.engine.listener.available: self._last_error=self.engine.listener.error or "Voice input is unavailable."; return False
        self._stop_event.clear(); self._voice_ready.clear(); self._muted=False; self.start()
        self._loop_thread=Thread(target=self._voice_loop,name="WebsterVoiceLoop",daemon=True); self._loop_thread.start(); return True

    def stop_voice_loop(self):
        self._stop_event.set(); self._voice_ready.clear(); self.engine.stop(); self._running=False
        thread=self._loop_thread
        if thread is not None and thread.is_alive() and thread is not current_thread(): thread.join(timeout=1.5)
        self._loop_thread=None

    def _voice_loop(self):
        print("[VOICE] Listening... Say 'mute' to stop voice mode.", flush=True)
        # Continuous mode: wake word is deliberately bypassed after startup.
        # The first and every subsequent turn use the same listening path.
        while not self._stop_event.is_set():
            try:
                # Re-arm the listener before every turn. This is intentionally
                # lightweight and prevents the first InputStream lifecycle from
                # becoming the only active capture session on Windows.
                self.engine.listener.start()
                if self._stop_event.is_set(): break
                text=self.engine.listen(ignore_wake_word=True)
                if self._stop_event.is_set(): break
                if not text:
                    # Silence is normal. Keep the loop alive and re-arm capture.
                    time.sleep(0.05)
                    continue
                normalized=text.strip().lower()
                if normalized in {"mute", "mute webster", "webster mute", "stop listening", "stop voice"}:
                    self._muted=True; print("[VOICE] Muted. Say 'voice' to resume.", flush=True); break
                try:
                    self.engine.begin_conversation(); self.engine._turns += 1; self._voice_ready.set(); self._process(text)
                except Exception as error:
                    self._last_error=str(error); print(f"[VOICE] Error: {error}", flush=True)
                finally:
                    self.engine.end_conversation(); self._voice_ready.clear()
                # Explicitly re-arm after TTS. No Enter key and no wake word.
                if not self._stop_event.is_set():
                    time.sleep(0.20)
                    print("[VOICE] Listening...", flush=True)
            except Exception as error:
                self._last_error=str(error); print(f"[VOICE] Voice loop recovered: {error}", flush=True)
                # Recover the capture backend without killing the voice thread.
                try: self.engine.listener.stop(); self.engine.listener.start()
                except Exception: pass
                if self._stop_event.wait(0.25): break
        self._voice_ready.clear()

    def converse_once(self):
        if not self._initialized: self.initialize()
        if self._processor is None: self._last_error="No voice conversation processor is configured."; return None
        text=self.engine.listen(ignore_wake_word=True)
        if not text: return None
        try: return self._process(text)
        except Exception as error: self._last_error=str(error); print(f"[VOICE] Error: {error}", flush=True); return None

    def devices(self):
        if not self._initialized: self.initialize()
        return self.engine.devices()

    def voice_diagnostics(self): return self.engine.voice_diagnostics()

    def health(self):
        thread=self._loop_thread
        return {"initialized":self._initialized,"running":self._running,"voice_loop_running":bool(thread and thread.is_alive()),"voice_input_ready":self._voice_ready.is_set(),"muted":self._muted,"processor_configured":self._processor is not None,"last_input":self._last_input,"last_response":self._last_response,"last_error":self._last_error,**self.engine.health()}

    @property
    def ready(self): return self._initialized and self.engine.listener.available
