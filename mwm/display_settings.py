# SPDX-License-Identifier: MIT
"""Pure dimension calculations shared by the settings preview and validation."""
import re
from fractions import Fraction

PRESETS = {'32:9': 2560, '21:9': 1680, '16:9': 1280, '4:3': 960, '3:2': 1080}

def even(value):
    return value + value % 2

def ratio_width(width, height):
    if not 1 <= width <= 99 or not 1 <= height <= 99:
        raise ValueError('Aspect ratio values must be between 1 and 99.')
    result = even((720 * width + height // 2) // height)
    if not 320 <= result <= 7680:
        raise ValueError('This aspect ratio exceeds the supported display range.')
    return result

def dimensions(mode, rtscale, custom=(16, 9), screen=(1920, 1080)):
    if mode == 'custom':
        width = ratio_width(*custom)
    elif mode == 'auto':
        sw, sh = screen
        if min(sw, sh) <= 0:
            raise ValueError('Display geometry is unavailable.')
        width = even((720 * sw + sh // 2) // sh)
    else:
        width = PRESETS[mode]
    return (even((width * 150 + 50) // 100), 1080) if rtscale else (width, 720)

def legacy_ratio(value):
    match = re.fullmatch(r'(\d+)[x:](\d+)', value)
    if not match or min(map(int, match.groups())) <= 0:
        return 16, 9
    ratio = Fraction(*map(int, match.groups()))
    if max(ratio.numerator, ratio.denominator) <= 99:
        return ratio.numerator, ratio.denominator
    # Keep two-digit inputs; the UI requires Apply before any migrated value runs.
    choices = [(w, h) for w in range(1, 100) for h in range(1, 100)
               if 320 <= even((720*w+h//2)//h) <= 7680]
    return min(choices, key=lambda pair: abs(Fraction(*pair) - ratio))
