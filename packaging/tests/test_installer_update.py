"""Exercise the actual user-file installer function without sudo or live state."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]

@unittest.skipUnless(shutil.which('rsync'),'rsync is required')
class InstallerUpdateTests(unittest.TestCase):
    def test_updates_same_timestamp_content_and_keeps_settings_logs(self):
        text=(ROOT/'install.sh').read_text()
        function='install_mwm_launcher() {'+text.split('install_mwm_launcher() {',1)[1].split('\nfinal_verify()',1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp);app=home/'app';cfg=home/'config/mwm'
            app.mkdir();cfg.mkdir(parents=True);(app/'logs').mkdir()
            (app/'logs/keep.log').write_text('retained')
            (cfg/'kwin-rtscale').write_text('10\n')
            (cfg/'custom-aspect').write_text('21:9\n')
            (cfg/'gamescope-span-enabled').write_text('on\n')
            source=ROOT/'mwm/mwm.py';target=app/'mwm.py'
            target.write_bytes(b'#'+b' '*(source.stat().st_size-1))
            os.utime(target,ns=(source.stat().st_atime_ns,source.stat().st_mtime_ns))
            env=dict(os.environ,HOME=str(home),XDG_CONFIG_HOME=str(home/'config'),APP_HOME=str(app),SCRIPT_DIR=str(ROOT),LOCAL_BIN=str(home/'bin'),DESKTOP_DIR=str(home/'applications'))
            script='set -Eeuo pipefail\nsay(){ :; }; ok(){ :; }; die(){ echo "$*" >&2; exit 1; }; pkill(){ return 1; }; update-desktop-database(){ :; };\n'+function+'\ninstall_mwm_launcher\n'
            subprocess.run(['bash','-c',script],env=env,check=True,capture_output=True,text=True)
            self.assertEqual(target.read_bytes(),source.read_bytes())
            self.assertEqual((cfg/'kwin-rtscale').read_text(),'8\n')
            self.assertEqual((cfg/'custom-aspect').read_text(),'21:9\n')
            self.assertEqual((cfg/'gamescope-span-enabled').read_text(),'on\n')
            self.assertEqual((app/'logs/keep.log').read_text(),'retained')
            self.assertTrue(os.access(home/'bin/mwm',os.X_OK))
            self.assertIn('Name=MLTD Waydroid Manager',(home/'applications/mwm.desktop').read_text())
