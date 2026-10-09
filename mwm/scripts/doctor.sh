#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -u
source "$(dirname "$0")/common.sh"

CFG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/mwm"
backend="$(cat "$CFG_DIR/display-backend" 2>/dev/null || echo gamescope)"
render="$(cat "$CFG_DIR/gamescope-render-mode" 2>/dev/null || { [[ "$backend" == kwin ]] && echo rtscale || echo fsr; })"
case "$render" in rtscale|fsr) ;; *) render=fsr ;; esac
aspect="$(cat "$CFG_DIR/aspect-ratio" 2>/dev/null || echo auto)"
expected_w=""
expected_h=""
case "$aspect" in
  32:9) expected_w=2560; expected_h=720 ;;
  21:9) expected_w=1680; expected_h=720 ;;
  16:9) expected_w=1280; expected_h=720 ;;
  4:3) expected_w=960; expected_h=720 ;;
  3:2) expected_w=1080; expected_h=720 ;;
  *x*)
    if [[ "$aspect" =~ ^([0-9]+)x720$ ]]; then expected_w="${BASH_REMATCH[1]}"; expected_h=720; fi
    ;;
esac

if [[ "$backend" == gamescope && "$render" == rtscale && -n "$expected_w" ]]; then
  expected_w=$(( (expected_w * 150 + 50) / 100 ))
  (( expected_w % 2 == 0 )) || ((expected_w++))
  expected_h=1080
fi
pass(){ echo "[PASS] $*"; }
warn(){ echo "[WARN] $*"; }
info(){ echo "[INFO] $*"; }

version="$(cat "$MWM_DIR/VERSION" 2>/dev/null || cat "$MWM_DIR/../VERSION" 2>/dev/null || echo unknown)"
echo "=== MWM v$version Doctor ==="
echo "Source: $MWM_DIR"
echo

echo "[Host]"
printf "Kernel: "; uname -r
printf "Session: "; echo "${XDG_SESSION_TYPE:-unknown}"
printf "Desktop: "; echo "${XDG_CURRENT_DESKTOP:-unknown}"
printf "Waydroid CLI: "; command -v waydroid || true
printf "Python: "; python --version 2>&1 || true
printf "kdotool: "; command -v kdotool || echo "not found"
printf "gamescope: "; command -v gamescope || echo "not found"
echo

echo "[MWM mode]"
echo "RTScale Display Fix (saved): $(cat "${XDG_CONFIG_HOME:-$HOME/.config}/mwm/rtscale-zoom-fix" 2>/dev/null || echo on) / Apply then Waydroid Refresh"
echo "Backend: $backend"
echo "Render mode: $render"
echo "Display preset: $aspect"
if [[ "$backend" == gamescope ]]; then
  "$(dirname "$0")/gamescope-control.sh" status 2>/dev/null || true
  sharp="$(cat "$CFG_DIR/gamescope-sharpness" 2>/dev/null || echo 10)"
  fsr_scale="$(cat "$CFG_DIR/gamescope-fsr-scale" 2>/dev/null || echo 150)"
  overlay_mode="$(cat "$CFG_DIR/performance-overlay-mode" 2>/dev/null || echo off)"
  if [[ "$sharp" =~ ^([0-9]|1[0-9]|20)$ ]]; then
    sharp_pct=$(( (20 - sharp) * 5 ))
  else
    sharp_pct="?"
  fi
  case "$fsr_scale" in 100|125|150|175|200) ;; *) warn "Invalid FSR scale: $fsr_scale"; fsr_scale=150 ;; esac
  if [[ "$render" == rtscale ]]; then
    echo "Gamescope + RTScale: scale $(cat "$CFG_DIR/kwin-rtscale" 2>/dev/null || echo 3) / 1080-high display / fullscreen"
    if [[ ! -f "$CFG_DIR/gamescope-fsr-enabled" ]]; then
      [[ "$(cat "$CFG_DIR/gamescope-rtscale-fsr-enabled" 2>/dev/null || echo off)" == on ]] || fsr_scale=100
    fi
  fi
  if [[ -f "$CFG_DIR/gamescope-fsr-enabled" && "$(cat "$CFG_DIR/gamescope-fsr-enabled")" != on ]]; then fsr_scale=100; fi
  if [[ "$fsr_scale" == 100 ]]; then sharp_enabled=off; else sharp_enabled=on; fi
  if [[ "$sharp" =~ ^([0-9]|1[0-9]|20)$ ]]; then sharp_level=$((21-sharp)); else sharp_level="?"; fi
  echo "Gamescope: FSR ${fsr_scale}% / RCAS $sharp_enabled / Sharpness level $sharp_level / additional CAS off"
  echo "Performance Overlay: $overlay_mode / MWM layer-shell HUD"

fi
echo

echo "[Waydroid]"
waydroid status 2>&1 || true
wd_w="$(read_waydroid_dimension width 2>/dev/null | tr -d '\r[:space:]' || true)"
wd_h="$(read_waydroid_dimension height 2>/dev/null | tr -d '\r[:space:]' || true)"
echo "persist.waydroid.width=${wd_w:-<unset>}"
echo "persist.waydroid.height=${wd_h:-<unset>}"
echo "persist.waydroid.multi_windows=$(waydroid prop get persist.waydroid.multi_windows 2>/dev/null | tr -d '\r' || true)"
echo "persist.waydroid.width_padding=$(waydroid prop get persist.waydroid.width_padding 2>/dev/null | tr -d '\r' || true)"
echo "persist.waydroid.height_padding=$(waydroid prop get persist.waydroid.height_padding 2>/dev/null | tr -d '\r' || true)"

