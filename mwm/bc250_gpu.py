# SPDX-License-Identifier: MIT
"""Experimental shared BC250 GPU activity cache (read-only hardware sampling)."""
import math
import os
import subprocess
import time
from pathlib import Path

STATE = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'mwm'
CFG = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'mwm'
CACHE = STATE / 'bc250-gpu'
FLAG = CFG / 'bc250-gpu-test'


def enabled():
    return FLAG.exists()


def read_load(device, cache=CACHE, now=None):
    now = time.monotonic() if now is None else now
    try:
        fields = Path(cache).read_text().split()
        if len(fields) != 4 or fields[0] != '1' or fields[1] != device:
            return None
        stamp, value = map(float, fields[2:])
        if not (math.isfinite(stamp) and math.isfinite(value) and 0 <= now-stamp <= 2 and 0 <= value <= 100):
            return None
        return value
    except (OSError, ValueError):
        return None


def ensure_collector():
    if enabled():
        script = Path(__file__).resolve().parent / 'scripts/bc250-gpu-collector.py'
        STATE.mkdir(parents=True, exist_ok=True)
        with (STATE / 'bc250-gpu-test.log').open('a') as log:
            subprocess.Popen(['/usr/bin/python3', str(script)], stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
