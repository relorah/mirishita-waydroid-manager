#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -u
source "$(dirname "$0")/common.sh"
set +e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/mwm"
CFG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/mwm"
OUT="${1:-$ROOT/logs/mwm-$(date +%Y%m%d-%H%M%S).log}"
mkdir -p "$(dirname "$OUT")" || exit 1
TMP="$(mktemp "$(dirname "$OUT")/.mwm-diagnostic.XXXXXXXX")" || exit 1
trap 'rm -f "$TMP"' EXIT
section() {
  local label="$1" seconds="$2" rc=0; shift 2
  printf '\n=== %s | %s ===\n' "$label" "$(date --iso-8601=ns)"
  timeout --kill-after=2 "$seconds" "$@" 2>&1 || rc=$?
  printf '\n[collection_exit=%s]\n' "$rc"
}
file_section() {
  local path="$1" lines="$2"
  printf '\n=== file: %s ===\n' "${path##*/}"
  if [[ -f "$path" ]]; then
    stat -c 'modified=%y bytes=%s' "$path"
    tail -n "$lines" "$path"
  else
    echo '[unavailable: file does not exist]'
  fi
}
{
  printf 'MWM_DIAGNOSTIC format=2 version=%s collected=%s\n' "$(cat "$ROOT/VERSION")" "$(date --iso-8601=ns)"
  echo 'Command sections record collection_exit. A zero CLI exit is not proof that Android was reachable.'
  echo 'Gamescope raw lines without timestamps cannot establish ordering against other logs.'
  section 'MWM doctor' 30 "$ROOT/scripts/doctor.sh"
  section 'Waydroid status' 5 waydroid status
  section 'Gamescope status' 5 "$ROOT/scripts/gamescope-control.sh" status
  section 'Gamescope exit code' 5 "$ROOT/scripts/gamescope-control.sh" exit-code
  section 'Installed implementation hashes' 5 sha256sum "$ROOT/mwm.py" "$ROOT/settings_safety.py" "$ROOT/scripts/waydroid-control.sh" "$MWM_ROOT_HELPER"
  echo '=== saved settings ==='
  if [[ -d "$CFG_DIR" ]]; then
    while IFS= read -r -d '' config; do
      printf '\n--- %s ---\n' "${config##*/}"
      head -c 8192 "$config" 2>&1
    done < <(find "$CFG_DIR" -maxdepth 1 -type f -print0 | sort -z)
  else echo '[settings unavailable]'; fi
  section 'Container service' 5 systemctl status waydroid-container --no-pager
  section 'Container journal' 8 journalctl -u waydroid-container -n 400 -o short-iso-precise --no-pager
  section 'Kernel journal (permission failures are retained)' 8 journalctl -k -n 200 -o short-iso-precise --no-pager
  section 'Gamescope core inventory' 8 coredumpctl list gamescope --no-pager
  section 'Gamescope latest core information' 8 coredumpctl info gamescope --no-pager
  section 'Display geometry' 5 "$ROOT/scripts/kwin-waydroid-geometry.sh"
  printf '\n=== Android logcat ===\n'
  android_rc=0
  android_log="$(timeout --kill-after=2 25 sudo -n "$MWM_ROOT_HELPER" logcat-dump 2>&1)" || android_rc=$?
  printf '%s\n[collection_exit=%s]\n' "$android_log" "$android_rc"
  if [[ -z "$android_log" ]] || grep -qiE 'container is STOPPED|container is not running|unrecognized arguments|permission denied|password is required' <<< "$android_log"; then
    echo '[ANDROID_LOG_NOT_ACQUIRED: CLI output is not Android crash history]'
  fi
  file_section "$STATE_DIR/kwin-fullscreen.log" 200
  file_section "$STATE_DIR/refresh-events.log" 500
  file_section "$STATE_DIR/rts-fast-state.json" 20
  file_section "$STATE_DIR/mirishita-launch.log" 500
  file_section "$STATE_DIR/mirishita-launch.log.1" 200
  file_section "$STATE_DIR/gamescope.log" 500
  for n in 1 2 3; do file_section "$STATE_DIR/gamescope.log.$n" 250; done
  file_section "$STATE_DIR/rtscale-debug.log" 800
  file_section "$STATE_DIR/performance-overlay.log" 200
  file_section "$STATE_DIR/gamescope-window-fit.log" 150
  section 'Process tree' 5 ps -u "$(id -u)" -o pid,ppid,pgid,sid,etimes,args --forest
  printf '\nMWM_DIAGNOSTIC_END collected=%s\n' "$(date --iso-8601=ns)"
} > "$TMP" 2>&1
mv -f "$TMP" "$OUT" || exit 1
trap - EXIT
printf '%s\n' "$OUT"
