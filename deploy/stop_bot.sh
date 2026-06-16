#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE_NAME="${SERVICE_NAME:-us-stock-alert-bot.service}"
APP_DIR="${APP_DIR:-/opt/usmart-quant}"
PID_FILE="${PID_FILE:-$APP_DIR/runtime/bot.pid}"
PROCESS_PATTERN="${PROCESS_PATTERN:-stock_alert_bot.app}"
TERM_TIMEOUT_SECONDS="${TERM_TIMEOUT_SECONDS:-10}"

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

stop_systemd_service() {
  sudo_cmd systemctl stop "$SERVICE_NAME"
  sudo_cmd systemctl status "$SERVICE_NAME" --no-pager -l || true
}

stop_pid_file_process() {
  if [[ ! -f "$PID_FILE" ]]; then
    return 1
  fi

  pid="$(cat "$PID_FILE")"
  if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$PID_FILE"
    return 1
  fi

  echo "Stopping bot PID $pid"
  kill -TERM "$pid" 2>/dev/null || true

  for _ in $(seq 1 "$TERM_TIMEOUT_SECONDS"); do
    if ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$PID_FILE"
      echo "Stopped bot PID $pid"
      return 0
    fi
    sleep 1
  done

  echo "PID $pid did not stop after ${TERM_TIMEOUT_SECONDS}s; sending SIGKILL"
  kill -KILL "$pid" 2>/dev/null || true
  rm -f "$PID_FILE"
}

stop_matching_processes() {
  matched_pids="$(pgrep -f "$PROCESS_PATTERN" || true)"
  if [[ -z "$matched_pids" ]]; then
    echo "No matching bot process found."
    return 0
  fi

  echo "Stopping matching processes: $matched_pids"
  pkill -TERM -f "$PROCESS_PATTERN" || true
  sleep 2
  if pgrep -f "$PROCESS_PATTERN" >/dev/null 2>&1; then
    echo "Some matching processes are still running; sending SIGKILL"
    pkill -KILL -f "$PROCESS_PATTERN" || true
  fi
}

main() {
  if service_exists; then
    stop_systemd_service
    return
  fi

  if ! stop_pid_file_process; then
    stop_matching_processes
  fi
}

main "$@"
