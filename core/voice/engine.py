"""Core voice conversation pipeline for Webster Alpha."""
from __future__ import annotations
import re
from core.voice.config import VoiceConfig
from core.voice.listener import VoiceListener
from core.voice.speaker import VoiceSpeaker
from core.voice.stt import SpeechToTextBackend
from core.voice.diagnostics import VoiceDiagnostics

class VoiceEngine:
    """Coordinates wake-word listening, natural turns and diagnostics.

    Audio-only barge-in is intentionally disabled for now. Later it can be
    connected to camera lip-motion detection + audio speech detection.
    """
    _SENTENCE_RE = re.compile(r".+?(?:[.!?]+(?=\s|$)|$)", re.DOTALL)
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
    @classmethod
    def _split_sentences(cls,text): return [p.strip() for p in cls._SENTENCE_RE.findall(text) if p.strip()] or [text.strip()]
    def speak(self,text):
        """Speak the complete response without audio-only interruption."""
        if not self._initialized: self.initialize()
        if not self.config.speak_enabled or not text.strip(): return False
        self.diagnostics.start_turn(); sentences=self._split_sentences(text); self._sentence_barge_ready=False; self._sentences_spoken=0; self._last_interrupted=False
        try:
            # BARGE-IN DISABLED: do not monitor microphone while Webster speaks.
            self.listener.set_speaker_active(True,False)
            for sentence in sentences:
                self.diagnostics.start_tts(); ok=self.speaker.speak(sentence); self.diagnostics.finish_tts()
                if not ok: return False
                self._sentences_spoken+=1; self._sentence_barge_ready=self._sentences_spoken>=1
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
