#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Migration cleanup for pre-Gamescope installations; never starts a mapper.
set -euo pipefail
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/mwm"
PID_FILE="$STATE_DIR/touch-mapper.pid"
pid="$(cat "$PID_FILE" 2>/dev/null || true)"
running() {
  [[ "$pid" =~ ^[0-9]+$ && -r "/proc/$pid/cmdline" ]] || return 1
  tr '\0' ' ' < "/proc/$pid/cmdline" | grep -Fq 'touch_mapper.py'
}
case "${1:-status}" in
  stop)
    if running; then kill "$pid" 2>/dev/null || true; fi
    rm -f "$PID_FILE"
    echo off
    ;;
  status) if running; then echo on; else echo off; fi ;;
  *) echo "Legacy mapper removed; usage: $0 stop|status" >&2; exit 2 ;;
esac
