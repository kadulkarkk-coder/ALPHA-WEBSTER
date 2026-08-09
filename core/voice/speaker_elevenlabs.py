"""ElevenLabs text-to-speech speaker for Webster Alpha."""

from __future__ import annotations

from threading import Event

import numpy as np

from core.voice.elevenlabs import ElevenLabsClient


class ElevenLabsSpeaker:
    """Cloud TTS backend with local playback and stop support."""

    name = "elevenlabs"

    def __init__(self, config, client: ElevenLabsClient | None = None) -> None:
        self.config = config
        self.client = client or ElevenLabsClient(
            tts_voice_id=config.elevenlabs_voice_id,
            tts_model_id=config.elevenlabs_tts_model,
            stt_model_id=config.elevenlabs_stt_model,
        )
        self._initialized = False
        self._speaking = False
        self._available = False
        self._error: str | None = None
        self._stop_event = Event()

    def initialize(self) -> None:
        if self._initialized:
            return
        try:
            import miniaudio
            import sounddevice
            del miniaudio, sounddevice
            if not self.client.configured:
                raise RuntimeError("ELEVENLABS_API_KEY is not configured.")
            self._available = True
            self._error = None
        except Exception as error:
            self._available = False
            self._error = str(error)
        self._initialized = True

    def speak(self, text: str) -> bool:
        if not self._initialized:
            self.initialize()
        if not self._available or not text.strip():
            return False

        try:
            import miniaudio
            import sounddevice as sd

            self._stop_event.clear()
            self._speaking = True
            audio_bytes = self.client.synthesize(text)
            if not audio_bytes or self._stop_event.is_set():
                return False

            decoded = miniaudio.decode(
                audio_bytes,
                output_format=miniaudio.SampleFormat.FLOAT32,
                nchannels=1,
            )
            samples = np.asarray(decoded.samples, dtype=np.float32)
            sd.play(samples, decoded.sample_rate)

            while not self._stop_event.wait(0.05):
                if not sd.get_stream():
                    break
                # sounddevice does not expose a portable is-playing flag;
                # wait() gives reliable completion for the normal path.
                break
            if not self._stop_event.is_set():
                sd.wait()
            else:
                sd.stop()
            return not self._stop_event.is_set()
        except Exception as error:
            self._error = str(error)
            return False
        finally:
            self._speaking = False

    def stop(self) -> None:
        self._stop_event.set()
        try:
            import sounddevice as sd
            sd.stop()
        except Exception:
            pass
        self._speaking = False

    def shutdown(self) -> None:
        self.stop()
        self._initialized = False
        self._available = False

    @property
    def speaking(self) -> bool:
        return self._speaking

    @property
    def available(self) -> bool:
        return self._available

    @property
    def error(self) -> str | None:
        return self._error
