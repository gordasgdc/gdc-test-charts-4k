#!/usr/bin/env python3
"""Genereaza README.md (EN), README.ro.md, README.es.md si docs/DOWNLOADS.md din packages.json (marimi + SHA-256)."""
import argparse, csv, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from site_text import FAM, CH, LANGS
ap = argparse.ArgumentParser(); ap.add_argument("--packages", required=True); ap.add_argument("--catalog", required=True)
ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..")); ap.add_argument("--tag", default="v1.0.0")
a = ap.parse_args()
pk = json.load(open(a.packages)); V = pk["version"]
REL = f"https://github.com/gordasgdc/gdc-test-charts-4k/releases/download/{a.tag}/"
PAGE = {"ro": "https://gordas.dev/gdc-test-charts-4k/", "en": "https://gordas.dev/gdc-test-charts-4k/en/", "es": "https://gordas.dev/gdc-test-charts-4k/es/"}
parts = sorted([p for p in pk["packages"] if "-complete-part" in p["file"]], key=lambda p: p["file"])
docs = next(p for p in pk["packages"] if "-docs-" in p["file"])
cfgp = [p for p in pk["packages"] if "-config-" in p["file"]]
meta = {r["variant"]: (r["gamut"], r["transfer"]) for r in csv.DictReader(open(a.catalog))}
def sz(n): return f"{n/1e9:.2f} GB" if n >= 1e9 else f"{n/1e6:.0f} MB"
def tbl(ps, hdr):
    s = f"| {hdr[0]} | {hdr[1]} | SHA-256 |\n|---|---:|---|\n"
    return s + "".join(f"| [`{p['file']}`]({REL}{p['file']}) | {sz(p['bytes'])} | `{p['sha256']}` |\n" for p in ps)
H = {"ro": ("Fișier", "Mărime"), "en": ("File", "Size"), "es": ("Archivo", "Tamaño")}

