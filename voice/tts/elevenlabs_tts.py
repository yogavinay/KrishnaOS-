"""
ElevenLabs Text-to-Speech Module
Converts text to speech and plays through speakers.
"""

import io
import threading
from config import settings


class ElevenLabsTTS:
    """Text-to-Speech using ElevenLabs API."""

    def __init__(self):
        self.client = None
        self.voice_id = settings.elevenlabs_voice_id
        self.status = "initializing"
        print("[TTS] 🔊 Initializing ElevenLabs Text-to-Speech...")

    def initialize(self):
        """Initialize ElevenLabs client."""
        try:
            if not settings.elevenlabs_api_key:
                print("[TTS] ⚠️ No ElevenLabs API key. Using print fallback.")
                self.status = "fallback"
                return

            from elevenlabs import ElevenLabs
            self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)
            self.status = "active"
            print("[TTS] ✅ ElevenLabs TTS ready.")
        except Exception as e:
            print(f"[TTS] ❌ Init failed: {e}. Using print fallback.")
            self.status = "fallback"

    def speak(self, text: str):
        """Convert text to speech and play it."""
        print(f"[TTS] 🗣️ KRISHNA: {text}")

        if self.status == "fallback" or not self.client:
            return

        try:
            audio_gen = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_monolingual_v1",
                output_format="mp3_44100_128"
            )

            # Collect audio bytes
            audio_bytes = b""
            for chunk in audio_gen:
                audio_bytes += chunk

            # Play audio in a thread to not block
            thread = threading.Thread(
                target=self._play_audio, args=(audio_bytes,), daemon=True
            )
            thread.start()
            thread.join()  # Wait for playback
        except Exception as e:
            print(f"[TTS] ⚠️ Speech failed: {e}")

    def _play_audio(self, audio_bytes: bytes):
        """Play audio bytes through speakers."""
        try:
            import tempfile, os
            # Save to temp file and play
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name

            # Platform-specific playback
            import platform
            if platform.system() == "Windows":
                os.system(f'start /min "" "wmplayer" "{temp_path}"')
                import time
                time.sleep(len(audio_bytes) / 16000)  # Rough estimate
            else:
                os.system(f"afplay {temp_path}")

            # Cleanup
            try:
                os.unlink(temp_path)
            except:
                pass
        except Exception as e:
            print(f"[TTS] ⚠️ Playback error: {e}")

    def speak_async(self, text: str):
        """Non-blocking speech."""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()
