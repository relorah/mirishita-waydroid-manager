"""Read saved FSR settings through the production Bash function."""
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class FSRScaleTests(unittest.TestCase):
    def read_scale(self, mode, value=None, enabled='on', legacy=False):
        text = (ROOT/'mwm/scripts/gamescope-control.sh').read_text()
        function = 'read_fsr_scale() {' + text.split('read_fsr_scale() {',1)[1].split('\nread_sharpness_native()',1)[0]
        with tempfile.TemporaryDirectory() as directory:
            cfg = pathlib.Path(directory)
            (cfg/('gamescope-rtscale-fsr-enabled' if legacy else 'gamescope-fsr-enabled')).write_text(enabled)
            if value is not None:
                (cfg/'gamescope-fsr-scale').write_text(str(value))
            env = dict(os.environ, CFG_DIR=directory, FSR_SCALE_FILE=str(cfg/'gamescope-fsr-scale'), TEST_MODE=mode)
            result = subprocess.run(['bash','-c','set -eu\nread_render_mode() { echo "$TEST_MODE"; }\n'+function+'\nread_fsr_scale'], env=env, capture_output=True,text=True,check=True)
            return int(result.stdout)

    def test_saved_scales_in_both_render_modes(self):
        for mode in ('rtscale','fsr'):
            for value in (125,150,175,200):
                with self.subTest(mode=mode,value=value):
                    self.assertEqual(self.read_scale(mode,value),value)

    def test_defaults_invalid_and_disabled(self):
        for mode in ('rtscale','fsr'):
            self.assertEqual(self.read_scale(mode),150)
            self.assertEqual(self.read_scale(mode,999),150)
            self.assertEqual(self.read_scale(mode,200,enabled='off'),100)

    def test_legacy_rtscale_setting(self):
        self.assertEqual(self.read_scale('rtscale',200,legacy=True),200)
        self.assertEqual(self.read_scale('rtscale',200,enabled='off',legacy=True),100)
