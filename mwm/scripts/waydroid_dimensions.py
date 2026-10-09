#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read Waydroid dimensions without treating diagnostic messages as values."""
import re
import subprocess
import sys
import time

def parse_dimension_output(text):
    values = [int(line.strip()) for line in text.splitlines()
              if re.fullmatch(r"[0-9]+", line.strip())]
    if not values or len(set(values)) != 1 or not 0 < values[0] <= 65535:
        raise ValueError("Waydroid dimension missing, invalid or ambiguous")
    return values[0]

def read_dimension(key, attempts=3, run=None, sleep=None):
    if key not in ("width", "height"):
        raise ValueError("Unsupported dimension property")
    run = run or subprocess.run
    sleep = sleep or time.sleep
    last = "unavailable"
    for attempt in range(attempts):
        try:
            result = run(["waydroid", "prop", "get", "persist.waydroid." + key],
                         capture_output=True, text=True, timeout=3, check=True)
            return parse_dimension_output(result.stdout)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            last = str(error)
            if attempt + 1 < attempts:
                sleep(0.25)
    raise RuntimeError("Waydroid " + key + " read failed after " + str(attempts) + " attempts: " + last)

def read_dimensions(attempts=1):
    return [read_dimension(key, attempts=attempts) for key in ("width", "height")]

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: waydroid_dimensions.py width|height")
        print(read_dimension(sys.argv[1]))
    except (ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
