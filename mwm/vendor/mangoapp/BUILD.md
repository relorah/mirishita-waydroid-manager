# MWM MangoApp integer alignment build

Upstream: https://github.com/flightlessmango/MangoHud
Tag v0.8.4, commit 992103e4fb744897826de04ea00a2f71e7018214.
License: MIT. MangoHud, ImGui and ImPlot licenses are included; patched MangoHud source, dependency wraps with download hashes, and notices are in MangoHud-0.8.4-mwm-source.tar.gz.

Local change: opt-in environment MWM_MANGOAPP_FPS_INTEGER_ALIGN makes exec render measured FPS rounded to an integer at the native CPU/GPU right-alignment anchor, followed by the small FPS superscript using the same ImGui calls as upstream HudElements::fps. Measurement precision stays unchanged. Other exec users retain upstream behavior when the environment variable is unset. The system MangoApp binary is not overwritten. The MWM wrapper selects scripts/mangoapp-native/mangoapp and enables the option.

Build host: CachyOS x86_64, GCC 16.2.1, Meson 1.12.1. ImGui 1.91.6, ImPlot 0.16, Vulkan-Headers/Utility-Libraries 1.4.346 wraps; system spdlog 1.17.0/fmt 12, GLFW 3.5.1. This AMD-targeted build disables NVML/XNVCtrl. No NVIDIA runtime validation. System dependencies required: GL, X11, Wayland client, xkbcommon, GLFW, spdlog 1.17, fmt 12, glibc. No additional shared libraries are redistributed.

Rebuild from the included patched source (Meson, Ninja, C/C++ compiler, Python Mako and dependency development files required):

```bash
meson setup build -Dmangoapp=true -Dwith_xnvctrl=disabled -Dwith_nvml=disabled -Dmangoplot=disabled -Dtests=disabled -Duse_system_spdlog=enabled -Dbuildtype=release
ninja -C build -j 4 src/mangoapp
```

Test integer anchors with the same ImGui and MangoHud font:

```bash
cc -c src/font_unispace.c -o font_unispace.o
c++ -std=c++17 -Isubprojects/imgui-1.91.6 -Isrc /path/to/MWM/tests/test_fps_alignment.cpp font_unispace.o build/subprojects/imgui-1.91.6/libimgui.a -o test-fps-alignment
./test-fps-alignment
```

Expected: 9.99, 60.00, 120.00, 240.00 and --.-- all have integer anchor 60 at font_size=29; displayed results are 10, 60, 120, 240, --. This verifies coordinates, not the BC250 screenshot. Reproduction and binary SHA256:

8a51bc4ef6aeed281a89a1808af4f6d33515471958f75183b719dcb237d869ae  scripts/mangoapp-native/mangoapp

Additional opt-in layout: preserve the 285px outer width and native window padding. Reduce both label-to-value and value-to-temperature gaps to 80%, using two-digit values as the baseline. Integer anchors of GPU/CPU/FPS remain shared. FPS label uses the engine/frametime color, and the small superscript uses upstream font_small. Tests verify 80% gap arithmetic with actual font widths. Final screen appearance remains unverified.

BC250 test build: opt-in MWM_BC250_GPU_CACHE reads the shared device-matched cache, expires after 2 seconds, and displays -- on invalid data. Read-only GRBM_STATUS sampling (2 ms, published every 0.5 seconds) uses the included bc250-gpu-probe.c and libdrm_amdgpu; no clock or voltage writes. Register choice references filippor/cyan-skillfish-governor commit 7b08fdcf542d1edd82f3a9077c902038019c9842. Rebuild probe: `cc -O2 scripts/bc250-gpu-probe.c $(pkg-config --cflags --libs libdrm_amdgpu) -o scripts/mangoapp-native/bc250-gpu-probe`. Enabled only when the existing config/mwm/bc250-gpu-test flag is present.

Current packaged binary SHA256:
3931971a3aa7498a780cd4a61215467d09b817249711f1e4a0d1d37178902274  scripts/mangoapp-native/mangoapp
504b7d7e14b9234562674b7f34dece4fedf7740ed6a9aefb3132045ddd7c08af  scripts/mangoapp-native/bc250-gpu-probe

BC250 register reference license: LICENSE-BC250-reference (MIT, copyright Marcus Medom Ryding). BC250 sampling is experimental and opt-in. The existing test flag is preserved by app updates. To enable it manually, create `${XDG_CONFIG_HOME:-$HOME/.config}/mwm/bc250-gpu-test`; to disable it, remove that file and restart the overlay. Hardware activity is a sampled GPU-wide busy ratio, not a per-game load metric.
