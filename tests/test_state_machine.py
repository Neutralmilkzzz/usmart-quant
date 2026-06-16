from __future__ import annotations

from stock_alert_bot.models import ScannerStatus
from stock_alert_bot.state.machine import StateMachine
from stock_alert_bot.state.store import StateStore


def test_state_machine_rejects_concurrent_scan_and_persists(tmp_path):
    store = StateStore(tmp_path / "state.json")
    machine = StateMachine(store)

    started = machine.try_start(trigger="manual")

    assert started is not None
    assert machine.try_start(trigger="manual") is None
    machine.finish(status=ScannerStatus.SUCCESS, result_count=10)

    snapshot = machine.snapshot()
    assert snapshot["scanner_state"] == "IDLE"
    assert snapshot["last_scan_status"] == "SUCCESS"
    assert snapshot["last_result_count"] == 10
    assert store.load()["last_scan_status"] == "SUCCESS"


def test_state_machine_records_failed_scan(tmp_path):
    machine = StateMachine(StateStore(tmp_path / "state.json"))

    assert machine.try_start(trigger="scheduled") is not None
    machine.finish(status=ScannerStatus.FAILED, result_count=0, error="boom")

    snapshot = machine.snapshot()
    assert snapshot["last_scan_status"] == "FAILED"
    assert snapshot["last_error"] == "boom"
