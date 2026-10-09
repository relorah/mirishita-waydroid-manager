#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import csv
import fcntl
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bc250_gpu as shared


def main():
    shared.STATE.mkdir(parents=True, exist_ok=True)
    with (shared.STATE / 'bc250-gpu.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        candidates = []
        for node in sorted(Path('/sys/class/drm').glob('renderD*/device')):
            try:
                if int((node / 'vendor').read_text(), 16) == 0x1002 and int((node / 'device').read_text(), 16) == 0x13fe:
                    candidates.append((Path('/dev/dri') / node.parent.name, node.resolve().name))
            except (OSError, ValueError):
                pass
        if len(candidates) != 1 or not shared.enabled():
            return
        node, pci = candidates[0]
        binary = Path(__file__).resolve().parent / 'mangoapp-native/bc250-gpu-probe'
        process = subprocess.Popen([str(binary), str(node), '2', '0'], stdout=subprocess.PIPE, text=True)
        def stop(*_):
            raise SystemExit
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        temp = shared.CACHE.with_name(shared.CACHE.name + f'.{os.getpid()}')
        try:
            for row in csv.DictReader(process.stdout):
                try:
                    mode = (shared.CFG / 'performance-overlay-mode').read_text().strip()
                except OSError:
                    mode = 'off'
                if not shared.enabled() or mode not in ('mangoapp', 'minimal', 'detailed'):
                    break
                value = float(row['gpu_active_percent'])
                if not 0 <= value <= 100:
                    break
                temp.write_text(f'1 {pci} {time.monotonic():.6f} {value:.2f}\n')
                temp.replace(shared.CACHE)
        finally:
            process.terminate()
            process.wait(timeout=3)
            temp.unlink(missing_ok=True)
            shared.CACHE.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
