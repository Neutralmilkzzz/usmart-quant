#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-/opt/usmart-quant}"
REPO_URL="${REPO_URL:-https://github.com/Neutralmilkzzz/usmart-quant.git}"
BRANCH="${BRANCH:-main}"
SERVICE_NAME="${SERVICE_NAME:-us-stock-alert-bot.service}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env/finnhub.env}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_TESTS="${RUN_TESTS:-0}"
START_SERVICE="${START_SERVICE:-1}"

sudo_cmd() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

install_system_packages() {
  if command -v apt-get >/dev/null 2>&1; then
    sudo_cmd apt-get update
    sudo_cmd apt-get install -y git python3 python3-venv python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    sudo_cmd dnf install -y git python3 python3-pip
  elif command -v yum >/dev/null 2>&1; then
    sudo_cmd yum install -y git python3 python3-pip
  else
    echo "No supported package manager found. Please install git, python3, venv, and pip manually." >&2
  fi
}

sync_source_code() {
  if [[ -d "$APP_DIR/.git" ]]; then
    echo "Updating existing repo at $APP_DIR"
    git -C "$APP_DIR" fetch origin "$BRANCH"
    git -C "$APP_DIR" checkout "$BRANCH"
    git -C "$APP_DIR" pull --ff-only origin "$BRANCH"
    return
  fi

  if [[ -e "$APP_DIR" ]] && [[ -n "$(find "$APP_DIR" -mindepth 1 -maxdepth 1 2>/dev/null)" ]]; then
    echo "APP_DIR exists and is not an empty git checkout: $APP_DIR" >&2
    echo "Set APP_DIR to an empty directory or deploy from an existing git checkout." >&2
    exit 1
  fi

  sudo_cmd mkdir -p "$APP_DIR"
  sudo_cmd chown "$(id -u):$(id -g)" "$APP_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
}

install_python_environment() {
  cd "$APP_DIR"
  "$PYTHON_BIN" -m venv "$APP_DIR/.venv"
  "$APP_DIR/.venv/bin/python" -m pip install --upgrade pip setuptools wheel

  if [[ "$RUN_TESTS" == "1" ]]; then
    "$APP_DIR/.venv/bin/python" -m pip install -e "$APP_DIR[dev]"
    "$APP_DIR/.venv/bin/python" -m pytest
  else
    "$APP_DIR/.venv/bin/python" -m pip install -e "$APP_DIR"
  fi

  "$APP_DIR/.venv/bin/python" -m compileall src tests
}

prepare_runtime_dirs() {
  mkdir -p "$APP_DIR/.env" "$APP_DIR/runtime/logs"
  chmod 700 "$APP_DIR/.env"
}

write_env_template_if_missing() {
  if [[ -f "$ENV_FILE" ]]; then
    chmod 600 "$ENV_FILE"
    return
  fi

  cat >"$ENV_FILE" <<'ENV'
FINNHUB_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=
DISCORD_APPLICATION_ID=
DISCORD_GUILD_ID=
ENV
  chmod 600 "$ENV_FILE"
  echo "Created env template at $ENV_FILE"
  echo "Fill the required tokens before starting the service."
}

env_has_value() {
  local key="$1"
  grep -E "^${key}=.+" "$ENV_FILE" >/dev/null 2>&1
}

env_ready_for_service() {
  env_has_value "FINNHUB_API_KEY" || return 1

  if env_has_value "TELEGRAM_BOT_TOKEN" && env_has_value "TELEGRAM_CHAT_ID"; then
    return 0
  fi

  if env_has_value "DISCORD_BOT_TOKEN" && env_has_value "DISCORD_CHANNEL_ID"; then
    return 0
  fi

  return 1
}

install_systemd_service() {
  service_path="/etc/systemd/system/$SERVICE_NAME"
  tmp_service="$(mktemp)"

  cat >"$tmp_service" <<UNIT
[Unit]
Description=US Stock Alert Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$APP_DIR/.venv/bin/python -m stock_alert_bot.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT

  sudo_cmd mv "$tmp_service" "$service_path"
  sudo_cmd chmod 644 "$service_path"
  sudo_cmd systemctl daemon-reload
  sudo_cmd systemctl enable "$SERVICE_NAME"
}

start_service_if_ready() {
  if [[ "$START_SERVICE" != "1" ]]; then
    echo "START_SERVICE is not 1; service was installed but not started."
    return
  fi

  if ! env_ready_for_service; then
    echo "Service not started because $ENV_FILE is missing required values."
    echo "Required: FINNHUB_API_KEY and at least one notifier channel."
    return
  fi

  sudo_cmd systemctl restart "$SERVICE_NAME"
  sudo_cmd systemctl status "$SERVICE_NAME" --no-pager -l
}

main() {
  install_system_packages
  sync_source_code
  install_python_environment
  prepare_runtime_dirs
  write_env_template_if_missing
  install_systemd_service
  start_service_if_ready
}

main "$@"
