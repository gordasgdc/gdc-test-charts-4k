#!/usr/bin/env python3
"""Impacheteaza biblioteca in ZIP-uri independente (<2 GiB) fara a modifica EXR-urile.
Citeste sursa, scrie DOAR in --out (volum extern). EXR = ZIP_STORED (deja comprimate lossless)."""
import argparse, csv, hashlib, json, os, re, sys, zipfile
ap = argparse.ArgumentParser()
ap.add_argument("--src", default="/Volumes/Sandisk/GDC_TEST_CHARTS_4K")
ap.add_argument("--out", required=True)
ap.add_argument("--version", default="1.0.0")
ap.add_argument("--parts", type=int, default=3)
a = ap.parse_args()
S, V = a.src, a.version
os.makedirs(a.out, exist_ok=True)
DT = (2026, 11, 2, 0, 0, 0)
LIMIT = 2 * 1024**3
rows = list(csv.DictReader(open(f"{S}/CATALOG.csv")))
cfgs = sorted({r["variant"] for r in rows})
by = {c: [r for r in rows if r["variant"] == c] for c in cfgs}
assert all(len(v) == 25 for v in by.values()) and len(cfgs) == 23
master = {c: next(f for f in os.listdir(f"{S}/EXR") if f"__{c}__" in f) for c in cfgs}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""): h.update(b)
    return h.hexdigest()

def add_file(z, arc, path, method):
    zi = zipfile.ZipInfo(arc, DT); zi.external_attr = 0o644 << 16; zi.compress_type = method
    with open(path, "rb") as f, z.open(zi, "w", force_zip64=True) as o:
        for b in iter(lambda: f.read(1 << 24), b""): o.write(b)
def add_bytes(z, arc, data, method=zipfile.ZIP_DEFLATED):
    zi = zipfile.ZipInfo(arc, DT); zi.external_attr = 0o644 << 16; zi.compress_type = method
    z.writestr(zi, data)

# sume SHA-256 ale EXR (din catalog = verificat; MASTER calculat)
msha = {c: sha(f"{S}/EXR/{master[c]}") for c in cfgs}
def entries(c, root, single):
    d = f"{root}/" if single else f"{root}/{c}/"
    out = [(f"{d}{os.path.basename(r['file'])}", f"{S}/{r['file']}", r["sha256"]) for r in by[c]]
    out.append((f"{d}MASTER/{master[c]}", f"{S}/EXR/{master[c]}", msha[c]))
    return out
size = {c: sum(os.path.getsize(p) for _, p, _ in entries(c, 'x', False)) for c in cfgs}

info = lambda title: (f"{title}\nGDC Test Charts 4K {V} - CC BY 4.0 - (c) Cristi Gordas / GDC\n"
    "Extract with the normal unzip of macOS/Windows; each ZIP has its own top-level folder, so several ZIPs never collide. EXR files are byte-identical to the originals.\n"
    "SHA256SUMS.txt lists every file. https://gordas.dev/gdc-test-charts-4k/ \n")
pk = []
def build(name, cfglist, title):
    p = f"{a.out}/{name}"; ROOT = name[:-4]; single = len(cfglist) == 1
    sums = []; n = 0
    with zipfile.ZipFile(p, "w", allowZip64=True) as z:
        for c in cfglist:
            for arc, path, h in entries(c, ROOT, single):
                add_file(z, arc, path, zipfile.ZIP_STORED); sums.append(f"{h}  {arc[len(ROOT)+1:]}"); n += 1
        add_bytes(z, f"{ROOT}/SHA256SUMS.txt", "\n".join(sums) + "\n")
        add_bytes(z, f"{ROOT}/PACKAGE_INFO.txt", info(title) + "Configurations: " + ", ".join(cfglist) + "\n")
    pk.append({"file": name, "bytes": os.path.getsize(p), "sha256": sha(p), "exr_files": n, "configs": cfglist, "title": title})
    assert os.path.getsize(p) < LIMIT * 0.75, name
    print(name, pk[-1]["bytes"], flush=True)

# 1) metadate + documentatie + preview-uri (VALIDATION_REPORT.json curatat de cai interne)
name = f"gdc-test-charts-4k-{V}-docs-metadata.zip"; p = f"{a.out}/{name}"; ROOT = name[:-4]
with zipfile.ZipFile(p, "w", allowZip64=True) as z:
    skip = {"Icon", ".DS_Store"}
    for top in ("MANIFESTS", "VALIDATION", "PREVIEWS"):
        for d, ds, fs in os.walk(f"{S}/{top}"):
            ds.sort()
            for f in sorted(fs):
                if f in skip or f.startswith("._") or f.startswith("prototype_sha256"): continue
                full = os.path.join(d, f); arc = f"{ROOT}/{os.path.relpath(full, S)}"
                if f == "VALIDATION_REPORT.json":
                    t = open(full).read(); t = re.sub(r"/Volumes/[^\"]*?GDC_TEST_CHARTS_4K/", "", t)
                    add_bytes(z, arc, t)
                else:
                    add_file(z, arc, full, zipfile.ZIP_DEFLATED)
    add_file(z, f"{ROOT}/CATALOG.csv", f"{S}/CATALOG.csv", zipfile.ZIP_DEFLATED)
    add_file(z, f"{ROOT}/SOURCE_README_1.0.0-proto.md", f"{S}/README.md", zipfile.ZIP_DEFLATED)
pk.append({"file": name, "bytes": os.path.getsize(p), "sha256": sha(p), "exr_files": 0, "configs": [], "title": "docs-metadata"})
print(name, pk[-1]["bytes"], flush=True)

# 2) pachete complete: partitionare greedy dupa dimensiune, ordine stabila
groups = [[] for _ in range(a.parts)]; gs = [0] * a.parts
for c in sorted(cfgs, key=lambda c: (-size[c], c)):
    i = gs.index(min(gs)); groups[i].append(c); gs[i] += size[c]
for i, g in enumerate(groups, 1):
    build(f"gdc-test-charts-4k-{V}-complete-part{i}of{a.parts}.zip", sorted(g), f"Complete library, part {i} of {a.parts}")
# 3) pe configuratie
for c in cfgs:
    build(f"gdc-test-charts-4k-{V}-config-{c}.zip", [c], f"Single configuration: {c}")
json.dump({"version": V, "packages": pk, "chart_ids": sorted({r['chart_id'] for r in rows}), "configs": cfgs,
           "master": master, "master_sha256": msha}, open(f"{a.out}/packages.json", "w"), indent=1)
open(f"{a.out}/SHA256SUMS.txt", "w").write("".join(f"{x['sha256']}  {x['file']}\n" for x in pk))
print("DONE", len(pk), "packages", sum(x["bytes"] for x in pk))
