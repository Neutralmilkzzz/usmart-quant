from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta

from stock_alert_bot.scan_dispatcher import ScanDispatcher

LOGGER = logging.getLogger(__name__)


class SchedulerRunner:
    def __init__(
        self,
        *,
        scan_dispatcher: ScanDispatcher,
        interval_minutes: int = 60,
    ) -> None:
        self.scan_dispatcher = scan_dispatcher
        self.interval_minutes = interval_minutes
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self.run_forever, name="scan-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def run_forever(self) -> None:
        LOGGER.info("scheduler_started interval_minutes=%s", self.interval_minutes)
        while not self._stop_event.is_set():
            wait_seconds = self._seconds_until_next_run()
            if self._stop_event.wait(wait_seconds):
                break
            self.run_once()

    def run_once(self) -> None:
        started = self.scan_dispatcher.start_scan(trigger="scheduled")
        if not started:
            LOGGER.info("scheduled_scan_skipped reason=already_running")
        else:
            LOGGER.info("scheduled_scan_dispatched")

    def _seconds_until_next_run(self) -> float:
        now = datetime.now()
        if self.interval_minutes == 60:
            next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
            return max((next_hour - now).total_seconds(), 1)
        return max(self.interval_minutes * 60, 1)
