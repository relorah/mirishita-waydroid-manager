#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -Eeuo pipefail

source "$(dirname "$0")/common.sh"

MODE="${1:-auto}"
CFG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/mwm"
STATE_FILE="$CFG_DIR/aspect-ratio"
BASE_H=720
BACKEND=gamescope
case "$BACKEND" in kwin|gamescope) ;; *) echo "Invalid display backend: $BACKEND" >&2; exit 2 ;; esac

host_screen_size() {
  local out
  out="$(QT_QPA_PLATFORM=wayland python - <<'PY' 2>/dev/null || true
from PySide6.QtGui import QGuiApplication
app = QGuiApplication([])
s = app.primaryScreen()
if s:
    g = s.geometry()
    print(f"{g.width()} {g.height()}")
PY
)"
  if [[ "$out" =~ ^([0-9]+)[[:space:]]+([0-9]+)$ ]]; then
    printf '%s %s\n' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
  else
    if [[ "$BACKEND" == kwin ]]; then
      echo "KWin logical screen geometry unavailable; refusing to guess Waydroid size." >&2
      return 1
    fi
    printf '1920 1080\n'
  fi
}

case "$MODE" in
  auto)
    TARGET_W=""
    TARGET_H=""
    ;;
  4:3) TARGET_W=960; TARGET_H=720 ;;
  3:2) TARGET_W=1080; TARGET_H=720 ;;
  16:9) TARGET_W=1280; TARGET_H=720 ;;
  21:9) TARGET_W=1680; TARGET_H=720 ;;
  32:9) TARGET_W=2560; TARGET_H=720 ;;
  *x*)
    if [[ ! "$MODE" =~ ^([0-9]+)x([0-9]+)$ ]]; then
      echo "Invalid custom width mode: $MODE" >&2; exit 2
    fi
    TARGET_W="${BASH_REMATCH[1]}"; TARGET_H="${BASH_REMATCH[2]}"
    (( TARGET_W >= 320 && TARGET_W <= 7680 )) || { echo "Custom width out of range: ${TARGET_W}px" >&2; exit 2; }
    (( TARGET_H == BASE_H )) || { echo "Custom height must be ${BASE_H}px: ${TARGET_W}x${TARGET_H}" >&2; exit 2; }
    ;;
  *:*)
    if [[ ! "$MODE" =~ ^([0-9]+):([0-9]+)$ ]]; then echo "Invalid aspect ratio: $MODE" >&2; exit 2; fi
    RW="${BASH_REMATCH[1]}"; RH="${BASH_REMATCH[2]}"
    (( RW > 0 && RH > 0 )) || { echo "Invalid aspect ratio: $MODE" >&2; exit 2; }
    TARGET_H=$BASE_H
    TARGET_W=$(( (BASE_H * RW + RH / 2) / RH ))
    (( TARGET_W % 2 == 0 )) || ((TARGET_W++))
    ;;
  *) echo "Invalid display preset: $MODE" >&2; exit 2 ;;
esac

# Resolve before any properties are changed. KWin must never use the
# Gamescope internal-render size or an unverified physical-size fallback.
if [[ "$BACKEND" == kwin ]]; then
  screen="$(host_screen_size)" || exit 4
  read -r sw sh <<< "$screen"
  (( sw > 0 && sh > 0 )) || { echo "Invalid KWin logical geometry" >&2; exit 4; }
  if [[ "$MODE" == auto ]]; then
    TARGET_W=$sw; TARGET_H=$sh
  else
    rw=$TARGET_W; rh=$TARGET_H
    # Leave room for titlebar and borders when using an aspect-fit window.
    if (( sw * rh != sh * rw )); then
      fit_w=$((sw - 16)); fit_h=$((sh - 48))
    else
      fit_w=$sw; fit_h=$sh
    fi
    # Exact integer aspect avoids changing the RTScale 720-high base profile.
    a=$rw; b=$rh
    while (( b != 0 )); do rem=$((a % b)); a=$b; b=$rem; done
    unit_w=$((rw / a)); unit_h=$((rh / a))
    units=$((fit_w / unit_w)); (( fit_h / unit_h >= units )) || units=$((fit_h / unit_h))
    TARGET_W=$((units * unit_w)); TARGET_H=$((units * unit_h))
    (( TARGET_W > 0 && TARGET_H > 0 && TARGET_W <= sw && TARGET_H <= sh )) || {
      echo "KWin aspect cannot fit logical geometry" >&2; exit 4;
    }
  fi
fi

require_waydroid_initialized
mkdir -p "$CFG_DIR"
printf '%s\n' "$MODE" > "$STATE_FILE"
# prop set can log an error and exit zero when the session is stopped.
# Prepare only the saved intent; apply and verify after the platform boots.
if [[ "${2:-}" == --prepare ]]; then
  echo "Display prepared: $MODE / backend=$BACKEND"
  exit 0
fi

# Keep the proven v0.5.31 single-display Waydroid path. Multi-window mode has
# caused alpha/transparency and input issues with Mirishita.
refresh_guard || exit $?
waydroid prop set persist.waydroid.multi_windows false >/dev/null
refresh_guard || exit $?
waydroid prop set persist.waydroid.uevent false >/dev/null
refresh_guard || exit $?
waydroid prop set persist.waydroid.width_padding "" >/dev/null 2>&1 || true
refresh_guard || exit $?
waydroid prop set persist.waydroid.height_padding "" >/dev/null 2>&1 || true

if [[ "$BACKEND" == gamescope ]]; then
  # Normal uses a 720-high client; High Quality uses a 1080-high client.
  # Auto derives the ratio from the host screen.
  if [[ "$MODE" == "auto" ]]; then
    read -r sw sh < <(host_screen_size)
    (( sh > 0 )) || sh=1080
    TARGET_H=720
    TARGET_W=$(( (TARGET_H * sw + sh / 2) / sh ))
    (( TARGET_W % 2 == 0 )) || ((TARGET_W++))
  fi
  render_mode="${MWM_RENDER_MODE_OVERRIDE:-$(cat "$CFG_DIR/gamescope-render-mode" 2>/dev/null || echo fsr)}"
  if [[ "$render_mode" == rtscale ]]; then
    TARGET_W=$(( (TARGET_W * 150 + 50) / 100 ))
    (( TARGET_W % 2 == 0 )) || ((TARGET_W++))
    TARGET_H=1080
  fi
fi
refresh_guard || exit $?
  waydroid prop set persist.waydroid.width "$TARGET_W" >/dev/null
refresh_guard || exit $?
  waydroid prop set persist.waydroid.height "$TARGET_H" >/dev/null

# Verify the live platform, rather than trusting prop set's exit status.
expected_w="${TARGET_W:-}"; expected_h="${TARGET_H:-}"
actual_w="$(read_waydroid_dimension width)"
actual_h="$(read_waydroid_dimension height)"
[[ "$actual_w" == "$expected_w" && "$actual_h" == "$expected_h" ]] || {
  echo "Display properties did not apply: expected ${expected_w}x${expected_h}, got ${actual_w}x${actual_h}" >&2
  exit 4
}

# Never combine physical-display properties with an Android wm-size override.
root_helper reset-wm-size >/dev/null 2>&1 || true

mkdir -p "$CFG_DIR"
printf '%s\n' "$MODE" > "$STATE_FILE"

echo "Display: $MODE / backend=$BACKEND / Waydroid ${TARGET_W}x${TARGET_H}"
