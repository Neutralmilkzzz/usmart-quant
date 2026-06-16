from __future__ import annotations

from datetime import datetime

from stock_alert_bot.models import CandidateRecord, ScanResult


def format_scan_result(result: ScanResult, *, max_message_chars: int = 3900) -> list[str]:
    lines = [
        "US Stock Scan - Top 10",
        f"Time: {_format_time(result.finished_at)}",
        "Universe: P0/P1",
        f"Market: {result.market_status.label}",
        f"Status: {result.status.value}",
        "Note: This is not trading advice.",
        "",
    ]

    if not result.candidates:
        lines.append("No sortable candidates found.")
        if result.errors:
            lines.append(f"Error: {result.errors[0]}")
        return _split_text("\n".join(lines), max_message_chars=max_message_chars)

    for index, candidate in enumerate(result.candidates, start=1):
        lines.extend(_format_candidate(index, candidate))

    return _split_text("\n".join(lines).rstrip(), max_message_chars=max_message_chars)


def format_status_text(state: dict[str, object], *, scheduler_enabled: bool) -> str:
    return "\n".join(
        [
            "US Stock Alert Bot Status",
            "Bot: online",
            f"Scheduler: {'enabled' if scheduler_enabled else 'disabled'}",
            f"Scanner: {state.get('scanner_state', 'UNKNOWN')}",
            f"Last scan started: {state.get('last_scan_started_at') or 'never'}",
            f"Last scan finished: {state.get('last_scan_finished_at') or 'never'}",
            f"Last scan status: {state.get('last_scan_status') or 'never'}",
            f"Last result count: {state.get('last_result_count', 0)}",
            f"Last error: {state.get('last_error') or 'none'}",
        ]
    )


def help_text() -> str:
    return "\n".join(
        [
            "/scan - run scan now",
            "/status - show bot and scanner status",
            "/help - show commands",
        ]
    )


def _format_candidate(index: int, candidate: CandidateRecord) -> list[str]:
    name = f" {candidate.name}" if candidate.name else ""
    market_cap = _format_optional_number(candidate.market_cap)
    avg_volume_10d = _format_optional_number(candidate.avg_volume_10d)
    reason = "; ".join(candidate.selected_reasons)
    return [
        (
            f"{index}. {candidate.symbol}{name} | Price {_format_price(candidate.price)} "
            f"| Day {_format_percent(candidate.day_change_pct)} | Priority {candidate.watch_priority}"
        ),
        f"   Market cap: {market_cap} | Avg volume 10d: {avg_volume_10d}",
        f"   Reason: {reason}",
        "",
    ]


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
        return "n/a"
    return f"{value:,.2f}"
