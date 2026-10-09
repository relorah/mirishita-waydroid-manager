// Loaded for one MWM-owned KWin window. No timer or release-time correction.
var targetId = __MWM_WINDOW_ID__;
var ratio = __MWM_ASPECT_RATIO__;

function copyRect(r) {
    return {x:r.x, y:r.y, width:r.width, height:r.height};
}

function attach(w) {
    if (String(w.internalId) !== targetId) return;
    var start = null, borderX = 0, borderY = 0, correcting = false;
    w.interactiveMoveResizeStarted.connect(function () {
        if (!w.resize || w.fullScreen || w.minimized) { start = null; return; }
        start = copyRect(w.frameGeometry);
        borderX = Math.max(0, start.width - w.clientGeometry.width);
        borderY = Math.max(0, start.height - w.clientGeometry.height);
    });
    w.interactiveMoveResizeStepped.connect(function (requested) {
        if (correcting || !start || !w.resize || w.fullScreen || w.minimized) return;
        var g = copyRect(requested);
        var oldW = start.width - borderX, oldH = start.height - borderY;
        var cw = Math.max(1, g.width - borderX), ch = Math.max(1, g.height - borderY);
        if (Math.abs(cw / ch - ratio) < 0.002) return;
        // Choose the dimension driven furthest by the user's pointer. Compare
        // proportional change, so ultrawide ratios don't always choose width.
        if (Math.abs(cw - oldW) / Math.max(1, oldW) >= Math.abs(ch - oldH) / Math.max(1, oldH)) {
            ch = Math.max(1, Math.round(cw / ratio));
        } else {
            cw = Math.max(1, Math.round(ch * ratio));
        }
        var area = workspace.clientArea(KWin.WorkArea, w);
        var limitW = Math.max(1, area.width - borderX);
        var limitH = Math.max(1, area.height - borderY);
        if (cw > limitW || ch > limitH) {
            cw = Math.min(cw, limitW, Math.round(limitH * ratio));
            ch = Math.max(1, Math.round(cw / ratio));
        }
        var fw = cw + borderX, fh = ch + borderY;
        // Anchor the opposite border for left/top drags.
        var x = Math.abs(g.x - start.x) > 0.5 ? start.x + start.width - fw : start.x;
        var y = Math.abs(g.y - start.y) > 0.5 ? start.y + start.height - fh : start.y;
        x = Math.max(area.x, Math.min(x, area.x + area.width - fw));
        y = Math.max(area.y, Math.min(y, area.y + area.height - fh));
        var next = {x:Math.round(x), y:Math.round(y), width:Math.round(fw), height:Math.round(fh)};
        correcting = true;
        try { w.frameGeometry = next; } finally { correcting = false; }
    });
    // Nothing is resized after mouse release: the last drag step is final.
    w.interactiveMoveResizeFinished.connect(function () { start = null; });
}

var windows = workspace.stackingOrder || [];
for (var i = 0; i < windows.length; i++) attach(windows[i]);
