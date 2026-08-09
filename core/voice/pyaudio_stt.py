"""PyAudio microphone transport with VAD and faster-whisper."""
from __future__ import annotations

import time
from collections import deque
from threading import Event

import numpy as np
from faster_whisper import WhisperModel

from core.voice.stt import SpeechToTextBackend


class PyAudioWhisperBackend(SpeechToTextBackend):
    name = "pyaudio_whisper"

    def __init__(self, config=None) -> None:
        self.config = config
        self.sample_rate = int(getattr(config, "sample_rate", 16000))
        self.channels = int(getattr(config, "channels", 1))
        self.chunk = int(getattr(config, "chunk_size", 480))
        self.device_index = getattr(config, "input_device", None)
        self.model_name = str(getattr(config, "whisper_model", "tiny.en"))
        self.whisper_device = str(getattr(config, "whisper_device", "cpu"))
        self.compute_type = str(getattr(config, "whisper_compute_type", "int8"))
        self.threshold = float(getattr(config, "vad_energy_threshold", 0.008))
        self.multiplier = float(getattr(config, "vad_multiplier", 2.0))
        self.calibration = float(getattr(config, "calibration_seconds", 0.45))
        self.silence = float(getattr(config, "silence_duration", 0.65))
        self.max_phrase = float(getattr(config, "max_phrase_seconds", 12.0))
        self.start_blocks = int(getattr(config, "start_blocks", 2))
        self._pa = None
        self._model = None
        self._available = False
        self._listening = False
        self._speaking = False
        self._allow_barge = False
        self._stop = Event()
        self._error = None
        self._device_name = None
        self._rms = 0.0
        self._last_threshold = self.threshold

    def initialize(self) -> None:
        if self._available:
            return
        try:
            import pyaudio
            self._pa = pyaudio.PyAudio()
            if self.device_index is None:
                self.device_index = int(self._pa.get_default_input_device_info()["index"])
            info = self._pa.get_device_info_by_index(self.device_index)
            if int(info.get("maxInputChannels", 0)) < 1:
                raise RuntimeError("Selected microphone has no input channels")
            self._device_name = str(info.get("name", self.device_index))
            self._model = WhisperModel(self.model_name, device=self.whisper_device, compute_type=self.compute_type)
            self._available = True
            self._error = None
        except Exception as exc:
            self._available = False
            self._error = f"PyAudio/Whisper initialization failed: {exc}"
            if self._pa is not None:
                try: self._pa.terminate()
                except Exception: pass
            self._pa = None

    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        if not self._available:
            self.initialize()
        if not self._available or self._pa is None or self._model is None:
            return None
        if self._speaking and not self._allow_barge:
            return None
        import pyaudio
        self._stop.clear()
        stream = None
        frames = []
        preroll = deque(maxlen=max(1, int(0.25 * self.sample_rate / self.chunk)))
        started = False
        voiced = 0
        started_at = time.monotonic()
        last_voice = started_at
        calibration = []
        calibrated = False
        block_seconds = self.chunk / self.sample_rate
        phrase_limit = min(float(phrase_timeout), self.max_phrase)
        try:
            stream = self._pa.open(format=pyaudio.paInt16, channels=self.channels, rate=self.sample_rate,
                                   input=True, input_device_index=self.device_index,
                                   frames_per_buffer=self.chunk)
            self._listening = True
            while not self._stop.is_set():
                now = time.monotonic()
                if not started and now - started_at >= max(0.5, float(timeout)):
                    break
                raw = stream.read(self.chunk, exception_on_overflow=False)
                audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                if self.channels > 1:
                    audio = audio.reshape(-1, self.channels).mean(axis=1)
                rms = float(np.sqrt(np.mean(audio * audio) + 1e-12))
                self._rms = rms
                if not started and not calibrated:
                    calibration.append(rms)
                    if len(calibration) >= max(5, int(self.calibration / block_seconds)):
                        self._last_threshold = max(self.threshold, float(np.median(calibration)) * self.multiplier)
                        calibrated = True
                limit = self._last_threshold if calibrated else self.threshold
                if self._speaking and self._allow_barge:
                    limit *= float(getattr(self.config, "barge_in_threshold_multiplier", 3.0))
                is_voice = rms >= limit
                preroll.append(audio)
                voiced = voiced + 1 if is_voice else 0
                if not started:
                    if voiced >= self.start_blocks:
                        started = True
                        frames.extend(preroll)
                        last_voice = now
                    continue
                frames.append(audio)
                if is_voice:
                    last_voice = now
                elif now - last_voice >= max(0.25, self.silence):
                    break
                elif now - started_at >= phrase_limit:
                    break
            if not started or not frames or self._stop.is_set():
                return None
            audio = np.concatenate(frames).astype(np.float32)
            audio -= float(np.mean(audio))
            segments, _ = self._model.transcribe(audio, language=str(getattr(self.config, "language", "en")).split("-")[0],
                                                  beam_size=1, best_of=1, temperature=0.0,
                                                  vad_filter=True, condition_on_previous_text=False,
                                                  without_timestamps=True)
            text = " ".join(s.text.strip() for s in segments).strip()
            return text or None
        except Exception as exc:
            self._error = f"PyAudio capture/transcription failed: {exc}"
            return None
        finally:
            self._listening = False
            if stream is not None:
                try: stream.stop_stream(); stream.close()
                except Exception: pass

    def set_speaking(self, speaking: bool, allow_barge_in: bool = False) -> None:
        self._speaking = bool(speaking)
        self._allow_barge = bool(allow_barge_in)

    def stop(self) -> None:
        self._stop.set()
        self._listening = False

    def shutdown(self) -> None:
        self.stop()
        self._model = None
        self._available = False
        if self._pa is not None:
            try: self._pa.terminate()
            except Exception: pass
        self._pa = None

    def devices(self) -> list[dict]:
        try:
            import pyaudio
            pa = self._pa or pyaudio.PyAudio()
            owned = self._pa is None
            result = []
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if int(info.get("maxInputChannels", 0)) > 0:
                    result.append({"index": i, "name": info.get("name"), "inputs": info.get("maxInputChannels"), "samplerate": info.get("defaultSampleRate")})
            if owned: pa.terminate()
            return result
        except Exception as exc:
            self._error = f"PyAudio device enumeration failed: {exc}"
            return []

    @property
    def available(self) -> bool: return self._available
    @property
    def listening(self) -> bool: return self._listening
    @property
    def error(self) -> str | None: return self._error
    @property
    def device_name(self) -> str | None: return self._device_name
    @property
    def last_rms(self) -> float: return self._rms
    @property
    def last_threshold(self) -> float: return self._last_threshold
