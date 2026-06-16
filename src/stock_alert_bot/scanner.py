from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Protocol

from stock_alert_bot.models import MarketStatus, ScanResult, ScannerStatus, StockSnapshot, UniverseItem, utc_now
from stock_alert_bot.selector.ranker import select_top_candidates
from stock_alert_bot.state.machine import ScanAlreadyRunningError, StateMachine
from stock_alert_bot.universe.loader import load_universe

LOGGER = logging.getLogger(__name__)


class FeedClient(Protocol):
    def get_market_status(self, exchange: str = "US") -> MarketStatus:
        ...

    def fetch_snapshot(self, item: UniverseItem) -> StockSnapshot:
        ...


class StockScanner:
    def __init__(
        self,
        *,
        universe_path: str | Path,
        feed_client: FeedClient,
        state_machine: StateMachine,
        last_scan_path: str | Path,
        top_n: int = 10,
        enabled_priorities: tuple[str, ...] = ("P0", "P1"),
    ) -> None:
        self.universe_path = Path(universe_path)
        self.feed_client = feed_client
        self.state_machine = state_machine
        self.last_scan_path = Path(last_scan_path)
        self.top_n = top_n
        self.enabled_priorities = enabled_priorities

    def run_scan(self, *, trigger: str = "manual") -> ScanResult:
        started_at = self.state_machine.try_start(trigger=trigger)
        if started_at is None:
            raise ScanAlreadyRunningError("扫描正在运行，请稍后再试。")

        market_status = MarketStatus.unknown()
        snapshots: list[StockSnapshot] = []
        errors: list[str] = []
        universe_count = 0

        try:
            LOGGER.info("scan_started trigger=%s", trigger)
            universe = load_universe(
                self.universe_path,
                enabled_priorities=self.enabled_priorities,
            )
            universe_count = len(universe)

            try:
                market_status = self.feed_client.get_market_status("US")
            except Exception as exc:  # noqa: BLE001
                message = f"market status failed: {exc}"
                LOGGER.warning(message)
                errors.append(message)

            for item in universe:
                try:
                    snapshots.append(self.feed_client.fetch_snapshot(item))
                except Exception as exc:  # noqa: BLE001
                    message = f"snapshot failed for {item.symbol}: {exc}"
                    LOGGER.warning(message)
                    snapshots.append(
                        StockSnapshot(
                            symbol=item.symbol,
                            name=item.name,
                            name_zh=item.name_zh,
                            asset_type=item.asset_type,
                            watch_priority=item.watch_priority,
                            errors=[message],
                        )
                    )

            candidates = select_top_candidates(
                snapshots,
                market_status=market_status,
                top_n=self.top_n,
                enabled_priorities=self.enabled_priorities,
            )
            symbol_error_count = sum(1 for snapshot in snapshots if snapshot.errors)
            errors.extend(error for snapshot in snapshots for error in snapshot.errors)

            if not candidates:
                status = ScannerStatus.FAILED
            elif symbol_error_count or errors:
                status = ScannerStatus.PARTIAL_SUCCESS
            else:
                status = ScannerStatus.SUCCESS

            finished_at = utc_now()
            result = ScanResult(
                status=status,
                trigger=trigger,
                market_status=market_status,
                candidates=candidates,
                started_at=started_at,
                finished_at=finished_at,
                universe_count=universe_count,
                snapshot_count=len(snapshots),
                error_count=len(errors),
                errors=errors,
            )
            self._write_last_scan(result)
            self.state_machine.finish(
                status=status,
                finished_at=finished_at,
                result_count=result.result_count,
                error=errors[0] if errors else None,
            )
            LOGGER.info(
                "scan_finished status=%s universe=%s snapshots=%s results=%s errors=%s",
                status.value,
                universe_count,
                len(snapshots),
                result.result_count,
                len(errors),
            )
            return result
        except Exception as exc:  # noqa: BLE001
            finished_at = utc_now()
            message = str(exc)
            result = ScanResult(
                status=ScannerStatus.FAILED,
                trigger=trigger,
                market_status=market_status,
                candidates=[],
                started_at=started_at,
                finished_at=finished_at,
                universe_count=universe_count,
                snapshot_count=len(snapshots),
                error_count=len(errors) + 1,
                errors=[*errors, message],
            )
            self._write_last_scan(result)
            self.state_machine.finish(
                status=ScannerStatus.FAILED,
                finished_at=finished_at,
                result_count=0,
                error=message,
            )
            LOGGER.error("scan_failed error=%s", message)
            return result

    def _write_last_scan(self, result: ScanResult) -> None:
        self.last_scan_path.parent.mkdir(parents=True, exist_ok=True)
        with self.last_scan_path.open("w", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
