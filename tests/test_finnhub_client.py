from __future__ import annotations

import pytest

from stock_alert_bot.feed.finnhub_client import FinnhubAPIError, FinnhubClient
from stock_alert_bot.models import UniverseItem


class StubFinnhubClient(FinnhubClient):
    def __init__(self, responses):
        super().__init__("test-token", max_retries=1)
        self.responses = responses

    def _get_json(self, endpoint, params):
        key = (endpoint, params.get("symbol") or params.get("exchange"))
        response = self.responses[key]
        if isinstance(response, Exception):
            raise response
        return response


def item(symbol: str = "AAPL") -> UniverseItem:
    return UniverseItem(
        symbol=symbol,
        name=symbol,
        asset_type="stock",
        category="core",
        watch_priority="P0",
    )


def test_finnhub_quote_profile_metric_mapping():
    client = StubFinnhubClient(
        {
            ("/quote", "AAPL"): {"c": 200, "d": 1, "dp": 0.5, "h": 201, "l": 198, "o": 199, "pc": 199, "t": 1},
            ("/stock/profile2", "AAPL"): {
                "name": "Apple",
                "marketCapitalization": 3000000,
                "finnhubIndustry": "Technology",
            },
            ("/stock/metric", "AAPL"): {
                "metric": {
                    "10DayAverageTradingVolume": 100,
                    "3MonthAverageTradingVolume": 200,
                }
            },
        }
    )

    snapshot = client.fetch_snapshot(item())

    assert snapshot.price == 200
    assert snapshot.day_change_pct == 0.5
    assert snapshot.name == "Apple"
    assert snapshot.market_cap == 3000000
    assert snapshot.avg_volume_10d == 100
    assert snapshot.errors == []


def test_finnhub_snapshot_keeps_symbol_errors_local():
    client = StubFinnhubClient(
        {
            ("/quote", "AAPL"): FinnhubAPIError("timeout"),
            ("/stock/profile2", "AAPL"): {"name": "Apple"},
            ("/stock/metric", "AAPL"): {"metric": {}},
        }
    )

    snapshot = client.fetch_snapshot(item())

    assert snapshot.price is None
    assert any("quote failed" in error for error in snapshot.errors)


def test_finnhub_quote_missing_price_does_not_crash():
    client = StubFinnhubClient(
        {
            ("/quote", "AAPL"): {"dp": 1.2},
            ("/stock/profile2", "AAPL"): {},
            ("/stock/metric", "AAPL"): {"metric": {}},
        }
    )

    snapshot = client.fetch_snapshot(item())

    assert snapshot.price is None
    assert snapshot.day_change_pct == 1.2
