#!/usr/bin/env python3
"""Verifica ZIP-urile (locale sau descarcate de la adresele publice): SHA-256 al arhivelor din packages.json,
continutul fiecarui EXR fata de CATALOG.csv, completitudinea (23x25 + 23 MASTER), fara symlink-uri, nume sigure.
Optional extrage in --extract (director NOU) si recompara pe disc."""
import argparse, csv, hashlib, json, os, sys, zipfile, stat
ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True, help="director cu ZIP-uri + packages.json")
ap.add_argument("--catalog", required=True, help="CATALOG.csv sursa")
ap.add_argument("--extract", help="director NOU, gol, pentru extragere reala")
a = ap.parse_args()
def sha(f):
    h = hashlib.sha256()
    for b in iter(lambda: f.read(1 << 24), b""): h.update(b)
    return h.hexdigest()
pk = json.load(open(f"{a.dir}/packages.json"))
cat = {os.path.basename(r["file"]): r["sha256"] for r in csv.DictReader(open(a.catalog))}
msha = pk["master_sha256"]; mnames = {v: k for k, v in pk["master"].items()}
bad = []; seen = {}; mseen = set()
for p in pk["packages"]:
    fp = f"{a.dir}/{p['file']}"
    with open(fp, "rb") as f: ok = sha(f) == p["sha256"] and os.path.getsize(fp) == p["bytes"]
    if not ok: bad.append(("archive-hash", p["file"]))
    with zipfile.ZipFile(fp) as z:
        if z.testzip(): bad.append(("crc", p["file"]))
        for i in z.infolist():
            if stat.S_ISLNK(i.external_attr >> 16): bad.append(("symlink", i.filename))
            if i.filename.startswith("/") or ".." in i.filename.split("/") or "/._" in i.filename or ".DS_Store" in i.filename:
                bad.append(("unsafe-name", i.filename))
            if not i.filename.endswith(".exr"): continue
            b = os.path.basename(i.filename)
            with z.open(i) as f: h = sha(f)
            if b in mnames:
                mseen.add(b)
                if h != msha[mnames[b]]: bad.append(("master-hash", i.filename))
            else:
                if cat.get(b) != h: bad.append(("exr-hash", i.filename))
                seen.setdefault(b, []).append(p["file"])
cp = lambda b, k: sum(1 for f in seen.get(b, []) if k in f)
miss = [b for b in cat if cp(b, "-complete-part") != 1]
miss2 = [b for b in cat if cp(b, "-config-") != 1]
res = {"packages": len(pk["packages"]), "exr_charts_expected": len(cat),
       "exr_charts_in_complete_parts_exactly_once": len(cat) - len(miss),
       "exr_charts_in_config_zips_exactly_once": len(cat) - len(miss2),
       "masters_seen": len(mseen), "masters_expected": len(mnames), "problems": bad}
if a.extract:
    os.makedirs(a.extract)
    assert not os.listdir(a.extract), "director de extragere nenul"
    for p in pk["packages"]:
        if "-docs-" in p["file"]: continue
        zipfile.ZipFile(f"{a.dir}/{p['file']}").extractall(a.extract)
    n = 0
    for d, ds, fs in os.walk(a.extract):
        for f in fs:
            fp = os.path.join(d, f)
            if os.path.islink(fp): bad.append(("symlink-ondisk", fp))
            if f.endswith(".exr"):
                with open(fp, "rb") as fh: h = sha(fh)
                exp = cat.get(f) or (msha[mnames[f]] if f in mnames else None)
                if h != exp: bad.append(("ondisk-hash", fp))
                n += 1
    res["extracted_exr_files_checked"] = n
ok = not bad and not miss and not miss2 and len(mseen) == len(mnames)
print(json.dumps(res, indent=1)); print("RESULT:", "OK" if ok else "FAIL"); sys.exit(0 if ok else 1)
