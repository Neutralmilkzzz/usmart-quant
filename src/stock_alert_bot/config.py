from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScannerConfig:
    scan_interval_minutes: int = 60
    top_n: int = 10
    enabled_priorities: tuple[str, ...] = ("P0", "P1")
    universe_path: Path = Path("data/universe_100.csv")
    state_path: Path = Path("runtime/state.json")
    last_scan_path: Path = Path("runtime/last_scan.json")


@dataclass
class FilterConfig:
    require_price: bool = True
    require_day_change_pct: bool = True


@dataclass
class FinnhubConfig:
    api_key: str | None = None
    timeout_seconds: float = 10
    max_retries: int = 3
    retry_backoff_seconds: float = 1
    calls_per_minute: int = 55


@dataclass
class NotifierConfig:
    telegram_enabled: bool = True
    discord_enabled: bool = True
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    discord_bot_token: str | None = None
    discord_channel_id: str | None = None
    discord_application_id: str | None = None
    discord_guild_id: str | None = None
    max_message_chars: int = 3900


@dataclass
class AppConfig:
    project_root: Path
    scanner: ScannerConfig = field(default_factory=ScannerConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    finnhub: FinnhubConfig = field(default_factory=FinnhubConfig)
    notifier: NotifierConfig = field(default_factory=NotifierConfig)

    def resolve_path(self, path: Path) -> Path:
        return path if path.is_absolute() else self.project_root / path


def load_config(
    config_path: str | Path | None = None,
    project_root: str | Path | None = None,
) -> AppConfig:
    root = Path(project_root or Path.cwd()).resolve()
    _load_env_dir(root / ".env")

    data: dict[str, Any] = {}
    if config_path:
        data = _read_yaml(Path(config_path))
    else:
        default_path = root / "config" / "config.yaml"
        if default_path.exists():
            data = _read_yaml(default_path)

    config = AppConfig(project_root=root)
    _apply_mapping(config, data)
    _apply_env(config)
    return config


def validate_runtime_config(
    config: AppConfig,
    *,
    require_finnhub: bool = True,
    require_notifier: bool = True,
) -> None:
    missing: list[str] = []
    if require_finnhub and not config.finnhub.api_key:
        missing.append("FINNHUB_API_KEY")

    telegram_ready = (
        config.notifier.telegram_enabled
        and config.notifier.telegram_bot_token
        and config.notifier.telegram_chat_id
    )
    discord_ready = (
        config.notifier.discord_enabled
        and config.notifier.discord_bot_token
        and config.notifier.discord_channel_id
    )
    if require_notifier and not (telegram_ready or discord_ready):
        missing.append("at least one configured notifier: Telegram or Discord")

    if missing:
        raise ValueError("Missing required runtime configuration: " + ", ".join(missing))


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to read YAML config files.") from exc
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Config file must contain a mapping: {path}")
    return loaded


def _apply_mapping(config: AppConfig, data: dict[str, Any]) -> None:
    scanner = data.get("scanner") or {}
    if scanner:
        config.scanner.scan_interval_minutes = int(
            scanner.get("scan_interval_minutes", config.scanner.scan_interval_minutes)
        )
        config.scanner.top_n = int(scanner.get("top_n", config.scanner.top_n))
        config.scanner.enabled_priorities = tuple(
            scanner.get("enabled_priorities", config.scanner.enabled_priorities)
        )
        config.scanner.universe_path = Path(
            scanner.get("universe_path", config.scanner.universe_path)
        )
        config.scanner.state_path = Path(scanner.get("state_path", config.scanner.state_path))
        config.scanner.last_scan_path = Path(
            scanner.get("last_scan_path", config.scanner.last_scan_path)
        )

    filters = data.get("filters") or {}
    if filters:
        config.filters.require_price = bool(
            filters.get("require_price", config.filters.require_price)
        )
        config.filters.require_day_change_pct = bool(
            filters.get("require_day_change_pct", config.filters.require_day_change_pct)
        )

    finnhub = data.get("finnhub") or {}
    if finnhub:
        config.finnhub.timeout_seconds = float(
            finnhub.get("timeout_seconds", config.finnhub.timeout_seconds)
        )
        config.finnhub.max_retries = int(finnhub.get("max_retries", config.finnhub.max_retries))
        config.finnhub.retry_backoff_seconds = float(
            finnhub.get("retry_backoff_seconds", config.finnhub.retry_backoff_seconds)
        )
        config.finnhub.calls_per_minute = int(
            finnhub.get("calls_per_minute", config.finnhub.calls_per_minute)
        )

    notifier = data.get("notifier") or {}
    if notifier:
        config.notifier.telegram_enabled = bool(
            notifier.get("telegram_enabled", config.notifier.telegram_enabled)
        )
        config.notifier.discord_enabled = bool(
            notifier.get("discord_enabled", config.notifier.discord_enabled)
        )
        config.notifier.max_message_chars = int(
            notifier.get("max_message_chars", config.notifier.max_message_chars)
        )


def _apply_env(config: AppConfig) -> None:
    config.finnhub.api_key = os.getenv("FINNHUB_API_KEY") or config.finnhub.api_key
    config.notifier.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    config.notifier.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    config.notifier.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
    config.notifier.discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")
    config.notifier.discord_application_id = os.getenv("DISCORD_APPLICATION_ID")
    config.notifier.discord_guild_id = os.getenv("DISCORD_GUILD_ID")


def _load_env_dir(path: Path) -> None:
    if not path.exists() or not path.is_dir():
        return
    for env_file in sorted(path.glob("*.env")):
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
