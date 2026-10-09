#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -Eeuo pipefail
source "$(dirname "$0")/common.sh"

PKG="com.bandainamcoent.imas_millionlive_theaterdays"
INTERVAL="${1:-0.2}"
LAYER=""
LAST_TS=""
STALE_COUNT=0

rh() {
  root_helper "$@" 2>/dev/null | tr -d '\r'
}

app_running() {
  [[ -n "$(rh pidof-mirishita || true)" ]]
}

latency_for() {
  local layer="$1"
  rh sf-latency "$layer" || true
}

latest_ts() {
  awk '
    NR == 1 { next }
    $1 ~ /^[0-9]+$/ && $1 > 0 { last=$1 }
    END { if (last) print last; else print 0 }
  '
}

calc_metrics() {
  # Output: "fps frametime_ms".  FPS uses a rolling history while frametime is
  # the latest complete SurfaceFlinger interval, so Detailed mode can expose
  # short pacing spikes instead of deriving 1000/FPS.
  awk '
    NR == 1 { next }
    $1 ~ /^[0-9]+$/ && $1 > 0 {
      v=$1+0
      if (n == 0 || v > t[n]) t[++n]=v
    }
    END {
      fps=0; ft=0
      if (n >= 2) {
        s=(n > 31 ? n-30 : 1)
        dt=t[n]-t[s]
        frames=n-s
        if (dt > 0 && frames > 0) fps=frames*1000000000/dt
        lastdt=t[n]-t[n-1]
        if (lastdt > 0) ft=lastdt/1000000
      }
      if (fps <= 0 || fps > 240) fps=0
      if (ft <= 0 || ft > 1000) ft=0
      printf "%.2f %.2f\n", fps, ft
    }
  '
}

find_layer() {
  local best="" best_ts=0 layer out ts
  while IFS= read -r layer; do
    [[ "$layer" == *"$PKG"* && "$layer" == *"TID:"* ]] || continue
    out="$(latency_for "$layer")"
    ts="$(printf '%s\n' "$out" | latest_ts)"
    [[ "$ts" =~ ^[0-9]+$ ]] || ts=0
    if (( ts > best_ts )); then
      best_ts="$ts"
      best="$layer"
    fi
  done < <(rh sf-list || true)
  printf '%s\n' "$best"
}

while true; do
  if ! app_running; then
    LAYER=""; LAST_TS=""; STALE_COUNT=0
    printf '0.00 0.00\n'
    sleep "$INTERVAL"
    continue
  fi

  if [[ -z "$LAYER" ]]; then
    LAYER="$(find_layer)"
    LAST_TS=""; STALE_COUNT=0
    if [[ -z "$LAYER" ]]; then
      printf '0.00 0.00\n'
      sleep "$INTERVAL"
      continue
    fi
  fi

  OUT="$(latency_for "$LAYER")"
  TS="$(printf '%s\n' "$OUT" | latest_ts)"
  METRICS="$(printf '%s\n' "$OUT" | calc_metrics)"

  if [[ "$TS" == "0" || -z "$TS" ]]; then
    LAYER=""; LAST_TS=""; STALE_COUNT=0
    printf '0.00 0.00\n'
    sleep "$INTERVAL"
    continue
  fi

  if [[ -n "$LAST_TS" && "$TS" == "$LAST_TS" ]]; then
    STALE_COUNT=$((STALE_COUNT + 1))
  else
    STALE_COUNT=0
  fi
  LAST_TS="$TS"

  if (( STALE_COUNT >= 2 )); then
    LAYER=""; LAST_TS=""; STALE_COUNT=0
    printf '0.00 0.00\n'
  else
    printf '%s\n' "$METRICS"
  fi
  sleep "$INTERVAL"
done
