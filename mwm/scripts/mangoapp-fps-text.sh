#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Fast exec reader: MangoHud 0.8.4 reads command output after only 50ms.
set -u
cache="${1:-${XDG_STATE_HOME:-$HOME/.local/state}/mwm/mirishita-fps}"
missing() { printf '%s\n' '--.--'; exit 0; }
exec 3< "$cache" 2>/dev/null || missing
IFS=' ' read -r value rest <&3 || [[ -n "${value:-}" ]] || missing
# Stat the opened inode, since the collector atomically replaces the path.
metadata=$(stat -Lc '%Y %y' "/proc/$$/fd/3" 2>/dev/null) || missing
[[ "$metadata" =~ ^([0-9]+).*\.([0-9]{9}) ]] || missing
seconds=${BASH_REMATCH[1]}
fraction=${BASH_REMATCH[2]:0:6}
modified=$((seconds * 1000000 + 10#$fraction))
now=${EPOCHREALTIME/./}
age=$((10#$now - modified))
(( age >= 0 && age <= 2000000 )) || missing
# Collector output is always two decimal places; reject malformed input.
[[ "$value" =~ ^([0-9]{1,3})\.([0-9]{2})$ ]] || missing
scaled=$((10#${BASH_REMATCH[1]} * 100 + 10#${BASH_REMATCH[2]}))
(( scaled > 0 && scaled <= 24000 )) || missing
printf '%s\n' "$value"
