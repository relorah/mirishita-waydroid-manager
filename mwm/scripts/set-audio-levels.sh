#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -u
source "$(dirname "$0")/common.sh"

WAIT_LOOPS=30
[[ "${1:-}" == "--nowait" ]] && WAIT_LOOPS=1

# MWM v0.5.52 treats audio normalization as always-on internal behavior.
root_helper set-media-volume >/dev/null 2>&1 || true
ANDROID_VOL="$(root_helper get-media-volume 2>/dev/null | tail -n1 || true)"
[[ -n "$ANDROID_VOL" ]] || ANDROID_VOL="15"
echo "Android media volume: $ANDROID_VOL/15"

find_waydroid_stream() {
  wpctl status 2>/dev/null |
    sed -n '/Streams:/,/^Video/p' |
    grep -m1 'Waydroid' |
    sed -E 's/^[^0-9]*([0-9]+)\..*/\1/' || true
}

for _ in $(seq 1 "$WAIT_LOOPS"); do
  STREAM_ID="$(find_waydroid_stream)"
  if [[ "$STREAM_ID" =~ ^[0-9]+$ ]]; then
    wpctl set-mute "$STREAM_ID" 0 >/dev/null 2>&1 || true
    wpctl set-volume "$STREAM_ID" 1.0 >/dev/null 2>&1 || true
    echo "Waydroid PipeWire stream $STREAM_ID: unmuted / 100%"
    exit 0
  fi
  (( WAIT_LOOPS > 1 )) && sleep 0.5
 done

echo "Waydroid PipeWire stream: not found (Android media level was still set)"
exit 0
