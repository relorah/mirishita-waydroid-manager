import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'mwm'))
from display_settings import dimensions, legacy_ratio, ratio_width

class DisplaySettingsTests(unittest.TestCase):
    def test_presets_and_rts_display_are_distinct(self):
        self.assertEqual(dimensions('16:9',False),(1280,720))
        self.assertEqual(dimensions('16:9',True),(1920,1080))
        self.assertEqual(dimensions('32:9',True),(3840,1080))

    def test_custom_ratio_and_legacy_migration(self):
        self.assertEqual(ratio_width(21,9),1680)
        self.assertEqual(dimensions('custom',True,(21,9)),(2520,1080))
        self.assertEqual(legacy_ratio('2560x1440'),(16,9))
        self.assertEqual(legacy_ratio('invalid'),(16,9))
        w,h=legacy_ratio('2272x720')
        self.assertTrue(1<=w<=99 and 1<=h<=99)
        self.assertLessEqual(abs(720*w/h-2272),2)

    def test_rejects_unsupported_ratios_and_unavailable_display(self):
        for ratio in ((0,9),(100,9),(99,1),(1,99)):
            with self.subTest(ratio=ratio),self.assertRaises(ValueError):ratio_width(*ratio)
        with self.assertRaises(ValueError):dimensions('auto',True,screen=(0,0))

    def test_auto_uses_display_aspect_and_even_dimensions(self):
        w,h=dimensions('auto',True,screen=(4371,1379))
        self.assertEqual(h,1080)
        self.assertEqual(w%2,0)
        self.assertLess(abs(w/h-4371/1379),.004)
