from __future__ import annotations

import io
import json
import urllib.error
import pytest

from stock_alert_bot.feed import finnhub_client as finnhub_client_module
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
        name_zh="测试标的",
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
    assert snapshot.name_zh == "测试标的"
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


def test_finnhub_rate_limiter_caps_requests_per_minute(monkeypatch):
    current = {"value": 0.0}

    def fake_monotonic():
        return current["value"]

    def fake_sleep(seconds: float):
        current["value"] += seconds

    monkeypatch.setattr(finnhub_client_module.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(finnhub_client_module.time, "sleep", fake_sleep)

    client = FinnhubClient("test-token", max_retries=1, calls_per_minute=2)

    client._wait_for_rate_limit_slot()
    client._wait_for_rate_limit_slot()
    assert len(client._request_timestamps) == 2

    client._wait_for_rate_limit_slot()

    assert current["value"] == pytest.approx(60.0)


def test_finnhub_retries_consume_rate_limit_slots(monkeypatch):
    current = {"value": 0.0}
    attempts = {"value": 0}

    def fake_monotonic():
        return current["value"]

    def fake_sleep(seconds: float):
        current["value"] += seconds

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"c": 123, "t": 1}).encode("utf-8")

    def fake_urlopen(request, timeout=0):
        attempts["value"] += 1
        if attempts["value"] == 1:
            raise urllib.error.HTTPError(
                request.full_url,
                429,
                "Too Many Requests",
                hdrs=None,
                fp=io.BytesIO(b""),
            )
        return FakeResponse()

    monkeypatch.setattr(finnhub_client_module.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(finnhub_client_module.time, "sleep", fake_sleep)
    monkeypatch.setattr(finnhub_client_module.urllib.request, "urlopen", fake_urlopen)

    client = FinnhubClient(
        "test-token",
        max_retries=2,
        retry_backoff_seconds=0,
        calls_per_minute=1,
    )

    quote = client.get_quote("AAPL")

    assert quote.price == 123
    assert attempts["value"] == 2
    assert current["value"] == pytest.approx(60.0)
