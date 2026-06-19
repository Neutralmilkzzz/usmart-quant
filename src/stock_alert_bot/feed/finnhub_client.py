from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from threading import Lock
from typing import Any

from stock_alert_bot.models import MarketStatus, Profile, Quote, StockSnapshot, UniverseItem, utc_now

LOGGER = logging.getLogger(__name__)


class FinnhubAPIError(RuntimeError):
    pass


class FinnhubClient:
    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(
        self,
        api_key: str,
        *,
        timeout_seconds: float = 10,
        max_retries: int = 3,
        retry_backoff_seconds: float = 1,
        calls_per_minute: int = 55,
    ) -> None:
        if not api_key:
            raise ValueError("FINNHUB_API_KEY is required.")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.calls_per_minute = calls_per_minute
        self._request_timestamps: deque[float] = deque()
        self._rate_limit_lock = Lock()

    def get_market_status(self, exchange: str = "US") -> MarketStatus:
        payload = self._get_json("/stock/market-status", {"exchange": exchange})
        return MarketStatus.from_api(payload)

    def get_quote(self, symbol: str) -> Quote:
        payload = self._get_json("/quote", {"symbol": symbol})
        return Quote.from_api(symbol, payload)

    def get_profile(self, symbol: str) -> Profile:
        payload = self._get_json("/stock/profile2", {"symbol": symbol})
        return Profile.from_api(symbol, payload)

    def get_metrics(self, symbol: str) -> dict[str, Any]:
        payload = self._get_json("/stock/metric", {"symbol": symbol, "metric": "all"})
        metric = payload.get("metric", {})
        return metric if isinstance(metric, dict) else {}

    def fetch_snapshot(self, item: UniverseItem) -> StockSnapshot:
        errors: list[str] = []
        quote: Quote | None = None
        profile: Profile | None = None
        metrics: dict[str, Any] = {}

        try:
            quote = self.get_quote(item.symbol)
        except Exception as exc:  # noqa: BLE001 - symbol-level failures must not stop scans.
            message = f"quote failed for {item.symbol}: {exc}"
            LOGGER.warning(message)
            errors.append(message)

        try:
            profile = self.get_profile(item.symbol)
        except Exception as exc:  # noqa: BLE001
            message = f"profile failed for {item.symbol}: {exc}"
            LOGGER.warning(message)
            errors.append(message)

        try:
            metrics = self.get_metrics(item.symbol)
        except Exception as exc:  # noqa: BLE001
            message = f"metrics failed for {item.symbol}: {exc}"
            LOGGER.warning(message)
            errors.append(message)

        market_cap = (
            profile.market_cap
            if profile and profile.market_cap is not None
            else _optional_float(metrics.get("marketCapitalization"))
        )
        return StockSnapshot(
            symbol=item.symbol,
            name=(profile.name if profile and profile.name else item.name),
            name_zh=item.name_zh,
            asset_type=item.asset_type,
            watch_priority=item.watch_priority,
            price=quote.price if quote else None,
            day_change=quote.day_change if quote else None,
            day_change_pct=quote.day_change_pct if quote else None,
            day_high=quote.day_high if quote else None,
            day_low=quote.day_low if quote else None,
            day_open=quote.day_open if quote else None,
            prev_close=quote.prev_close if quote else None,
            market_cap=market_cap,
            industry=profile.industry if profile else None,
            avg_volume_10d=_optional_float(metrics.get("10DayAverageTradingVolume")),
            avg_volume_3m=_optional_float(metrics.get("3MonthAverageTradingVolume")),
            metrics=metrics,
            quote_timestamp=quote.timestamp if quote else None,
            fetched_at=utc_now(),
            errors=errors,
        )

    def _get_json(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        query = dict(params)
        query["token"] = self.api_key
        url = f"{self.BASE_URL}{endpoint}?{urllib.parse.urlencode(query)}"
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            self._wait_for_rate_limit_slot()
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "usmart-quant/0.1"})
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    payload = response.read().decode("utf-8")
                data = json.loads(payload) if payload else {}
                if isinstance(data, dict) and "error" in data:
                    raise FinnhubAPIError(str(data["error"]))
                if not isinstance(data, dict):
                    raise FinnhubAPIError(f"Unexpected Finnhub payload type: {type(data).__name__}")
                return data
            except urllib.error.HTTPError as exc:
                last_error = FinnhubAPIError(f"HTTP {exc.code}: {exc.reason}")
                if exc.code == 429 or 500 <= exc.code < 600:
                    self._sleep_before_retry(attempt)
                    continue
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, FinnhubAPIError) as exc:
                last_error = exc
                self._sleep_before_retry(attempt)

        raise FinnhubAPIError(str(last_error or "unknown Finnhub error"))

    def _sleep_before_retry(self, attempt: int) -> None:
        if attempt >= self.max_retries:
            return
        time.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))

    def _wait_for_rate_limit_slot(self) -> None:
        if self.calls_per_minute <= 0:
            return

        window_seconds = 60.0
        while True:
            sleep_for = 0.0
            now = time.monotonic()
            with self._rate_limit_lock:
                while self._request_timestamps and now - self._request_timestamps[0] >= window_seconds:
                    self._request_timestamps.popleft()
                if len(self._request_timestamps) < self.calls_per_minute:
                    self._request_timestamps.append(now)
                    return
                sleep_for = window_seconds - (now - self._request_timestamps[0])
            if sleep_for > 0:
                time.sleep(sleep_for)


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
