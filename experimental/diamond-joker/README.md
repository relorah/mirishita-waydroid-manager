# Diamond Joker: opt-in scaled MSAA storage candidate

MWM main `2bca8b06762d7b13d5861618d3facd0262aa088e` / Mesa RTScale reconstruction at `acbb4f6b8de2768b5ea7d6a83a8e52a263eac5cc`.

This experimental candidate reduces samples only on RTScale-promoted render targets: requests of four or more samples use two physical samples. RTScale Zoom Fix must remain enabled. Fragment multisample fetches query the physical sample count and wrap the index, so a four-index depth-minimum/color-average shader does not read nonexistent samples. GLES advertised limits stay unchanged. It changes antialiasing quality and is **not pixel-identical** to four-sample rendering. The default remains application-requested samples (`msaa_samples=0`, or absent).

The Mesa patch applies to the integrated source in the matching `graphics-sources.tar.zst`, after the existing RTScale reconstruction. Keep upstream per-file notices, 0BSD reconstruction notices, Mesa/LLVM/libdrm attribution and LGPL libelf source/relink requirements. Attribution: [mogareta7731 Zenn](https://zenn.dev/mogareta7731/articles/82f3f0d9567abc), [note](https://note.com/mogareta7731/n/n4db668be92b5). This is an MWM-local modification, not the original author's source release.

The helper accepts an optional sixth argument `msaa_samples=0|2`. Legacy calls write the same configuration as before. Selecting `2` fails before writing if the installed overlay lacks the matching parser. `set-rtscale.sh` reads `~/.config/mwm/rtscale-msaa-samples` (absent/0 preserves the old path). The existing fast-refresh fingerprint includes this file, so a policy change requires a full restart.

The draft PR carries reviewable source changes; the experimental binary (GLES probes passed; final full-driver MV benchmark pending), full corresponding source, licenses, measurements and verification text are delivered separately in the Drive candidate ZIP. There is no Release publication. RX 9060 XT/Android 11 is the measured target; successful compilation of other Gallium drivers does not establish their runtime behavior.

## Regression probes

`test-helper.py` tests legacy output, explicit opt-in, invalid arguments and rejection of old overlays without requiring root/Android writes. Compile `test-config.c` with the patched `gles_rtscale_config.c` and `-pthread` to check parser defaults/duplicates/invalid values.

`msaa-storage-probe.c` is independently written test code, not game shader source. Build for Android API30 against EGL/GLES3.2. Run with the package-matching executable name and matching configuration. Arguments are scale and policy (`6 0` / `6 1`), where the second argument selects expected results, **not** the configuration. It checks color/depth storage dimensions, sample count, FBO completeness, corrected TexelSize, four-index color resolve and minimum depth. Use an isolated library path outside game userdata.

## Candidate package controls

The candidate ZIP's `candidate-control.sh apply|restore <absolute installed MWM directory> <absolute backup directory>` changes only the Mesa gallium library, restricted helper, RTScale settings script and one MWM setting file. `apply` requires the measured v0.83 library hash, verifies package hashes and backs up every changed path. `restore` retains the backup and checks for subsequent library/helper/script changes before restoring. It stops/restarts Waydroid; game userdata is neither deleted nor initialized. No sudoers rule is added. On interruption, inspect the retained backup before continuing. The option is controlled by the settings file; this draft does not add a GUI checkbox.

To compile the standalone Android probe, link against the candidate Mesa stage's `libEGL.so` and `libGLESv2.so` (which exports GLES3.2); do not accidentally link the platform `libGLESv3.so` against isolated Mesa EGL. For example with the NDK API30 compiler: `x86_64-linux-android30-clang msaa-storage-probe.c -L/path/to/mesa-stage/usr/local/lib -lEGL -lGLESv2 -o com.bandainamcoent.imas_millionlive_theaterdays-msaa-probe`.
