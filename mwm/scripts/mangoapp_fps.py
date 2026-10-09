#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Display Android game-layer FPS through MangoApp's external-text element."""
import argparse
import math
import os
import shlex
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "mwm"


def fps_text(cache=None, now=None):
    cache = Path(cache) if cache is not None else STATE / "mirishita-fps"
    now = time.time() if now is None else now
    try:
        with cache.open(encoding="ascii") as stream:
            age = now - os.fstat(stream.fileno()).st_mtime
            values = stream.read().split()
        fps = float(values[0])
        if not (0 <= age <= 2 and math.isfinite(fps) and 0 < fps <= 240):
            return "--.--"
        return f"{fps:.2f}"
    except (OSError, ValueError, IndexError):
        return "--.--"


def render_config(visible):
    text = (ROOT / "config/MangoApp.conf").read_text(encoding="utf-8")
    command = shlex.join(["/bin/bash", str(Path(__file__).resolve().with_name("mangoapp-fps-text.sh"))])
    text = text.replace("@MWM_GAME_FPS@", command)
    lines = [line for line in text.splitlines() if not line.strip().startswith("no_display")]
    return "\n".join(lines) + f"\nno_display={0 if visible else 1}\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="store_true")
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args()
    print(render_config(args.visible), end="") if args.config else print(fps_text())
