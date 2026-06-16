from __future__ import annotations

from stock_alert_bot.models import CandidateRecord, MarketStatus, ScanResult, ScannerStatus, utc_now
from stock_alert_bot.notifier.formatter import (
    format_progress_text,
    format_scan_result,
    format_status_text,
    help_text,
)


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
                name_zh="英伟达",
                watch_priority="P0",
                price=132.4,
                day_change_pct=2.3456,
                selected_reasons=["核心观察标的", "P0/P1 观察池内当日涨幅靠前"],
            )
        ]
    )

    [message] = format_scan_result(result)

    assert "美股扫描 - Top 10" in message
    assert "NVDA 英伟达 / NVIDIA" in message
    assert "日涨跌幅 +2.35%" in message
    assert "提示：本结果不构成交易建议。" in message


def test_format_empty_result_is_clear():
    [message] = format_scan_result(make_result([]))

    assert "暂无可排序候选标的。" in message


def test_format_splits_long_messages():
    candidates = [
        CandidateRecord(
            symbol=f"S{i}",
            name="Name",
            name_zh="名称",
            watch_priority="P1",
            price=100,
            day_change_pct=float(i),
            selected_reasons=["P0/P1 观察池内当日涨幅靠前"],
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
            "current_scan_total": 0,
            "current_scan_processed": 0,
        },
        scheduler_enabled=True,
    )

    assert "定时扫描：已启用" in status
    assert "上次扫描状态：成功" in status
    assert "当前进度：0/0 (0%)" in status
    assert "/progress - 查看当前扫描进度" in help_text()


def test_progress_text_for_running_scan():
    progress = format_progress_text(
        {
            "scanner_state": "RUNNING",
            "current_scan_total": 20,
            "current_scan_processed": 5,
            "current_scan_symbol": "NVDA",
            "last_scan_started_at": "2026-06-16T10:00:00+00:00",
            "last_scan_status": "PARTIAL_SUCCESS",
        }
    )

    assert "扫描器：运行中" in progress
    assert "进度：5/20 (25.0%)" in progress
    assert "当前标的：NVDA" in progress
