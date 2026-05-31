"""
Whisper Speech-to-Text Module
Records audio from microphone and transcribes using OpenAI Whisper.
"""

import io
import tempfile
import numpy as np
from config import settings


class WhisperSTT:
    """Speech-to-Text using OpenAI Whisper (local model)."""

    def __init__(self):
        self.model = None
        self.sample_rate = 16000
        self.status = "initializing"
        print("[STT] 🎤 Initializing Whisper Speech-to-Text...")

    def initialize(self):
        """Load whisper model."""
        try:
            import whisper
            self.model = whisper.load_model(settings.whisper_model)
            self.status = "active"
            print(f"[STT] ✅ Whisper '{settings.whisper_model}' model loaded.")
        except Exception as e:
            print(f"[STT] ❌ Whisper init failed: {e}")
            self.status = "error"

    def listen(self, duration: int = 5) -> str:
        """Record audio and transcribe."""
        try:
            import sounddevice as sd
            print(f"[STT] 🎤 Listening for {duration} seconds...")
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1, dtype='float32'
            )
            sd.wait()
            print("[STT] 🔄 Transcribing...")
            return self._transcribe_array(audio.flatten())
        except Exception as e:
            print(f"[STT] ❌ Listen failed: {e}")
            return ""

    def listen_until_silence(self, silence_threshold: float = 0.01,
                              silence_duration: float = 1.5,
                              max_duration: int = 30) -> str:
        """Record until silence is detected, then transcribe."""
        try:
            import sounddevice as sd
            print("[STT] 🎤 Listening (speak now, will stop on silence)...")
            chunk_size = int(self.sample_rate * 0.5)
            audio_chunks = []
            silent_chunks = 0
            max_silent = int(silence_duration / 0.5)
            max_chunks = int(max_duration / 0.5)

            for i in range(max_chunks):
                chunk = sd.rec(chunk_size, samplerate=self.sample_rate,
                             channels=1, dtype='float32')
                sd.wait()
                audio_chunks.append(chunk.flatten())

                volume = np.abs(chunk).mean()
                if volume < silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if silent_chunks >= max_silent and len(audio_chunks) > 2:
                    break

            if not audio_chunks:
                return ""

            full_audio = np.concatenate(audio_chunks)
            print("[STT] 🔄 Transcribing...")
            return self._transcribe_array(full_audio)
        except Exception as e:
            print(f"[STT] ❌ Listen failed: {e}")
            return ""

    def _transcribe_array(self, audio_array: np.ndarray) -> str:
        """Transcribe a numpy audio array."""
        if self.model is None:
            return ""
        try:
            result = self.model.transcribe(audio_array, language="en")
            text = result.get("text", "").strip()
            print(f"[STT] 📝 Transcribed: '{text}'")
            return text
        except Exception as e:
            print(f"[STT] ❌ Transcription failed: {e}")
            return ""

    def contains_wake_word(self, text: str) -> bool:
        """Check if text contains the wake word."""
        wake = settings.wake_word.lower()
        return wake in text.lower()
