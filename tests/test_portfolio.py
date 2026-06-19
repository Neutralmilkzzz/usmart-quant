from __future__ import annotations

import pytest

from stock_alert_bot.models import Profile, Quote
from stock_alert_bot.portfolio import PositionLookupError, PositionService, PositionStore


class FakePortfolioFeed:
    def __init__(self) -> None:
        self.quotes = {
            "QQQ": Quote(symbol="QQQ", price=500, day_change_pct=1.5),
            "SOXX": Quote(symbol="SOXX", price=250, day_change_pct=-0.5),
        }
        self.profiles = {
            "QQQ": Profile(symbol="QQQ", name="Invesco QQQ Trust", currency="USD"),
            "SOXX": Profile(symbol="SOXX", name="iShares Semiconductor ETF", currency="USD"),
        }

    def get_quote(self, symbol: str) -> Quote:
        return self.quotes[symbol]

    def get_profile(self, symbol: str) -> Profile:
        return self.profiles[symbol]


def test_position_service_adds_feed_validated_symbol(tmp_path):
    service = PositionService(
        store=PositionStore(tmp_path / "positions.json"),
        feed_client=FakePortfolioFeed(),
    )

    position = service.add_position(
        symbol="soxx",
        buy_price=200,
        invested_amount=100,
        buy_date="2026-06-19",
    )

    assert position.symbol == "SOXX"
    assert position.name == "iShares Semiconductor ETF"
    assert position.estimated_shares == pytest.approx(0.5)
    assert position.source == "external_feed"

    [loaded] = service.store.load()
    assert loaded.symbol == "SOXX"


def test_position_service_rejects_unknown_symbol(tmp_path):
    service = PositionService(
        store=PositionStore(tmp_path / "positions.json"),
        feed_client=FakePortfolioFeed(),
    )

    with pytest.raises(PositionLookupError):
        service.add_position(symbol="DRAM", buy_price=10, invested_amount=100)


def test_position_service_lists_profit_snapshots(tmp_path):
    service = PositionService(
        store=PositionStore(tmp_path / "positions.json"),
        feed_client=FakePortfolioFeed(),
    )
    service.add_position(
        symbol="QQQ",
        buy_price=400,
        invested_amount=800,
        buy_date="2026-06-19",
    )

    [snapshot] = service.list_snapshots()

    assert snapshot.current_price == 500
    assert snapshot.day_change_pct == 1.5
    assert snapshot.current_value == pytest.approx(1000)
    assert snapshot.total_profit == pytest.approx(200)
    assert snapshot.total_return_pct == pytest.approx(25)
