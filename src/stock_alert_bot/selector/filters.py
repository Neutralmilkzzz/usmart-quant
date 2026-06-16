from __future__ import annotations

from stock_alert_bot.models import StockSnapshot


def is_sortable_snapshot(
    snapshot: StockSnapshot,
    *,
    enabled_priorities: tuple[str, ...] = ("P0", "P1"),
    require_price: bool = True,
    require_day_change_pct: bool = True,
) -> bool:
    if snapshot.watch_priority not in enabled_priorities:
        return False
    if require_price and snapshot.price is None:
        return False
    if require_day_change_pct and snapshot.day_change_pct is None:
        return False
    return True
