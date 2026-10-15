# RTScale depth/stencil framebuffer blit correction

The v0.84 RTScale rectangle conversion determines a framebuffer's coordinate space from COLOR0. A framebuffer with only a scaled depth/stencil attachment has no COLOR0. This leaves its blit rectangle in logical coordinates. A multisample source with COLOR0 and a depth-only destination consequently returns `GL_INVALID_OPERATION`; two depth-only endpoints can instead copy only a small physical subregion without returning an error.

The eight-line final candidate checks attachment availability and falls back to the depth or stencil attachment selected by the blit mask when COLOR0 has no storage. When a requested depth attachment is absent, the search continues to stencil; ignored mask bits must not hide a valid attachment. The existing Zoom Fix / scale >= 2 guard, application-requested sample default, color framebuffer behavior, and source/destination rectangle conversion remain in place. This is an MWM-local modification of the Mesa RTScale reconstruction, with attribution to [mogareta7731's RTScale explanation](https://zenn.dev/mogareta7731/articles/82f3f0d9567abc) and [note article](https://note.com/mogareta7731/n/n4db668be92b5). It is not the original author's source release.

## Verification and scope

Independent Android GLES pixel tests on RX 9060 XT 8GB passed all 230 final candidate cases:

- Eight color/depth-MSAA resolve cases: x1/x3/x5/x6, standard and opt-in MSAA2. The baseline fails the six scaled cases with error 0x502; the corrected candidate preserves the expected left/right depth values (64/191).
- 96 depth-only source/destination cases with multisample storage, plus 96 with single-sample storage. These cover x1/x3/x5/x6; both MSAA policies; all Texture/Renderbuffer endpoint combinations; depth, stencil, and combined masks; copied values on both sides of the full physical extent; and preservation of the plane excluded by the mask. All 48 baseline x6 cases fail the pixel coverage assertions. Native x1 controls pass.

- Twelve extra packed DEPTH24_STENCIL8 stencil-only attachment cases exposed a missing-depth + combined-mask failure in the first candidate; the final candidate passes all twelve. Twelve DEPTH_COMPONENT16 Renderbuffer cases and six unscaled STENCIL_INDEX8 controls also pass. STENCIL_INDEX8 is not promoted by the current profile; an initial test that assumed its storage scaled was excluded as an invalid premise, not counted as a driver failure.

The JSON results retain baseline failures as expected regressions; they are not reported as passing tests. Waydroid's outer CLI returned 0 even when an Android probe failed. Results therefore use the explicit `MWM_PROBE_RC` emitted inside Android, plus pixel assertions and the `PASS` marker.

This is an independently reproduced API bug, **not a confirmed cause of the Thank You! 39-person loading interval or Diamond Joker FPS issue**. A 150-second OFF-profile trace recorded no Blit or CopyImage calls from the actual 39-person MV. The Blit trace was checked with an independent positive control; the CopyImage family did not receive its own positive control in that pass.

The final v2 binary was subsequently loaded by the actual Mirishita process on RX 9060 XT (the SHA256 was read through `/proc/<pid>/root/vendor/lib64/libgallium_dri.so`). It completed the true Thank You! 39-person free MV and Diamond Joker at x5/FSR150/default MSAA. Both Diamond Joker chorus endings were inspected, including the four-character close-up: facial/hair detail remained visible, with no newly observed white-fog or occlusion corruption. Diamond Joker was also replayed at x6/FSR150/opt-in MSAA2 without screenshot capture during the measured singing window. Detailed present intervals and the isolated first-run 50ms interval are documented in `../../investigations/2026-10-14-pr5-final-game-validation.md`.

The earlier first-variant Native Bridge SIGSEGV is retained as an unexplained observation, not attributed to this fix. A single occurrence is not a rejection criterion for this change; the final candidate's game validation is evaluated separately. Loading intervals are reference records, excluded from live-rendering defects and further investigation.

This PR now updates the normal `payload/graphics/mesa-rtscale-overlay.tar.zst` and its SHA256 manifests to the final tested library. EGL/GLES wrapper binaries are byte-identical to v0.84; only the gallium library changes. The published v0.84 Release asset is not replaced. The test machine is restored to its starting library/configuration after validation. This is limited regression coverage on this machine, not full game or driver conformance.

Packed DEPTH24_STENCIL8, DEPTH_COMPONENT16 Renderbuffers, unscaled STENCIL_INDEX8 controls, and full matching rectangles are covered. Other formats, partial/flipped rectangles, full GLES conformance, and other GPUs remain unverified. Game data, APKs, and the Native Bridge implementation were not modified.

## Sources and build provenance

Mesa upstream base: `acbb4f6b8de2768b5ea7d6a83a8e52a263eac5cc`, 26.3.0-devel. Use the integrated base archive in the existing [v0.83 package](https://github.com/relorah/mirishita-waydroid-manager/releases/download/v0.83/MWM_v0.83.zip), member `MWM_v0.83/payload/sources/graphics-sources.tar.zst`, SHA256 `6ddc1e4dbf0c5663d2ed70df3c6eed406211cffad6c0f406f53c2e87b236d9dd`. Follow that archive's BUILD.md and libelf relink instructions; do not rerun integrate.py.

Apply `../msaa/mesa-msaa-storage2.patch` and then `mesa-depth-only-blit.patch` at the Mesa source root with `patch -p1`. Reapplying both patches to the base archive produced byte-identical copies of all seven changed source files. A comparison of all 11,692 Mesa source files found changes in exactly those seven files. The unpatched local rebuild is byte-identical to the installed v0.84 gallium library:

```
v0.84 / unpatched rebuild: 6a77eba981aa1163edf3351f15be38752a9a0da7ecd2a04ee273f388cb8b7116
first variant (game startup failure observed once): 7e027d005deae4aab936206373d8969bd2ba4c362877a4863ee8a9cff7037efa
final v2 (native GLES + actual game regression verified): f34d06ed52a6576dd1f558fc0c01b503f960e5933acf5be83e1e42611548a773
```

The existing Android API30 / NDK r27c / LLVM21 ABI-checks-ON configuration and all eleven gallium drivers were retained. Stage the build with Meson install; the distributed-stage candidate has no RPATH or RUNPATH. No CopyImage prototype is included.

To compile either independent C probe, use the NDK API30 compiler with the Mesa stage's EGL and GLESv2 libraries (GLESv2 exports GLES3.2):

```
x86_64-linux-android30-clang depth-stencil-blit-probe.c -L/path/to/mesa-stage/usr/local/lib -lEGL -lGLESv2 -Wl,--allow-shlib-undefined -Wall -Wextra -o mwm-independent-depth-blit-probe-stencil
```

Run outside game userdata with an isolated library path and an explicitly backed-up, process-matching RTScale test profile. Arguments for the stencil probe are `scale source_rb destination_rb mask_bits expected_physical_samples requested_samples`; mask bits 1/2/3 mean depth/stencil/both. `requested_samples=0` selects single-sample storage. The formats probe adds `format` as a final optional argument: 0=packed depth/stencil, 1=DEPTH_COMPONENT16, 2=STENCIL_INDEX8, 3=packed DEPTH24_STENCIL8 attached only to stencil. The original depth probe takes `scale expected_msaa2`.

Preserve Mesa's per-file MIT notices, the reconstruction's 0BSD notices, upstream attribution, LLVM notices, and LGPL libelf source/relink requirements. The three independently written probes are 0BSD. The historical source-only ZIP contains no Mesa binary. The updated normal overlay and validation/fix ZIP include the tested Mesa library with corresponding source/build links and notices, and contain no proprietary game source, shaders, APK, or Native Bridge payload.
