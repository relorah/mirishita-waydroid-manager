#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "mwm"))
runpy.run_path(str(HERE / "mwm" / "mwm.py"), run_name="__main__")
