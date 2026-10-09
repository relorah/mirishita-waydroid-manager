#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Own the Gamescope session and retain the exit status for startup diagnostics.
set -u
exit_file="$1"; shift
trap 'printf "143\n" > "$exit_file"; exit 143' TERM
"$@"
rc=$?
printf '%s\n' "$rc" > "$exit_file"
exit "$rc"