T = {
"en": dict(
 name="README.md", alt="[Română](README.ro.md) · [Español](README.es.md) · [Web page](%s)" % PAGE["en"],
 h1="GDC Test Charts 4K", tag="Free, open test charts for colour pipelines: 575 EXR float32 images at 3840×2160 in 23 colour configurations and 12 test families.",
 s_what="What it is", what="A library of mathematically defined test charts to check IDTs, ODTs, DRTs, LUTs, OFX plugins and DCTL transforms in DaVinci Resolve (or any scene-referred pipeline). The same 25 charts are rendered separately in 23 gamut-and-curve configurations, so you can test a tool in the space it actually works in.",
 s_dl="Download", dl_intro="No account, payment or app is needed. **The complete library is 4 ZIP files** (three parts that hold different configurations, plus the documentation/metadata archive). A single “everything” ZIP is not offered: the data is about 3.05 GB and a GitHub asset is limited to 2 GiB. Every ZIP has its own top-level folder, so archives never collide.",
 dl_part="Complete library (download all three parts, plus docs-metadata)", dl_cfg="Single configurations (optional, about 130 MB each; they repeat content of the parts)",
 s_files="What is in the data", files="Each configuration folder holds the 25 charts (`GDC-TC-<ID>_<slug>__<configuration>__3840x2160.exr`) and a `MASTER/` subfolder with its `GDC_STUDIO_MASTER_4K` reference file. The `docs-metadata` archive holds per-chart manifests (ROIs, reference values, intended tests, limitations, provenance, SHA-256), the validation report, `CATALOG.csv` and sRGB previews.",
 s_fam="Families", fam_cols=("ID", "Family", "What it tests"),
 s_cfg="Configurations", cfg_cols=("Folder = configuration id", "Gamut", "Curve"),
 s_use="How to use (DaVinci Resolve)", use=[
  "Pick the configuration that matches the space in which the tool under test works (for example `dwg_davinci_intermediate` for a DaVinci Wide Gamut / Intermediate pipeline).",
  "Extract the ZIP and import the EXR files from that configuration's folder into the Media Pool.",
  "Declare the input space exactly: the gamut and curve named by the folder, either through the project's colour management (clip input space) or a Color Space Transform node.",
  "Avoid a double transform: if the project already converts the input, do not add a second conversion for the same space. EXR files carry no transfer curve for the host to guess.",
  "Measure on real pixels using the ROIs (pixel rectangles) and reference values in each chart's manifest (`docs-metadata`).",
  "Read the limits below before drawing conclusions."],
 s_ct="Data contract", ct="OpenEXR, RGB, float32 (IEEE binary32), lossless ZIP compression, 3840×2160, scene-referred, full-range, no tone mapping or display rendering, no clipping. Negative values and values above 1 are intentional (gamut stress, headroom, sub-black). Each chart is composed once in ACES2065-1 (AP0, linear) and converted AP0 → XYZ D65 (Bradford) → target gamut → target curve. Identical code values in two configurations are **not** the same colour. The EXR files are byte-identical to the originals: no half-float conversion, no clipping, no recompression.",
 s_pv="Previews are not data", pv="`previews/` holds WebP renders for sRGB screens; they may be clipped and exist only for browsing. Measure on the EXR files, never on previews or screenshots.",
 s_ver="Verify your download", ver="Compare the SHA-256 of each ZIP with the table above or with `SHA256SUMS.txt` in the release. Inside each ZIP, `SHA256SUMS.txt` lists every EXR.",
 s_lim="Limits", lim=[
  "The charts are synthetic: not camera captures and not measured physical charts. ColorChecker (CC24) values are published nominal CIELAB averages adapted to D65 (physical lots differ by about 1–2 ΔE).",
  "They are not a calibration or certification of monitors, lenses or cameras. 02B (synthetic bust) and family 12 (lens and optics) are illustrations/simulations.",
  "Generator version: 1.0.0-proto. Its internal report records 32,364 automated checks with 0 failures; this publication did **not** rerun that validation. We verified file presence, sizes and SHA-256 against the catalogue, and that the 23 MASTER files exist. Visual approval of the layout by a person is still pending.",
  "08B contains controlled Gaussian noise on purpose (fixed seed). The quantised rows of 11A are quantised in the stored code domain, per configuration.",
  "The generator is not part of this release."],
 s_lic="License and attribution", lic="Charts, manifests and documentation: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) — use, modify and redistribute, including commercially, with attribution. The small helper scripts in `scripts/` are published separately under the MIT License (see `LICENSE-SCRIPTS`); CC BY is not used for software. Camera, format and colour-space names are trademarks of their owners and appear only as technical identifiers; formulas come from public specifications.",
 credit="Suggested credit: `GDC Test Charts 4K © 2026 Dumitru Cristinel Gordas — https://gordas.dev/gdc-test-charts-4k/ — CC BY 4.0`",
 s_repo="Repository contents", repo="`scripts/` inventory, packaging, verification, README/site generation · `previews/` optimized WebP previews · `docs/` downloads table and publication notes · `LICENSE` CC BY 4.0 legal code · `LICENSE-SCRIPTS` MIT. The EXR files live only in GitHub Releases, never in the Git history.",
 s_rep="Reproduce the checks", rep="`python3 scripts/inventory.py --hash --out report.json` (source reconciliation) · `python3 scripts/verify_archives.py --dir <folder with the ZIPs and packages.json> --catalog CATALOG.csv --extract <new empty folder>` (archive contents, SHA-256, extraction)."),
"ro": dict(
 name="README.ro.md", alt="[English](README.md) · [Español](README.es.md) · [Pagina web](%s)" % PAGE["ro"],
 h1="GDC Test Charts 4K", tag="Chart-uri de test gratuite și deschise pentru fluxuri de culoare: 575 de imagini EXR float32 3840×2160, în 23 de configurații colorimetrice și 12 familii de teste.",
 s_what="Ce este", what="O bibliotecă de chart-uri de test definite matematic, pentru verificarea IDT, ODT, DRT, LUT-urilor, pluginurilor OFX și transformărilor DCTL în DaVinci Resolve (sau în orice flux scene-referred). Aceleași 25 de chart-uri sunt redate separat în 23 de configurații de gamut și curbă, ca să testezi un instrument în spațiul în care lucrează de fapt.",
 s_dl="Descărcare", dl_intro="Nu e nevoie de cont, plată sau aplicație. **Biblioteca completă înseamnă 4 fișiere ZIP** (trei părți cu configurații diferite, plus arhiva de documentație și metadate). Nu se oferă un singur ZIP „tot”: datele au aproximativ 3,05 GB, iar un asset GitHub e limitat la 2 GiB. Fiecare ZIP are propriul folder principal, deci arhivele nu se suprapun.",
 dl_part="Biblioteca completă (descarcă toate cele trei părți, plus docs-metadata)", dl_cfg="Configurații individuale (opțional, aprox. 130 MB fiecare; repetă conținutul părților)",
 s_files="Ce conțin datele", files="Fiecare folder de configurație conține cele 25 de chart-uri (`GDC-TC-<ID>_<slug>__<configurație>__3840x2160.exr`) și un subfolder `MASTER/` cu fișierul lui de referință `GDC_STUDIO_MASTER_4K`. Arhiva `docs-metadata` conține manifestele per chart (ROI-uri, valori de referință, teste urmărite, limitări, proveniență, SHA-256), raportul de validare, `CATALOG.csv` și previzualizări sRGB.",
 s_fam="Familii", fam_cols=("ID", "Familie", "Ce testează"),
 s_cfg="Configurații", cfg_cols=("Folder = identificator de configurație", "Gamut", "Curbă"),
 s_use="Utilizare (DaVinci Resolve)", use=[
  "Alege configurația care corespunde spațiului în care lucrează instrumentul testat (de exemplu `dwg_davinci_intermediate` pentru un flux DaVinci Wide Gamut / Intermediate).",
  "Extrage ZIP-ul și importă fișierele EXR din folderul configurației în Media Pool.",
  "Declară exact spațiul de intrare: gamutul și curba din numele folderului, prin gestiunea culorii a proiectului (spațiul de intrare al clipului) sau printr-un nod Color Space Transform.",
  "Evită transformarea dublă: dacă proiectul convertește deja intrarea, nu adăuga o a doua conversie pentru același spațiu. Fișierele EXR nu poartă o curbă de transfer pe care aplicația să o ghicească.",
  "Măsoară pe pixeli reali, folosind ROI-urile (dreptunghiuri în pixeli) și valorile de referință din manifestul fiecărui chart (`docs-metadata`).",
  "Citește limitele de mai jos înainte de a trage concluzii."],
 s_ct="Contractul datelor", ct="OpenEXR, RGB, float32 (IEEE binary32), compresie ZIP fără pierderi, 3840×2160, scene-referred, full-range, fără tone mapping sau randare pentru afișaj, fără clipping. Valorile negative și cele peste 1 sunt intenționate (stres de gamut, headroom, sub-negru). Fiecare chart se compune o dată în ACES2065-1 (AP0, liniar) și se convertește AP0 → XYZ D65 (Bradford) → gamut țintă → curbă țintă. Aceleași valori de cod în două configurații **nu** sunt aceeași culoare. Fișierele EXR sunt identice octet cu octet cu originalele: fără conversie half-float, fără clipping, fără recomprimare.",
 s_pv="Previzualizările nu sunt date", pv="`previews/` conține randări WebP pentru ecrane sRGB; pot fi clipate și servesc doar la navigare. Măsoară pe fișierele EXR, niciodată pe previzualizări sau capturi de ecran.",
 s_ver="Verifică descărcarea", ver="Compară SHA-256 al fiecărui ZIP cu tabelul de mai sus sau cu `SHA256SUMS.txt` din release. În fiecare ZIP, `SHA256SUMS.txt` listează fiecare EXR.",
 s_lim="Limite", lim=[
  "Chart-urile sunt sintetice: nu sunt capturi de cameră și nici chart-uri fizice măsurate. Valorile ColorChecker (CC24) sunt medii CIELAB nominale publicate, adaptate la D65 (loturile fizice diferă cu aprox. 1–2 ΔE).",
  "Nu reprezintă calibrare sau certificare pentru monitoare, obiective ori camere. 02B (bust sintetic) și familia 12 (lentilă și optică) sunt ilustrații/simulări.",
  "Versiunea generatorului: 1.0.0-proto. Raportul lui intern consemnează 32 364 de verificări automate, 0 eșecuri; la această publicare validarea **nu** a fost rerulată. Am verificat prezența fișierelor, dimensiunile și SHA-256 față de catalog, plus existența celor 23 de fișiere MASTER. Aprobarea vizuală a layoutului de către un om este încă în așteptare.",
  "08B conține intenționat zgomot gaussian controlat (seed fix). Rândurile cuantizate din 11A sunt cuantizate în domeniul codului stocat, per configurație.",
  "Generatorul nu face parte din acest release."],
 s_lic="Licență și atribuire", lic="Chart-uri, manifeste și documentație: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) — utilizare, modificare și redistribuire, inclusiv comercială, cu atribuire. Scripturile ajutătoare din `scripts/` sunt publicate separat sub licența MIT (vezi `LICENSE-SCRIPTS`); CC BY nu se folosește pentru software. Numele de camere, formate și spații de culoare aparțin proprietarilor lor și apar doar ca identificatori tehnici; formulele provin din specificații publice.",
 credit="Atribuire recomandată: `GDC Test Charts 4K © 2026 Dumitru Cristinel Gordas — https://gordas.dev/gdc-test-charts-4k/ — CC BY 4.0`",
 s_repo="Conținutul depozitului", repo="`scripts/` inventar, împachetare, verificare, generare README/pagină · `previews/` previzualizări WebP optimizate · `docs/` tabel de descărcări și note de publicare · `LICENSE` textul juridic CC BY 4.0 · `LICENSE-SCRIPTS` MIT. Fișierele EXR există doar în GitHub Releases, niciodată în istoricul Git.",
 s_rep="Reproduce verificările", rep="`python3 scripts/inventory.py --hash --out report.json` (reconcilierea sursei) · `python3 scripts/verify_archives.py --dir <folder cu ZIP-urile și packages.json> --catalog CATALOG.csv --extract <folder nou, gol>` (conținut, SHA-256, extragere)."),
"es": dict(
 name="README.es.md", alt="[English](README.md) · [Română](README.ro.md) · [Página web](%s)" % PAGE["es"],
 h1="GDC Test Charts 4K", tag="Cartas de prueba gratuitas y abiertas para flujos de color: 575 imágenes EXR float32 de 3840×2160 en 23 configuraciones colorimétricas y 12 familias de pruebas.",
 s_what="Qué es", what="Una biblioteca de cartas de prueba definidas matemáticamente para comprobar IDT, ODT, DRT, LUT, plugins OFX y transformaciones DCTL en DaVinci Resolve (o en cualquier flujo scene-referred). Las mismas 25 cartas se generan por separado en 23 configuraciones de gamut y curva, para probar una herramienta en el espacio en el que realmente trabaja.",
 s_dl="Descarga", dl_intro="No hace falta cuenta, pago ni aplicación. **La biblioteca completa son 4 archivos ZIP** (tres partes con configuraciones distintas más el archivo de documentación y metadatos). No se ofrece un único ZIP «todo»: los datos rondan los 3,05 GB y un asset de GitHub está limitado a 2 GiB. Cada ZIP tiene su propia carpeta principal, así que los archivos no chocan.",
 dl_part="Biblioteca completa (descarga las tres partes y docs-metadata)", dl_cfg="Configuraciones individuales (opcional, unos 130 MB cada una; repiten contenido de las partes)",
 s_files="Qué contienen los datos", files="Cada carpeta de configuración contiene las 25 cartas (`GDC-TC-<ID>_<slug>__<configuración>__3840x2160.exr`) y una subcarpeta `MASTER/` con su archivo de referencia `GDC_STUDIO_MASTER_4K`. El archivo `docs-metadata` incluye los manifiestos por carta (ROI, valores de referencia, pruebas previstas, limitaciones, procedencia, SHA-256), el informe de validación, `CATALOG.csv` y vistas previas sRGB.",
 s_fam="Familias", fam_cols=("ID", "Familia", "Qué prueba"),
 s_cfg="Configuraciones", cfg_cols=("Carpeta = identificador de configuración", "Gamut", "Curva"),
 s_use="Uso (DaVinci Resolve)", use=[
  "Elige la configuración que corresponde al espacio en el que trabaja la herramienta que pruebas (por ejemplo `dwg_davinci_intermediate` para un flujo DaVinci Wide Gamut / Intermediate).",
  "Extrae el ZIP e importa al Media Pool los EXR de la carpeta de esa configuración.",
  "Declara exactamente el espacio de entrada: el gamut y la curva del nombre de la carpeta, mediante la gestión de color del proyecto (espacio de entrada del clip) o un nodo Color Space Transform.",
  "Evita la doble transformación: si el proyecto ya convierte la entrada, no añadas una segunda conversión para el mismo espacio. Los EXR no llevan una curva de transferencia que la aplicación pueda deducir.",
  "Mide sobre píxeles reales con los ROI (rectángulos en píxeles) y los valores de referencia del manifiesto de cada carta (`docs-metadata`).",
  "Lee los límites siguientes antes de sacar conclusiones."],
 s_ct="Contrato de datos", ct="OpenEXR, RGB, float32 (IEEE binary32), compresión ZIP sin pérdida, 3840×2160, scene-referred, full-range, sin tone mapping ni renderizado para pantalla, sin clipping. Los valores negativos y superiores a 1 son intencionados (estrés de gamut, headroom, sub-negro). Cada carta se compone una vez en ACES2065-1 (AP0, lineal) y se convierte AP0 → XYZ D65 (Bradford) → gamut de destino → curva de destino. Los mismos valores de código en dos configuraciones **no** son el mismo color. Los EXR son idénticos byte a byte a los originales: sin conversión a half-float, sin clipping, sin recompresión.",
 s_pv="Las vistas previas no son datos", pv="`previews/` contiene renders WebP para pantallas sRGB; pueden estar recortados y sirven solo para navegar. Mide sobre los EXR, nunca sobre vistas previas o capturas de pantalla.",
 s_ver="Verifica la descarga", ver="Compara el SHA-256 de cada ZIP con la tabla anterior o con `SHA256SUMS.txt` del release. Dentro de cada ZIP, `SHA256SUMS.txt` lista cada EXR.",
 s_lim="Límites", lim=[
  "Las cartas son sintéticas: no son capturas de cámara ni cartas físicas medidas. Los valores del ColorChecker (CC24) son medias CIELAB nominales publicadas, adaptadas a D65 (los lotes físicos difieren en torno a 1–2 ΔE).",
  "No son una calibración ni una certificación de monitores, objetivos o cámaras. 02B (busto sintético) y la familia 12 (lente y óptica) son ilustraciones/simulaciones.",
  "Versión del generador: 1.0.0-proto. Su informe interno registra 32 364 comprobaciones automáticas con 0 fallos; en esta publicación esa validación **no** se volvió a ejecutar. Verificamos presencia de archivos, tamaños y SHA-256 contra el catálogo, y la existencia de los 23 archivos MASTER. La aprobación visual de la maquetación por una persona sigue pendiente.",
  "08B contiene a propósito ruido gaussiano controlado (semilla fija). Las filas cuantizadas de 11A se cuantizan en el dominio del código almacenado, por configuración.",
  "El generador no forma parte de este release."],
 s_lic="Licencia y atribución", lic="Cartas, manifiestos y documentación: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) — uso, modificación y redistribución, también comercial, con atribución. Los scripts auxiliares de `scripts/` se publican aparte bajo la licencia MIT (ver `LICENSE-SCRIPTS`); CC BY no se usa para software. Los nombres de cámaras, formatos y espacios de color pertenecen a sus propietarios y aparecen solo como identificadores técnicos; las fórmulas proceden de especificaciones públicas.",
 credit="Atribución recomendada: `GDC Test Charts 4K © 2026 Dumitru Cristinel Gordas — https://gordas.dev/gdc-test-charts-4k/ — CC BY 4.0`",
 s_repo="Contenido del repositorio", repo="`scripts/` inventario, empaquetado, verificación, generación de README/página · `previews/` vistas previas WebP optimizadas · `docs/` tabla de descargas y notas de publicación · `LICENSE` texto legal CC BY 4.0 · `LICENSE-SCRIPTS` MIT. Los EXR solo existen en GitHub Releases, nunca en el historial de Git.",
 s_rep="Reproducir las comprobaciones", rep="`python3 scripts/inventory.py --hash --out report.json` (conciliación de la fuente) · `python3 scripts/verify_archives.py --dir <carpeta con los ZIP y packages.json> --catalog CATALOG.csv --extract <carpeta nueva y vacía>` (contenido, SHA-256, extracción)."),
}

