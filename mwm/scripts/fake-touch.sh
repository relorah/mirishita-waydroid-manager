#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -Eeuo pipefail
source "$(dirname "$0")/common.sh"
PKG="com.bandainamcoent.imas_millionlive_theaterdays"
ACTION="${1:-status}"

if ! waydroid_initialized; then
  [[ "$ACTION" == "status" ]] && { echo "unavailable"; exit 0; }
  require_waydroid_initialized
fi

case "$ACTION" in
  on) waydroid prop set persist.waydroid.fake_touch "$PKG"; echo "on" ;;
  off) waydroid prop set persist.waydroid.fake_touch ""; echo "off" ;;
  status)
    value="$(waydroid prop get persist.waydroid.fake_touch 2>/dev/null || true)"
    [[ "$value" == *"$PKG"* ]] && echo "on" || echo "off"
    ;;
  *) echo "usage: $0 on|off|status" >&2; exit 2 ;;
esac
