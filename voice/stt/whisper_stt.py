"""
Whisper Speech-to-Text Module
Records audio from microphone with LIVE visual feedback.
Auto-detects speech start/stop based on silence.
"""

import io
import sys
import tempfile
import threading
import numpy as np
from config import settings


class WhisperSTT:
    """Speech-to-Text using OpenAI Whisper (local model) with live visualization."""

    def __init__(self):
        self.model = None
        self.sample_rate = 16000
        self.status = "initializing"
        self.is_recording = False
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

    def _volume_bar(self, volume: float, width: int = 30) -> str:
        """Create a visual volume bar."""
        # Normalize volume (typical range 0.0 - 0.1)
        level = min(int(volume * 500), width)
        if level < width * 0.3:
            color_char = "░"
        elif level < width * 0.7:
            color_char = "▒"
        else:
            color_char = "▓"

        bar = color_char * level + "·" * (width - level)
        return bar

    def listen_continuous(self, silence_threshold: float = 0.001,
                          silence_duration: float = 1.5,
                          speech_threshold: float = 0.003,
                          min_speech_chunks: int = 2,
                          max_duration: int = 30) -> str:
        """
        Continuously listen with live visual feedback.
        - Waits for speech to start (above speech_threshold)
        - Records until silence is detected
        - Shows live volume bar in terminal
        """
        try:
            import sounddevice as sd
        except ImportError:
            print("[STT] ❌ sounddevice not installed.")
            return ""

        if self.model is None:
            print("[STT] ❌ Whisper model not loaded.")
            return ""

        chunk_duration = 0.3  # 300ms chunks for responsive feedback
        chunk_size = int(self.sample_rate * chunk_duration)
        max_chunks = int(max_duration / chunk_duration)
        max_silent = int(silence_duration / chunk_duration)

        audio_chunks = []
        silent_chunks = 0
        speech_chunks = 0
        speech_started = False
        self.is_recording = True

        try:
            sys.stdout.write("\r[STT] 🎤 Listening... speak now!                    \n")
            sys.stdout.flush()

            for i in range(max_chunks):
                if not self.is_recording:
                    break

                # Record a chunk
                chunk = sd.rec(chunk_size, samplerate=self.sample_rate,
                               channels=1, dtype='float32')
                sd.wait()
                flat = chunk.flatten()
                volume = np.abs(flat).mean()

                # Live volume visualization
                bar = self._volume_bar(volume)
                if speech_started:
                    status = "🔴 REC"
                else:
                    status = "⚪ WAIT"

                sys.stdout.write(f"\r  {status} |{bar}| vol:{volume:.4f}")
                sys.stdout.flush()

                if not speech_started:
                    # Waiting for speech to start
                    if volume >= speech_threshold:
                        speech_started = True
                        audio_chunks.append(flat)
                        speech_chunks = 1
                        silent_chunks = 0
                        sys.stdout.write(f"\r  🔴 REC  |{bar}| Speech detected!      ")
                        sys.stdout.flush()
                else:
                    # Recording - check for silence
                    audio_chunks.append(flat)

                    if volume >= silence_threshold:
                        speech_chunks += 1
                        silent_chunks = 0
                    else:
                        silent_chunks += 1

                    # Stop if enough silence after sufficient speech
                    if silent_chunks >= max_silent and speech_chunks >= min_speech_chunks:
                        sys.stdout.write(f"\r  ⏹️ DONE |{'·' * 30}| Silence detected.      \n")
                        sys.stdout.flush()
                        break
                    # Also stop if way too much silence even without enough speech
                    elif silent_chunks >= max_silent * 3:
                        sys.stdout.write(f"\r  ⏹️ DONE |{'·' * 30}| Timeout - no speech.   \n")
                        sys.stdout.flush()
                        break

            self.is_recording = False

            if not audio_chunks or not speech_started or speech_chunks < min_speech_chunks:
                sys.stdout.write(f"\r  ⚠️ No speech detected (need to speak longer).         \n")
                sys.stdout.flush()
                return ""

            # Transcribe
            full_audio = np.concatenate(audio_chunks)
            duration_sec = len(full_audio) / self.sample_rate
            sys.stdout.write(f"\r  🔄 Transcribing {duration_sec:.1f}s of audio...              \n")
            sys.stdout.flush()

            text = self._transcribe_array(full_audio)
            return text

        except KeyboardInterrupt:
            self.is_recording = False
            sys.stdout.write("\n")
            return ""
        except Exception as e:
            self.is_recording = False
            print(f"\n[STT] ❌ Listen failed: {e}")
            return ""

    def listen(self, duration: int = 5) -> str:
        """Record audio for fixed duration and transcribe."""
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
        """Record until silence is detected, then transcribe. (Legacy method)"""
        # Redirect to the new continuous listener with visualization
        return self.listen_continuous(
            silence_threshold=silence_threshold,
            silence_duration=silence_duration,
            max_duration=max_duration
        )

    def _transcribe_array(self, audio_array: np.ndarray) -> str:
        """Transcribe a numpy audio array."""
        if self.model is None:
            return ""
        try:
            result = self.model.transcribe(audio_array, language="en")
            text = result.get("text", "").strip()
            if text:
                print(f"  📝 You said: \"{text}\"")
            return text
        except Exception as e:
            print(f"[STT] ❌ Transcription failed: {e}")
            return ""

    def contains_wake_word(self, text: str) -> bool:
        """Check if text contains the wake word."""
        wake = settings.wake_word.lower()
        return wake in text.lower()

    def stop_recording(self):
        """Stop the current recording."""
        self.is_recording = False
