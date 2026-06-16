from __future__ import annotations

from stock_alert_bot.models import ScanResult
from stock_alert_bot.notifier.formatter import format_scan_result, format_status_text, help_text
from stock_alert_bot.scanner import StockScanner
from stock_alert_bot.state.machine import ScanAlreadyRunningError, StateMachine


class BotCommandHandler:
    def __init__(
        self,
        *,
        scanner: StockScanner,
        state_machine: StateMachine,
        scheduler_enabled: bool,
        max_message_chars: int = 3900,
    ) -> None:
        self.scanner = scanner
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
        if normalized in {"/scan", "scan"}:
            return self.run_scan()
        return [help_text()]

    def run_scan(self) -> list[str]:
        try:
            result: ScanResult = self.scanner.run_scan(trigger="manual")
        except ScanAlreadyRunningError:
            return ["Scan already running. Please wait."]
        return format_scan_result(result, max_message_chars=self.max_message_chars)
