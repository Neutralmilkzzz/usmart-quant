from __future__ import annotations

from stock_alert_bot.models import CandidateRecord, MarketStatus, ScanResult, ScannerStatus, utc_now
from stock_alert_bot.notifier.formatter import format_scan_result, format_status_text, help_text


def make_result(candidates: list[CandidateRecord]) -> ScanResult:
    now = utc_now()
    return ScanResult(
        status=ScannerStatus.SUCCESS if candidates else ScannerStatus.FAILED,
        trigger="manual",
        market_status=MarketStatus(is_open=True),
        candidates=candidates,
        started_at=now,
        finished_at=now,
        universe_count=1,
        snapshot_count=1,
    )


def test_format_scan_result_includes_top_record_and_stable_percent():
    result = make_result(
        [
            CandidateRecord(
                symbol="NVDA",
                name="NVIDIA",
                watch_priority="P0",
                price=132.4,
                day_change_pct=2.3456,
                selected_reasons=["Core watchlist symbol", "Top intraday mover"],
            )
        ]
    )

    [message] = format_scan_result(result)

    assert "US Stock Scan - Top 10" in message
    assert "NVDA NVIDIA" in message
    assert "Day +2.35%" in message
    assert "Note: This is not trading advice." in message


def test_format_empty_result_is_clear():
    [message] = format_scan_result(make_result([]))

    assert "No sortable candidates found." in message


def test_format_splits_long_messages():
    candidates = [
        CandidateRecord(
            symbol=f"S{i}",
            name="Name",
            watch_priority="P1",
            price=100,
            day_change_pct=float(i),
            selected_reasons=["Top intraday mover in P0/P1 universe"],
        )
        for i in range(10)
    ]

    messages = format_scan_result(make_result(candidates), max_message_chars=500)

    assert len(messages) > 1
    assert all(len(message) <= 500 for message in messages)


def test_status_and_help_text():
    status = format_status_text(
        {
            "scanner_state": "IDLE",
            "last_scan_status": "SUCCESS",
            "last_result_count": 10,
        },
        scheduler_enabled=True,
    )

    assert "Scheduler: enabled" in status
    assert "/scan - run scan now" in help_text()
