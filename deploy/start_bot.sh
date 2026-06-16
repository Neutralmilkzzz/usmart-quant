#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE_NAME="${SERVICE_NAME:-us-stock-alert-bot.service}"
APP_DIR="${APP_DIR:-/opt/usmart-quant}"
PYTHON_BIN="${PYTHON_BIN:-$APP_DIR/.venv/bin/python}"
LOG_FILE="${LOG_FILE:-$APP_DIR/runtime/logs/app.log}"
PID_FILE="${PID_FILE:-$APP_DIR/runtime/bot.pid}"

sudo_cmd() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

service_exists() {
  command -v systemctl >/dev/null 2>&1 \
    && systemctl list-unit-files "$SERVICE_NAME" --no-legend 2>/dev/null | grep -q "$SERVICE_NAME"
}

start_with_systemd() {
  sudo_cmd systemctl daemon-reload
  sudo_cmd systemctl start "$SERVICE_NAME"
  sudo_cmd systemctl status "$SERVICE_NAME" --no-pager -l
}

start_with_nohup() {
  if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Python runtime not found or not executable: $PYTHON_BIN" >&2
    exit 1
  fi

  mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$PID_FILE")"
  cd "$APP_DIR"

  if [[ -f "$PID_FILE" ]]; then
    existing_pid="$(cat "$PID_FILE")"
    if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
      echo "Bot is already running with PID $existing_pid"
      exit 0
    fi
  fi

  nohup "$PYTHON_BIN" -m stock_alert_bot.app >>"$LOG_FILE" 2>&1 &
  bot_pid="$!"
  echo "$bot_pid" >"$PID_FILE"
  echo "Started US Stock Alert Bot with PID $bot_pid"
  echo "Log file: $LOG_FILE"
}

main() {
  if service_exists; then
    start_with_systemd
  else
    start_with_nohup
  fi
}

main "$@"
