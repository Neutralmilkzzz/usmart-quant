from __future__ import annotations

import logging
import threading

from stock_alert_bot.notifier.base import NotifierManager
from stock_alert_bot.notifier.formatter import format_scan_result
from stock_alert_bot.scanner import ScanAlreadyRunningError, StockScanner

LOGGER = logging.getLogger(__name__)


class ScanDispatcher:
    def __init__(
        self,
        *,
        scanner: StockScanner,
        notifier_manager: NotifierManager,
        max_message_chars: int = 3900,
    ) -> None:
        self.scanner = scanner
        self.notifier_manager = notifier_manager
        self.max_message_chars = max_message_chars
        self._launch_lock = threading.Lock()
        self._worker: threading.Thread | None = None

    def start_scan(self, *, trigger: str) -> bool:
        with self._launch_lock:
            if self._worker and self._worker.is_alive():
                return False
            self._worker = threading.Thread(
                target=self._run_scan,
                kwargs={"trigger": trigger},
                name=f"scan-{trigger}",
                daemon=True,
            )
            self._worker.start()
            return True

    def _run_scan(self, *, trigger: str) -> None:
        LOGGER.info("scan_worker_started trigger=%s", trigger)
        try:
            result = self.scanner.run_scan(trigger=trigger)
        except ScanAlreadyRunningError:
            LOGGER.info("scan_worker_skipped trigger=%s reason=already_running", trigger)
            return

        messages = format_scan_result(
            result,
            max_message_chars=self.max_message_chars,
        )
        notify_errors = self.notifier_manager.send_messages(messages)
        if notify_errors:
            LOGGER.error(
                "scan_worker_notify_errors trigger=%s count=%s",
                trigger,
                len(notify_errors),
            )
        LOGGER.info(
            "scan_worker_finished trigger=%s status=%s results=%s",
            trigger,
            result.status.value,
            result.result_count,
        )
