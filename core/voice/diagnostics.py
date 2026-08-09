"""Diagnostics and lightweight latency telemetry for Webster voice."""
from __future__ import annotations
from collections import deque
from time import monotonic

class VoiceDiagnostics:
    def __init__(self, history_size: int = 20) -> None:
        self._stt_started = 0.0
        self._tts_started = 0.0
        self._turn_started = 0.0
        self._stt_ms = deque(maxlen=history_size)
        self._tts_ms = deque(maxlen=history_size)
        self._round_trip_ms = deque(maxlen=history_size)
        self._errors = deque(maxlen=10)

    def start_turn(self): self._turn_started = monotonic()
    def start_stt(self): self._stt_started = monotonic()
    def finish_stt(self):
        if not self._stt_started: return 0.0
        value = (monotonic() - self._stt_started) * 1000
        self._stt_ms.append(value); self._stt_started = 0.0; return value
    def start_tts(self): self._tts_started = monotonic()
    def finish_tts(self):
        if not self._tts_started: return 0.0
        value = (monotonic() - self._tts_started) * 1000
        self._tts_ms.append(value); self._tts_started = 0.0
        if self._turn_started:
            self._round_trip_ms.append((monotonic() - self._turn_started) * 1000)
            self._turn_started = 0.0
        return value
    def error(self, message):
        if message: self._errors.append(str(message))
    @staticmethod
    def _avg(values): return sum(values) / len(values) if values else 0.0
    def snapshot(self, health):
        errors = list(self._errors)
        for key in ("input_error", "output_error"):
            if health.get(key): errors.append(str(health[key]))
        return {
            "status": "healthy" if not errors and health.get("input_available", False) else "degraded",
            "input": {"available": bool(health.get("input_available")), "backend": health.get("input_backend"), "device": health.get("input_device"), "listening": bool(health.get("listening")), "rms": round(float(health.get("input_rms", 0.0)), 5), "threshold": round(float(health.get("input_threshold", 0.0)), 5), "vad": bool(health.get("vad_enabled"))},
            "stt": {"latency_ms": round(self._avg(self._stt_ms), 1), "samples": len(self._stt_ms)},
            "wake_word": {"enabled": bool(health.get("wake_word_enabled")), "word": health.get("wake_word"), "detected": bool(health.get("wake_word_detected")), "score": round(float(health.get("wake_word_score", 0.0)), 3)},
            "conversation": {"active": bool(health.get("conversation_active")), "turns": int(health.get("turns", 0)), "last_heard": health.get("last_heard")},
            "barge_in": {"enabled": bool(health.get("barge_in_enabled")), "ready": bool(health.get("sentence_barge_ready")), "sentences_spoken": int(health.get("sentences_spoken", 0)), "last_interrupted": bool(health.get("last_interrupted"))},
            "output": {"available": bool(health.get("output_available")), "backend": health.get("output_backend"), "speaking": bool(health.get("speaking")), "tts_latency_ms": round(self._avg(self._tts_ms), 1)},
            "round_trip_ms": round(self._avg(self._round_trip_ms), 1),
            "errors": errors,
        }
