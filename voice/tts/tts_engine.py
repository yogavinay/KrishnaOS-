"""
Edge-TTS Engine - Free Microsoft Text-to-Speech
High quality voices, no API key needed. Requires internet.
Replaces ElevenLabs.
"""

import asyncio
import tempfile
import threading
import os
from config import settings


class EdgeTTSEngine:
    """Text-to-Speech using Microsoft Edge TTS (free, high quality)."""

    def __init__(self):
        self.voice = settings.tts_voice
        self.enabled = settings.tts_enabled
        self.status = "initializing"
        self._loop = None
        print("[TTS] 🔊 Initializing Edge-TTS Engine...")

    def initialize(self):
        """Initialize the TTS engine."""
        if not self.enabled:
            self.status = "disabled"
            print("[TTS] ⚠️ TTS disabled in config.")
            return

        try:
            import edge_tts
            self.status = "active"
            print(f"[TTS] ✅ Edge-TTS ready. Voice: {self.voice}")
        except ImportError:
            print("[TTS] ❌ edge-tts not installed. Run: pip install edge-tts")
            self.status = "fallback"
        except Exception as e:
            print(f"[TTS] ❌ Init failed: {e}")
            self.status = "fallback"

    def speak(self, text: str):
        """Convert text to speech and play it."""
        # Always print the text
        print(f"[TTS] 🗣️ KRISHNA: {text}")

        if self.status != "active" or not self.enabled:
            return

        try:
            # Run async TTS in a sync context
            self._speak_sync(text)
        except Exception as e:
            print(f"[TTS] ⚠️ Speech failed: {e}")

    def _speak_sync(self, text: str):
        """Synchronous wrapper for async TTS."""
        try:
            # Create a new event loop for this thread if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(self._generate_and_play(text))
        except Exception as e:
            print(f"[TTS] ⚠️ Sync speech failed: {e}")

    async def _generate_and_play(self, text: str):
        """Generate speech audio and play it."""
        import edge_tts

        # Truncate very long text
        if len(text) > 2000:
            text = text[:2000] + "..."

        temp_path = None
        try:
            # Generate audio
            communicate = edge_tts.Communicate(text, self.voice)

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            await communicate.save(temp_path)

            # Play the audio
            self._play_audio(temp_path)

        except Exception as e:
            print(f"[TTS] ⚠️ TTS generation failed: {e}")
        finally:
            # Cleanup temp file
            if temp_path:
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def _play_audio(self, filepath: str):
        """Play an audio file using available system tools."""
        try:
            # Try pygame first (best cross-platform option)
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                return
            except ImportError:
                pass

            # Fallback: Windows Media Player (silent)
            import platform
            if platform.system() == "Windows":
                import subprocess
                # Use PowerShell to play audio more reliably
                ps_cmd = f"""
                Add-Type -AssemblyName PresentationCore
                $player = New-Object System.Windows.Media.MediaPlayer
                $player.Open('{filepath}')
                $player.Play()
                Start-Sleep -Milliseconds 500
                while ($player.Position -lt $player.NaturalDuration.TimeSpan) {{
                    Start-Sleep -Milliseconds 200
                }}
                $player.Close()
                """
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    capture_output=True, timeout=30
                )
            else:
                os.system(f"afplay {filepath} 2>/dev/null || aplay {filepath} 2>/dev/null")

        except Exception as e:
            print(f"[TTS] ⚠️ Playback error: {e}")

    def speak_async(self, text: str):
        """Non-blocking speech."""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()

    @staticmethod
    async def list_voices():
        """List all available Edge-TTS voices."""
        import edge_tts
        voices = await edge_tts.list_voices()
        return [{"name": v["ShortName"], "gender": v["Gender"], "locale": v["Locale"]} for v in voices]
