#!/usr/bin/env python3
"""Descarca de la adresele PUBLICE (fara autentificare) toate assetele listate in downloads.json-ul paginii
si packages.json din release, intr-un director nou. Apoi ruleaza verify_archives.py pe el."""
import argparse, json, os, sys, urllib.request
ap = argparse.ArgumentParser(); ap.add_argument("--base", required=True, help="URL de baza al release-ului (…/releases/download/vX/)")
ap.add_argument("--out", required=True); a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
def get(name):
    req = urllib.request.Request(a.base + name, headers={"User-Agent": "gdc-test-charts-verify"})
    with urllib.request.urlopen(req, timeout=120) as r, open(os.path.join(a.out, name), "wb") as o:
        n = 0
        while True:
            b = r.read(1 << 22)
            if not b: break
            o.write(b); n += len(b)
        print(r.status, name, n, flush=True); return n, r.status
get("packages.json"); get("SHA256SUMS.txt")
pk = json.load(open(os.path.join(a.out, "packages.json")))
bad = 0
for p in pk["packages"]:
    n, st = get(p["file"])
    if st != 200 or n != p["bytes"]: bad += 1; print("MISMATCH", p["file"], n, p["bytes"])
sys.exit(1 if bad else 0)
