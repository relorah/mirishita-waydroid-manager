# MWM 0.84: Diamond Joker flare correction and opt-in MSAA storage

Measured v0.83 runtime/source base `2bca8b06762d7b13d5861618d3facd0262aa088e`; latest main `bb7ebcc0c5c19146311f8cd82120bb9da17a4973` inspected / Mesa RTScale reconstruction at `acbb4f6b8de2768b5ea7d6a83a8e52a263eac5cc`.

This implementation reduces samples only on RTScale-promoted render targets: requests of four or more samples use two physical samples. RTScale Zoom Fix must remain enabled. Multisample fetches in fragment, vertex and other common shader variants query the physical sample count and wrap the index, so a four-index depth-minimum/color-average shader does not read nonexistent samples. GLES advertised limits stay unchanged. The accompanying optical correction keeps `_ScreenRTSize.xy` in the same coordinate space as the promoted `_ColorBuffer` sampler, preserving its camera aspect ratio in z. Separate full-MV visual tests at x6 with original four-sample storage restored visible faces and hair at both chorus endings. The combined distribution build passed two primary full-MV performance runs (minimum 59.51/59.52 FPS; no present interval above 25ms) and a separate full-MV visual capture confirmed visible faces/hair at both target cuts. It changes antialiasing quality and is **not pixel-identical** to four-sample rendering. The default remains application-requested samples (`msaa_samples=0`, or absent).

The Mesa patch applies to the integrated source in the matching `graphics-sources.tar.zst`, after the existing RTScale reconstruction. Keep upstream per-file notices, 0BSD reconstruction notices, Mesa/LLVM/libdrm attribution and LGPL libelf source/relink requirements. Attribution: [mogareta7731 Zenn](https://zenn.dev/mogareta7731/articles/82f3f0d9567abc), [note](https://note.com/mogareta7731/n/n4db668be92b5). This is an MWM-local modification, not the original author's source release.

The helper accepts an optional sixth argument `msaa_samples=0|2`. Legacy calls write the same configuration as before. Selecting `2` fails before writing if the installed overlay lacks the matching parser. `set-rtscale.sh` reads `~/.config/mwm/rtscale-msaa-samples` (absent/0 preserves the old path). The existing fast-refresh fingerprint includes this file, so a policy change requires a full restart.

The draft PR carries reviewable source changes; the experimental binary (GLES color/depth/renderbuffer and vertex-fetch probes passed; two full-driver MV performance runs maintained approximately 60 FPS at x6/FSR150), full corresponding source, licenses, measurements and verification text are delivered separately in the Drive candidate ZIP. There is no Release publication. RX 9060 XT/Android 11 is the measured target; successful compilation of other Gallium drivers does not establish their runtime behavior.

## Optical correction

With RTScale x6, the color sampler texel-size dimensions were promoted by six while `_ScreenRTSize.xy` retained logical reciprocals. A synthetic UV probe reproduced the resulting sixfold coordinate mapping and clipping. Adjusting the paired reciprocals only for the corresponding scaled color sampler restored the mapping; z remains the camera aspect ratio. The fix also applies with original MSAA storage (`msaa_samples=0`) and does not change advertised limits or unscaled samplers. The optical-only build still reproduced GPU-bound FPS drops with four-sample storage.

## Regression probes

`test-helper.py` tests legacy output, explicit opt-in, invalid arguments and rejection of old overlays without requiring root/Android writes. Compile `test-config.c` with the patched `gles_rtscale_config.c` and `-pthread` to check parser defaults/duplicates/invalid values.

`msaa-storage-probe.c` is independently written test code, not game shader source. Build for Android API30 against EGL/GLES3.2. Run with the package-matching executable name and matching configuration. Arguments are scale and policy (`6 0` / `6 1`), where the second argument selects expected results, **not** the configuration. It checks color/depth storage dimensions, sample count, FBO completeness, corrected TexelSize, four-index color resolve and minimum depth, and sample index two fetched in a vertex shader. Use an isolated library path outside game userdata. `rt-pair-probe.c [width height]` checks the paired coordinate mapping and preserved camera aspect at full width, quarter width, unscaled small targets and scale one.

## Distribution and regression sources

Use the ordinary root install.sh to install the current payload. The old 0.83-only candidate installer has been retired. Independent GLES probes and helper/parser checks are in tests/graphics/msaa/ in the Git repository. They are development checks, not required at runtime.

The v0.84 Git payload contains the same verified gallium binary. Complete corresponding sources are available in the existing public [v0.83 archive](https://github.com/relorah/mirishita-waydroid-manager/releases/download/v0.83/MWM_v0.83.zip), member `MWM_v0.83/payload/sources/graphics-sources.tar.zst` (SHA256 `6ddc1e4dbf0c5663d2ed70df3c6eed406211cffad6c0f406f53c2e87b236d9dd`), plus this directory’s Mesa patch and the subsequent ../depth-blit/mesa-depth-only-blit.patch. The current library includes both patches. The Drive verification ZIP also includes both base archive and patch. Follow its BUILD.md; do not rerun integrate.py.
