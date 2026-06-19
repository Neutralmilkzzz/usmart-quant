from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

from stock_alert_bot.models import Profile, Quote


class PositionLookupError(RuntimeError):
    pass


class PositionFeed(Protocol):
    def get_quote(self, symbol: str) -> Quote:
        ...

    def get_profile(self, symbol: str) -> Profile:
        ...


@dataclass(frozen=True)
class Position:
    symbol: str
    name: str | None
    asset_type: str
    buy_date: str
    buy_price: float
    invested_amount: float
    estimated_shares: float
    currency: str = "USD"
    source: str = "external_feed"
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Position":
        return cls(
            symbol=str(data["symbol"]).upper(),
            name=str(data["name"]) if data.get("name") else None,
            asset_type=str(data.get("asset_type") or "unknown"),
            buy_date=str(data["buy_date"]),
            buy_price=float(data["buy_price"]),
            invested_amount=float(data["invested_amount"]),
            estimated_shares=float(data["estimated_shares"]),
            currency=str(data.get("currency") or "USD"),
            source=str(data.get("source") or "external_feed"),
            notes=str(data.get("notes") or ""),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PositionSnapshot:
    position: Position
    current_price: float
    day_change_pct: float | None

    @property
    def current_value(self) -> float:
        return self.current_price * self.position.estimated_shares

    @property
    def total_profit(self) -> float:
        return self.current_value - self.position.invested_amount

    @property
    def total_return_pct(self) -> float:
        if self.position.invested_amount == 0:
            return 0.0
        return self.total_profit / self.position.invested_amount * 100


class PositionStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Position]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        if not isinstance(loaded, list):
            raise ValueError(f"Positions file must contain a list: {self.path}")
        return [Position.from_dict(item) for item in loaded if isinstance(item, dict)]

    def save(self, positions: list[Position]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump([position.to_dict() for position in positions], handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temp_path.replace(self.path)


class PositionService:
    def __init__(self, *, store: PositionStore, feed_client: PositionFeed) -> None:
        self.store = store
        self.feed_client = feed_client

    def add_position(
        self,
        *,
        symbol: str,
        buy_price: float,
        invested_amount: float,
        buy_date: str | None = None,
        notes: str = "",
    ) -> Position:
        normalized_symbol = _normalize_symbol(symbol)
        if buy_price <= 0:
            raise ValueError("buy_price must be greater than 0.")
        if invested_amount <= 0:
            raise ValueError("invested_amount must be greater than 0.")

        quote = self._get_valid_quote(normalized_symbol)
        profile = self._get_profile(normalized_symbol)
        name = profile.name or normalized_symbol
        asset_type = "etf" if "ETF" in name.upper() else "stock"
        position = Position(
            symbol=normalized_symbol,
            name=name,
            asset_type=asset_type,
            buy_date=buy_date or date.today().isoformat(),
            buy_price=buy_price,
            invested_amount=invested_amount,
            estimated_shares=invested_amount / buy_price,
            currency=profile.currency or "USD",
            source="external_feed",
            notes=notes,
        )

        positions = [item for item in self.store.load() if item.symbol != normalized_symbol]
        positions.append(position)
        positions.sort(key=lambda item: item.symbol)
        self.store.save(positions)
        _ = quote
        return position

    def list_snapshots(self) -> list[PositionSnapshot]:
        snapshots: list[PositionSnapshot] = []
        for position in self.store.load():
            quote = self._get_valid_quote(position.symbol)
            snapshots.append(
                PositionSnapshot(
                    position=position,
                    current_price=quote.price or 0.0,
                    day_change_pct=quote.day_change_pct,
                )
            )
        return snapshots

    def _get_valid_quote(self, symbol: str) -> Quote:
        try:
            quote = self.feed_client.get_quote(symbol)
        except Exception as exc:  # noqa: BLE001
            raise PositionLookupError(f"当前 feed 无法识别或获取 {symbol}: {exc}") from exc
        if quote.price is None or quote.price <= 0:
            raise PositionLookupError(f"当前 feed 未返回 {symbol} 的有效现价。")
        return quote

    def _get_profile(self, symbol: str) -> Profile:
        try:
            return self.feed_client.get_profile(symbol)
        except Exception:
            return Profile(symbol=symbol, name=symbol, currency="USD")


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("symbol is required.")
    return normalized
