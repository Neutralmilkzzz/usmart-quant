from __future__ import annotations

import pytest

from stock_alert_bot.universe.loader import UniverseLoadError, load_universe


def test_load_universe_keeps_p0_p1_skips_empty_and_dedupes(tmp_path):
    csv_path = tmp_path / "universe.csv"
    csv_path.write_text(
        "\n".join(
            [
                "symbol,name,asset_type,category,watch_priority,notes",
                "AAPL,Apple,stock,core,P0,core",
                "MSFT,Microsoft,stock,core,P1,core",
                "TSLA,Tesla,stock,auto,P2,skip",
                ",Empty,stock,core,P0,skip",
                "AAPL,Apple Duplicate,stock,core,P0,skip",
            ]
        ),
        encoding="utf-8",
    )

    items = load_universe(csv_path)

    assert [item.symbol for item in items] == ["AAPL", "MSFT"]
    assert items[0].watch_priority == "P0"


def test_load_universe_missing_required_column(tmp_path):
    csv_path = tmp_path / "universe.csv"
    csv_path.write_text("symbol,name\nAAPL,Apple\n", encoding="utf-8")

    with pytest.raises(UniverseLoadError, match="missing required columns"):
        load_universe(csv_path)


def test_load_universe_missing_file(tmp_path):
    with pytest.raises(UniverseLoadError, match="does not exist"):
        load_universe(tmp_path / "missing.csv")


def test_load_real_universe_filters_to_p0_p1():
    items = load_universe("data/universe_100.csv")

    assert items
    assert {item.watch_priority for item in items} <= {"P0", "P1"}
    assert len({item.symbol for item in items}) == len(items)
    assert all(item.name_zh for item in items)
    assert "XLP" not in {item.symbol for item in items}
