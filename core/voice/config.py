"""Configuration for Webster's local voice subsystem."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class VoiceConfig:
    enabled: bool=True; listen_enabled: bool=True; speak_enabled: bool=True; language: str="en"; rate: int=175; volume: float=1.0
    input_backend: str="faster_whisper"; output_backend: str="pyttsx3"; whisper_model: str="tiny.en"; whisper_device: str="cpu"; whisper_compute_type: str="int8"
    sample_rate: int=16000; channels: int=1; chunk_size: int=480; block_ms: int=30; input_device: int|None=None
    listen_timeout: float=8.0; max_phrase_seconds: float=20.0; silence_duration: float=1.35; pre_roll_seconds: float=0.35; start_blocks: int=2
    vad_enabled: bool=True; vad_energy_threshold: float=0.008; vad_multiplier: float=2.0; calibration_seconds: float=0.45
    wake_word_enabled: bool=True; wake_word: str="webster"; wake_word_similarity: float=0.72; wake_followup_timeout: float=10.0
    # Audio-only barge-in is temporarily disabled. Camera/lip-motion gating will be added later.
    barge_in_enabled: bool=False; barge_in_threshold_multiplier: float=3.0; barge_in_start_blocks: int=4; echo_calibration_seconds: float=0.35; echo_multiplier: float=1.8
    def __post_init__(self):
        self.rate=max(50,min(int(self.rate),400)); self.volume=max(0.0,min(float(self.volume),1.0)); self.sample_rate=max(8000,int(self.sample_rate)); self.channels=max(1,int(self.channels)); self.chunk_size=max(160,int(self.chunk_size)); self.block_ms=max(10,int(self.block_ms)); self.listen_timeout=max(1.0,float(self.listen_timeout)); self.max_phrase_seconds=max(1.0,float(self.max_phrase_seconds)); self.silence_duration=max(.6,float(self.silence_duration)); self.pre_roll_seconds=max(0.0,float(self.pre_roll_seconds)); self.start_blocks=max(1,int(self.start_blocks)); self.vad_energy_threshold=max(.001,float(self.vad_energy_threshold)); self.vad_multiplier=max(1.1,float(self.vad_multiplier)); self.calibration_seconds=max(.15,float(self.calibration_seconds)); self.wake_word=self.wake_word.strip().lower() or "webster"; self.wake_word_similarity=max(.5,min(float(self.wake_word_similarity),1.0)); self.wake_followup_timeout=max(1.0,float(self.wake_followup_timeout)); self.barge_in_threshold_multiplier=max(1.1,float(self.barge_in_threshold_multiplier)); self.barge_in_start_blocks=max(2,int(self.barge_in_start_blocks)); self.echo_calibration_seconds=max(.15,float(self.echo_calibration_seconds)); self.echo_multiplier=max(1.1,float(self.echo_multiplier)); self.input_backend=self.input_backend.strip().lower() or "faster_whisper"; self.output_backend=self.output_backend.strip().lower() or "pyttsx3"; self.whisper_model=self.whisper_model.strip() or "tiny.en"; self.whisper_device=self.whisper_device.strip().lower() or "cpu"; self.whisper_compute_type=self.whisper_compute_type.strip().lower() or "int8"
