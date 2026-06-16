from __future__ import annotations

import logging
from typing import Protocol

LOGGER = logging.getLogger(__name__)


class Notifier(Protocol):
    name: str

    def send_messages(self, messages: list[str]) -> None:
        ...


class NotifierManager:
    def __init__(self, notifiers: list[Notifier] | None = None) -> None:
        self.notifiers = notifiers or []

    def send_messages(self, messages: list[str]) -> list[str]:
        errors: list[str] = []
        for notifier in self.notifiers:
            try:
                notifier.send_messages(messages)
            except Exception as exc:  # noqa: BLE001 - one channel must not block another.
                message = f"{notifier.name} notifier failed: {exc}"
                LOGGER.error(message)
                errors.append(message)
        return errors


class ConsoleNotifier:
    name = "console"

    def send_messages(self, messages: list[str]) -> None:
        for message in messages:
            print(message)


class FakeNotifier:
    name = "fake"

    def __init__(self) -> None:
        self.messages: list[str] = []

    def send_messages(self, messages: list[str]) -> None:
        self.messages.extend(messages)
