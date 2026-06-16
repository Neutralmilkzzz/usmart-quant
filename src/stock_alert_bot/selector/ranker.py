from __future__ import annotations

from math import inf

from stock_alert_bot.models import CandidateRecord, MarketStatus, StockSnapshot
from stock_alert_bot.selector.filters import is_sortable_snapshot


def select_top_candidates(
    snapshots: list[StockSnapshot],
    *,
    market_status: MarketStatus,
    top_n: int = 10,
    enabled_priorities: tuple[str, ...] = ("P0", "P1"),
) -> list[CandidateRecord]:
    candidates = [
        candidate
        for snapshot in snapshots
        if is_sortable_snapshot(snapshot, enabled_priorities=enabled_priorities)
        if (candidate := build_candidate(snapshot, market_status=market_status)) is not None
    ]
    ranked = sorted(candidates, key=_sort_key, reverse=True)
    return ranked[:top_n]


def build_candidate(
    snapshot: StockSnapshot,
    *,
    market_status: MarketStatus,
) -> CandidateRecord | None:
    if snapshot.price is None or snapshot.day_change_pct is None:
        return None

    missing_fields: list[str] = []
    for field_name in ("market_cap", "avg_volume_10d", "avg_volume_3m"):
        if getattr(snapshot, field_name) is None:
            missing_fields.append(field_name)

    reasons = ["P0/P1 观察池内当日涨幅靠前"]
    if snapshot.watch_priority == "P0":
        reasons.insert(0, "核心观察标的")
    if not market_status.is_open:
        reasons.append("市场当前休市，结果基于最近可用行情")

    return CandidateRecord(
        symbol=snapshot.symbol,
        name=snapshot.name,
        name_zh=snapshot.name_zh,
        watch_priority=snapshot.watch_priority,
        price=snapshot.price,
        day_change_pct=snapshot.day_change_pct,
        day_change=snapshot.day_change,
        market_cap=snapshot.market_cap,
        avg_volume_10d=snapshot.avg_volume_10d,
        avg_volume_3m=snapshot.avg_volume_3m,
        selected_reasons=reasons[:3],
        missing_fields=missing_fields,
    )


def _sort_key(candidate: CandidateRecord) -> tuple[float, int, float]:
    priority_score = 1 if candidate.watch_priority == "P0" else 0
    market_cap = candidate.market_cap if candidate.market_cap is not None else -inf
    return (candidate.day_change_pct, priority_score, market_cap)
