"""
Telegram Integration
Send messages and files to the user via Telegram Bot API.
"""

from typing import Dict, Any, Optional
from config import settings


class TelegramIntegration:
    """Send notifications via Telegram Bot API."""

    API_BASE = "https://api.telegram.org/bot{token}"

    def __init__(self):
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.enabled = bool(self.token and self.chat_id)

    def send_message(self, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """Send a text message via Telegram."""
        if not self.enabled:
            return {"success": False, "error": "Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"}

        try:
            import httpx
            url = f"{self.API_BASE.format(token=self.token)}/sendMessage"
            response = httpx.post(url, json={
                "chat_id": self.chat_id,
                "text": text[:4096],  # Telegram message limit
                "parse_mode": parse_mode
            }, timeout=15)

            if response.status_code == 200:
                return {"success": True, "summary": "Message sent via Telegram."}
            return {"success": False, "error": f"Telegram API error: {response.text[:300]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_file(self, filepath: str, caption: str = "") -> Dict[str, Any]:
        """Send a file via Telegram."""
        if not self.enabled:
            return {"success": False, "error": "Telegram not configured."}

        try:
            import httpx
            import os
            url = f"{self.API_BASE.format(token=self.token)}/sendDocument"

            if not os.path.exists(filepath):
                return {"success": False, "error": f"File not found: {filepath}"}

            with open(filepath, "rb") as f:
                response = httpx.post(
                    url,
                    data={"chat_id": self.chat_id, "caption": caption[:1024]},
                    files={"document": (os.path.basename(filepath), f)},
                    timeout=30
                )

            if response.status_code == 200:
                return {"success": True, "summary": f"File sent via Telegram: {os.path.basename(filepath)}"}
            return {"success": False, "error": f"Telegram API error: {response.text[:300]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_photo(self, filepath: str, caption: str = "") -> Dict[str, Any]:
        """Send a photo via Telegram."""
        if not self.enabled:
            return {"success": False, "error": "Telegram not configured."}

        try:
            import httpx
            import os
            url = f"{self.API_BASE.format(token=self.token)}/sendPhoto"

            with open(filepath, "rb") as f:
                response = httpx.post(
                    url,
                    data={"chat_id": self.chat_id, "caption": caption[:1024]},
                    files={"photo": (os.path.basename(filepath), f)},
                    timeout=30
                )

            if response.status_code == 200:
                return {"success": True, "summary": "Photo sent via Telegram."}
            return {"success": False, "error": f"Telegram API error: {response.text[:300]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def notify(self, title: str, message: str) -> Dict[str, Any]:
        """Send a formatted notification."""
        text = f"🕉️ *MAHABHARATA SYSTEM*\n\n*{title}*\n{message}"
        return self.send_message(text)
