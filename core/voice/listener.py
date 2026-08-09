"""Speech input coordinator for Webster Alpha."""
from __future__ import annotations
import re
from difflib import SequenceMatcher
from core.voice.config import VoiceConfig
from core.voice.stt import FasterWhisperSpeechBackend, NullSpeechBackend

class VoiceListener:
    """Owns faster-whisper microphone input, wake-word filtering and microphone policy."""
    _WAKE_PREFIX_RE = re.compile(r"^[,.:;!?\-\s]+")
    def __init__(self, config: VoiceConfig | None = None, backend=None) -> None:
        self.config=config or VoiceConfig(); self._backend=backend or self._build_backend(); self._initialized=False; self._listening=False; self._error=None; self._wake_word_detected=False; self._last_heard=None; self._last_wake_score=0.0; self._wake_candidates=0
    def _build_backend(self):
        # faster-whisper + sounddevice is the supported Python 3.14 microphone path.
        if self.config.input_backend in {"pyaudio","pyaudio_whisper","microphone"}: return FasterWhisperSpeechBackend(self.config)
        if self.config.input_backend in {"sounddevice_whisper","faster_whisper","faster-whisper"}: return FasterWhisperSpeechBackend(self.config)
        return NullSpeechBackend()
    def initialize(self):
        if self._initialized: return
        self._error=None
        if not self.config.enabled or not self.config.listen_enabled: self._backend=NullSpeechBackend()
        try: self._backend.initialize()
        except Exception as exc: self._error=str(exc)
        self._initialized=True
    def start(self):
        if not self._initialized: self.initialize()
        self._listening=False
    def stop(self):
        try: self._backend.stop()
        except Exception as exc: self._error=str(exc)
        self._listening=False
    @staticmethod
    def _normalize(text):
        text=re.sub(r"[^a-z0-9\s]"," ",VoiceListener._WAKE_PREFIX_RE.sub("",text.lower().strip())); return " ".join(text.split())
    def _wake_aliases(self):
        configured=str(self.config.wake_word or "webster").strip().lower(); return list(dict.fromkeys([configured,"web stir","webster"] if configured=="webster" else [configured]))
    def _match_wake_word(self,text):
        normalized=self._normalize(text)
        if not normalized: return False,"",0.0
        aliases=self._wake_aliases(); words=normalized.split(); best_score=0.0; best_alias=aliases[0]; best_index=-1
        for alias in aliases:
            aw=alias.split(); width=len(aw)
            for index in range(max(1,len(words)-width+1)):
                if " ".join(words[index:index+width])==alias: best_score=1.0; best_alias=alias; best_index=index; break
            if best_score==1.0: break
        if best_score<1.0:
            for count in (1,2):
                if len(words)>=count:
                    candidate=" ".join(words[:count])
                    for alias in aliases:
                        score=SequenceMatcher(None,candidate,alias).ratio()
                        if score>best_score: best_score=score; best_alias=alias; best_index=0
        if best_score<float(getattr(self.config,"wake_word_similarity",0.78)): return False,"",best_score
        self._wake_candidates+=1; remainder=words[best_index+len(best_alias.split()):] if best_index>=0 else []
        return True," ".join(remainder).strip(),best_score
    def listen(self,ignore_wake_word=False):
        if not self._initialized: self.initialize()
        if not self.config.enabled or not self.config.listen_enabled or not self._backend.available: return None
        try:
            self._listening=True; text=self._backend.listen(timeout=self.config.listen_timeout,phrase_timeout=self.config.max_phrase_seconds)
            if not text: self._wake_word_detected=False; self._last_wake_score=0.0; return None
            text=" ".join(text.strip().split()); self._last_heard=text
            if ignore_wake_word or not self.config.wake_word_enabled: self._wake_word_detected=True; self._last_wake_score=1.0; return text
            matched,command,score=self._match_wake_word(text); self._last_wake_score=score; self._wake_word_detected=matched
            if not matched: return None
            if command: return command
            follow=self._backend.listen(timeout=self.config.wake_followup_timeout,phrase_timeout=self.config.max_phrase_seconds)
            if follow: self._last_heard=" ".join(follow.strip().split()); return self._last_heard or None
            return None
        except Exception as exc: self._error=str(exc); return None
        finally: self._listening=False
    def set_speaker_active(self,active,allow_barge_in=False):
        setter=getattr(self._backend,"set_speaking",None)
        if callable(setter): setter(active,allow_barge_in)
    def listen_for_barge_in(self,stop_event):
        method=getattr(self._backend,"listen_for_barge_in",None)
        if callable(method): return bool(method(stop_event))
        return False
    def devices(self):
        method=getattr(self._backend,"devices",None); return method() if callable(method) else []
    @property
    def initialized(self): return self._initialized
    @property
    def listening(self): return self._listening or bool(getattr(self._backend,"listening",False))
    @property
    def available(self): return self._backend.available
    @property
    def backend_name(self): return self._backend.name
    @property
    def wake_word_detected(self): return self._wake_word_detected
    @property
    def wake_word_score(self): return self._last_wake_score
    @property
    def wake_word_candidates(self): return self._wake_candidates
    @property
    def last_heard(self): return self._last_heard
    @property
    def error(self): return self._error or getattr(self._backend,"error",None)
    @property
    def device_name(self): return getattr(self._backend,"device_name",None)
    @property
    def last_rms(self): return float(getattr(self._backend,"last_rms",0.0))
    @property
    def last_threshold(self): return float(getattr(self._backend,"last_threshold",0.0))
    def shutdown(self):
        self.stop()
        try: self._backend.shutdown()
        except Exception as exc: self._error=str(exc)
        self._initialized=False
