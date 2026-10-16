# Corresponding source and rebuild

`graphics-sources.tar.zst` contains the integrated graphics base (Mesa, RTScale reconstruction and the recorded LLVM/libdrm/gralloc/libelf sources and build inputs). Its SHA256 is `6ddc1e4dbf0c5663d2ed70df3c6eed406211cffad6c0f406f53c2e87b236d9dd`. Extract it to a separate build directory and read its `BUILD.md`, including the libelf relinking instructions. Do not rerun `integrate.py` on the integrated source.

Apply the following patches at the Mesa source root, in order, before compiling:

```bash
patch -p1 < /path/to/sources/docs/graphics/msaa/mesa-msaa-storage2.patch
patch -p1 < /path/to/sources/docs/graphics/depth-blit/mesa-depth-only-blit.patch
```

Follow the base archive's Android API30 / NDK r27c / LLVM21 build configuration and stage the resulting libraries. The retained RTScale documents describe the local shader-coordinate, MSAA and depth/stencil changes and their verification scope. `packaging/tests/graphics/` contains their independent probes.

Before hashing or packaging the staged `libgallium_dri.so`, run:

```bash
python packaging/anonymize-build-paths.py /path/to/stage/vendor/lib64/libgallium_dri.so
```

This normalizes diagnostic build-path strings; for future libelf builds prefer a stable `-ffile-prefix-map` setting. Archive owners should be normalized to root. The tested binary hashes are in `packaging/payload/manifests/`; timestamps and diagnostic paths can affect byte-for-byte reproducibility. A rebuilt or locally modified library needs its own hashes.

MWM's runtime scripts and Python sources are also present here. Modified MangoApp source, notices and its build procedure are in `mwm/vendor/mangoapp/`. Component licenses are retained in `LICENSES/` and in the graphics base archive. The source package omits runtime binary duplicates and general application test tooling.
