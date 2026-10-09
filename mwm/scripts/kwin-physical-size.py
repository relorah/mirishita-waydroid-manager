#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare Android physical size with the scaled primary-screen logical size."""
import math
import os
import re
import sys
os.environ.setdefault("QT_QPA_PLATFORM", "wayland")
from PySide6.QtGui import QGuiApplication
from waydroid_dimensions import parse_dimension_output

def main():
    width, height = parse_dimension_output(sys.argv[1]), parse_dimension_output(sys.argv[2])
    match = re.search(r"Physical size:\s*(\d+)x(\d+)", sys.argv[3])
    if min(width, height) <= 0 or not match:
        raise ValueError("Android physical size unavailable")
    app = QGuiApplication([])
    screen = app.primaryScreen()
    if screen is None:
        raise ValueError("Primary screen unavailable")
    scale = float(screen.devicePixelRatio())
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("Display scale unavailable")
    actual = tuple(map(int, match.groups()))
    expected = (width * scale, height * scale)
    tolerance = max(2, math.ceil(scale) + 1)
    ok = all(abs(a - e) <= tolerance for a, e in zip(actual, expected))
    print(f"KWin size check: logical={width}x{height} scale={scale:g} "
          f"expected={expected[0]:.2f}x{expected[1]:.2f} "
          f"physical={actual[0]}x{actual[1]} tolerance={tolerance}px match={ok}", flush=True)
    return 0 if ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, IndexError, RuntimeError) as error:
        print("KWin size check unavailable: " + str(error), file=sys.stderr)
        sys.exit(2)
