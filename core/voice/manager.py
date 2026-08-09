"""High-level voice manager for Webster Alpha."""
from __future__ import annotations
from collections.abc import Callable
from threading import Event, Thread, current_thread
import time
from core.voice.config import VoiceConfig
from core.voice.engine import VoiceEngine

class VoiceManager:
    """Lifecycle and persistent hands-free conversation controller."""
    def __init__(self, engine: VoiceEngine | None = None, config: VoiceConfig | None = None) -> None:
        self.config=config or VoiceConfig(); self.engine=engine or VoiceEngine(config=self.config); self._initialized=False; self._running=False; self._processor: Callable[[str], str] | None=None; self._last_input=None; self._last_response=None; self._last_error=None; self._loop_thread=None; self._stop_event=Event(); self._voice_ready=Event()
    def initialize(self):
        if self._initialized: return
        self.engine.initialize(); self._initialized=True
        if not self.engine.listener.available: self._last_error=self.engine.listener.error or "No usable microphone/STT backend is available."
    def start(self):
        if not self._initialized: self.initialize()
        if self._running: return
        self.engine.start(); self._running=True
    def stop(self): self._stop_event.set(); self._voice_ready.clear(); self.engine.stop(); self._running=False
    def shutdown(self):
        self.stop_voice_loop()
        if self._initialized: self.engine.shutdown(); self._initialized=False
    def listen(self, ignore_wake_word=False):
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
    def _listen_wake(self):
        print("[VOICE] Listening for wake word...", flush=True)
        return self.engine.listen(ignore_wake_word=False)
    def _listen_followup(self):
        print("[VOICE] Listening for your next sentence...", flush=True)
        return self.engine.listen(ignore_wake_word=True)
    def start_voice_loop(self):
        if self._processor is None: self._last_error="No voice conversation processor is configured."; return False
        if self._loop_thread is not None and self._loop_thread.is_alive(): return True
        if not self._initialized: self.initialize()
        if not self.engine.listener.available: self._last_error=self.engine.listener.error or "Voice input is unavailable."; return False
        self._stop_event.clear(); self._voice_ready.clear(); self.start(); self._loop_thread=Thread(target=self._voice_loop,name="WebsterVoiceLoop",daemon=True); self._loop_thread.start(); return True
    def stop_voice_loop(self):
        self._stop_event.set(); self._voice_ready.clear(); self.engine.stop(); self._running=False
        thread=self._loop_thread
        if thread is not None and thread.is_alive() and thread is not current_thread(): thread.join(timeout=1.5)
        self._loop_thread=None
    def _voice_loop(self):
        print("[VOICE] Hands-free voice mode active. Say 'Webster' to wake me.", flush=True)
        while not self._stop_event.is_set():
            try:
                text=self._listen_wake()
                if self._stop_event.is_set(): break
                if not text: continue
                try:
                    self.engine.begin_conversation(); self.engine._turns += 1; self._process(text)
                except Exception as error:
                    self._last_error=str(error); print(f"[VOICE] Error: {error}", flush=True); self.engine.end_conversation(); continue
                # Let Windows release the output device before opening the mic again.
                time.sleep(0.20)
                while not self._stop_event.is_set():
                    self._voice_ready.set(); follow=self._listen_followup(); self._voice_ready.clear()
                    if self._stop_event.is_set(): break
                    if not follow:
                        self.engine.end_conversation(); time.sleep(0.10); break
                    try:
                        self.engine._turns += 1; self._process(follow); time.sleep(0.20)
                    except Exception as error:
                        self._last_error=str(error); print(f"[VOICE] Error: {error}", flush=True); self.engine.end_conversation(); break
            except Exception as error:
                self._last_error=str(error); print(f"[VOICE] Voice loop recovered: {error}", flush=True)
                if not self._stop_event.wait(0.15): continue
    def converse_once(self):
        if not self._initialized: self.initialize()
        if self._processor is None: self._last_error="No voice conversation processor is configured."; return None
        text=self._listen_wake()
        if not text: return None
        try: return self._process(text)
        except Exception as error: self._last_error=str(error); print(f"[VOICE] Error: {error}", flush=True); return None
    def devices(self):
        if not self._initialized: self.initialize()
        return self.engine.devices()
    def voice_diagnostics(self): return self.engine.voice_diagnostics()
    def health(self):
        thread=self._loop_thread
        return {"initialized":self._initialized,"running":self._running,"voice_loop_running":bool(thread and thread.is_alive()),"voice_input_ready":self._voice_ready.is_set(),"processor_configured":self._processor is not None,"last_input":self._last_input,"last_response":self._last_response,"last_error":self._last_error,**self.engine.health()}
    @property
    def ready(self): return self._initialized and self.engine.listener.available
