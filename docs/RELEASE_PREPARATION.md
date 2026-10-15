# 0.85 release preparation

## Source and distribution

The repository is https://github.com/relorah/mltd-waydroid-manager. The official title is MLTD Waydroid Manager (MWM). Version 0.85 retains Gamescope as its supported runtime; KWin Direct is disabled. Span Displays and BC250 register sampling remain experimental and off by default.

Build a candidate from a clean committed checkout:

```bash
python packaging/check-release.py
python -m unittest discover -s tests -v
python tests/graphics/msaa/test-helper.py
python packaging/build-release.py --graphics-sources /path/to/graphics-sources.tar.zst --output /path/to/artifacts --label rc1
```

The expected base-source SHA256 is `6ddc1e4dbf0c5663d2ed70df3c6eed406211cffad6c0f406f53c2e87b236d9dd`. The candidate includes that source archive, both local Mesa patches, component notices, the modified MangoApp source and build/relink instructions. Do not confuse GitHub's automatic source archive with this complete distribution.

`RELEASE_MANIFEST.json` pins the source commit and base-source hash. `payload/SHA256SUMS` authenticates the graphics archives/config/manifests, and `payload/manifests/overlay-SHA256SUMS` records all twelve installed files. The builder preserves installer executable permissions, rejects dirty/untracked source and refuses to overwrite an existing candidate. It never publishes a release.

## Publication checklist

- Re-fetch main and preserve unrelated changes before uploading.
- Review root files and remove obsolete candidate ZIPs, work directories, caches, credentials, game assets and proprietary Native Bridge binaries from the release tree.
- Run the offline audit, Python tests, helper guard tests and native HUD/config tests; record versions and source commit.
- Verify base-source hash and successful application of MSAA and depth-blit patches.
- Verify the actual packaged Mesa hash in Android; record which UI/MV tests use it.
- Capture README comparisons with identical quality, unit, outfits, display aspect and FSR settings. Retain original PNGs and a capture manifest. Verify that x3 is actually applied before recording.
- Test ZIP integrity and source inclusion, executable permissions, checksums and extracted installer help.
- Attach the complete candidate ZIP, an explicit source snapshot and SHA256 manifest. Document any fresh-install or hardware combinations not tested.
- Verify the uploaded assets and release tag/commit after publishing.

Do not run a graphics reinstall on a user's environment as a substitute for a clean-machine installer test. The isolated user-file update test verifies settings/log preservation and replacement of stale same-size/same-timestamp files without touching live state. Full new-machine setup remains a separate test.
