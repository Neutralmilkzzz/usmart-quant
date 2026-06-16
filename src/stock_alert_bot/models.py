from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class ScannerStatus(str, Enum):
    IDLE = "IDLE"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    COOLDOWN = "COOLDOWN"


@dataclass(frozen=True)
class UniverseItem:
    symbol: str
    name: str
    asset_type: str
    category: str
    watch_priority: str
    notes: str = ""


@dataclass
class MarketStatus:
    exchange: str = "US"
    is_open: bool = False
    session: str | None = None
    holiday: str | None = None
    timezone: str | None = None
    timestamp: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, payload: dict[str, Any]) -> "MarketStatus":
        return cls(
            exchange=str(payload.get("exchange") or "US"),
            is_open=bool(payload.get("isOpen")),
            session=_optional_str(payload.get("session")),
            holiday=_optional_str(payload.get("holiday")),
            timezone=_optional_str(payload.get("timezone")),
            timestamp=_optional_int(payload.get("t")),
            raw=payload,
        )

    @classmethod
    def unknown(cls, exchange: str = "US") -> "MarketStatus":
        return cls(exchange=exchange, session="unknown")

    @property
    def label(self) -> str:
        return "Open" if self.is_open else "Closed"


@dataclass
class Quote:
    symbol: str
    price: float | None = None
    day_change: float | None = None
    day_change_pct: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    day_open: float | None = None
    prev_close: float | None = None
    timestamp: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, symbol: str, payload: dict[str, Any]) -> "Quote":
        price = _optional_float(payload.get("c"))
        return cls(
            symbol=symbol,
            price=price if price and price > 0 else None,
            day_change=_optional_float(payload.get("d")),
            day_change_pct=_optional_float(payload.get("dp")),
            day_high=_optional_float(payload.get("h")),
            day_low=_optional_float(payload.get("l")),
            day_open=_optional_float(payload.get("o")),
            prev_close=_optional_float(payload.get("pc")),
            timestamp=_optional_int(payload.get("t")),
            raw=payload,
        )


@dataclass
class Profile:
    symbol: str
    name: str | None = None
    country: str | None = None
    currency: str | None = None
    exchange: str | None = None
    ipo: str | None = None
    market_cap: float | None = None
    share_outstanding: float | None = None
    floating_share: float | None = None
    industry: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, symbol: str, payload: dict[str, Any]) -> "Profile":
        return cls(
            symbol=symbol,
            name=_optional_str(payload.get("name")),
            country=_optional_str(payload.get("country")),
            currency=_optional_str(payload.get("currency")),
            exchange=_optional_str(payload.get("exchange")),
            ipo=_optional_str(payload.get("ipo")),
            market_cap=_optional_float(payload.get("marketCapitalization")),
            share_outstanding=_optional_float(payload.get("shareOutstanding")),
            floating_share=_optional_float(payload.get("floatingShare")),
            industry=_optional_str(payload.get("finnhubIndustry")),
            raw=payload,
        )


@dataclass
class StockSnapshot:
    symbol: str
    name: str | None
    asset_type: str | None
    watch_priority: str
    price: float | None = None
    day_change: float | None = None
    day_change_pct: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    day_open: float | None = None
    prev_close: float | None = None
    market_cap: float | None = None
    industry: str | None = None
    avg_volume_10d: float | None = None
    avg_volume_3m: float | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    quote_timestamp: int | None = None
    fetched_at: datetime = field(default_factory=utc_now)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["fetched_at"] = self.fetched_at.isoformat()
        return data


@dataclass
class CandidateRecord:
    symbol: str
    name: str | None
    watch_priority: str
    price: float
    day_change_pct: float
    day_change: float | None = None
    market_cap: float | None = None
    avg_volume_10d: float | None = None
    avg_volume_3m: float | None = None
    selected_reasons: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScanResult:
    status: ScannerStatus
    trigger: str
    market_status: MarketStatus
    candidates: list[CandidateRecord]
    started_at: datetime
    finished_at: datetime
    universe_count: int
    snapshot_count: int
    error_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def result_count(self) -> int:
        return len(self.candidates)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "trigger": self.trigger,
            "market_status": asdict(self.market_status),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "universe_count": self.universe_count,
            "snapshot_count": self.snapshot_count,
            "result_count": self.result_count,
            "error_count": self.error_count,
            "errors": self.errors,
        }


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
