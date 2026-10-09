#!/usr/bin/env bash
# Wait for Android's actual display, not just saved Waydroid properties.
set -Eeuo pipefail
source "$(dirname "$0")/common.sh"
w="$(read_waydroid_dimension width)"
h="$(read_waydroid_dimension height)"
[[ "$w" =~ ^[0-9]+$ && "$h" =~ ^[0-9]+$ ]] || exit 4
stable=0
for ((attempt=0; attempt<40; attempt++)); do
  refresh_guard || exit $?
  size="$(root_helper wm-size 2>/dev/null || true)"
  frames="$(root_helper display-frames 2>/dev/null || true)"
  actual="$(sed -nE 's/^(Physical|Override) size: ([0-9]+x[0-9]+).*$/\2/p' <<<"$size" | tail -n1)"
  if [[ "$actual" == "${w}x${h}" ]] &&
     grep -Eq "logicalFrame=Rect\\(0, 0 - ${w}, ${h}\\)" <<<"$frames"; then
    ((stable+=1))
    if (( stable >= 4 )); then
      refresh_guard || exit $?
      echo "Display READY: ${w}x${h} / Android geometry stable"
      exit 0
    fi
  else
    stable=0
  fi
  sleep 0.25
done
echo "Android display did not settle at ${w}x${h}; refusing to launch the game with stale geometry." >&2
exit 42
