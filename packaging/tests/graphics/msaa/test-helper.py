#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise argument and overlay guards without root or an Android write."""
import json, os, pathlib, subprocess, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[4]
class HelperTest(unittest.TestCase):
    def run_helper(self, extra=(), compatible=True):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            library = root / 'libgallium_dri.so'
            library.write_bytes(b'msaa_samples=%d (MWM reconstruction)' if compatible else b'old Mesa')
            text = (ROOT / 'packaging/mwm-root-helper').read_text()
            text = text.replace('need_root\n\ncase', 'case').replace('/var/lib/waydroid/overlay/vendor/lib64/libgallium_dri.so', str(library))
            helper = root / 'helper'; helper.write_text(text)
            mock = root / 'waydroid'
            mock.write_text('#!/usr/bin/env python3\nimport json,sys,pathlib\npathlib.Path(__file__).with_name("args.json").write_text(json.dumps(sys.argv[1:]))\nprint("MWM_RTSCALE_WRITTEN")\n')
            mock.chmod(0o755)
            p = subprocess.run(['bash', str(helper), 'rtscale-write', '6', '1280', '720', *extra], env=dict(os.environ, PATH=str(root)+':'+os.environ['PATH']), capture_output=True, text=True)
            log = root / 'args.json'
            return p, json.loads(log.read_text())[-1] if log.exists() else None
    def test_legacy_default(self):
        p, conf = self.run_helper(); self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(conf, 'schema_version=1\n\n[application.0]\nname=com.bandainamcoent.imas_millionlive_theaterdays\nbase_width=1280\nbase_height=720\nscale=6\nsurface=1\ntexelsize=0\nzoom_fix=1')
    def test_optin(self):
        p, conf = self.run_helper(('1','1','2')); self.assertEqual(p.returncode, 0, p.stderr); self.assertTrue(conf.endswith('\nmsaa_samples=2'))
    def test_invalid(self):
        p, conf = self.run_helper(('1','1','4')); self.assertEqual(p.returncode, 2); self.assertIsNone(conf)
    def test_zoom_fix_required(self):
        p, conf = self.run_helper(('1','0','2')); self.assertEqual(p.returncode, 2); self.assertIsNone(conf)
    def test_old_overlay_rejected(self):
        p, conf = self.run_helper(('1','1','2'), False); self.assertEqual(p.returncode, 2); self.assertIsNone(conf)
if __name__ == '__main__': unittest.main()
