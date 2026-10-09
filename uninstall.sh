#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
exec bash "$(dirname -- "${BASH_SOURCE[0]}")/mwm/scripts/uninstall.sh" "$@"
