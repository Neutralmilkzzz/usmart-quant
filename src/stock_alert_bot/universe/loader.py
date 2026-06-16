from __future__ import annotations

import csv
import logging
import re
from pathlib import Path
from typing import Iterable

from stock_alert_bot.models import UniverseItem

LOGGER = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "symbol",
    "name",
    "asset_type",
    "category",
    "watch_priority",
    "notes",
}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.\-]*$")


class UniverseLoadError(RuntimeError):
    pass


def load_universe(
    path: str | Path,
    *,
    enabled_priorities: Iterable[str] = ("P0", "P1"),
) -> list[UniverseItem]:
    universe_path = Path(path)
    if not universe_path.exists():
        raise UniverseLoadError(f"Universe file does not exist: {universe_path}")

    enabled = {priority.upper() for priority in enabled_priorities}
    seen: set[str] = set()
    items: list[UniverseItem] = []

    with universe_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise UniverseLoadError(
                f"Universe file is missing required columns: {', '.join(sorted(missing))}"
            )

        for row_number, row in enumerate(reader, start=2):
            symbol = _clean_symbol(row.get("symbol"))
            if not symbol:
                LOGGER.warning("Skipping universe row %s with empty symbol", row_number)
                continue
            if not SYMBOL_PATTERN.match(symbol):
                LOGGER.warning("Skipping universe row %s with invalid symbol %s", row_number, symbol)
                continue

            priority = (row.get("watch_priority") or "").strip().upper()
            if priority not in enabled:
                continue
            if symbol in seen:
                LOGGER.warning("Skipping duplicate universe symbol %s", symbol)
                continue

            seen.add(symbol)
            items.append(
                UniverseItem(
                    symbol=symbol,
                    name=(row.get("name") or "").strip(),
                    name_zh=(row.get("name_zh") or "").strip() or None,
                    asset_type=(row.get("asset_type") or "").strip().lower(),
                    category=(row.get("category") or "").strip(),
                    watch_priority=priority,
                    notes=(row.get("notes") or "").strip(),
                )
            )

    if not items:
        raise UniverseLoadError("Universe contains no enabled P0/P1 symbols.")
    return items


def _clean_symbol(value: str | None) -> str:
    return (value or "").strip().upper()
