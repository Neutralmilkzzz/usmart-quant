from __future__ import annotations

import json
import logging
import time
import urllib.parse
import urllib.request
from typing import Any

from stock_alert_bot.notifier.commands import BotCommandHandler

LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    name = "telegram"

    def __init__(self, *, token: str, chat_id: str, timeout_seconds: float = 10) -> None:
        self.token = token
        self.chat_id = str(chat_id)
        self.timeout_seconds = timeout_seconds
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_messages(self, messages: list[str]) -> None:
        for message in messages:
            self._post("sendMessage", {"chat_id": self.chat_id, "text": message})

    def set_commands(self) -> None:
        commands = [
            {"command": "scan", "description": "立即执行一次扫描"},
            {"command": "status", "description": "查看 Bot 和扫描器状态"},
            {"command": "progress", "description": "查看当前扫描进度"},
            {"command": "help", "description": "查看命令列表"},
        ]
        self._post("setMyCommands", {"commands": json.dumps(commands)})

    def _post(self, method: str, data: dict[str, str]) -> dict[str, Any]:
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        request = urllib.request.Request(f"{self.base_url}/{method}", data=encoded, method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
        parsed = json.loads(payload) if payload else {}
        if not parsed.get("ok", False):
            raise RuntimeError(f"Telegram {method} failed: {parsed}")
        return parsed


class TelegramPollingBot:
    def __init__(
        self,
        *,
        notifier: TelegramNotifier,
        command_handler: BotCommandHandler,
        poll_interval_seconds: float = 2,
    ) -> None:
        self.notifier = notifier
        self.command_handler = command_handler
        self.poll_interval_seconds = poll_interval_seconds
        self._offset = 0

    def poll_forever(self) -> None:
        self.notifier.set_commands()
        LOGGER.info("telegram_polling_started")
        while True:
            for update in self._get_updates():
                self._handle_update(update)
            time.sleep(self.poll_interval_seconds)

    def _get_updates(self) -> list[dict[str, Any]]:
        params = urllib.parse.urlencode({"timeout": 20, "offset": self._offset})
        url = f"{self.notifier.base_url}/getUpdates?{params}"
        with urllib.request.urlopen(url, timeout=25) as response:
            payload = response.read().decode("utf-8")
        parsed = json.loads(payload) if payload else {}
        if not parsed.get("ok", False):
            raise RuntimeError(f"Telegram getUpdates failed: {parsed}")
        return parsed.get("result", [])

    def _handle_update(self, update: dict[str, Any]) -> None:
        self._offset = max(self._offset, int(update.get("update_id", 0)) + 1)
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = str(chat.get("id") or "")
        if chat_id != self.notifier.chat_id:
            LOGGER.warning("telegram_unauthorized_chat chat_id=%s", chat_id)
            return

        text = str(message.get("text") or "").strip()
        if not text.startswith("/"):
            return
        responses = self.command_handler.handle_command(text)
        self.notifier.send_messages(responses)
