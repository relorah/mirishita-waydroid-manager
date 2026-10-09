#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fullscreen matching aspects; center fixed-size windows for other aspects."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from waydroid_dimensions import read_dimensions

SELF = Path(__file__).resolve()
STATE = Path(os.environ.get('XDG_STATE_HOME', str(Path.home()/'.local/state')))/'mwm'
PLACED = set()
JS = r'''
var list=workspace.stackingOrder || [], result=[];
var tw=TARGET_W, th=TARGET_H, placed=PLACED_KEYS;
for(var i=0;i<list.length;i++) {
 var w=list[i], cls=String(w.resourceClass || '').toLowerCase();
 var desktop=String(w.desktopFileName || '').toLowerCase();
 if(!(cls==='waydroid' || cls.indexOf('waydroid.')===0 || desktop==='waydroid' || desktop.indexOf('waydroid.')===0)) continue;
 if(w.minimized) continue;
 var a=workspace.clientArea(KWin.FullScreenArea,w);
 var full=Math.abs(tw*a.height-th*a.width)<=Math.max(a.width,a.height);
 var key=String(w.internalId)+':'+tw+'x'+th+':'+a.x+','+a.y+','+a.width+','+a.height;
 if(placed.indexOf(key)<0) {
  if(full) { if(!w.fullScreen) w.fullScreen=true; }
  else {
   if(w.fullScreen) w.fullScreen=false;
   w.setMaximize(false,false);
   var g=w.frameGeometry, c=w.clientGeometry;
   var bw=Math.max(0,g.width-c.width), bh=Math.max(0,g.height-c.height);
   var area=workspace.clientArea(KWin.WorkArea,w);
   w.frameGeometry={x:area.x+Math.round((area.width-tw-bw)/2),
    y:area.y+Math.round((area.height-th-bh)/2),width:tw+bw,height:th+bh};
  }
 }
 var g=w.frameGeometry,c=w.clientGeometry,area=workspace.clientArea(KWin.WorkArea,w);
 result.push({id:String(w.internalId),key:key,desired_fullscreen:full,fullscreen:!!w.fullScreen,
  frame:[g.x,g.y,g.width,g.height],client:[c.x,c.y,c.width,c.height],
  area:[a.x,a.y,a.width,a.height],workarea:[area.x,area.y,area.width,area.height],target:[tw,th]});
}
output_result(JSON.stringify(result));
'''

def query():
    values=read_dimensions(attempts=1)
    js=JS.replace('TARGET_W',str(values[0])).replace('TARGET_H',str(values[1])).replace('PLACED_KEYS',json.dumps(sorted(PLACED)))
    r=subprocess.run(['kdotool','kwinscript','--inline',js],capture_output=True,text=True,timeout=3)
    if r.returncode: raise RuntimeError('KWin query failed: '+r.stderr.strip())
    for line in reversed(r.stdout.splitlines()):
        if line.startswith('['):
            rows=json.loads(line)
            if isinstance(rows,list):
                if signature(rows) is not None: PLACED.update(row['key'] for row in rows)
                return rows
    raise RuntimeError('KWin did not return placement state')

def signature(rows):
    if not rows: return None
    result=[]
    for row in rows:
        x,y,w,h=row['frame']; ax,ay,aw,ah=row['area']
        if min(w,h,aw,ah)<=0: return None
        if row['desired_fullscreen']:
            if not row['fullscreen'] or any(abs(v-t)>2 for v,t in zip((x,y,w,h),(ax,ay,aw,ah))): return None
        else:
            if row['fullscreen']: return None
            cx,cy,cw,ch=row['client'];tw,th=row['target'];wx,wy,ww,wh=row['workarea']
            if abs(cw-tw)>2 or abs(ch-th)>2: return None
            if abs(x-(wx+(ww-w)/2))>2 or abs(y-(wy+(wh-h)/2))>2: return None
            if x<wx-1 or y<wy-1 or x+w>wx+ww+1 or y+h>wy+wh+1: return None
        result.append((row['id'],tuple(row['frame']),row['fullscreen']))
    return tuple(sorted(result))

def wait_ready(timeout=20, query_fn=None, sleep_fn=time.sleep, clock=time.monotonic, expected=None):
    query_fn=query_fn or query
    deadline=clock()+timeout; previous=None; stable=0; last='no Waydroid surface'
    while clock()<deadline:
        try:
            rows=query_fn(); current=signature(rows); last=json.dumps(rows)
        except (OSError,ValueError,KeyError,TypeError,RuntimeError,subprocess.SubprocessError) as error:
            current=None; last=str(error)
        stable=stable+1 if current is not None and current==previous else (1 if current is not None else 0)
        previous=current
        if stable>=3:
            print('KWin placement READY: '+last,flush=True);return rows
        sleep_fn(.3)
    raise RuntimeError('KWin placement did not settle: '+last)

def instances():
    found=[]
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit(): continue
        try:
            args=(proc/'cmdline').read_bytes().split(b'\0')
            if proc.stat().st_uid==os.getuid() and os.fsencode(SELF) in args and b'run' in args:
                found.append(int(proc.name))
        except OSError: pass
    return found

def stop():
    for pid in instances():
        try: os.kill(pid,signal.SIGTERM)
        except ProcessLookupError: pass
    deadline=time.monotonic()+2
    while instances() and time.monotonic()<deadline: time.sleep(.05)
    if instances(): raise RuntimeError('Previous KWin fullscreen monitor did not stop')

def monitor():
    previous=None; failures=0
    while True:
        try:
            rows=query(); failures=0
            current=json.dumps(rows,sort_keys=True)
            if current!=previous:
                print('KWin fullscreen: '+current,flush=True); previous=current
        except (OSError,ValueError,KeyError,TypeError,RuntimeError,subprocess.SubprocessError) as error:
            failures+=1
            if failures==1 or failures%30==0: print(str(error),flush=True)
            if failures>=30: raise RuntimeError('KWin fullscreen monitor lost compositor access')
        time.sleep(1)

def main(action):
    if action=='stop': stop(); return
    if not shutil.which('kdotool'): raise RuntimeError('kdotool is required for KWin fullscreen; install kdotool and retry')
    if action=='wait':
        # The wait loop retries transient property errors itself.
        wait_ready(); return
    if action=='run': monitor(); return
    stop(); STATE.mkdir(parents=True,exist_ok=True)
    with (STATE/'kwin-fullscreen.log').open('a') as log:
        proc=subprocess.Popen([sys.executable,str(SELF),'run'],stdin=subprocess.DEVNULL,
                              stdout=log,stderr=log,start_new_session=True)
    time.sleep(.2)
    if proc.poll() is not None: raise RuntimeError('KWin fullscreen monitor exited; see kwin-fullscreen.log')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=('start','stop','wait','run'))
    try: main(parser.parse_args().action)
    except (OSError,RuntimeError,ValueError,subprocess.SubprocessError) as error:
        print('KWin fullscreen error: '+str(error),file=sys.stderr); sys.exit(4)
