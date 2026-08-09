"""Reliable local microphone, VAD and faster-whisper speech recognition."""
from __future__ import annotations
import time
from abc import ABC, abstractmethod
from collections import deque
from threading import Event, Lock
import numpy as np

class SpeechToTextBackend(ABC):
    name = "unknown"
    @abstractmethod
    def initialize(self) -> None: ...
    @abstractmethod
    def listen(self, timeout: float, phrase_timeout: float) -> str | None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def shutdown(self) -> None: ...
    @property
    @abstractmethod
    def available(self) -> bool: ...

class NullSpeechBackend(SpeechToTextBackend):
    name = "none"
    def initialize(self) -> None: return
    def listen(self, timeout, phrase_timeout): return None
    def stop(self) -> None: return
    def shutdown(self) -> None: return
    @property
    def available(self): return False

class FasterWhisperSpeechBackend(SpeechToTextBackend):
    """Persistent sounddevice microphone + faster-whisper backend."""
    name = "sounddevice_whisper"

    def __init__(self, config=None):
        self.config=config
        self.sample_rate=int(getattr(config,"sample_rate",16000)); self.channels=1
        self.block_size=max(160,int(self.sample_rate*int(getattr(config,"block_ms",30))/1000))
        self.max_phrase_seconds=float(getattr(config,"max_phrase_seconds",20.0))
        self.energy_threshold=float(getattr(config,"vad_energy_threshold",0.008))
        self.vad_multiplier=float(getattr(config,"vad_multiplier",2.2))
        self.silence_duration=float(getattr(config,"silence_duration",1.35))
        self.pre_roll_seconds=float(getattr(config,"pre_roll_seconds",0.35))
        self.start_blocks=max(1,int(getattr(config,"start_blocks",2)))
        self.model_name=str(getattr(config,"whisper_model","tiny.en")); self.device=str(getattr(config,"whisper_device","cpu")); self.compute_type=str(getattr(config,"whisper_compute_type","int8")); self.language=str(getattr(config,"language","en")).split("-")[0]
        self.input_device=getattr(config,"input_device",None); self._model=None; self._stream=None; self._available=False; self._listening=False; self._speaking=False; self._allow_barge_in=False; self._error=None; self._stop_event=Event(); self._lock=Lock(); self._queue=deque(maxlen=1200); self._last_rms=0.0; self._last_threshold=self.energy_threshold; self._device_name=None

    def initialize(self):
        if self._available: return
        try:
            import sounddevice as sd
            device=self.input_device if self.input_device is not None else sd.default.device[0]
            info=sd.query_devices(device,"input")
            if int(info.get("max_input_channels",0))<1: raise RuntimeError("Selected microphone has no input channels.")
            self._device_name=str(info.get("name",device)); samplerate=int(round(float(info.get("default_samplerate",self.sample_rate))))
            try: sd.check_input_settings(device=device,samplerate=self.sample_rate,channels=1,dtype="float32")
            except Exception: self.sample_rate=samplerate; self.block_size=max(160,int(self.sample_rate*.03))
            from faster_whisper import WhisperModel
            self._model=WhisperModel(self.model_name,device=self.device,compute_type=self.compute_type); self._available=True; self._error=None
        except Exception as error:
            self._available=False; self._model=None; self._error=f"Voice input initialization failed: {error}"

    def start(self):
        if not self._available: self.initialize()
        if not self._available or self._stream is not None: return
        try:
            import sounddevice as sd
            self._stop_event.clear()
            with self._lock: self._queue.clear()
            def callback(indata,frames,callback_time,status):
                if status: self._error=f"Microphone status: {status}"
                # Keep the persistent stream alive, but discard speaker echo.
                if self._speaking and not self._allow_barge_in: return
                samples=np.asarray(indata,dtype=np.float32)
                if samples.ndim>1: samples=samples[:,0]
                with self._lock: self._queue.append(samples.copy())
            self._stream=sd.InputStream(device=self.input_device,samplerate=self.sample_rate,channels=1,dtype="float32",blocksize=self.block_size,callback=callback); self._stream.start(); self._error=None
        except Exception as error:
            self._stream=None; self._error=f"Microphone stream failed to start: {error}"

    def prepare_for_user(self):
        """Discard audio captured before the user turn without restarting the stream."""
        with self._lock: self._queue.clear()
        self._stop_event.clear()

    def _get_block(self):
        with self._lock: return self._queue.popleft() if self._queue else None

    def listen(self,timeout,phrase_timeout):
        if not self._available: self.initialize()
        if not self._available or self._model is None: return None
        if self._stream is None: self.start()
        if self._stream is None: return None
        # Do not clear the queue here. A user may already be speaking while the
        # previous turn is being finalized. The manager explicitly calls
        # prepare_for_user() after TTS when a clean boundary is required.
        self._stop_event.clear(); captured=[]; pre_roll=deque(maxlen=max(1,int(self.pre_roll_seconds/.03))); speech_started=False; voiced_blocks=0; start_time=time.monotonic(); last_voice=start_time; block_seconds=self.block_size/self.sample_rate; silence_limit=max(.8,self.silence_duration); phrase_limit=max(2.,min(float(phrase_timeout),self.max_phrase_seconds)); timeout_limit=max(.5,float(timeout)); calibration=[]; calibrated=False
        try:
            self._listening=True
            while not self._stop_event.is_set():
                now=time.monotonic(); block=self._get_block()
                if block is None:
                    if not speech_started and now-start_time>=timeout_limit: break
                    time.sleep(.005); continue
                rms=float(np.sqrt(np.mean(np.square(block))+1e-12)); self._last_rms=rms
                if not speech_started and not calibrated:
                    calibration.append(rms)
                    if len(calibration)>=max(5,int(.45/block_seconds)):
                        ambient=float(np.median(calibration)); self._last_threshold=max(self.energy_threshold,ambient*self.vad_multiplier); calibrated=True
                threshold=self._last_threshold if calibrated else self.energy_threshold; pre_roll.append(block); voiced=rms>=threshold; voiced_blocks=voiced_blocks+1 if voiced else 0
                if not speech_started:
                    if voiced_blocks>=self.start_blocks: speech_started=True; captured.extend(list(pre_roll)); last_voice=now
                    elif now-start_time>=timeout_limit: break
                else:
                    captured.append(block)
                    if voiced: last_voice=now
                    elif now-last_voice>=silence_limit: break
                    elif now-start_time>=phrase_limit: break
            if not speech_started or not captured or self._stop_event.is_set(): return None
            audio=np.concatenate(captured).astype(np.float32); audio=audio-float(np.mean(audio)); peak=float(np.max(np.abs(audio))) if audio.size else 0.0
            if 0<peak<.15: audio=np.clip(audio*(.15/peak),-1.,1.)
            return self._transcribe(audio)
        except Exception as error:
            self._error=f"Microphone capture failed: {error}"; return None
        finally: self._listening=False

    def _transcribe(self,audio):
        try:
            segments,_info=self._model.transcribe(audio,language=self.language,task="transcribe",beam_size=1,best_of=1,temperature=0.0,vad_filter=True,vad_parameters={"min_silence_duration_ms":900},condition_on_previous_text=False,without_timestamps=True)
            text=" ".join(segment.text.strip() for segment in segments).strip(); return text or None
        except Exception as error:
            self._error=f"Whisper transcription failed: {error}"; return None

    def set_speaking(self,speaking,allow_barge_in=False): self._speaking=speaking; self._allow_barge_in=allow_barge_in
    def stop(self):
        self._stop_event.set(); self._listening=False; stream,self._stream=self._stream,None
        if stream is not None:
            try: stream.stop(); stream.close()
            except Exception: pass
    def shutdown(self): self.stop(); self._model=None; self._available=False
    def devices(self):
        try:
            import sounddevice as sd
            return [{"index":i,"name":x.get("name"),"inputs":x.get("max_input_channels"),"samplerate":x.get("default_samplerate")} for i,x in enumerate(sd.query_devices()) if int(x.get("max_input_channels",0))>0]
        except Exception as error: self._error=f"Could not enumerate microphones: {error}"; return []
    @property
    def available(self): return self._available
    @property
    def listening(self): return self._listening
    @property
    def speaking(self): return self._speaking
    @property
    def error(self): return self._error
    @property
    def device_name(self): return self._device_name
    @property
    def last_rms(self): return self._last_rms
    @property
    def last_threshold(self): return self._last_threshold

MicrophoneSpeechBackend=FasterWhisperSpeechBackend
