"""Telegram notification handler."""

import time
from typing import Optional, Callable
import requests

class TelegramNotifier:
    """Handles Telegram messaging."""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        session: Optional[requests.Session] = None,
        verbose: bool = False,
        logger: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
            session: Optional Requests session for API calls
            verbose: Enable verbose logging
            logger: Optional logging function
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.session = session or requests.Session()
        self.verbose = verbose
        self.logger = logger or (lambda msg: print(msg) if verbose else None)
        self.enabled = bool(bot_token and chat_id)
        self.last_update_id = None

    def send_message(self, text: str) -> Optional[int]:
        """Send message, returning message ID."""
        if not self.enabled:
            return None

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text.replace("<br>", "\n"),
            "parse_mode": "html",
            "disable_web_page_preview": True,
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result.get("result", {}).get("message_id")

        except requests.HTTPError as e:
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    self.logger(
                        f"[TELEGRAM ERROR] Failed to send message: {e.response.status_code} - {error_detail}"
                    )
                except:
                    self.logger(f"[TELEGRAM ERROR] Failed to send message: {e}")
            else:
                self.logger(f"[TELEGRAM ERROR] Failed to send message: {e}")
            return None
        except requests.RequestException as e:
            self.logger(f"[TELEGRAM ERROR] Failed to send message: {e}")
            return None 

    def update_message(self, message_id: int, text: str) -> bool:
        """Update existing message."""
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/editMessageText"
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": text.replace("<br>", "\n"),
            "parse_mode": "html",
            "disable_web_page_preview": True,
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            self.logger(f"[TELEGRAM ERROR] Network error updating message {message_id}: {e}")
            return False

    def get_updates(self) -> list[str]:
        """Check for new messages."""
        if not self.enabled:
            return []

        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            "timeout": 0,
            "allowed_updates": ["message"]
        }
        if self.last_update_id:
            params["offset"] = self.last_update_id + 1

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = data.get("result", [])
            messages = []
            
            for update in result:
                self.last_update_id = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = str(update["message"]["chat"]["id"])
                    # Only accept commands from the configured chat_id for security
                    if chat_id == self.chat_id:
                        messages.append(update["message"]["text"])
            
            return messages

        except Exception as e:
            self.logger(f"[TELEGRAM ERROR] Failed to get updates: {e}")
            return []
