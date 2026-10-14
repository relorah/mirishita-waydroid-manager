# Span Displays (Experimental)

Gamescope can present one Waydroid surface across the bounding rectangle of all enabled, connected KDE displays. Enable **Span Displays (Experimental)** in Display and use Auto to follow the combined aspect ratio. The default is off; existing single-display behavior is preserved.

The outer Gamescope uses SDL/X11 and a borderless window. MWM places only its own Gamescope process window using KWin window APIs; Android rendering remains inside Gamescope. This requires KScreen, kdotool and an available XWayland session. The window is held at the startup geometry while the session runs. Restart after changing the desktop layout.

This is not independent scaling or cropping for each monitor. KDE display scales and positions still determine the physical seam. A desktop bounding rectangle includes empty regions above/below shorter displays. Gamescope uniform scaling cannot compensate independently for unequal physical pixel densities. Use KDE display calibration first; per-output image transforms are not implemented.

test-system validation: initial canvas 4569×1490, Android source 3312×1080, RTScale x3. Both Android geometry and owned outer client geometry were confirmed stable after a manual Gamescope close/restart. The calibrated desktop profile uses HDMI-A-1 scale 1.55 at 0,0 and DP-2 scale 1 at 2477,157, giving 4397×1394. MV performance, physical seam and recording remain separate live checks.

The setting is included in the ordinary settings snapshot/save/reset flow and the settings validation allowlist. MWM settings backups already copy the configuration directory. No game data, graphics libraries or monitor settings are changed by enabling this option. Disable the option and restart to return to the normal single-display path.

A further physical calibration trial raises HDMI-A-1 to 1.5666667 and moves DP-2 to 2451,149: canvas 4371×1379, Android 3424×1080, x3 base 2284×720. Android retained old dimensions on the first restart; the existing single rebuild retry settled successfully. The user confirmed this final fine adjustment with OK.

## Measured RTScale base

The initial union-aspect calculation did not match test-system's actual Unity render target. Gamescope Android display 3424×1080 yielded a game surface 3424×1032 and render target 2388×720; the assumed base 2284×720 caused the x3 rule to miss it. No scaled targets were observed in the first MV capture.

This prototype accepts `gamescope-span-rts-base.json` in MWM configuration, containing integer `display_width`, `display_height`, `base_width`, `base_height`. For this measured test-system session use 3424,1080,2388,720. The calibration is used only with Span Displays enabled and is rejected if the Android display dimensions change. It is preserved by ordinary directory-based settings backups. Automatic calibration is not implemented; this is a measured profile for this desktop. Recalibrate when changing display dimensions or game render settings.

After a full restart, GPU resources and FBOs were measured at 7164×2160 with scaled flags; a second read during Diamond Joker confirmed the same. This distinguishes verified rendering from merely reading back the x3 configuration. The GPU read-only debugger briefly pauses the process; that probe is outside the normal runtime and may appear as a short hitch in the validation video.

KWin Direct launch/run/wait entry points are disabled; stop remains available to clean up an older direct-session monitor. New settings accept only Gamescope. KDE itself and the KWin window-placement API used by the Gamescope outer window remain active.
