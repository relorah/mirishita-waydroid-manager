#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
source "$(dirname "$0")/common.sh"
require_waydroid_initialized

VALUE="${1:-}"
CFG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/mwm"
SCALE_STATE="$CFG_DIR/kwin-rtscale"
mkdir -p "$CFG_DIR"
BACKEND=gamescope
case "$BACKEND" in kwin|gamescope) ;; *) echo "Invalid display backend: $BACKEND" >&2; exit 2 ;; esac

resolve_base() {
  local w="" h=""
  if [[ "$BACKEND" == gamescope ]]; then
    # The game has been force-stopped here. Surface detection can therefore
    # return nothing (or stale geometry); use the applied display properties.
    w="$(read_waydroid_dimension width)" || return 1
    h="$(read_waydroid_dimension height)" || return 1
    if [[ ! "$w" =~ ^[0-9]+$ || "$h" != 1080 ]] ||
       (( 10#$w < 320 || 10#$w > 11520 )); then
      echo "RTScale: Gamescope display size unavailable or invalid (${w}x${h}); Refresh must apply Display first." >&2
      return 1
    fi
    # RTScale matches the game's 720-high render targets, even though the
    # Android/Gamescope display is 1080-high (known-working checkpoint).
    w=$(( (10#$w * 720 + 540) / 1080 ))
    (( w % 2 == 0 )) || ((w++))
    printf '%sx720\n' "$w"
    return 0
  fi

  # Keep RTScale's 720-high render-target profile separate from the
  # logical KWin display size, using its applied aspect ratio.
  w="$(read_waydroid_dimension width)" || return 1
  h="$(read_waydroid_dimension height)" || return 1
  [[ "$w" =~ ^[0-9]+$ && "$h" =~ ^[0-9]+$ ]] &&
    (( 10#$w > 0 && 10#$h > 0 )) || {
      echo "RTScale: KWin display size unavailable; apply Display first." >&2; return 1;
    }
  w=$(( (10#$w * 720 + 10#$h / 2) / 10#$h ))
  (( w % 2 == 0 )) || ((w++))
  printf '%sx720\n' "$w"
}

# The RTScale-OFF render profile removes the Android RTScale configuration.
# The RTScale-ON profile may also use Gamescope FSR for presentation.
RENDER_MODE="${MWM_RENDER_MODE_OVERRIDE:-$(cat "$CFG_DIR/gamescope-render-mode" 2>/dev/null || { [[ "$BACKEND" == kwin ]] && echo rtscale || echo fsr; })}"
if [[ "$BACKEND" == "gamescope" && "$RENDER_MODE" != "rtscale" ]]; then
  removed="$(root_helper rtscale-remove)" || exit 1
  if ! grep -qx 'MWM_RTSCALE_ABSENT' <<<"$removed"; then
    echo "Mesa GLES Render Scale disable verification failed" >&2
    exit 1
  fi
  echo "Mesa GLES Render Scale=OFF / Gamescope backend (Android-side verified)"
  exit 0
fi

if [[ "$VALUE" == "off" ]]; then
  removed="$(root_helper rtscale-remove)" || exit 1
  if ! grep -qx 'MWM_RTSCALE_ABSENT' <<<"$removed"; then
    echo "Mesa GLES Render Scale disable verification failed" >&2
    exit 1
  fi
  printf 'off\n' > "$SCALE_STATE"
  echo "Mesa GLES Render Scale=OFF"
  exit 0
fi

[[ "$VALUE" =~ ^([1-9]|10)$ ]] || {
  echo "invalid scale: $VALUE (allowed: 1-10)" >&2
  exit 2
}
printf '%s\n' "$VALUE" > "$SCALE_STATE"

BASE="$(resolve_base)"
BASE_W="${BASE%x*}"
BASE_H="${BASE#*x}"

SURFACE="${MWM_RTSCALE_SURFACE:-1}"
[[ "$SURFACE" == 0 || "$SURFACE" == 1 ]] || { echo "Invalid RTScale surface override (allowed: 0 or 1)" >&2; exit 2; }
# Keep the 0.5.72 policy by default; allow a single-variable diagnostic comparison.
ZOOM_FIX=1
if [[ -f "$CFG_DIR/rtscale-zoom-fix" ]]; then
  case "$(tr -d '\r\n' < "$CFG_DIR/rtscale-zoom-fix")" in
    on) ZOOM_FIX=1 ;;
    off) ZOOM_FIX=0 ;;
    *) echo "Invalid abnormal zoom fix setting; Apply settings again." >&2; exit 2 ;;
  esac
fi
written="$(root_helper rtscale-write "$VALUE" "$BASE_W" "$BASE_H" "$SURFACE" "$ZOOM_FIX")"
if ! grep -qx MWM_RTSCALE_WRITTEN <<<"$written"; then
  echo "Mesa GLES Render Scale write was not confirmed inside Android. Update the MWM root helper with install.sh --update-app." >&2
  exit 1
fi
actual="$(root_helper rtscale-read)" || {
  echo "Mesa GLES Render Scale config could not be read back from Android" >&2
  exit 1
}
for expected in \
  "schema_version=1" \
  "name=$APP_ID" \
  "base_width=$BASE_W" \
  "base_height=$BASE_H" \
  "scale=$VALUE" \
  "surface=$SURFACE" \
  "texelsize=0" \
  "zoom_fix=$ZOOM_FIX"
do
  grep -Fqx "$expected" <<<"$actual" || {
    echo "Mesa GLES Render Scale verification failed: missing '$expected'" >&2
    echo "--- Android-side config ---" >&2
    printf '%s\n' "$actual" >&2
    exit 1
  }
done

echo "Mesa GLES Render Scale=${VALUE} base=${BASE_W}x${BASE_H} surface=${SURFACE} / ${BACKEND} ${RENDER_MODE} (Android-side verified)"
