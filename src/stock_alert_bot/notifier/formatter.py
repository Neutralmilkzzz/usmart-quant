from __future__ import annotations

from datetime import datetime

from stock_alert_bot.models import CandidateRecord, ScanResult


def format_scan_result(result: ScanResult, *, max_message_chars: int = 3900) -> list[str]:
    lines = [
        "美股扫描 - Top 10",
        f"时间：{_format_time(result.finished_at)}",
        "股票池：P0/P1",
        f"市场状态：{result.market_status.label}",
        f"扫描状态：{_format_status(result.status.value)}",
        "提示：本结果不构成交易建议。",
        "",
    ]

    if not result.candidates:
        lines.append("暂无可排序候选标的。")
        if result.errors:
            lines.append(f"错误：{result.errors[0]}")
        return _split_text("\n".join(lines), max_message_chars=max_message_chars)

    for index, candidate in enumerate(result.candidates, start=1):
        lines.extend(_format_candidate(index, candidate))

    return _split_text("\n".join(lines).rstrip(), max_message_chars=max_message_chars)


def format_status_text(state: dict[str, object], *, scheduler_enabled: bool) -> str:
    return "\n".join(
        [
            "美股提醒 Bot 状态",
            "Bot：在线",
            f"定时扫描：{'已启用' if scheduler_enabled else '未启用'}",
            f"扫描器：{_format_status(str(state.get('scanner_state', 'UNKNOWN')))}",
            f"当前进度：{_format_progress(state)}",
            f"当前标的：{state.get('current_scan_symbol') or '无'}",
            f"上次扫描开始：{state.get('last_scan_started_at') or '从未运行'}",
            f"上次扫描结束：{state.get('last_scan_finished_at') or '从未运行'}",
            f"上次扫描状态：{_format_status(str(state.get('last_scan_status') or 'never'))}",
            f"上次结果数量：{state.get('last_result_count', 0)}",
            f"上次错误：{state.get('last_error') or '无'}",
        ]
    )


def format_progress_text(state: dict[str, object]) -> str:
    scanner_state = str(state.get("scanner_state", "UNKNOWN"))
    return "\n".join(
        [
            "当前扫描进度",
            f"扫描器：{_format_status(scanner_state)}",
            f"进度：{_format_progress(state)}",
            f"当前标的：{state.get('current_scan_symbol') or '无'}",
            f"上次扫描开始：{state.get('last_scan_started_at') or '从未运行'}",
            f"上次扫描状态：{_format_status(str(state.get('last_scan_status') or 'never'))}",
        ]
    )


def help_text() -> str:
    return "\n".join(
        [
            "/scan - 立即执行一次扫描",
            "/status - 查看 Bot 和扫描器状态",
            "/progress - 查看当前扫描进度",
            "/help - 查看命令列表",
        ]
    )


def _format_candidate(index: int, candidate: CandidateRecord) -> list[str]:
    name = _format_display_name(candidate)
    market_cap = _format_optional_number(candidate.market_cap)
    avg_volume_10d = _format_optional_number(candidate.avg_volume_10d)
    reason = "；".join(candidate.selected_reasons)
    return [
        (
            f"{index}. {candidate.symbol} {name} | 价格 {_format_price(candidate.price)} "
            f"| 日涨跌幅 {_format_percent(candidate.day_change_pct)} | 优先级 {candidate.watch_priority}"
        ),
        f"   市值：{market_cap} | 10日均量：{avg_volume_10d}",
        f"   理由：{reason}",
        "",
    ]


def _format_display_name(candidate: CandidateRecord) -> str:
    if candidate.name_zh and candidate.name:
        return f"{candidate.name_zh} / {candidate.name}"
    if candidate.name_zh:
        return candidate.name_zh
    return candidate.name or ""


def _split_text(text: str, *, max_message_chars: int) -> list[str]:
    if len(text) <= max_message_chars:
        return [text]

    messages: list[str] = []
    current = ""
    for block in text.split("\n\n"):
        candidate = block if not current else f"{current}\n\n{block}"
        if len(candidate) <= max_message_chars:
            current = candidate
            continue
        if current:
            messages.append(current)
        current = block
    if current:
        messages.append(current)
    return messages


def _format_time(value: datetime) -> str:
    return value.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _format_price(value: float) -> str:
    return f"{value:.2f}"


def _format_percent(value: float) -> str:
    return f"{value:+.2f}%"


def _format_optional_number(value: float | None) -> str:
    if value is None:
        return "无"
    return f"{value:,.2f}"


def _format_status(value: str) -> str:
    labels = {
        "IDLE": "空闲",
        "SCHEDULED": "已计划",
        "RUNNING": "运行中",
        "SUCCESS": "成功",
        "PARTIAL_SUCCESS": "部分成功",
        "FAILED": "失败",
        "COOLDOWN": "冷却中",
        "UNKNOWN": "未知",
        "never": "从未运行",
    }
    return labels.get(value, value)


def _format_progress(state: dict[str, object]) -> str:
    total = int(state.get("current_scan_total", 0) or 0)
    processed = int(state.get("current_scan_processed", 0) or 0)
    if total <= 0:
        return "0/0 (0%)"
    percent = processed / total * 100
    return f"{processed}/{total} ({percent:.1f}%)"
