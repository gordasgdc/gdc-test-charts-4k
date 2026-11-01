# Provenance and exclusions (1.0.0)

**Source:** a local library of 1,445 regular files (3,147,484,535 bytes), read-only during publication. 575 charts are listed in `CATALOG.csv` (23 configurations × 25 charts); the same directory holds 23 `GDC_STUDIO_MASTER_4K` files in `EXR/`. All 575 catalogue SHA-256 values and sizes matched the files on disk; the 23 MASTER hashes were computed for this release.

**Provenance of content:** all charts are generated procedurally by the author's own generator (label 1.0.0-proto) from published definitions (CIE 15, CIE 1931 2°, Bradford/CAT02/CAT16/HPE adaptation, Kim et al. 2002 Planckian locus, manufacturers' published curve and primary specifications). CC24 values are nominal published CIELAB averages, not X-Rite measurement data. No third-party images or code are included. Colour Science (BSD-3) was used only as a validation oracle during the author's QA and is not part of the data.

**Published as-is:** all 575 EXR charts and 23 MASTER EXR (byte-identical; MASTER placed in `MASTER/` inside each configuration folder), per-chart manifests, validation reports, `CATALOG.csv`, original `README.md` of the source (as `SOURCE_README_1.0.0-proto.md`), sRGB previews.

**Modified:** `VALIDATION/VALIDATION_REPORT.json` — internal absolute paths were removed (the only edit). The preview PNGs were re-encoded to WebP for the web page and repository; the PNG originals are included in the docs-metadata archive.

**Excluded on purpose:** `_FINDER_STYLE/` (internal personal icon concepts and backups), `00_MASTER` (a symlink pointing outside the library; the 23 MASTER files are shipped instead from `EXR/`), `index.html` (offline viewer of the source; replaced by the web page), `VALIDATION/prototype_sha256_before_restructure.json` (internal pre-restructure hashes), `.DS_Store`, `Icon` files and AppleDouble (`._*`) files.

**Not included:** the chart generator (unmerged development branch with constants shared with a proprietary project; reproducibility is by SHA-256 and manifests).
