#!/usr/bin/env python3
"""PNG sRGB (display-rendered, clipate) -> WebP optimizate pentru web: 640 px (grila) si 1920 px (vizualizare)."""
import argparse, glob, os
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("--src", default="/Volumes/Sandisk/GDC_TEST_CHARTS_4K/PREVIEWS"); ap.add_argument("--out", required=True)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
for f in sorted(glob.glob(f"{a.src}/GDC-TC-*__display_sRGB.png")):
    cid = os.path.basename(f).split("__")[0]; im = Image.open(f).convert("RGB")
    im.save(f"{a.out}/{cid}-1920.webp", "WEBP", quality=84, method=6)
    im.resize((640, 360), Image.LANCZOS).save(f"{a.out}/{cid}-640.webp", "WEBP", quality=80, method=6)
print(len(glob.glob(f"{a.out}/*-640.webp")), "chart-uri")
