#!/usr/bin/env python3
"""Genereaza pagina RO/EN/ES (HTML static) + CSS/JS + imagini in --out.
Intrari: packages.json (marimi, SHA-256), CATALOG.csv (gamut/curba), previews/*.webp."""
import argparse, csv, html, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from site_text import *

ap = argparse.ArgumentParser()
ap.add_argument("--packages", required=True)
ap.add_argument("--catalog", required=True)
ap.add_argument("--previews", default=os.path.join(os.path.dirname(__file__), "..", "previews"))
ap.add_argument("--out", required=True)
ap.add_argument("--tag", default="v1.0.0")
a = ap.parse_args()
E = html.escape
HOST = "https://gordas.dev"
REL = f"https://github.com/gordasgdc/gdc-test-charts-4k/releases/download/{a.tag}/"
REPO = "https://github.com/gordasgdc/gdc-test-charts-4k"
ICON_V = "3c492a5c"
pk = json.load(open(a.packages))
P = {p["file"]: p for p in pk["packages"]}
rows = list(csv.DictReader(open(a.catalog)))
cfg_meta = {}
for r in rows: cfg_meta[r["variant"]] = (r["gamut"], r["transfer"])
cfgs = pk["configs"]
parts = sorted([p for p in pk["packages"] if "-complete-part" in p["file"]], key=lambda p: p["file"])
docs = next(p for p in pk["packages"] if "-docs-" in p["file"])
part_of = {c: i + 1 for i, p in enumerate(parts) for c in p["configs"]}
V = pk["version"]
total_gb = (sum(p["bytes"] for p in parts) + 0) / 1e9
GN = {  # nume de gamut din catalog (RO) -> EN, ES
 "Rec.2020 (gamutul Apple Log)": ("Rec.2020 (Apple Log gamut)", "Rec.2020 (gamut de Apple Log)"),
 "Fujifilm F-Gamut (primare Rec.2020)": ("Fujifilm F-Gamut (Rec.2020 primaries)", "Fujifilm F-Gamut (primarios Rec.2020)"),
 "Rec.2020 (gamutul GP-Log2 conform GoPro)": ("Rec.2020 (GP-Log2 gamut per GoPro)", "Rec.2020 (gamut GP-Log2 según GoPro)"),
 "Rec.2020 (gamutul N-Log conform Nikon)": ("Rec.2020 (N-Log gamut per Nikon)", "Rec.2020 (gamut N-Log según Nikon)"),
}
def gname(s, i): return s if i == 0 or s not in GN else GN[s][i - 1]
def mb(n): return f"{n/1e6:,.0f} MB".replace(",", " ") if n < 1e9 else f"{n/1e9:.2f} GB"
def numfmt(n, i): return f"{n:,}".replace(",", " " if i == 0 else ("," if i == 1 else " "))
CHARTS = sorted(CH)
FAMS = sorted(FAM)
FILES = {  # alias
 "href_css": "/gdc-test-charts-4k/assets/charts.css", "href_js": "/gdc-test-charts-4k/assets/charts.js",
}

