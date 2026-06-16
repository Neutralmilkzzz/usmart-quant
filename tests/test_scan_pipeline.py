from __future__ import annotations

import time

from stock_alert_bot.models import MarketStatus, StockSnapshot, UniverseItem
from stock_alert_bot.notifier.base import FakeNotifier, NotifierManager
from stock_alert_bot.notifier.commands import BotCommandHandler
from stock_alert_bot.notifier.formatter import format_scan_result
from stock_alert_bot.scanner import StockScanner
from stock_alert_bot.state.machine import StateMachine
from stock_alert_bot.state.store import StateStore


class FakeFeed:
    def __init__(self, *, fail_symbols: set[str] | None = None) -> None:
        self.fail_symbols = fail_symbols or set()

    def get_market_status(self, exchange: str = "US") -> MarketStatus:
        return MarketStatus(exchange=exchange, is_open=True, session="regular")

    def fetch_snapshot(self, item: UniverseItem) -> StockSnapshot:
        if item.symbol in self.fail_symbols:
            raise RuntimeError("api down")
        rank = int(item.symbol.replace("S", ""))
        return StockSnapshot(
            symbol=item.symbol,
            name=item.name,
            asset_type=item.asset_type,
            watch_priority=item.watch_priority,
            price=100 + rank,
            day_change_pct=float(rank),
            market_cap=float(rank),
        )


class SlowScanner:
    def run_scan(self, *, trigger: str = "manual"):
        time.sleep(0.2)
        return None


def write_universe(path, count: int = 12) -> None:
    rows = ["symbol,name,asset_type,category,watch_priority,notes"]
    for index in range(count):
        priority = "P0" if index % 2 == 0 else "P1"
        rows.append(f"S{index},Name {index},stock,test,{priority},test")
    path.write_text("\n".join(rows), encoding="utf-8")


def build_scanner(tmp_path, *, fail_symbols: set[str] | None = None) -> StockScanner:
    universe_path = tmp_path / "universe.csv"
    write_universe(universe_path)
    return StockScanner(
        universe_path=universe_path,
        feed_client=FakeFeed(fail_symbols=fail_symbols),
        state_machine=StateMachine(StateStore(tmp_path / "state.json")),
        last_scan_path=tmp_path / "last_scan.json",
        top_n=10,
    )


def test_full_scan_with_fake_feed_sends_message(tmp_path):
    scanner = build_scanner(tmp_path)
    result = scanner.run_scan(trigger="manual")
    messages = format_scan_result(result)
    fake = FakeNotifier()

    NotifierManager([fake]).send_messages(messages)

    assert result.status.value == "SUCCESS"
    assert result.result_count == 10
    assert fake.messages
    assert "S11" in fake.messages[0]


def test_partial_failure_scan_returns_partial_success(tmp_path):
    scanner = build_scanner(tmp_path, fail_symbols={"S1", "S3", "S5"})

    result = scanner.run_scan(trigger="manual")

    assert result.status.value == "PARTIAL_SUCCESS"
    assert result.result_count == 9
    assert result.error_count == 3


def test_all_failure_scan_returns_failed(tmp_path):
    scanner = build_scanner(tmp_path, fail_symbols={f"S{i}" for i in range(12)})

    result = scanner.run_scan(trigger="manual")

    assert result.status.value == "FAILED"
    assert result.result_count == 0


def test_command_handler_reports_busy_scan(tmp_path):
    state_machine = StateMachine(StateStore(tmp_path / "state.json"))
    universe_path = tmp_path / "universe.csv"
    write_universe(universe_path, count=1)
    scanner = StockScanner(
        universe_path=universe_path,
        feed_client=FakeFeed(),
        state_machine=state_machine,
        last_scan_path=tmp_path / "last_scan.json",
    )
    assert state_machine.try_start(trigger="scheduled") is not None
    handler = BotCommandHandler(
        scanner=scanner,
        state_machine=state_machine,
        scheduler_enabled=True,
    )

    assert handler.handle_command("/scan") == ["Scan already running. Please wait."]
