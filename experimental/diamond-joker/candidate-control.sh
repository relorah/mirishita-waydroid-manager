#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# The ZIP supplies candidate/ and SHA256SUMS next to this script.
set -Eeuo pipefail
here="$(cd -- "$(dirname -- "$0")" && pwd)"
mode="${1:-}"
manager="${2:-}"
[[ "$mode" == apply || "$mode" == restore ]] || { echo "usage: $0 apply|restore <installed-MWM-directory> <backup-directory>" >&2; exit 2; }
[[ "$manager" == /* && -f "$manager/mwm/scripts/waydroid-control.sh" && -f "$manager/mwm/scripts/set-rtscale.sh" ]] || { echo "An absolute installed MWM directory is required" >&2; exit 2; }
backup="${3:-}"
[[ "$backup" == /* ]] || { echo "An absolute backup directory is required" >&2; exit 2; }
conf="${XDG_CONFIG_HOME:-$HOME/.config}/mwm"
lib=/var/lib/waydroid/overlay/vendor/lib64/libgallium_dri.so
helper=/usr/local/libexec/mwm-root-helper
original=c948f8a46180779872b214f2597a36d1d0ee59abb32dc00274c0df9e57de331a
candidate=6a77eba981aa1163edf3351f15be38752a9a0da7ecd2a04ee273f388cb8b7116
hash() { sha256sum "$1" | cut -d ' ' -f1; }
if [[ "$mode" == apply ]]; then
  [[ "$(hash "$lib")" == "$original" ]] || { echo "This candidate requires the verified v0.83 overlay checkpoint" >&2; exit 2; }
  [[ ! -e "$backup" ]] || { echo "Backup directory already exists; choose a new one" >&2; exit 2; }
  [[ "$(hash "$here/candidate/libgallium_dri.so")" == "$candidate" ]] || { echo "Candidate hash mismatch" >&2; exit 2; }
  (cd "$here"; sha256sum -c SHA256SUMS) || exit 2
  mkdir -m 700 -p -- "$backup"
  printf '%s\n' "$manager" > "$backup/manager-path"
  cp -a -- "$manager/mwm/scripts/set-rtscale.sh" "$backup/set-rtscale.sh"
  sudo cp -a -- "$lib" "$backup/libgallium_dri.so"
  sudo cp -a -- "$helper" "$backup/mwm-root-helper"
  if [[ -f "$conf/rtscale-msaa-samples" ]]; then
    cp -a -- "$conf/rtscale-msaa-samples" "$backup/rtscale-msaa-samples"
  else
    : > "$backup/msaa-setting-was-absent"
  fi
  # Every modified path has a backup before stopping the working runtime.
  bash "$manager/mwm/scripts/waydroid-control.sh" stop
  sudo install -m 0644 -- "$here/candidate/libgallium_dri.so" "$lib"
  sudo install -m 0755 -- "$here/candidate/mwm-root-helper" "$helper"
  install -m 0755 -- "$here/candidate/set-rtscale.sh" "$manager/mwm/scripts/set-rtscale.sh"
  printf '2\n' > "$conf/rtscale-msaa-samples"
  printf '%s\n' "$candidate" > "$backup/applied-candidate-sha256"
else
  [[ -f "$backup/applied-candidate-sha256" && "$(cat "$backup/manager-path")" == "$manager" ]] || { echo "This backup does not identify an applied candidate for this manager" >&2; exit 2; }
  [[ "$(hash "$lib")" == "$candidate" && "$(hash "$backup/libgallium_dri.so")" == "$original" ]] || { echo "Overlay changed since applying; inspect before restoring" >&2; exit 2; }
  # Do not overwrite subsequent script/helper updates.
  [[ "$(hash "$manager/mwm/scripts/set-rtscale.sh")" == "$(hash "$here/candidate/set-rtscale.sh")" && "$(hash "$helper")" == "$(hash "$here/candidate/mwm-root-helper")" ]] || { echo "Helper or script changed since applying; inspect before restoring" >&2; exit 2; }
  bash "$manager/mwm/scripts/waydroid-control.sh" stop
  sudo cp -a -- "$backup/libgallium_dri.so" "$lib"
  sudo cp -a -- "$backup/mwm-root-helper" "$helper"
  cp -a -- "$backup/set-rtscale.sh" "$manager/mwm/scripts/set-rtscale.sh"
  if [[ -f "$backup/msaa-setting-was-absent" ]]; then
    rm -f -- "$conf/rtscale-msaa-samples"
  else
    cp -a -- "$backup/rtscale-msaa-samples" "$conf/rtscale-msaa-samples"
  fi
fi
bash "$manager/mwm/scripts/waydroid-control.sh" restart
actual="$(sudo -n "$helper" rtscale-read)"
if [[ "$mode" == apply ]]; then
  grep -Fqx msaa_samples=2 <<< "$actual" || { echo "Policy readback failed; restore using $backup" >&2; exit 1; }
fi
printf '%s\n' "$actual"
echo "$mode complete; backup retained at $backup"
