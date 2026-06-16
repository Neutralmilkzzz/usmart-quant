from __future__ import annotations

import argparse
import logging
import signal
import threading
import time
from pathlib import Path

from stock_alert_bot.config import load_config, validate_runtime_config
from stock_alert_bot.feed.finnhub_client import FinnhubClient
from stock_alert_bot.notifier.base import ConsoleNotifier, NotifierManager
from stock_alert_bot.notifier.commands import BotCommandHandler
from stock_alert_bot.notifier.discord_bot import DiscordNotifier
from stock_alert_bot.notifier.formatter import format_scan_result
from stock_alert_bot.notifier.telegram_bot import TelegramNotifier, TelegramPollingBot
from stock_alert_bot.scanner import StockScanner
from stock_alert_bot.scheduler.runner import SchedulerRunner
from stock_alert_bot.state.machine import StateMachine
from stock_alert_bot.state.store import StateStore
from stock_alert_bot.utils.logging import configure_logging

LOGGER = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="US stock alert bot")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--scan-once", action="store_true")
    parser.add_argument("--console", action="store_true", help="Also print alerts to stdout.")
    parser.add_argument("--no-scheduler", action="store_true")
    parser.add_argument("--no-bots", action="store_true", help="Do not start Telegram/Discord command loops.")
    args = parser.parse_args()

    configure_logging()
    config = load_config(args.config)
    validate_runtime_config(
        config,
        require_finnhub=True,
        require_notifier=not args.console,
    )

    feed_client = FinnhubClient(
        config.finnhub.api_key or "",
        timeout_seconds=config.finnhub.timeout_seconds,
        max_retries=config.finnhub.max_retries,
        retry_backoff_seconds=config.finnhub.retry_backoff_seconds,
    )
    state_machine = StateMachine(StateStore(config.resolve_path(config.scanner.state_path)))
    scanner = StockScanner(
        universe_path=config.resolve_path(config.scanner.universe_path),
        feed_client=feed_client,
        state_machine=state_machine,
        last_scan_path=config.resolve_path(config.scanner.last_scan_path),
        top_n=config.scanner.top_n,
        enabled_priorities=config.scanner.enabled_priorities,
    )
    notifiers, telegram_notifier, discord_notifier = _build_notifiers(config, console=args.console)
    notifier_manager = NotifierManager(notifiers)

    if args.scan_once:
        result = scanner.run_scan(trigger="manual")
        messages = format_scan_result(
            result,
            max_message_chars=config.notifier.max_message_chars,
        )
        notifier_manager.send_messages(messages)
        return

    scheduler_enabled = not args.no_scheduler
    command_handler = BotCommandHandler(
        scanner=scanner,
        state_machine=state_machine,
        scheduler_enabled=scheduler_enabled,
        max_message_chars=config.notifier.max_message_chars,
    )

    scheduler = None
    if scheduler_enabled:
        scheduler = SchedulerRunner(
            scanner=scanner,
            notifier_manager=notifier_manager,
            interval_minutes=config.scanner.scan_interval_minutes,
            max_message_chars=config.notifier.max_message_chars,
        )
        scheduler.start()

    if not args.no_bots:
        _start_telegram_if_configured(telegram_notifier, command_handler)
        if discord_notifier:
            discord_notifier.run_slash_bot(command_handler)
            return

    _wait_forever(scheduler)


def _build_notifiers(config, *, console: bool) -> tuple[list[object], TelegramNotifier | None, DiscordNotifier | None]:
    notifiers: list[object] = []
    telegram_notifier = None
    discord_notifier = None

    if console:
        notifiers.append(ConsoleNotifier())

    if (
        config.notifier.telegram_enabled
        and config.notifier.telegram_bot_token
        and config.notifier.telegram_chat_id
    ):
        telegram_notifier = TelegramNotifier(
            token=config.notifier.telegram_bot_token,
            chat_id=config.notifier.telegram_chat_id,
            timeout_seconds=config.finnhub.timeout_seconds,
        )
        notifiers.append(telegram_notifier)

    if (
        config.notifier.discord_enabled
        and config.notifier.discord_bot_token
        and config.notifier.discord_channel_id
    ):
        discord_notifier = DiscordNotifier(
            token=config.notifier.discord_bot_token,
            channel_id=config.notifier.discord_channel_id,
            application_id=config.notifier.discord_application_id,
            guild_id=config.notifier.discord_guild_id,
            timeout_seconds=config.finnhub.timeout_seconds,
        )
        notifiers.append(discord_notifier)

    if not notifiers:
        raise ValueError("No notifier configured.")
    return notifiers, telegram_notifier, discord_notifier


def _start_telegram_if_configured(
    telegram_notifier: TelegramNotifier | None,
    command_handler: BotCommandHandler,
) -> None:
    if not telegram_notifier:
        return
    bot = TelegramPollingBot(notifier=telegram_notifier, command_handler=command_handler)
    thread = threading.Thread(target=bot.poll_forever, name="telegram-polling", daemon=True)
    thread.start()


def _wait_forever(scheduler: SchedulerRunner | None) -> None:
    stop_event = threading.Event()

    def _stop(_signum, _frame) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    LOGGER.info("bot_runtime_started")
    try:
        while not stop_event.is_set():
            time.sleep(1)
    finally:
        if scheduler:
            scheduler.stop()
        LOGGER.info("bot_runtime_stopped")


if __name__ == "__main__":
    main()
