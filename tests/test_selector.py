from __future__ import annotations

from stock_alert_bot.models import MarketStatus, StockSnapshot
from stock_alert_bot.selector.ranker import select_top_candidates


def snapshot(
    symbol: str,
    priority: str,
    pct: float | None,
    *,
    price: float | None = 100,
    market_cap: float | None = None,
) -> StockSnapshot:
    return StockSnapshot(
        symbol=symbol,
        name=symbol,
        asset_type="stock",
        watch_priority=priority,
        price=price,
        day_change_pct=pct,
        market_cap=market_cap,
    )


def test_selector_sorts_by_day_change_then_priority_then_market_cap():
    snapshots = [
        snapshot("P1_BIG", "P1", 5.0, market_cap=500),
        snapshot("P0_SMALL", "P0", 5.0, market_cap=100),
        snapshot("WINNER", "P1", 9.0, market_cap=1),
        snapshot("P0_BIG", "P0", 5.0, market_cap=900),
    ]

    selected = select_top_candidates(
        snapshots,
        market_status=MarketStatus(is_open=True),
        top_n=10,
    )

    assert [candidate.symbol for candidate in selected] == [
        "WINNER",
        "P0_BIG",
        "P0_SMALL",
        "P1_BIG",
    ]


def test_selector_filters_p2_missing_price_and_missing_day_change_pct():
    snapshots = [
        snapshot("GOOD", "P1", 1.0),
        snapshot("P2", "P2", 9.0),
        snapshot("NO_PRICE", "P0", 8.0, price=None),
        snapshot("NO_PCT", "P0", None),
    ]

    selected = select_top_candidates(
        snapshots,
        market_status=MarketStatus(is_open=True),
        top_n=10,
    )

    assert [candidate.symbol for candidate in selected] == ["GOOD"]


def test_selector_limits_to_top_n_and_adds_market_closed_reason():
    snapshots = [snapshot(f"S{i}", "P1", float(i)) for i in range(20)]

    selected = select_top_candidates(
        snapshots,
        market_status=MarketStatus(is_open=False),
        top_n=10,
    )

    assert len(selected) == 10
    assert selected[0].symbol == "S19"
    assert any("Market closed" in reason for reason in selected[0].selected_reasons)
