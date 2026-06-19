from __future__ import annotations

import threading
import time

from stock_alert_bot.models import MarketStatus, StockSnapshot, UniverseItem
from stock_alert_bot.notifier.base import FakeNotifier, NotifierManager
from stock_alert_bot.notifier.commands import BotCommandHandler
from stock_alert_bot.notifier.formatter import format_scan_result
from stock_alert_bot.scan_dispatcher import ScanDispatcher
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
            name_zh=item.name_zh,
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


class FakeScanStarter:
    def __init__(self, *, started: bool = True) -> None:
        self.started = started
        self.triggers: list[str] = []

    def start_scan(self, *, trigger: str) -> bool:
        self.triggers.append(trigger)
        return self.started


class BlockingFeed(FakeFeed):
    def __init__(self, *, started_event: threading.Event, release_event: threading.Event) -> None:
        super().__init__()
        self.started_event = started_event
        self.release_event = release_event

    def fetch_snapshot(self, item: UniverseItem) -> StockSnapshot:
        self.started_event.set()
        self.release_event.wait(timeout=2)
        return super().fetch_snapshot(item)


def write_universe(path, count: int = 12) -> None:
    rows = ["symbol,name,name_zh,asset_type,category,watch_priority,notes"]
    for index in range(count):
        priority = "P0" if index % 2 == 0 else "P1"
        rows.append(f"S{index},Name {index},名称{index},stock,test,{priority},test")
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
    assert "S11 名称11 / Name 11" in fake.messages[0]


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
    starter = FakeScanStarter(started=False)
    handler = BotCommandHandler(
        scan_starter=starter,
        state_machine=state_machine,
        scheduler_enabled=True,
    )

    assert handler.handle_command("/scan") == ["扫描正在运行，请稍后再试。"]


def test_command_handler_reports_scan_progress(tmp_path):
    state_machine = StateMachine(StateStore(tmp_path / "state.json"))
    assert state_machine.try_start(trigger="manual") is not None
    state_machine.update_progress(total=12, processed=3, current_symbol="S3")

    handler = BotCommandHandler(
        scan_starter=FakeScanStarter(),
        state_machine=state_machine,
        scheduler_enabled=True,
    )

    [message] = handler.handle_command("/progress")

    assert "进度：3/12 (25.0%)" in message
    assert "当前标的：S3" in message


def test_command_handler_scan_returns_immediately_with_async_ack(tmp_path):
    handler = BotCommandHandler(
        scan_starter=FakeScanStarter(),
        state_machine=StateMachine(StateStore(tmp_path / "state.json")),
        scheduler_enabled=True,
    )

    started = time.monotonic()
    [message] = handler.handle_command("/scan")
    elapsed = time.monotonic() - started

    assert elapsed < 0.1
    assert "已开始扫描" in message


def test_progress_remains_available_while_async_scan_runs(tmp_path):
    universe_path = tmp_path / "universe.csv"
    write_universe(universe_path, count=2)
    state_machine = StateMachine(StateStore(tmp_path / "state.json"))
    started_event = threading.Event()
    release_event = threading.Event()
    scanner = StockScanner(
        universe_path=universe_path,
        feed_client=BlockingFeed(started_event=started_event, release_event=release_event),
        state_machine=state_machine,
        last_scan_path=tmp_path / "last_scan.json",
        top_n=10,
    )
    notifier = FakeNotifier()
    dispatcher = ScanDispatcher(
        scanner=scanner,
        notifier_manager=NotifierManager([notifier]),
    )
    handler = BotCommandHandler(
        scan_starter=dispatcher,
        state_machine=state_machine,
        scheduler_enabled=True,
    )

    [scan_message] = handler.handle_command("/scan")
    assert "已开始扫描" in scan_message
    assert started_event.wait(timeout=1)

    [progress_message] = handler.handle_command("/progress")

    assert "扫描器：运行中" in progress_message
    assert "当前标的：" in progress_message

    release_event.set()
    for _ in range(20):
        if notifier.messages:
            break
        time.sleep(0.05)

    assert notifier.messages
