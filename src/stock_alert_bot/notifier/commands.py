from __future__ import annotations

from typing import Protocol

from stock_alert_bot.notifier.formatter import (
    format_holdings_text,
    format_position_added,
    format_progress_text,
    format_status_text,
    help_text,
)
from stock_alert_bot.portfolio import PositionService
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
        position_service: PositionService | None = None,
        max_message_chars: int = 3900,
    ) -> None:
        self.scan_starter = scan_starter
        self.state_machine = state_machine
        self.scheduler_enabled = scheduler_enabled
        self.position_service = position_service
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
        if normalized in {"/position_add", "position_add", "/track", "track"}:
            return [self.add_position(command)]
        if normalized in {"/holdings", "holdings"}:
            return [self.list_holdings()]
        if normalized in {"/scan", "scan"}:
            return self.run_scan()
        return [help_text()]

    def run_scan(self) -> list[str]:
        started = self.scan_starter.start_scan(trigger="manual")
        if not started:
            return ["扫描正在运行，请稍后再试。"]
        return ["已开始扫描，可用 /progress 查看进度。扫描完成后会自动推送结果。"]

    def add_position(self, command: str) -> str:
        if not self.position_service:
            return "持仓观察功能未启用。"
        parts = command.strip().split()
        if len(parts) < 4:
            return "格式错误：/position_add SYMBOL BUY_PRICE INVESTED_AMOUNT，例如 /position_add QQQ 450 1000"
        try:
            position = self.position_service.add_position(
                symbol=parts[1],
                buy_price=float(parts[2]),
                invested_amount=float(parts[3]),
                buy_date=parts[4] if len(parts) >= 5 else None,
                notes=" ".join(parts[5:]) if len(parts) >= 6 else "",
            )
        except Exception as exc:  # noqa: BLE001
            return f"录入失败：{exc}"
        return format_position_added(position)

    def list_holdings(self) -> str:
        if not self.position_service:
            return "持仓观察功能未启用。"
        try:
            return format_holdings_text(self.position_service.list_snapshots())
        except Exception as exc:  # noqa: BLE001
            return f"查询失败：{exc}"
