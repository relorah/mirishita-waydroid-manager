"""Exercise the production stop function without touching the live game."""
import pathlib
import subprocess
import tempfile
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'mwm/scripts/waydroid-control.sh'

class RestartStopTests(unittest.TestCase):
    def run_stop(self, mode):
        source = SOURCE.read_text()
        function = source.split('stop_mirishita_for_refresh() {', 1)[1].split('\ntry_rts_fast_refresh()', 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            script = '''set -eu
refresh_phase() { :; }
sleep() { :; }
root_helper() {
  echo "$1" >> "$LOG"
  case "$1" in
    force-stop-app) [[ "$MODE" != stop_fail ]] ;;
    game-process-state)
      case "$MODE" in
        query_fail) return 1;;
        missing_marker) echo 123;;
        alive) printf '123\nMWM_PID_QUERY_OK\n';;
        delayed)
          if [[ ! -f "$LOG.done" ]]; then
            touch "$LOG.done"
            printf '123\nMWM_PID_QUERY_OK\n'
          else echo MWM_PID_QUERY_OK; fi;;
        *) echo MWM_PID_QUERY_OK;;
      esac;;
  esac
}
stop_mirishita_for_refresh() {''' + function + '\nstop_mirishita_for_refresh\n'
            log = pathlib.Path(directory) / 'calls'
            result = subprocess.run(['bash', '-c', script], env={'PATH':'/usr/bin:/bin', 'MODE':mode, 'LOG':str(log)}, capture_output=True, text=True)
            return result.returncode, log.read_text().splitlines()

    def test_stopped_and_delayed_exit(self):
        for mode, count in [('stopped',1), ('delayed',2)]:
            with self.subTest(mode=mode):
                rc, calls = self.run_stop(mode)
                self.assertEqual(rc, 0)
                self.assertEqual(calls, ['force-stop-app'] + ['game-process-state'] * count)

    def test_force_stop_failure(self):
        self.assertEqual(self.run_stop('stop_fail'), (4, ['force-stop-app']))

    def test_cannot_confirm_exit(self):
        for mode in ('query_fail', 'missing_marker'):
            self.assertEqual(self.run_stop(mode)[0], 78)

    def test_timeout(self):
        rc, calls = self.run_stop('alive')
        self.assertEqual(rc, 4)
        self.assertEqual(len(calls), 21)

    def test_stop_precedes_guard_and_settings(self):
        body = SOURCE.read_text().split('try_rts_fast_refresh() {',1)[1].split('\nsave_rts_fast_state()',1)[0]
        self.assertLess(body.index('stop_mirishita_for_refresh || return $?'), body.index('export MWM_REFRESH_GUARD_FILE'))
        self.assertLess(body.index('stop_mirishita_for_refresh || return $?'), body.index('/set-rtscale.sh'))
        self.assertIn('auto_start_after_refresh || return $?', body)
        self.assertNotIn('Close Mirishita before', body)
