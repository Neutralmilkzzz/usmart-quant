from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta

from stock_alert_bot.notifier.base import NotifierManager
from stock_alert_bot.notifier.formatter import format_scan_result
from stock_alert_bot.scanner import StockScanner
from stock_alert_bot.state.machine import ScanAlreadyRunningError

LOGGER = logging.getLogger(__name__)


class SchedulerRunner:
    def __init__(
        self,
        *,
        scanner: StockScanner,
        notifier_manager: NotifierManager,
        interval_minutes: int = 60,
        max_message_chars: int = 3900,
    ) -> None:
        self.scanner = scanner
        self.notifier_manager = notifier_manager
        self.interval_minutes = interval_minutes
        self.max_message_chars = max_message_chars
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
        try:
            result = self.scanner.run_scan(trigger="scheduled")
        except ScanAlreadyRunningError:
            LOGGER.info("scheduled_scan_skipped reason=already_running")
            return
        messages = format_scan_result(result, max_message_chars=self.max_message_chars)
        notify_errors = self.notifier_manager.send_messages(messages)
        if notify_errors:
            LOGGER.error("scheduled_scan_notify_errors count=%s", len(notify_errors))

    def _seconds_until_next_run(self) -> float:
        now = datetime.now()
        if self.interval_minutes == 60:
            next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
            return max((next_hour - now).total_seconds(), 1)
        return max(self.interval_minutes * 60, 1)
