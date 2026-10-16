"""Regression coverage for installed fast-path imports and guard lifecycle."""
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class FastRuntimeTests(unittest.TestCase):
    def test_version_import_in_installed_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            app = pathlib.Path(directory) / 'share/mwm'
            scripts = app / 'scripts'
            scripts.mkdir(parents=True)
            for name in ('rts-fast-state.py', 'waydroid_dimensions.py'):
                (scripts / name).write_bytes((ROOT / 'mwm/scripts' / name).read_bytes())
            (app / 'version.py').write_text('__version__ = "0.84-test"\n')
            code = 'import runpy,sys; sys.path.insert(0,sys.argv[1]); m=runpy.run_path(sys.argv[2]); print(m["__version__"])'
            result = subprocess.run(['python', '-I', '-c', code, str(scripts), str(scripts/'rts-fast-state.py')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), '0.84-test')

    def run_fast(self, automatic='on', write_status=0, launch_status=0):
        text = (ROOT/'mwm/scripts/waydroid-control.sh').read_text()
        function = 'try_rts_fast_refresh() {' + text.split('try_rts_fast_refresh() {',1)[1].split('\nsave_rts_fast_state()',1)[0]
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            state = root/'state/mwm'; state.mkdir(parents=True)
            (state/'rts-fast-config.txt').write_text('original\n')
            cfg = root/'cfg'; cfg.mkdir(); (cfg/'auto-start-mirishita').write_text(automatic)
            script = root/'runner.sh'
            (root/'set-rtscale.sh').write_text('#!/bin/bash\n[[ -f "$MWM_REFRESH_GUARD_FILE" ]] || exit 99\nexit "$WRITE_STATUS"\n')
            (root/'set-rtscale.sh').chmod(0o755)
            script.write_text('set -Eeuo pipefail\nwaydroid() { echo \'Session: RUNNING\'; }\nbackend() { echo gamescope; }\nsaved_render_mode() { echo rtscale; }\nsaved_scale() { echo 6; }\ndisplay_exit_status() { return 0; }\npython() { return 0; }\nroot_helper() { echo original; }\nstop_mirishita_for_refresh() { echo stopped >> "$LOG"; }\nrefresh_phase() { :; }\nrefresh_guard() { return 0; }\nsave_rts_fast_state() { echo saved >> "$LOG"; }\nauto_start_after_refresh() { [[ -z "${MWM_REFRESH_GUARD_FILE:-}" ]] || return 98; echo launched >> "$LOG"; return "$LAUNCH_STATUS"; }\n' + function + '\ntry_rts_fast_refresh\n')
            env = dict(os.environ, XDG_STATE_HOME=str(root/'state'), CFG_DIR=str(cfg), LOG=str(root/'calls'), WRITE_STATUS=str(write_status), LAUNCH_STATUS=str(launch_status))
            result = subprocess.run(['bash', str(script)], env=env, capture_output=True, text=True, timeout=12)
            calls=(root/'calls').read_text() if (root/'calls').exists() else ''
            self.assertEqual(list(state.glob('refresh-guard.*')), [], result.stderr)
            return result, calls

    def test_success_with_auto_start(self):
        result, calls = self.run_fast()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('stopped', calls); self.assertIn('saved', calls); self.assertIn('launched', calls)

    def test_success_without_auto_start(self):
        result, calls = self.run_fast(automatic='off')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('launched', calls)

    def test_write_failure_keeps_status_and_cleans_guard(self):
        result, calls = self.run_fast(write_status=1)
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertNotIn('saved', calls); self.assertNotIn('launched', calls)

    def test_launch_failure_keeps_status(self):
        result, _ = self.run_fast(launch_status=4)
        self.assertEqual(result.returncode, 4, result.stderr)
