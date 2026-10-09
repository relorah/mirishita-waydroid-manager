import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bc250_gpu', ROOT / 'mwm/bc250_gpu.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)

class CacheReaderTests(unittest.TestCase):
    def test_values_identity_and_freshness(self):
        cases = [
            ('1 0000:01:00.0 100.0 25.5', 101, 25.5),
            ('1 0000:01:00.0 100.0 0', 101, 0),
            ('1 0000:01:00.0 100.0 100', 102, 100),
            ('1 0000:01:00.0 100.0 101', 101, None),
            ('1 0000:01:00.0 100.0 nan', 101, None),
            ('1 0000:01:00.0 100.0 25', 102.01, None),
            ('1 0000:01:00.0 100.0 25', 99, None),
            ('1 0000:02:00.0 100.0 25', 101, None),
            ('1 0000:01:00.0 100.0 25 extra', 101, None),
            ('bad', 101, None),
        ]
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'cache'
            for text, now, expected in cases:
                with self.subTest(text=text, now=now):
                    p.write_text(text)
                    self.assertEqual(shared.read_load('0000:01:00.0', p, now), expected)
            self.assertIsNone(shared.read_load('0000:01:00.0', p.with_name('missing'), 101))
