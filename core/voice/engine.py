"""Core voice conversation pipeline for Webster Alpha."""
from __future__ import annotations
from core.voice.config import VoiceConfig
from core.voice.listener import VoiceListener
from core.voice.speaker import VoiceSpeaker
from core.voice.stt import SpeechToTextBackend
from core.voice.diagnostics import VoiceDiagnostics

class VoiceEngine:
    """Coordinates continuous voice turns and diagnostics.

    Audio-only barge-in is intentionally disabled for now. It will later be
    gated by camera lip-motion detection + audio speech detection.
    """
    def __init__(self, listener=None, speaker=None, config=None, stt_backend: SpeechToTextBackend | None = None):
        self.config=config or VoiceConfig(); self.listener=listener or VoiceListener(config=self.config, backend=stt_backend); self.speaker=speaker or VoiceSpeaker(self.config); self.diagnostics=VoiceDiagnostics(); self._initialized=False; self._sentence_barge_ready=False; self._sentences_spoken=0; self._conversation_active=False; self._turns=0; self._last_interrupted=False
    def initialize(self):
        if self._initialized: return
        self.listener.initialize(); self.speaker.initialize(); self._initialized=True
    def start(self):
        if not self._initialized: self.initialize()
        self.listener.start()
    def stop(self):
        self.listener.stop(); self.speaker.stop(); self._sentence_barge_ready=False; self._conversation_active=False; self.listener.set_speaker_active(False,False)
    def listen(self, ignore_wake_word=False):
        if not self._initialized: self.initialize()
        self.diagnostics.start_stt()
        try: return self.listener.listen(ignore_wake_word=ignore_wake_word)
        except Exception as exc: self.diagnostics.error(exc); return None
        finally: self.diagnostics.finish_stt()
    def listen_turn(self): self._conversation_active=True; return self.listen(ignore_wake_word=True)
    def speak(self,text):
        """Speak the complete response in ONE TTS job; audio barge-in is disabled."""
        if not self._initialized: self.initialize()
        if not self.config.speak_enabled or not text.strip(): return False
        self.diagnostics.start_turn(); self._sentence_barge_ready=False; self._sentences_spoken=0; self._last_interrupted=False
        try:
            self.listener.set_speaker_active(True,False)
            self.diagnostics.start_tts(); ok=self.speaker.speak(str(text).strip()); self.diagnostics.finish_tts()
            if not ok: return False
            self._sentences_spoken=max(1, sum(1 for ch in str(text) if ch in ".!?")); self._sentence_barge_ready=True
            return True
        except Exception as exc: self.diagnostics.error(exc); return False
        finally:
            self.listener.set_speaker_active(False,False); self._sentence_barge_ready=False
    def begin_conversation(self): self._conversation_active=True; self._turns=0
    def end_conversation(self): self._conversation_active=False; self._turns=0; self._sentence_barge_ready=False
    @property
    def conversation_active(self): return self._conversation_active
    @property
    def turns(self): return self._turns
    @property
    def sentence_barge_ready(self): return self._sentence_barge_ready
    @property
    def sentences_spoken(self): return self._sentences_spoken
    @property
    def last_interrupted(self): return self._last_interrupted
    def devices(self): return self.listener.devices()
    def shutdown(self):
        if not self._initialized: return
        self.stop(); self.listener.shutdown(); self.speaker.shutdown(); self._initialized=False
    def health(self):
        return {"initialized":self._initialized,"enabled":self.config.enabled,"listening":self.listener.listening,"speaking":self.speaker.speaking,"conversation_active":self._conversation_active,"turns":self._turns,"barge_in_enabled":False,"sentence_barge_ready":False,"sentences_spoken":self._sentences_spoken,"last_interrupted":False,"wake_word_enabled":self.config.wake_word_enabled,"wake_word":self.config.wake_word,"wake_word_detected":self.listener.wake_word_detected,"wake_word_score":self.listener.wake_word_score,"last_heard":self.listener.last_heard,"vad_enabled":self.config.vad_enabled,"input_backend":self.listener.backend_name,"input_available":self.listener.available,"input_error":self.listener.error,"input_device":self.listener.device_name,"input_rms":self.listener.last_rms,"input_threshold":self.listener.last_threshold,"output_backend":self.speaker.__class__.__name__,"output_available":self.speaker.available,"output_error":self.speaker.error}
    def voice_diagnostics(self): return self.diagnostics.snapshot(self.health())
