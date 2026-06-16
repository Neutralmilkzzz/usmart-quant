from __future__ import annotations

import threading
from datetime import datetime
from typing import Any

from stock_alert_bot.models import ScannerStatus, isoformat_or_none, utc_now
from stock_alert_bot.state.store import StateStore


class ScanAlreadyRunningError(RuntimeError):
    pass


class StateMachine:
    def __init__(self, store: StateStore | None = None) -> None:
        self._store = store
        self._lock = threading.Lock()
        self._state: dict[str, Any] = store.load() if store else {}
        self._scanner_state = ScannerStatus.IDLE

    @property
    def scanner_state(self) -> ScannerStatus:
        return self._scanner_state

    def try_start(self, *, trigger: str) -> datetime | None:
        with self._lock:
            if self._scanner_state == ScannerStatus.RUNNING:
                return None
            now = utc_now()
            self._scanner_state = ScannerStatus.RUNNING
            self._state.update(
                {
                    "scanner_state": ScannerStatus.RUNNING.value,
                    "last_scan_trigger": trigger,
                    "last_scan_started_at": now.isoformat(),
                    "last_error": None,
                }
            )
            self._persist()
            return now

    def finish(
        self,
        *,
        status: ScannerStatus,
        finished_at: datetime | None = None,
        result_count: int = 0,
        error: str | None = None,
    ) -> None:
        with self._lock:
            finished = finished_at or utc_now()
            self._scanner_state = ScannerStatus.IDLE
            self._state.update(
                {
                    "scanner_state": ScannerStatus.IDLE.value,
                    "last_scan_finished_at": finished.isoformat(),
                    "last_scan_status": status.value,
                    "last_result_count": result_count,
                    "last_error": error,
                }
            )
            self._persist()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            data = dict(self._state)
            data["scanner_state"] = self._scanner_state.value
            return data

    def mark_scheduled(self) -> None:
        with self._lock:
            if self._scanner_state == ScannerStatus.IDLE:
                self._scanner_state = ScannerStatus.SCHEDULED
                self._state["scanner_state"] = ScannerStatus.SCHEDULED.value
                self._persist()

    def _persist(self) -> None:
        if self._store:
            self._store.save(self._state)


def serialize_datetime(value: datetime | None) -> str | None:
    return isoformat_or_none(value)
