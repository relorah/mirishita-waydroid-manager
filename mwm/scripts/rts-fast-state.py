#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Conservative successful-session fingerprint; unknown state means full Refresh."""
import json, os, sys, subprocess
from pathlib import Path
from waydroid_dimensions import read_dimensions
CFG=Path(os.environ.get("XDG_CONFIG_HOME",str(Path.home()/".config")))/"mwm"
STATE=Path(os.environ.get("XDG_STATE_HOME",str(Path.home()/".local/state")))/"mwm/rts-fast-state.json"
def compatible(old, value):
    if old.get('scale') not in [str(i) for i in range(1,11)]: return False
    if value.get('scale') not in [str(i) for i in range(1,11)]: return False
    if old['scale']==value['scale']: return False
    return {k:v for k,v in old.items() if k!='scale'} == {k:v for k,v in value.items() if k!='scale'}

def current():
    from PySide6.QtGui import QGuiApplication
    app=QGuiApplication.instance() or QGuiApplication([])
    screens=[]
    for s in app.screens():
        g=s.geometry(); a=s.availableGeometry()
        screens.append([s.name(),g.x(),g.y(),g.width(),g.height(),a.x(),a.y(),a.width(),a.height(),s.devicePixelRatio()])
    if not screens: raise RuntimeError("No screen")
    config={p.name:p.read_text() for p in CFG.iterdir() if p.is_file() and p.name != "kwin-rtscale"}
    scale=(CFG/"kwin-rtscale").read_text().strip()
    if scale not in [str(i) for i in range(1,11)]: raise RuntimeError("RTScale not enabled")
    identities=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit(): continue
        try:
            comm=(p/'comm').read_text().strip(); cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            # SDL may rename the main thread to gamescope-wl.
            try: exe=(p/'exe').readlink().name.removesuffix(' (deleted)')
            except OSError: exe=''
            if exe=='gamescope' or comm in ('gamescope','kwin_wayland') or ('waydroid' in cmd and 'session start' in cmd):
                stat=(p/'stat').read_text().rsplit(')',1)[1].split()
                identities.append([int(p.name),comm,stat[19]])
        except (OSError,IndexError): continue
    if not identities: raise RuntimeError("Session identity unavailable")
    runtime=subprocess.run(['sudo','-n','/usr/local/libexec/mwm-root-helper','runtime-state'],
                           check=True,capture_output=True,text=True,timeout=12).stdout
    lines=[line.strip() for line in runtime.splitlines()]
    if 'MWM_RUNTIME_OK' not in lines: raise RuntimeError('Android runtime identity unavailable')
    runtime='\n'.join(line for line in lines if line.startswith(('system_server=', 'persist.waydroid.', 'Physical size:', 'Override size:')))
    if not any(line.startswith('system_server=') for line in lines): raise RuntimeError('Missing Android identity')
    # Read-only surface probe: a RUNNING Android session can have no visible UI.
    backend=(CFG/'display-backend').read_text().strip()
    js="""var rows=[], list=workspace.stackingOrder||[];
for(var i=0;i<list.length;i++) {
 var w=list[i], c=String(w.resourceClass||'').toLowerCase(), d=String(w.desktopFileName||'').toLowerCase();
 var match=BACKEND==='gamescope' ? (c.indexOf('gamescope')>=0 || d.indexOf('gamescope')>=0) : (c==='waydroid' || c.indexOf('waydroid.')===0 || d==='waydroid' || d.indexOf('waydroid.')===0);
 if(!match || w.minimized) continue;
 var g=w.frameGeometry;
 rows.push([String(w.internalId),g.x,g.y,g.width,g.height,!!w.fullScreen]);
}
output_result(JSON.stringify(rows));""".replace('BACKEND',json.dumps(backend))
    output=subprocess.run(['kdotool','kwinscript','--inline',js],check=True,
                          capture_output=True,text=True,timeout=3).stdout
    surfaces=None
    for line in reversed(output.splitlines()):
        if line.startswith('['): surfaces=json.loads(line); break
    if not isinstance(surfaces,list) or not surfaces: raise RuntimeError('Display surface unavailable')
    for row in surfaces:
        if len(row)!=6 or not isinstance(row[0],str) or not all(isinstance(v,(int,float)) for v in row[1:5]) or min(row[3:5])<=0:
            raise RuntimeError('Invalid display surface geometry')
    surfaces.sort(key=lambda row:row[0])
    # Session/compositor process identities plus host boot prevent stale PID reuse.
    fsr_enabled=(CFG/'gamescope-fsr-enabled').read_text().strip() if (CFG/'gamescope-fsr-enabled').exists() else 'off'
    fsr_profile='off' if backend=='gamescope' and int(scale)>=7 else fsr_enabled
    return dict(version=(Path(__file__).parent.parent/'VERSION').read_text(),config=config,scale=scale,fsr_profile=fsr_profile,
                screens=screens,dimensions=read_dimensions(),identities=sorted(identities),
                boot=Path('/proc/sys/kernel/random/boot_id').read_text(),runtime=runtime,surfaces=surfaces)
def main():
    value=current()
    if sys.argv[1]=='save':
        STATE.parent.mkdir(parents=True,exist_ok=True)
        tmp=STATE.with_suffix('.tmp'); tmp.write_text(json.dumps(value)); tmp.replace(STATE)
        return
    old=json.loads(STATE.read_text())
    if not compatible(old,json.loads(json.dumps(value))): raise RuntimeError('Session or settings changed')
if __name__=='__main__':
    try: main()
    except Exception as e:
        print('RTScale fast path unavailable: '+str(e),file=sys.stderr); sys.exit(10)
