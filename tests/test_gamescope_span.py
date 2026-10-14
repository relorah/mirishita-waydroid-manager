import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('span', Path(__file__).resolve().parents[1] / 'mwm/scripts/gamescope_span.py')
span = importlib.util.module_from_spec(spec)
spec.loader.exec_module(span)

def output(w, h, scale, x, y, enabled=True):
    return dict(enabled=enabled, connected=True, size=dict(width=w,height=h), scale=scale, pos=dict(x=x,y=y))

class SpanTests(unittest.TestCase):
    def test_measured_base_does_not_follow_outer_display_ratio(self):
        self.assertEqual(span.calibrated_base(dict(display_width=3424,display_height=1080,base_width=2388,base_height=720),3424,1080),'2388x720')

    def test_rejects_stale_or_invalid_calibration(self):
        for fields in ([],dict(display_width=3408,display_height=1080,base_width=2388,base_height=720),dict(display_width=3424,display_height=1080,base_width=2388,base_height=2160)):
            with self.assertRaises(ValueError):span.calibrated_base(fields,3424,1080)

    def test_test_system_fractional_and_offset(self):
        self.assertEqual(span.geometry([output(3840,2160,1.45,0,0),output(1920,1080,1,2649,410)]),dict(x=0,y=0,width=4569,height=1490))

    def test_negative_origin_and_disabled_output(self):
        self.assertEqual(span.geometry([output(1920,1080,1,-1920,-200),output(1920,1080,1,0,0),output(7680,4320,1,10000,0,False)]),dict(x=-1920,y=-200,width=3840,height=1280))

    def test_requires_two_outputs(self):
        with self.assertRaises(ValueError): span.geometry([output(1920,1080,1,0,0)])

    def test_rejects_invalid_scales_and_oversized_canvas(self):
        for scale in (0,-1,float('nan'),float('inf')):
            with self.subTest(scale=scale), self.assertRaises(ValueError):
                span.geometry([output(1920,1080,scale,0,0),output(1920,1080,1,1920,0)])
        with self.assertRaises(ValueError): span.geometry([output(1920,1080,1,0,0),output(1920,1080,1,20000,0)])
