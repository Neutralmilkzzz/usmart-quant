from __future__ import annotations

from typing import Protocol

from stock_alert_bot.notifier.formatter import (
    format_progress_text,
    format_status_text,
    help_text,
)
from stock_alert_bot.state.machine import StateMachine


class ScanStarter(Protocol):
    def start_scan(self, *, trigger: str) -> bool:
        ...


class BotCommandHandler:
    def __init__(
        self,
        *,
        scan_starter: ScanStarter,
        state_machine: StateMachine,
        scheduler_enabled: bool,
        max_message_chars: int = 3900,
    ) -> None:
        self.scan_starter = scan_starter
        self.state_machine = state_machine
        self.scheduler_enabled = scheduler_enabled
        self.max_message_chars = max_message_chars

    def handle_command(self, command: str) -> list[str]:
        normalized = command.strip().split(maxsplit=1)[0].lower()
        if normalized in {"/help", "help"}:
            return [help_text()]
        if normalized in {"/status", "status"}:
            return [
                format_status_text(
                    self.state_machine.snapshot(),
                    scheduler_enabled=self.scheduler_enabled,
                )
            ]
        if normalized in {"/progress", "progress"}:
            return [format_progress_text(self.state_machine.snapshot())]
        if normalized in {"/scan", "scan"}:
            return self.run_scan()
        return [help_text()]

    def run_scan(self) -> list[str]:
        started = self.scan_starter.start_scan(trigger="manual")
        if not started:
            return ["扫描正在运行，请稍后再试。"]
        return ["已开始扫描，可用 /progress 查看进度。扫描完成后会自动推送结果。"]
