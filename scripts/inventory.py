#!/usr/bin/env python3
"""Reconciliere sursa <-> CATALOG.csv <-> MASTER. Doar citire. Scrie JSON in --out."""
import csv, hashlib, json, os, sys, argparse
ap = argparse.ArgumentParser()
ap.add_argument("--src", default="/Volumes/Sandisk/GDC_TEST_CHARTS_4K")
ap.add_argument("--out", required=True)
ap.add_argument("--hash", action="store_true", help="recalculeaza SHA-256 (citire completa)")
a = ap.parse_args()
S = a.src
rows = list(csv.DictReader(open(f"{S}/CATALOG.csv")))
cfgs = sorted({r["variant"] for r in rows})
disk_cfg = sorted(d for d in os.listdir(S) if os.path.isdir(f"{S}/{d}") and d not in
    {"EXR","MANIFESTS","PREVIEWS","VALIDATION","_FINDER_STYLE"})
exr_dir = sorted(f for f in os.listdir(f"{S}/EXR") if f.endswith(".exr"))
rep = {"catalog_rows": len(rows), "configs_catalog": cfgs, "configs_disk": disk_cfg,
       "charts": sorted({r["chart_id"] for r in rows}), "master_in_EXR": len(exr_dir),
       "missing": [], "size_mismatch": [], "hash_mismatch": [], "extra_on_disk": []}
cat_files = set()
tot = 0
for r in rows:
    p = f"{S}/{r['file']}"; cat_files.add(r["file"])
    if not os.path.isfile(p): rep["missing"].append(r["file"]); continue
    sz = os.path.getsize(p); tot += sz
    if sz != int(r["bytes"]): rep["size_mismatch"].append(r["file"])
    if a.hash:
        h = hashlib.sha256()
        with open(p,"rb") as f:
            for b in iter(lambda: f.read(1<<24), b""): h.update(b)
        if h.hexdigest() != r["sha256"]: rep["hash_mismatch"].append(r["file"])
for c in disk_cfg:
    for f in os.listdir(f"{S}/{c}"):
        if f.endswith(".exr") and f"{c}/{f}" not in cat_files: rep["extra_on_disk"].append(f"{c}/{f}")
rep["catalog_bytes"] = tot
rep["master_bytes"] = sum(os.path.getsize(f"{S}/EXR/{f}") for f in exr_dir)
rep["master_cfg_missing"] = [c for c in cfgs if not any(f"__{c}__" in f for f in exr_dir)]
json.dump(rep, open(a.out,"w"), indent=1)
print({k:(v if not isinstance(v,list) or len(v)<6 else f"{len(v)} items") for k,v in rep.items()})