def head(i, lang):
    t, d = U["title"][i], U["desc"][i]
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{HOST}{PATH[l]}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{HOST}{PATH["en"]}">'
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "GDC Test Charts 4K", "description": d, "version": V,
          "url": HOST + PATH[lang], "inLanguage": lang, "license": "https://creativecommons.org/licenses/by/4.0/",
          "creator": {"@type": "Person", "name": "Dumitru Cristinel Gordas"}, "isAccessibleForFree": True,
          "encodingFormat": "image/x-exr", "datePublished": "2026-11-02",
          "distribution": [{"@type": "DataDownload", "encodingFormat": "application/zip", "contentUrl": REL + p["file"], "contentSize": f"{p['bytes']} B"} for p in parts + [docs]]}
    return (f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{E(t)}</title><meta name="description" content="{E(d)}"><link rel="canonical" href="{HOST}{PATH[lang]}">{alts}'
        f'<meta property="og:type" content="website"><meta property="og:title" content="{E(t)}"><meta property="og:description" content="{E(d)}">'
        f'<meta property="og:url" content="{HOST}{PATH[lang]}"><meta property="og:locale" content="{LOCALE[lang]}">'
        f'<meta property="og:image" content="{HOST}/gdc-test-charts-4k/img/GDC-TC-01A-1920.webp"><meta name="twitter:card" content="summary_large_image">'
        f'<meta name="color-scheme" content="light"><meta name="theme-color" content="#f4f1ea">'
        f'<link rel="icon" type="image/x-icon" href="/favicon.ico?v={ICON_V}"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png?v={ICON_V}">'
        f'<link rel="apple-touch-icon" href="/apple-touch-icon.png?v={ICON_V}"><link rel="stylesheet" href="{FILES["href_css"]}">'
        f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head>')

def lang_switch(i, lang):
    return (f'<div class="sw" role="group" aria-label="{E(U["lang_aria"][i])}">' + "".join(
        f'<a href="{PATH[l]}" hreflang="{l}" lang="{l}" aria-label="{n}"' + (' aria-current="true" class="cur"' if l == lang else "") + f'>{l.upper()}</a>'
        for l, n in (("ro", "Română"), ("en", "English"), ("es", "Español"))) + "</div>")

def sha_block(p, i):
    return (f'<span class="sha"><code>{p["sha256"]}</code><button type="button" class="copy" data-copy="{p["sha256"]}" data-done="{E(U["dl_copied"][i])}">{E(U["dl_copy"][i])}</button></span>')

def hero(i):
    return (f'<section id="intro" class="hero"><div class="wrap hero-g"><div class="hl"><p class="kicker">{E(U["kicker"][i])}</p><h1>{U["h1"][i]}</h1>'
        f'<p class="lead">{E(U["lead"][i])}</p><p class="cta"><a class="btn big" href="#download">{E(U["cta_dl"][i])}</a><a class="ghost" href="#gallery">{E(U["cta_gal"][i])} →</a></p>'
        f'<ul class="facts"><li><b>575</b> {E(U["f_charts"][i])}</li><li><b>23</b> {E(U["f_cfg"][i])}</li><li><b>12</b> {E(U["f_fam"][i])}</li>'
        f'<li><b>{total_gb:.2f}&nbsp;GB</b> {E(U["f_size"][i])}</li></ul></div>'
        f'<figure class="hero-fig"><img src="/gdc-test-charts-4k/img/GDC-TC-01A-1920.webp" srcset="/gdc-test-charts-4k/img/GDC-TC-01A-640.webp 640w, /gdc-test-charts-4k/img/GDC-TC-01A-1920.webp 1920w" '
        f'sizes="(min-width:960px) 56vw, 92vw" width="1920" height="1080" alt="{E(U["hero_alt"][i])}" fetchpriority="high"><figcaption>{E(U["hero_note"][i])}</figcaption></figure></div>'
        f'<div class="wedge" role="img" aria-label="{E(U["wedge_aria"][i])}"></div></section>')

def what(i):
    li = "".join(f'<li><span class="n">{k+1}</span><div><h3>{E(u[i])}</h3><p>{E(u[3+i])}</p></div></li>' for k, u in enumerate(U["uses"]))
    return (f'<section id="what" class="sec"><div class="wrap two"><header class="sh"><p class="kicker">{E(U["what_k"][i])}</p><h2>{U["what_h"][i]}</h2><p class="lead">{E(U["what_p"][i])}</p></header>'
            f'<ol class="uses">{li}</ol></div></section>')

def contract(i):
    rows_ = "".join(f'<div class="kv"><dt>{E(r[i])}</dt><dd>{E(r[3+i])}</dd></div>' for r in U["ct_rows"])
    return (f'<section id="contract" class="sec alt"><div class="wrap two"><header class="sh"><p class="kicker">{E(U["ct_k"][i])}</p><h2>{E(U["ct_h"][i])}</h2>'
            f'<aside class="note"><h3>{E(U["pv_h"][i])}</h3><p>{E(U["pv_p"][i])}</p></aside></header><dl class="kvs">{rows_}</dl></div></section>')

def gallery(i, lang):
    out = [f'<section id="gallery" class="sec"><div class="wrap"><header class="sh wide"><p class="kicker">{E(U["g_k"][i])}</p><h2>{E(U["g_h"][i])}</h2><p class="lead">{E(U["g_p"][i])}</p></header>']
    for f in FAMS:
        name, txt = FAM[f][0][i], FAM[f][1][i]
        figs = ""
        for c in CHARTS:
            if not c.startswith(f): continue
            cid = "GDC-TC-" + c; cap = CH[c][i]
            tag = ""
            if c == "02B": tag = U["illus"][i]
            elif f == "12": tag = U["synth"][i]
            elif c == "08B": tag = U["noisy"][i]
            figs += (f'<figure class="chart"><a class="open" href="/gdc-test-charts-4k/img/{cid}-1920.webp" data-full="/gdc-test-charts-4k/img/{cid}-1920.webp" '
                     f'data-title="{E(cid)} · {E(cap)}" aria-label="{E(U["g_open"][i])}: {E(cid)}">'
                     f'<img src="/gdc-test-charts-4k/img/{cid}-640.webp" width="640" height="360" loading="lazy" decoding="async" alt="{E(U["g_alt"][i])} {E(cid)}: {E(cap)}"></a>'
                     f'<figcaption><b>{E(cid)}</b>' + (f' <span class="tag">{E(tag)}</span>' if tag else "") + f'<span>{E(cap)}</span></figcaption></figure>')
        out.append(f'<article class="fam" id="fam-{f}"><div class="ft"><span class="fn">{f}</span><h3>{E(name)}</h3><p>{E(txt)}</p></div><div class="figs">{figs}</div></article>')
    out.append(f'<p class="fine">{E(U["g_cap"][i])}</p></div></section>')
    return "".join(out)

def configs(i):
    cols = U["cf_cols"][i]
    th = "".join(f"<th scope='col'>{E(c)}</th>" for c in cols)
    trs = ""
    for c in cfgs:
        g, t = cfg_meta[c]; zf = f"gdc-test-charts-4k-{V}-config-{c}.zip"; p = P[zf]
        trs += (f'<tr><th scope="row" data-l="{E(cols[0])}"><code>{c}</code></th><td data-l="{E(cols[1])}">{E(gname(g, i))}</td><td data-l="{E(cols[2])}">{E(t)}</td>'
                f'<td data-l="{E(cols[3])}"><a href="{REL}{zf}" rel="noopener">{E(U["dl_btn"][i])} · {mb(p["bytes"])}</a>{sha_block(p, i)}</td>'
                f'<td data-l="{E(cols[4])}">{part_of[c]}/3</td></tr>')
    return (f'<section id="configs" class="sec alt"><div class="wrap"><header class="sh wide"><p class="kicker">{E(U["cf_k"][i])}</p><h2>{E(U["cf_h"][i])}</h2><p class="lead">{E(U["cf_p"][i])}</p></header>'
            f'<div class="tw"><table class="cfg"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div><p class="fine">{E(U["cf_master"][i])}</p></div></section>')

def guide(i):
    li = "".join(f'<li><h3>{E(s[i])}</h3><p>{E(s[3+i])}</p></li>' for s in U["steps"])
    return (f'<section id="guide" class="sec"><div class="wrap two"><header class="sh"><p class="kicker">{E(U["gd_k"][i])}</p><h2>{E(U["gd_h"][i])}</h2></header><ol class="steps">{li}</ol></div></section>')

def download(i):
    pc = ""
    for n, p in enumerate(parts, 1):
        pc += (f'<li class="pk"><div class="pkh"><h4>{E(U["dl_part"][i])} {n} {E(U["dl_of"][i])} 3</h4><a class="btn" href="{REL}{p["file"]}" rel="noopener">{E(U["dl_btn"][i])} · {mb(p["bytes"])}</a></div>'
               f'<p class="fine"><code>{p["file"]}</code> · {p["exr_files"]} {E(U["dl_charts"][i])}</p>{sha_block(p, i)}'
               f'<p class="cf"><span>{E(U["dl_configs"][i])}:</span> {", ".join("<code>"+c+"</code>" for c in p["configs"])}</p></li>')
    pc += (f'<li class="pk docs"><div class="pkh"><h4>docs-metadata</h4><a class="btn" href="{REL}{docs["file"]}" rel="noopener">{E(U["dl_btn"][i])} · {mb(docs["bytes"])}</a></div>'
           f'<p class="fine"><code>{docs["file"]}</code> · {E(U["dl_docs_n"][i])}</p><p>{E(U["dl_docs"][i])}</p>{sha_block(docs, i)}</li>')
    return (f'<section id="download" class="sec dark"><div class="wrap"><header class="sh wide"><p class="kicker">{E(U["dl_k"][i])}</p><h2>{E(U["dl_h"][i])}</h2><p class="lead">{E(U["dl_p"][i])}</p></header>'
            f'<h3 class="sub">{E(U["dl_full"][i])}</h3><ul class="pks">{pc}</ul>'
            f'<div class="three"><div><h3>{E(U["dl_alt_h"][i])}</h3><p>{E(U["dl_alt_p"][i])}</p></div>'
            f'<div><h3>{E(U["dl_ver_h"][i])}</h3><p>{E(U["dl_ver_p"][i])}</p><pre><code>shasum -a 256 gdc-test-charts-4k-{V}-complete-part1of3.zip</code></pre><pre><code>Get-FileHash -Algorithm SHA256 .\\gdc-test-charts-4k-{V}-complete-part1of3.zip</code></pre></div>'
            f'<div><h3>{E(U["dl_ext_h"][i])}</h3><p>{E(U["dl_ext_p"][i])}</p></div></div>'
            f'<p class="links"><a href="{REPO}/releases/tag/{a.tag}" rel="noopener">{E(U["dl_rel"][i])}</a> · <a href="{REL}SHA256SUMS.txt" rel="noopener">{E(U["dl_sums"][i])}</a> · <a href="{REPO}" rel="noopener">{E(U["dl_repo"][i])}</a></p></div></section>')

def limits(i):
    li = "".join(f'<li><h3>{E(x[i])}</h3><p>{E(x[3+i])}</p></li>' for x in U["lm"])
    return (f'<section id="limits" class="sec"><div class="wrap two"><header class="sh"><p class="kicker">{E(U["lm_k"][i])}</p><h2>{E(U["lm_h"][i])}</h2></header><ul class="lims">{li}</ul></div></section>')

def licence(i):
    return (f'<section id="license" class="sec alt"><div class="wrap two"><header class="sh"><p class="kicker">{E(U["lc_k"][i])}</p><h2>{E(U["lc_h"][i])}</h2><p class="lead">{E(U["lc_p"][i])}</p>'
            f'<p><a href="https://creativecommons.org/licenses/by/4.0/" rel="license noopener">CC BY 4.0</a></p></header><div class="lic"><h3>{E(U["lc_credit_h"][i])}</h3><blockquote>{E(U["lc_credit"][i])}</blockquote>'
            f'<h3>{E(U["lc_3p"][i])}</h3><p>{E(U["lc_3p_p"][i])}</p><dl class="kvs sm"><div class="kv"><dt>{E(U["lc_ver"][i])}</dt><dd>{E(U["lc_ver_v"][i])}</dd></div>'
            f'<div class="kv"><dt>{E(U["lc_sup"][i])}</dt><dd>{E(U["lc_sup_v"][i])} <a href="{REPO}/issues" rel="noopener">GitHub Issues</a></dd></div></dl></div></div></section>')

def faq(i):
    li = "".join(f'<details><summary>{E(q[i])}</summary><p>{E(q[3+i])}</p></details>' for q in U["faq"])
    return (f'<section id="faq" class="sec"><div class="wrap two"><header class="sh"><p class="kicker">{E(U["faq_k"][i])}</p><h2>{E(U["faq_h"][i])}</h2></header><div class="faq">{li}</div></div></section>')

def page(lang):
    i = LANGS.index(lang)
    nav = "".join(f'<a href="#{k}">{E(v[i])}</a>' for k, v in U["nav"].items())
    top = (f'<a class="skip" href="#main">{E(U["skip"][i])}</a><header class="top"><div class="wrap bar"><a class="brand" href="{PATH[lang]}#intro" aria-label="GDC Test Charts 4K">'
           f'<img src="/icons/icon-192.png?v={ICON_V}" alt="" width="28" height="28"><span>GDC <b>TEST CHARTS</b> 4K</span></a>'
           f'<nav class="nav" id="nav" aria-label="{E(U["nav_aria"][i])}">{nav}</nav>{lang_switch(i, lang)}'
           f'<a class="btn sm" href="#download">{E(U["dl_btn"][i])}</a><button class="burger" type="button" aria-expanded="false" aria-controls="nav" aria-label="{E(U["menu"][i])}"><span></span><span></span><span></span></button></div></header>')
    foot = (f'<footer class="foot"><div class="wrap"><p>{E(U["foot_a"][i])}</p><p><a href="https://gordas.dev/">{E(U["home"][i])}</a> · '
            f'<a href="https://gordas.dev/termeni">{E(U["foot_t"][i])}</a> · <a href="https://gordas.dev/confidentialitate">{E(U["foot_p"][i])}</a> · <a href="https://gordas.dev/cookie">{E(U["foot_c"][i])}</a> · '
            f'<a href="{REPO}" rel="noopener">GitHub</a> · CC BY 4.0</p></div></footer>'
            f'<dialog id="lb" aria-label="{E(U["g_open"][i])}"><button class="lbx" type="button" aria-label="{E(U["g_close"][i])}">×</button><img alt=""><p></p><p class="fine">{E(U["g_cap"][i])}</p></dialog>')
    return (head(i, lang) + "<body>" + top + '<main id="main">' + hero(i) + what(i) + contract(i) + gallery(i, lang) + configs(i) + guide(i) + download(i) + limits(i) + licence(i) + faq(i)
            + "</main>" + foot + f'<script src="{FILES["href_js"]}" defer></script></body></html>\n')

out = a.out
for lang, sub in (("ro", ""), ("en", "en"), ("es", "es")):
    d = os.path.join(out, sub); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(page(lang))
os.makedirs(os.path.join(out, "img"), exist_ok=True)
for f in os.listdir(a.previews):
    if f.endswith(".webp"): shutil.copyfile(os.path.join(a.previews, f), os.path.join(out, "img", f))
os.makedirs(os.path.join(out, "assets"), exist_ok=True)
for f in ("charts.css", "charts.js"):
    shutil.copyfile(os.path.join(os.path.dirname(__file__), "site_assets", f), os.path.join(out, "assets", f))
json.dump({"name": "GDC Test Charts 4K", "version": V, "tag": a.tag, "release": f"{REPO}/releases/tag/{a.tag}",
           "packages": [{"file": p["file"], "bytes": p["bytes"], "sha256": p["sha256"], "url": REL + p["file"]} for p in pk["packages"]]},
          open(os.path.join(out, "downloads.json"), "w"), indent=1)
print("site ->", out)
