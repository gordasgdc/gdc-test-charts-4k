#!/usr/bin/env python3
"""Verifica pagina publica (3 limbi) FARA autentificare: HTTP 200, imagini, CSS/JS, hreflang, linkuri de descarcare (HEAD),
si ca marimile din downloads.json coincid cu Content-Length-ul asseturilor."""
import json, re, sys, urllib.request, urllib.parse
BASE = sys.argv[1] if len(sys.argv) > 1 else "https://gordas.dev"
UA = {"User-Agent": "gdc-test-charts-check"}
def req(u, m="GET"):
    r = urllib.request.Request(u, headers=UA, method=m)
    return urllib.request.urlopen(r, timeout=60)
bad = []; seen = set()
for path in ("/gdc-test-charts-4k/", "/gdc-test-charts-4k/en/", "/gdc-test-charts-4k/es/"):
    r = req(BASE + path); h = r.read().decode()
    if r.status != 200: bad.append((path, r.status))
    for m in set(re.findall(r'(?:src|href)="(/[^"#]*)"', h)) | set(re.findall(r'srcset="([^"]+)"', h)):
        for u in re.split(r",\s*", m):
            u = u.split(" ")[0]
            if not u.startswith("/") or u in seen or u.startswith("/gdc-test-charts-4k/#"): continue
            seen.add(u)
            try:
                rr = req(BASE + u, "HEAD")
                if rr.status != 200: bad.append((u, rr.status))
            except Exception as e: bad.append((u, str(e)[:60]))
    for u in set(re.findall(r'href="(https://github\.com/[^"]+releases/download/[^"]+)"', h)):
        if u in seen: continue
        seen.add(u)
        try:
            rr = req(u, "HEAD")
            if rr.status != 200: bad.append((u, rr.status))
        except Exception as e: bad.append((u, str(e)[:60]))
    for l in ("ro", "en", "es"):
        if f'hreflang="{l}"' not in h: bad.append((path, "hreflang " + l))
dl = json.load(urllib.request.urlopen(urllib.request.Request(BASE + "/gdc-test-charts-4k/downloads.json", headers=UA)))
for p in dl["packages"]:
    rr = req(p["url"], "HEAD")
    if int(rr.headers.get("Content-Length", -1)) != p["bytes"]: bad.append((p["file"], "size"))
print("urls checked:", len(seen), "assets:", len(dl["packages"]), "problems:", bad)
sys.exit(1 if bad else 0)
