import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('safety',ROOT/'mwm/settings_safety.py')
safety=importlib.util.module_from_spec(spec)
spec.loader.exec_module(safety)

class KWinDisabledTests(unittest.TestCase):
    def test_rejects_new_kwin_setting(self):
        with self.assertRaises(ValueError):safety.validate({'display-backend':'kwin'})
        safety.validate({'display-backend':'gamescope'})

    def test_direct_entry_points_fail_before_compositor_access(self):
        for action in ('start','run','wait'):
            with self.subTest(action=action):
                p=subprocess.run([sys.executable,str(ROOT/'mwm/scripts/kwin-fullscreen.py'),action],capture_output=True,text=True)
                self.assertEqual(p.returncode,4)
                self.assertIn('KWin Direct is disabled',p.stderr)
