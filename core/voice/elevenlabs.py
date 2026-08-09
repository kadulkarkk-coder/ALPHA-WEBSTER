"""ElevenLabs voice backend for Webster Alpha.

This module keeps cloud voice concerns behind Webster's existing voice
interfaces. It uses the ElevenLabs HTTP API so the core voice engine does
not depend on a particular SDK version.
"""

from __future__ import annotations

import io
import os
import time
import wave
from collections import deque
from threading import Event, Lock

import numpy as np


class ElevenLabsError(RuntimeError):
    """Raised when an ElevenLabs voice request cannot be completed."""


class ElevenLabsClient:
    """Small API client for ElevenLabs STT and TTS."""

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: str | None = None, *, tts_voice_id: str = "JBFqnCBsd6RMkjVDRZzb", tts_model_id: str = "eleven_multilingual_v2", stt_model_id: str = "scribe_v2") -> None:
        self.api_key = (api_key or os.getenv("ELEVENLABS_API_KEY", "")).strip()
        self.tts_voice_id = tts_voice_id.strip()
        self.tts_model_id = tts_model_id.strip()
        self.stt_model_id = stt_model_id.strip()

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.tts_voice_id)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ElevenLabsError("ELEVENLABS_API_KEY is not configured.")
        return {"xi-api-key": self.api_key}

    def transcribe(self, audio_wav: bytes, language_code: str | None = None) -> str:
        import requests

        data = {"model_id": self.stt_model_id}
        if language_code and language_code.lower() not in {"auto", "none"}:
            data["language_code"] = language_code.split("-")[0].lower()
        try:
            response = requests.post(
                f"{self.BASE_URL}/speech-to-text",
                headers=self._headers(),
                data=data,
                files={"file": ("webster.wav", audio_wav, "audio/wav")},
                timeout=60,
            )
            response.raise_for_status()
            return str(response.json().get("text", "")).strip()
        except Exception as error:
            raise ElevenLabsError(f"ElevenLabs STT failed: {error}") from error

    def synthesize(self, text: str, output_format: str = "mp3_44100_128") -> bytes:
        import requests

        if not text.strip():
            return b""
        try:
            response = requests.post(
                f"{self.BASE_URL}/text-to-speech/{self.tts_voice_id}",
                params={"output_format": output_format},
                headers={**self._headers(), "Content-Type": "application/json"},
                json={"text": text, "model_id": self.tts_model_id},
                timeout=60,
            )
            response.raise_for_status()
            return response.content
        except Exception as error:
            raise ElevenLabsError(f"ElevenLabs TTS failed: {error}") from error


def pcm16_wav(samples: np.ndarray, sample_rate: int = 16_000) -> bytes:
    """Encode mono float32 samples as 16-bit PCM WAV."""
    samples = np.clip(np.asarray(samples, dtype=np.float32).reshape(-1), -1.0, 1.0)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes((samples * 32767.0).astype(np.int16).tobytes())
    return buffer.getvalue()


class ElevenLabsSpeechBackend:
    """Microphone backend using sounddevice + ElevenLabs Scribe STT.

    VAD waits for speech energy, records until sustained silence, and then
    sends the captured WAV to Scribe. No PyAudio dependency is required.
    """

    name = "elevenlabs"

    def __init__(self, client: ElevenLabsClient | None = None, *, sample_rate: int = 16_000, channels: int = 1, block_ms: int = 30, max_phrase_seconds: float = 12.0, silence_seconds: float = 0.8) -> None:
        self.client = client or ElevenLabsClient()
        self.sample_rate = sample_rate
        self.channels = channels
        self.block_size = max(160, int(sample_rate * block_ms / 1000))
        self.max_phrase_seconds = max(1.0, float(max_phrase_seconds))
        self.silence_seconds = max(0.2, float(silence_seconds))
        self._available = False
        self._listening = False
        self._speaking = False
        self._allow_barge_in = False
        self._error: str | None = None
        self._stop_event = Event()
        self._lock = Lock()
        self._energy_threshold = 0.015

    def initialize(self) -> None:
        if self._available:
            return
        try:
            import sounddevice as sd
            sd.check_input_settings(samplerate=self.sample_rate, channels=self.channels, dtype="float32")
            if not self.client.configured:
                raise ElevenLabsError("ELEVENLABS_API_KEY is not configured.")
            self._available = True
            self._error = None
        except Exception as error:
            self._available = False
            self._error = str(error)

    def configure_vad(self, energy_threshold: int = 300, pause_threshold: float = 0.8) -> None:
        self._energy_threshold = max(0.005, min(0.08, float(energy_threshold) / 20000.0))
        self.silence_seconds = max(0.2, float(pause_threshold))

    def listen(self, timeout: float, phrase_timeout: float) -> str | None:
        if not self._available:
            self.initialize()
        if not self._available or (self._speaking and not self._allow_barge_in):
            return None

        try:
            import sounddevice as sd
        except Exception as error:
            self._error = str(error)
            return None

        self._stop_event.clear()
        queue: deque[np.ndarray] = deque()
        captured: list[np.ndarray] = []
        speech_started = False
        silence_blocks = 0
        start = time.monotonic()
        last_speech = start
        wait_limit = max(0.1, float(timeout))
        phrase_limit = max(0.5, float(phrase_timeout), self.max_phrase_seconds)
        silence_block_count = max(1, int(self.silence_seconds * 1000 / 30))

        def callback(indata, frames, callback_time, status) -> None:
            if status:
                self._error = str(status)
            with self._lock:
                queue.append(indata[:, 0].copy())

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype="float32", blocksize=self.block_size, callback=callback):
                self._listening = True
                while not self._stop_event.is_set():
                    now = time.monotonic()
                    if not speech_started and now - start >= wait_limit:
                        break
                    if speech_started and now - last_speech >= phrase_limit:
                        break

                    with self._lock:
                        block = queue.popleft() if queue else None
                    if block is None:
                        time.sleep(0.01)
                        continue

                    rms = float(np.sqrt(np.mean(np.square(block)) + 1e-12))
                    if rms >= self._energy_threshold:
                        speech_started = True
                        last_speech = now
                        silence_blocks = 0
                    elif speech_started:
                        silence_blocks += 1
                        if silence_blocks >= silence_block_count:
                            captured.append(block)
                            break

                    if speech_started:
                        captured.append(block)

                with self._lock:
                    while queue:
                        captured.append(queue.popleft())

            if not speech_started or not captured:
                return None
            audio = np.concatenate(captured).astype(np.float32)
            return self.client.transcribe(pcm16_wav(audio, self.sample_rate), language_code=None)
        except Exception as error:
            self._error = str(error)
            return None
        finally:
            self._listening = False

    def set_speaking(self, speaking: bool, allow_barge_in: bool = False) -> None:
        self._speaking = speaking
        self._allow_barge_in = allow_barge_in

    def stop(self) -> None:
        self._stop_event.set()
        self._listening = False

    def shutdown(self) -> None:
        self.stop()
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