if [[ "$backend" == kwin ]]; then
  if [[ "$wd_w" =~ ^[0-9]+$ && "$wd_h" =~ ^[0-9]+$ ]] && (( wd_w > 0 && wd_h > 0 )); then
    info "KWin logical display ${wd_w}x${wd_h}; compare with Qt primaryScreen geometry"
  else
    warn "KWin logical display properties unavailable; Refresh must apply Display"
  fi
elif [[ -n "$expected_h" ]]; then
  if [[ "$wd_w" == "$expected_w" && "$wd_h" == "$expected_h" ]]; then
    pass "Fixed preset Waydroid output is ${expected_w}x${expected_h}"
  else
    warn "Fixed preset expected ${expected_w}x${expected_h} but properties are ${wd_w:-unset}x${wd_h:-unset}"
  fi
elif [[ "$backend" == gamescope && "$aspect" == auto ]]; then
  auto_height=720
  [[ "$render" != rtscale ]] || auto_height=1080
  if [[ "$wd_h" == "$auto_height" && "$wd_w" =~ ^[0-9]+$ ]]; then pass "Gamescope Auto uses ${wd_w}x${wd_h}"; else warn "Gamescope Auto should be ${auto_height}-high"; fi
fi

echo
printf "Android wm size: "
root_helper wm-size 2>/dev/null || echo "unavailable"
echo

echo "[Environment prerequisites]"
printf "Mirishita: "
if root_helper app-installed 2>/dev/null | grep -q '^package:'; then echo "installed"; else echo "NOT FOUND"; fi
printf "Native Bridge: "
nb="$(root_helper native-bridge 2>/dev/null || true)"
if [[ -n "$nb" && "$nb" != "0" ]]; then echo "$nb"; else echo "not detected"; fi
echo

echo "[Mesa GLES Render Scale]"
if [[ "$backend" == gamescope && "$render" == fsr ]]; then
  rtscale_state="$(root_helper rtscale-state 2>/dev/null || true)"
  if [[ "$rtscale_state" == present ]]; then
    warn "RTScale config still exists although FSR render mode is selected"
    root_helper rtscale-read 2>/dev/null || true
  elif [[ "$rtscale_state" == absent ]]; then
    pass "RTScale config absent on FSR render mode"
  else
    warn "RTScale state unknown (session unavailable or root helper requires update)"
  fi
else
  if cfg="$(root_helper rtscale-read 2>/dev/null)"; then
    printf '%s\n' "$cfg"
    scale="$(awk -F= '$1=="scale"{gsub(/[[:space:]]/,"",$2);print $2;exit}' <<<"$cfg")"
    base_w="$(awk -F= '$1=="base_width"{gsub(/[[:space:]]/,"",$2);print $2;exit}' <<<"$cfg")"
    base_h="$(awk -F= '$1=="base_height"{gsub(/[[:space:]]/,"",$2);print $2;exit}' <<<"$cfg")"
    if [[ "$backend" == gamescope ]]; then
      if [[ "$wd_w" =~ ^[0-9]+$ && "$wd_h" == 1080 ]]; then
        target_base=$(( (10#$wd_w * 720 + 540) / 1080 ))
        (( target_base % 2 == 0 )) || ((target_base++))
        [[ "$base_w" == "$target_base" && "$base_h" == 720 ]] && pass "RTScale base ${base_w}x720 / display ${wd_w}x1080 (configuration only)" || warn "RTScale base differs from 720-high render-target profile"
      else
        warn "RTScale requires the 1080-high Gamescope display; got ${wd_w}x${wd_h}"
      fi
    elif [[ "$wd_w" =~ ^[0-9]+$ && "$wd_h" =~ ^[0-9]+$ ]] && (( wd_h > 0 )); then
      target_base=$(( (10#$wd_w * 720 + 10#$wd_h / 2) / 10#$wd_h ))
      (( target_base % 2 == 0 )) || ((target_base++))
      [[ "$base_w" == "$target_base" && "$base_h" == 720 ]] && pass "KWin RTScale base matches applied display aspect" || warn "KWin RTScale base differs from applied display aspect"
    fi
    [[ "$scale" =~ ^([1-9]|10)$ ]] && pass "RTScale configured x$scale" || warn "RTScale scale invalid"
  else
    info "RTScale OFF"
  fi
fi
echo

echo "[Window aspect helper]"
printf "qdbus6: "; command -v qdbus6 || echo "not found (drag-time ratio lock unavailable)"
echo

echo "[Foreground App]"
"$(dirname "$0")/detect-running-app.sh" 2>&1 || true
echo

echo "[Play Assist]"
echo "Audio normalization: installer / legacy launch only; manual launch not normalized by Refresh"
printf "Performance Overlay: "
if [[ -f "$CFG_DIR/performance-overlay-mode" ]]; then cat "$CFG_DIR/performance-overlay-mode"; else echo "off (default)"; fi
if [[ "$backend" == gamescope ]]; then
  echo "Overlay renderer: MWM layer-shell HUD"
else
  echo "Overlay renderer: MWM layer-shell HUD"
fi
printf "Mouse as Touch setting: "
if [[ -f "$CFG_DIR/mouse-as-touch" ]]; then cat "$CFG_DIR/mouse-as-touch"; else echo "on (default)"; fi
printf "Mouse as Touch mapper runtime: "
"$(dirname "$0")/touch-mapper.sh" status 2>/dev/null || echo off
printf "RTScale Debug: "
"$(dirname "$0")/rtscale-debug.sh" status 2>/dev/null || true