def fam_table(i, t):
    s = f"| {t['fam_cols'][0]} | {t['fam_cols'][1]} | {t['fam_cols'][2]} |\n|---|---|---|\n"
    for f in sorted(FAM):
        s += f"| {f} | {FAM[f][0][i]} | {FAM[f][1][i]} |\n"
    return s
def cfg_table(i, t):
    s = f"| {t['cfg_cols'][0]} | {t['cfg_cols'][1]} | {t['cfg_cols'][2]} |\n|---|---|---|\n"
    return s + "".join(f"| `{c}` | {g} | {tr} |\n" for c, (g, tr) in sorted(meta.items()))

root = a.root; os.makedirs(os.path.join(root, "docs"), exist_ok=True)
for lang in LANGS:
    i = LANGS.index(lang); t = T[lang]; h = H[lang]
    md = f"# {t['h1']}\n\n{t['alt']}\n\n**{t['tag']}**\n\n## {t['s_what']}\n\n{t['what']}\n\n"
    md += f"## {t['s_dl']}\n\n{t['dl_intro']}\n\n**{t['dl_part']}**\n\n" + tbl(parts + [docs], h)
    md += f"\n{t['dl_cfg']}: " + ", ".join(f"[`{p['file'].split('-config-')[1][:-4]}`]({REL}{p['file']})" for p in cfgp) + f"\n\n[SHA256SUMS.txt]({REL}SHA256SUMS.txt) · [release {a.tag}](https://github.com/gordasgdc/gdc-test-charts-4k/releases/tag/{a.tag})\n\n"
    md += f"## {t['s_files']}\n\n{t['files']}\n\n## {t['s_fam']}\n\n" + fam_table(i, t) + f"\n## {t['s_cfg']}\n\n" + cfg_table(i, t)
    md += f"\n## {t['s_use']}\n\n" + "".join(f"{n}. {x}\n" for n, x in enumerate(t["use"], 1))
    md += f"\n## {t['s_ct']}\n\n{t['ct']}\n\n### {t['s_pv']}\n\n{t['pv']}\n\n![GDC-TC-01A](previews/GDC-TC-01A-640.webp)\n\n## {t['s_ver']}\n\n{t['ver']}\n\n```bash\nshasum -a 256 gdc-test-charts-4k-{V}-complete-part1of3.zip      # macOS / Linux\n```\n\n```powershell\nGet-FileHash -Algorithm SHA256 .\\gdc-test-charts-4k-{V}-complete-part1of3.zip   # Windows\n```\n\n"
    md += f"## {t['s_lim']}\n\n" + "".join(f"- {x}\n" for x in t["lim"])
    md += f"\n## {t['s_lic']}\n\n{t['lic']}\n\n{t['credit']}\n\n## {t['s_repo']}\n\n{t['repo']}\n\n### {t['s_rep']}\n\n{t['rep']}\n"
    open(os.path.join(root, t["name"]), "w").write(md)
open(os.path.join(root, "docs", "DOWNLOADS.md"), "w").write(f"# Downloads — {a.tag}\n\n" + tbl(parts + [docs] + cfgp, H["en"]))
print("ok")
