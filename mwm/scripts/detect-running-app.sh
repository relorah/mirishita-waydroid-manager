#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
source "$(dirname "$0")/common.sh"

pkg="$(waydroid prop get waydroid.active_apps 2>/dev/null \
  | tr ', ' '\n' \
  | grep -E '^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+$' \
  | head -n1 || true)"

if [[ -z "$pkg" ]]; then
  pkg="$(root_helper foreground-package 2>/dev/null | head -n1 || true)"
fi

[[ -n "$pkg" ]] || { echo "NO_FOREGROUND_APP"; exit 3; }

case "$pkg" in
  com.android.systemui|com.android.launcher*|com.google.android.apps.nexuslauncher)
    echo "SYSTEM_APP:$pkg"
    exit 4
    ;;
esac

echo "$pkg"
