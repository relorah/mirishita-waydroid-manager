#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail

command -v kdotool >/dev/null 2>&1 || exit 1
CFG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/mwm"
backend="$(cat "$CFG_DIR/display-backend" 2>/dev/null || echo kwin)"

if [[ "$backend" == "gamescope" ]]; then
  JS='
var list = workspace.stackingOrder || [];
var found = null;
for (var i = list.length - 1; i >= 0; i--) {
    var w = list[i];
    var cls = String(w.resourceClass || "").toLowerCase();
    var cap = String(w.caption || "").toLowerCase();
    var desktop = String(w.desktopFileName || "").toLowerCase();
    if (!w.minimized && (cls.indexOf("gamescope") >= 0 || desktop.indexOf("gamescope") >= 0 || cap.indexOf("gamescope") >= 0)) {
        found = w; if (w.active) break;
    }
}
if (found) {
    var a = workspace.activeWindow;
    var active = !!found.active || (!!a && (a === found
        || String(a.resourceClass || "").toLowerCase().indexOf("com.bandainamcoent.imas_millionlive_theaterdays") >= 0
        || String(a.desktopFileName || "").toLowerCase().indexOf("com.bandainamcoent.imas_millionlive_theaterdays") >= 0));
    var g = found.clientGeometry || found.frameGeometry;
    output_result(Math.round(g.x)+" "+Math.round(g.y)+" "+Math.round(g.width)+" "+Math.round(g.height)+" "+(active ? "1" : "0"));
}
'
else
  JS='
var target = "waydroid.com.bandainamcoent.imas_millionlive_theaterdays";
var list = workspace.stackingOrder || [];
var found = null;
for (var i = list.length - 1; i >= 0; i--) {
    var w = list[i];
    var cls = String(w.resourceClass || "").toLowerCase();
    var desktop = String(w.desktopFileName || "").toLowerCase();
    if ((cls === target || desktop === target) && !w.minimized) {
        found = w; if (w.active) break;
    }
}
if (found) {
    var active = !!(found.active || workspace.activeWindow === found);
    var g = found.clientGeometry || found.frameGeometry;
    output_result(Math.round(g.x)+" "+Math.round(g.y)+" "+Math.round(g.width)+" "+Math.round(g.height)+" "+(active ? "1" : "0"));
}
'
fi

kdotool kwinscript --inline "$JS" 2>/dev/null \
  | grep -E '^-?[0-9]+ +-?[0-9]+ +[0-9]+ +[0-9]+( +[01])?$' \
  | tail -n1
