# Experimental RTScale depth-only framebuffer blit correction

The v0.84 RTScale rectangle conversion determines a framebuffer's coordinate space from COLOR0. A framebuffer with only a scaled depth/stencil attachment has no COLOR0. This leaves its blit rectangle in logical coordinates. A multisample source with COLOR0 and a depth-only destination consequently returns `GL_INVALID_OPERATION`; two depth-only endpoints can instead copy only a small physical subregion without returning an error.

The eight-line candidate falls back to the depth or stencil attachment selected by the blit mask when COLOR0 has no storage. The existing Zoom Fix / scale >= 2 guard, application-requested sample default, color framebuffer behavior, and source/destination rectangle conversion remain in place. This is an MWM-local modification of the Mesa RTScale reconstruction, with attribution to [mogareta7731's RTScale explanation](https://zenn.dev/mogareta7731/articles/82f3f0d9567abc) and [note article](https://note.com/mogareta7731/n/n4db668be92b5). It is not the original author's source release.

## Verification and scope

Independent Android GLES pixel tests on RX 9060 XT 8GB passed all 200 candidate cases:

- Eight color/depth-MSAA resolve cases: x1/x3/x5/x6, standard and opt-in MSAA2. The baseline fails the six scaled cases with error 0x502; the corrected candidate preserves the expected left/right depth values (64/191).
- 96 depth-only source/destination cases with multisample storage, plus 96 with single-sample storage. These cover x1/x3/x5/x6; both MSAA policies; all Texture/Renderbuffer endpoint combinations; depth, stencil, and combined masks; copied values on both sides of the full physical extent; and preservation of the plane excluded by the mask. All 48 baseline x6 cases fail the pixel coverage assertions. Native x1 controls pass.

The JSON results retain baseline failures as expected regressions; they are not reported as passing tests. Waydroid's outer CLI returned 0 even when an Android probe failed. Results therefore use the explicit `MWM_PROBE_RC` emitted inside Android, plus pixel assertions and the `PASS` marker.

This is an independently reproduced API bug, **not a confirmed cause of the Thank You! 39-person loading interval or Diamond Joker FPS issue**. A 150-second OFF-profile trace recorded no Blit or CopyImage calls from the actual 39-person MV. The Blit trace was checked with an independent positive control; the CopyImage family did not receive its own positive control in that pass.

Game validation is still in progress. The first candidate startup ended with a Native Bridge (`libhoudini.so`) SIGSEGV; the restored v0.84 started normally, and a second candidate startup reached the title/home screens normally. Causality is unresolved. The binary is withheld from this source candidate ZIP, the normal payload is unchanged, and no new Release or main merge has been made. Do not treat independent GLES passes as complete game compatibility validation.

Only DEPTH24_STENCIL8 and full matching rectangles are covered by these tests. Other formats, partial/flipped rectangles, full GLES conformance, and other GPUs remain unverified. Game data, APKs, and the Native Bridge implementation were not modified.

## Sources and build provenance

Mesa upstream base: `acbb4f6b8de2768b5ea7d6a83a8e52a263eac5cc`, 26.3.0-devel. Use the integrated base archive in the existing [v0.83 package](https://github.com/relorah/mirishita-waydroid-manager/releases/download/v0.83/MWM_v0.83.zip), member `MWM_v0.83/payload/sources/graphics-sources.tar.zst`, SHA256 `6ddc1e4dbf0c5663d2ed70df3c6eed406211cffad6c0f406f53c2e87b236d9dd`. Follow that archive's BUILD.md and libelf relink instructions; do not rerun integrate.py.

Apply `../diamond-joker/mesa-msaa-storage2.patch` and then `mesa-depth-only-blit.patch` at the Mesa source root with `patch -p1`. Reapplying both patches to the base archive produced byte-identical copies of all seven changed source files. A comparison of all 11,692 Mesa source files found changes in exactly those seven files. The unpatched local rebuild is byte-identical to the installed v0.84 gallium library:

```
v0.84 / unpatched rebuild: 6a77eba981aa1163edf3351f15be38752a9a0da7ecd2a04ee273f388cb8b7116
experimental depth-only build: 7e027d005deae4aab936206373d8969bd2ba4c362877a4863ee8a9cff7037efa
```

The existing Android API30 / NDK r27c / LLVM21 ABI-checks-ON configuration and all eleven gallium drivers were retained. Stage the build with Meson install; the distributed-stage candidate has no RPATH or RUNPATH. No CopyImage prototype is included.

To compile either independent C probe, use the NDK API30 compiler with the Mesa stage's EGL and GLESv2 libraries (GLESv2 exports GLES3.2):

```
x86_64-linux-android30-clang depth-stencil-blit-probe.c -L/path/to/mesa-stage/usr/local/lib -lEGL -lGLESv2 -Wl,--allow-shlib-undefined -Wall -Wextra -o mwm-independent-depth-blit-probe-stencil
```

Run outside game userdata with an isolated library path and an explicitly backed-up, process-matching RTScale test profile. Arguments for the stencil probe are `scale source_rb destination_rb mask_bits expected_physical_samples requested_samples`; mask bits 1/2/3 mean depth/stencil/both. `requested_samples=0` selects single-sample storage. The original depth probe takes `scale expected_msaa2`.

Preserve Mesa's per-file MIT notices, the reconstruction's 0BSD notices, upstream attribution, LLVM notices, and LGPL libelf source/relink requirements. The two independently written probes are 0BSD. This source-only bundle contains no Mesa binary, proprietary game source, shaders, APK, or Native Bridge payload.
