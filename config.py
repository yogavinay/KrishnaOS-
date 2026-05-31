"""
MAHABHARATA SYSTEM - Central Configuration
All settings loaded from environment variables via .env file.
Migrated to local Ollama LLM + edge-tts.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    """Central configuration for the Mahabharata System."""

    # Ollama (local LLM - OpenAI-compatible API)
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    # Edge-TTS (free Microsoft voices)
    tts_voice: str = os.getenv("TTS_VOICE", "en-US-GuyNeural")
    tts_enabled: bool = os.getenv("TTS_ENABLED", "true").lower() == "true"

    # Tavily Search
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    # PostgreSQL
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mahabharata")

    # Whisper
    whisper_model: str = os.getenv("WHISPER_MODEL", "base")

    # System
    user_name: str = os.getenv("USER_NAME", "Yogavinay")
    wake_word: str = os.getenv("WAKE_WORD", "krishna")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Integrations
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")

    # Paths
    base_dir: str = str(Path(__file__).parent)

    class Config:
        env_file = ".env"
        extra = "allow"


# Singleton instance
settings = Settings()
