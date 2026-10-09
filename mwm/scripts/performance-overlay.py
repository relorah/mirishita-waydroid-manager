#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""One saved-settings HUD owner for the GUI and runtime start/stop paths."""
import argparse,fcntl,os,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RENDERER=ROOT/'fps_overlay.py'
CFG=Path(os.environ.get('XDG_CONFIG_HOME',str(Path.home()/'.config')))/'mwm'
STATE=Path(os.environ.get('XDG_STATE_HOME',str(Path.home()/'.local/state')))/'mwm'
def instances():
    found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            if p.stat().st_uid!=os.getuid():continue
            args=(p/'cmdline').read_bytes().split(b'\0')
            if os.fsencode(RENDERER) in args:found.append((int(p.name),args))
        except (OSError,PermissionError):pass
    return found
def running():
    try:
        if (CFG/'display-backend').read_text().strip()=='kwin':
            status=subprocess.run(['waydroid','status'],capture_output=True,text=True,timeout=3,
                                  env={**os.environ,'LC_ALL':'C'})
            return status.returncode==0 and __import__('re').search(r'Session:\s*RUNNING',status.stdout) is not None
    except (OSError,ValueError,subprocess.SubprocessError):
        return False
    try:
        pid=int((STATE/'gamescope.pid').read_text().strip())
        args=Path(f'/proc/{pid}/cmdline').read_bytes()
        return b'gamescope-supervisor.sh' in args or b'gamescope' in args.split(b'\0')[0]
    except (OSError,ValueError):return False

def mango_running():
    """Recognize our live client, not a marker left by a previous session."""
    expected=os.fsencode(CFG/'MangoApp.conf')
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            if p.stat().st_uid!=os.getuid():continue
            if (p/'exe').resolve().name!='mangoapp':continue
            env=(p/'environ').read_bytes().split(b'\0')
            if b'MANGOHUD_CONFIGFILE='+expected in env:return True
        except (OSError,RuntimeError):pass
    return False

def reconcile(action='sync',if_running=False):
    STATE.mkdir(parents=True,exist_ok=True)
    with (STATE/'performance-overlay.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:mode=(CFG/'performance-overlay-mode').read_text().strip().lower()
        except FileNotFoundError:mode='off'
        if action=='stop':mode='off'
        if mode not in ('off','minimal','detailed','mangoapp'):raise ValueError('Invalid saved FPS counter mode')
        use_mango = mango_running()
        if use_mango:
            cfg=CFG/'MangoApp.conf'
            text=(ROOT/'config/MangoApp.conf').read_text()
            text='\n'.join(line for line in text.splitlines() if not line.strip().startswith('no_display'))+'\n'
            visible = mode == 'mangoapp'
            text += 'no_display=' + ('0' if visible else '1') + '\n'
            CFG.mkdir(parents=True,exist_ok=True)
            temp=cfg.with_suffix('.tmp');temp.write_text(text);temp.replace(cfg)
            try:
                subprocess.run(['mangohudctl','set','reload_config','1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=3,check=True)
                subprocess.run(['mangohudctl','set','no_display','0' if visible else '1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=3,check=True)
            except (OSError,subprocess.SubprocessError) as e:
                raise RuntimeError('MangoApp visibility could not be updated; check that mangohudctl is installed and the client is running') from e
            if mode in ('off','mangoapp'):
                for pid,_ in instances():
                    try:os.kill(pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                print('FPS Counter: MangoApp ' + ('On' if visible else 'Off') + ' / applied')
                return
            # Legacy MWM HUD selections hide MangoApp before applying that HUD.
        if mode=='mangoapp':
            # MangoApp must be attached when Gamescope starts. Never silently
            # replace the selected renderer with the old Minimal HUD.
            for pid,_ in instances():
                try:os.kill(pid,signal.SIGTERM)
                except ProcessLookupError:pass
            print('FPS Counter: MangoApp saved; Restart is required to start MangoApp')
            return
        current=instances()
        if if_running and mode!='off' and not current and not running():
            print('FPS Counter: saved; display session is stopped')
            return
        def matches(args):
            try:return args[args.index(b'--style')+1]==mode.encode()
            except (ValueError,IndexError):return False
        if mode!='off' and len(current)==1 and matches(current[0][1]):
            print(f'FPS Counter: {mode} / already running');return
        for pid,_ in current:
            try:os.kill(pid,signal.SIGTERM)
            except ProcessLookupError:pass
        deadline=time.monotonic()+1
        while instances() and time.monotonic()<deadline:time.sleep(.05)
        for pid,_ in instances():
            try:os.kill(pid,signal.SIGKILL)
            except ProcessLookupError:pass
        if mode=='off':
            print('FPS Counter: Off');return
        with (STATE/'performance-overlay.log').open('a') as log:
            proc=subprocess.Popen([sys.executable,str(RENDERER),'--style',mode,'--size','small','--position','top-left','--interval','0.2','--follow-window'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
        time.sleep(.3)
        if proc.poll() is not None:raise RuntimeError('FPS counter exited; see performance-overlay.log')
        print(f'FPS Counter: {mode} / applied')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('sync','stop'),nargs='?',default='sync');parser.add_argument('--if-running',action='store_true');args=parser.parse_args()
    try:reconcile(args.action,args.if_running)
    except (OSError,ValueError,RuntimeError) as e:print(f'FPS Counter error: {e}',file=sys.stderr);sys.exit(1)
