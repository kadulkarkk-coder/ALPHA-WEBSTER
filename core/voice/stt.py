"""Local speech-to-text and voice-activity backends for Webster Alpha."""

from __future__ import annotations

import io
import time
import wave
from abc import ABC, abstractmethod
from collections import deque
from threading import Event, Lock

import numpy as np


class SpeechToTextBackend(ABC):
    """Contract for microphone/STT backends."""

    name = "unknown"

    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError


class NullSpeechBackend(SpeechToTextBackend):
    name = "none"

    def initialize(self) -> None:
        return

    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        return None

    def stop(self) -> None:
        return

    def shutdown(self) -> None:
        return

    @property
    def available(self) -> bool:
        return False


class FasterWhisperSpeechBackend(SpeechToTextBackend):
    """Local microphone + VAD + faster-whisper backend.

    Audio is captured with sounddevice, speech is detected from RMS energy,
    recording ends after sustained silence, and transcription happens locally.
    No PyAudio, API key, or cloud request is used.
    """

    name = "faster_whisper"

    def __init__(self, config=None) -> None:
        self.config = config
        self.sample_rate = int(getattr(config, "sample_rate", 16_000))
        self.channels = int(getattr(config, "channels", 1))
        block_ms = int(getattr(config, "block_ms", 30))
        self.block_size = max(160, int(self.sample_rate * block_ms / 1000))
        self.max_phrase_seconds = float(getattr(config, "max_phrase_seconds", 12.0))
        self.energy_threshold = float(getattr(config, "vad_energy_threshold", 0.015))
        self.pause_threshold = float(getattr(config, "vad_pause_threshold", 0.8))
        self.model_name = str(getattr(config, "whisper_model", "tiny.en"))
        self.device = str(getattr(config, "whisper_device", "cpu"))
        self.compute_type = str(getattr(config, "whisper_compute_type", "int8"))
        self.language = str(getattr(config, "language", "en")).split("-")[0]

        self._model = None
        self._available = False
        self._listening = False
        self._speaking = False
        self._allow_barge_in = False
        self._error: str | None = None
        self._stop_event = Event()
        self._lock = Lock()
        self._audio_queue: deque[np.ndarray] = deque()

    def initialize(self) -> None:
        if self._available:
            return
        try:
            import sounddevice as sd

            sd.check_input_settings(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
            )

            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
            self._available = True
            self._error = None
        except Exception as error:
            self._available = False
            self._model = None
            self._error = str(error)

    def configure_vad(self, energy_threshold: float = 0.015, pause_threshold: float = 0.8) -> None:
        self.energy_threshold = max(0.001, float(energy_threshold))
        self.pause_threshold = max(0.2, float(pause_threshold))

    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        if not self._available:
            self.initialize()
        if not self._available or self._model is None:
            return None
        if self._speaking and not self._allow_barge_in:
            return None

        try:
            import sounddevice as sd
        except Exception as error:
            self._error = str(error)
            return None

        self._stop_event.clear()
        with self._lock:
            self._audio_queue.clear()

        captured: list[np.ndarray] = []
        speech_started = False
        silence_blocks = 0
        start = time.monotonic()
        last_speech = start
        wait_limit = max(0.1, float(timeout))
        phrase_limit = max(0.5, min(float(phrase_timeout), self.max_phrase_seconds))
        silence_block_count = max(1, int(self.pause_threshold * 1000 / max(10, int(self.block_size * 1000 / self.sample_rate))))

        def callback(indata, frames, callback_time, status) -> None:
            if status:
                self._error = str(status)
            samples = np.asarray(indata[:, 0], dtype=np.float32).copy()
            with self._lock:
                self._audio_queue.append(samples)

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                blocksize=self.block_size,
                callback=callback,
            ):
                self._listening = True

                while not self._stop_event.is_set():
                    now = time.monotonic()
                    if not speech_started and now - start >= wait_limit:
                        break
                    if speech_started and now - last_speech >= phrase_limit:
                        break

                    with self._lock:
                        block = self._audio_queue.popleft() if self._audio_queue else None
                    if block is None:
                        time.sleep(0.01)
                        continue

                    rms = float(np.sqrt(np.mean(np.square(block)) + 1e-12))
                    is_speech = rms >= self.energy_threshold

                    if is_speech:
                        speech_started = True
                        last_speech = now
                        silence_blocks = 0
                        captured.append(block)
                    elif speech_started:
                        captured.append(block)
                        silence_blocks += 1
                        if silence_blocks >= silence_block_count:
                            break

                with self._lock:
                    while self._audio_queue:
                        captured.append(self._audio_queue.popleft())

            if not speech_started or not captured or self._stop_event.is_set():
                return None

            audio = np.concatenate(captured).astype(np.float32)
            wav = self._to_wav(audio)
            return self._transcribe(wav)

        except Exception as error:
            self._error = str(error)
            return None
        finally:
            self._listening = False

    def _transcribe(self, wav_data: bytes) -> str | None:
        if self._model is None:
            return None

        try:
            segments, _info = self._model.transcribe(
                io.BytesIO(wav_data),
                language=self.language,
                beam_size=1,
                vad_filter=True,
                condition_on_previous_text=False,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            return text or None
        except Exception as error:
            self._error = str(error)
            return None

    def _to_wav(self, samples: np.ndarray) -> bytes:
        clipped = np.clip(samples, -1.0, 1.0)
        pcm = (clipped * 32767.0).astype(np.int16).tobytes()
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(pcm)
        return buffer.getvalue()

    def set_speaking(self, speaking: bool, allow_barge_in: bool = False) -> None:
        self._speaking = speaking
        self._allow_barge_in = allow_barge_in

    def stop(self) -> None:
        self._stop_event.set()
        self._listening = False

    def shutdown(self) -> None:
        self.stop()
        self._model = None
        self._available = False

    @property
    def available(self) -> bool:
        return self._available and (not self._speaking or self._allow_barge_in)

    @property
    def listening(self) -> bool:
        return self._listening

    @property
    def speaking(self) -> bool:
        return self._speaking

    @property
    def error(self) -> str | None:
        return self._error


# Backward-compatible name for code that expects a microphone backend.
MicrophoneSpeechBackend = FasterWhisperSpeechBackend
