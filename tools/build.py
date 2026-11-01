#!/usr/bin/env python3
"""Baut die Website aus seite.json und angebote/*.json. Nur Python-Standardbibliothek.

python3 tools/build.py          prüft alles und schreibt die Seite nach _site/
python3 tools/build.py --check  prüft nur und schreibt nichts

Bei einem Fehler endet das Skript mit Exit-Code 1. Dann wird nichts veröffentlicht,
die alte Seite bleibt online.
"""
import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
BILDER = {".jpg", ".jpeg", ".png", ".webp"}

SEITE_PFLICHT = {"name", "person", "titel", "headline", "intro", "indexieren"}
SEITE_OPTIONAL = {"stichworte", "kontakt_email", "impressum", "datenschutz"}
FUNKE = "M0-100C13-13 13-13 100 0C13 13 13 13 0 100C-13 13-13 13-100 0C-13-13-13-13 0-100Z"
ANGEBOT_PFLICHT = {"status", "titel", "teaser", "kategorie", "beschreibung"}
ANGEBOT_OPTIONAL = {"zeit", "termine", "ort", "preis", "anmelde_link", "bild", "bild_text", "inhalte", "abschluss"}


def e(text):
    return html.escape(str(text), quote=True)


def text_ok(wert, feld, fehler, ort, maximal=None):
    if not isinstance(wert, str) or not wert.strip():
        fehler.append(f'{ort}: Feld "{feld}" muss ein nicht leerer Text sein.')
    elif maximal and len(wert) > maximal:
        fehler.append(f'{ort}: Feld "{feld}" ist mit {len(wert)} Zeichen zu lang (höchstens {maximal}).')


def link_ok(wert, feld, fehler, ort):
    teile = urlparse(wert) if isinstance(wert, str) else None
    if not teile or teile.scheme != "https" or not teile.netloc:
        fehler.append(f'{ort}: Feld "{feld}" muss ein Link sein, der mit https:// beginnt.')


def pruefe_seite(fehler):
    ort = "seite.json"
    try:
        seite = json.loads((ROOT / ort).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        fehler.append(f"{ort}: nicht lesbar ({err}).")
        return {}
    for feld in sorted(set(seite) - SEITE_PFLICHT - SEITE_OPTIONAL):
        fehler.append(f'{ort}: unbekanntes Feld "{feld}".')
    for feld in sorted(SEITE_PFLICHT - set(seite)):
        fehler.append(f'{ort}: Feld "{feld}" fehlt.')
    for feld in ("name", "person", "titel", "headline", "intro"):
        if feld in seite:
            text_ok(seite[feld], feld, fehler, ort)
    for feld in ("stichworte", "impressum", "datenschutz"):
        wert = seite.get(feld, [])
        if not isinstance(wert, list) or not all(isinstance(x, str) and x.strip() for x in wert):
            fehler.append(f'{ort}: Feld "{feld}" muss eine Liste aus Texten sein.')
    if "kontakt_email" in seite and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(seite["kontakt_email"])):
        fehler.append(f'{ort}: Feld "kontakt_email" ist keine gültige E-Mail-Adresse.')
    if not isinstance(seite.get("indexieren"), bool):
        fehler.append(f'{ort}: Feld "indexieren" muss true oder false sein.')
    elif seite["indexieren"] and not (seite.get("impressum") and seite.get("datenschutz")):
        fehler.append(f'{ort}: "indexieren" darf erst true sein, wenn "impressum" und "datenschutz" ausgefüllt sind.')
    return seite


def pruefe_angebot(pfad, fehler):
    ort = f"angebote/{pfad.name}"
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pfad.stem):
        fehler.append(f"{ort}: Dateiname nur aus Kleinbuchstaben, Ziffern und Bindestrichen, ohne Umlaute.")
    try:
        a = json.loads(pfad.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        fehler.append(f"{ort}: kein gültiges JSON ({err}).")
        return None
    if not isinstance(a, dict):
        fehler.append(f"{ort}: muss ein JSON-Objekt sein.")
        return None
    for feld in sorted(set(a) - ANGEBOT_PFLICHT - ANGEBOT_OPTIONAL):
        fehler.append(f'{ort}: unbekanntes Feld "{feld}".')
    for feld in sorted(ANGEBOT_PFLICHT - set(a)):
        fehler.append(f'{ort}: Pflichtfeld "{feld}" fehlt.')

    if a.get("status") not in ("online", "entwurf"):
        fehler.append(f'{ort}: Feld "status" muss "online" oder "entwurf" sein.')
    if "titel" in a:
        text_ok(a["titel"], "titel", fehler, ort, 90)
    if "teaser" in a:
        text_ok(a["teaser"], "teaser", fehler, ort, 200)
    if "kategorie" in a:
        text_ok(a["kategorie"], "kategorie", fehler, ort, 40)
    for feld in ("zeit", "ort", "preis", "bild_text", "abschluss"):
        if feld in a:
            text_ok(a[feld], feld, fehler, ort)

    absaetze = a.get("beschreibung")
    if "beschreibung" in a and (not isinstance(absaetze, list) or not absaetze or
                                not all(isinstance(x, str) and x.strip() for x in absaetze)):
        fehler.append(f'{ort}: Feld "beschreibung" muss eine Liste mit mindestens einem Absatz sein.')

    tage = []
    termine = a.get("termine", [])
    if not isinstance(termine, list):
        fehler.append(f'{ort}: Feld "termine" muss eine Liste sein, zum Beispiel ["2027-02-13", "2027-02-20"].')
    else:
        for tag in termine:
            try:
                tage.append(dt.date.fromisoformat(tag))
            except (TypeError, ValueError):
                fehler.append(f'{ort}: Termin "{tag}" hat nicht das Format JJJJ-MM-TT.')
    a["_tage"] = sorted(tage)

    inhalte = a.get("inhalte", [])
    if not isinstance(inhalte, list) or not all(
            isinstance(i, dict) and set(i) == {"titel", "text"} and
            all(isinstance(v, str) and v.strip() for v in i.values()) for i in inhalte):
        fehler.append(f'{ort}: Feld "inhalte" muss eine Liste aus Einträgen mit "titel" und "text" sein.')

    if "anmelde_link" in a:
        link_ok(a["anmelde_link"], "anmelde_link", fehler, ort)
    if "bild" in a:
        name = a["bild"]
        ziel = ROOT / "bilder" / str(name)
        if not isinstance(name, str) or "/" in name or Path(name).suffix.lower() not in BILDER or not ziel.is_file():
            fehler.append(f'{ort}: Bild "{name}" liegt nicht im Ordner bilder/ (erlaubt: jpg, png, webp).')
        elif not a.get("bild_text"):
            fehler.append(f'{ort}: Zum Bild fehlt "bild_text" mit einer kurzen Bildbeschreibung.')
    a["_slug"] = pfad.stem
    return a


def wann(a):
    if a["_tage"]:
        return ", ".join(f"{WOCHENTAGE[t.weekday()]} {t:%d.%m.%Y}" for t in a["_tage"])
    return "Termine folgen"


def fuss_links(seite, wurzel):
    links = []
    if seite.get("kontakt_email"):
        links.append(f'<a href="mailto:{e(seite["kontakt_email"])}">Kontakt</a>')
    if seite.get("impressum"):
        links.append(f'<a href="{wurzel}impressum/index.html">Impressum</a>')
    if seite.get("datenschutz"):
        links.append(f'<a href="{wurzel}datenschutz/index.html">Datenschutz</a>')
    return f'<nav aria-label="Rechtliches">{"".join(links)}</nav>' if links else ""


def rahmen(seite, titel, beschreibung, tiefe, inhalt):
    wurzel = "../" * tiefe
    robots = "" if seite["indexieren"] else '<meta name="robots" content="noindex">\n'
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titel)}</title>
<meta name="description" content="{e(beschreibung)}">
{robots}<meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="{e(beschreibung)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#1048E6">
<link rel="icon" href="{wurzel}assets/marke/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{wurzel}assets/marke/icon-180.png">
<link rel="preload" href="{wurzel}assets/fonts/inter-tight-900.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{wurzel}assets/style.css">
</head>
<body>
<a class="sprung" href="#inhalt">Zum Inhalt springen</a>
{inhalt}
<footer class="fuss"><div class="innen fuss-inhalt">
<span>{e(seite["name"])} · {e(seite["person"])}</span>
{fuss_links(seite, wurzel)}
</div></footer>
<script>
document.querySelectorAll("[data-bis]").forEach(function (el) {{
  if (el.dataset.bis < new Date().toISOString().slice(0, 10)) el.remove();
}});
</script>
</body>
</html>
"""


def kopf(seite, wurzel):
    return f"""<div class="innen kopf">
<a class="logo" href="{wurzel}index.html"><img src="{wurzel}assets/marke/logo-auf-blau.svg" alt="{e(seite["name"])}, zur Startseite" width="534" height="282"></a>
</div>"""


def karte(a):
    bis = f' data-bis="{a["_tage"][-1].isoformat()}"' if a["_tage"] else ""
    bild = ""
    if a.get("bild"):
        bild = f'<img src="bilder/{e(a["bild"])}" alt="{e(a["bild_text"])}" loading="lazy">'
    info = a.get("zeit") or wann(a)
    return f"""<li{bis}><a class="karte" href="angebote/{e(a["_slug"])}/index.html">{bild}
<div class="karte-text">
<span class="kat">{e(a["kategorie"])}</span>
<h3>{e(a["titel"])}</h3>
<p>{e(a["teaser"])}</p>
<div class="karte-fuss"><span class="sticker">{e(info)}</span><span class="mehr">Ansehen →</span></div>
</div></a></li>"""


def hero_bild(seite):
    funken = "".join(f'<svg class="funke f{n}" viewBox="-100 -100 200 200"><path d="{FUNKE}"/></svg>' for n in (1, 2, 3))
    sticker = "".join(f'<span class="sticker s{n}">{e(w)}</span>' for n, w in enumerate(seite.get("stichworte", [])[:3], 1))
    return f'<div class="hero-bild" aria-hidden="true">{funken}{sticker}</div>'


def startseite(seite, angebote):
    if angebote:
        liste = f'<ul class="raster">{"".join(karte(a) for a in angebote)}</ul>'
    else:
        liste = '<p class="leer">Gerade ist hier nichts online. Schau bald wieder vorbei.</p>'
    inhalt = f"""<header class="hero auf-blau">
{kopf(seite, "")}
<div class="innen"><div class="hero-inhalt">
<h1>{e(seite["headline"])}</h1>
<p>{e(seite["intro"])}</p>
<a class="knopf" href="#inhalt">Zu den Angeboten</a>
</div></div>
{hero_bild(seite)}
</header>
<main id="inhalt" class="angebote"><div class="innen">
<h2>Aktuelle Angebote</h2>
{liste}
</div></main>"""
    return rahmen(seite, seite["titel"], seite["intro"], 0, inhalt)


def angebotsseite(seite, a):
    fakten = [("Wann", a["zeit"])] if a.get("zeit") else []
    fakten.append(("Termine", wann(a) if a["_tage"] else "Werden noch bekannt gegeben"))
    if a.get("ort"):
        fakten.append(("Wo", a["ort"]))
    if a.get("preis"):
        fakten.append(("Preis", a["preis"]))
    fakten_html = "".join(f'<div class="fakt"><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in fakten)
    bild = ""
    if a.get("bild"):
        bild = f'<img src="../../bilder/{e(a["bild"])}" alt="{e(a["bild_text"])}">'
    absaetze = "".join(f"<p>{e(p)}</p>" for p in a["beschreibung"])
    inhalte = ""
    if a.get("inhalte"):
        punkte = "".join(f'<li><strong>{e(i["titel"])}</strong>{e(i["text"])}</li>' for i in a["inhalte"])
        inhalte = f'<h2>Das erwartet dich</h2><ul class="inhalte">{punkte}</ul>'
    abschluss = f'<p class="abschluss">{e(a["abschluss"])}</p>' if a.get("abschluss") else ""
    if a.get("anmelde_link"):
        knopf = f'<a class="knopf" href="{e(a["anmelde_link"])}">Jetzt anmelden</a>'
    elif seite.get("kontakt_email"):
        betreff = quote(f'Anfrage: {a["titel"]}')
        knopf = f'<a class="knopf" href="mailto:{e(seite["kontakt_email"])}?subject={betreff}">Jetzt anfragen</a>'
    else:
        knopf = ""
    inhalt = f"""<header class="seitenkopf auf-blau">
{kopf(seite, "../../")}
<div class="innen seitenkopf-inhalt">
<a class="zurueck" href="../../index.html">← Alle Angebote</a><br>
<span class="sticker weiss kat">{e(a["kategorie"])}</span>
<h1>{e(a["titel"])}</h1>
<p>{e(a["teaser"])}</p>
{knopf}
</div>
</header>
<main id="inhalt"><div class="innen">
<dl class="fakten">{fakten_html}</dl>
<div class="text">
{bild}{absaetze}
{inhalte}
{abschluss}
{knopf}
</div>
</div></main>"""
    return rahmen(seite, f'{a["titel"]} · {seite["name"]}', a["teaser"], 2, inhalt)


def rechtsseite(seite, titel, zeilen):
    text = "".join(f"<p>{e(z)}</p>" for z in zeilen)
    inhalt = f"""<header class="seitenkopf auf-blau">
{kopf(seite, "../")}
<div class="innen seitenkopf-inhalt">
<a class="zurueck" href="../index.html">← Zur Startseite</a>
<h1>{e(titel)}</h1>
</div>
</header>
<main id="inhalt"><div class="innen"><div class="text">{text}</div></div></main>"""
    return rahmen(seite, f'{titel} · {seite["name"]}', f'{titel} von {seite["name"]}', 1, inhalt)


def main():
    nur_pruefen = "--check" in sys.argv[1:]
    fehler = []
    seite = pruefe_seite(fehler)
    alle = [pruefe_angebot(p, fehler) for p in sorted((ROOT / "angebote").glob("*.json"))]
    if fehler:
        print("Fehler gefunden, es wird nichts veröffentlicht:", file=sys.stderr)
        for zeile in fehler:
            print(f"- {zeile}", file=sys.stderr)
        return 1

    heute = dt.date.today()
    online = [a for a in alle if a["status"] == "online"]
    sichtbar = [a for a in online if not a["_tage"] or a["_tage"][-1] >= heute]
    sichtbar.sort(key=lambda a: (not a["_tage"], a["_tage"][0] if a["_tage"] else dt.date.max, a["titel"]))
    print(f"{len(alle)} Angebote geprüft, {len(sichtbar)} sichtbar auf der Startseite.")
    if nur_pruefen:
        return 0

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    bilder = [p for p in (ROOT / "bilder").iterdir() if p.suffix.lower() in BILDER]
    (OUT / "bilder").mkdir()
    for bild in bilder:
        shutil.copy2(bild, OUT / "bilder" / bild.name)
    (OUT / "index.html").write_text(startseite(seite, sichtbar), encoding="utf-8")
    for a in online:
        ziel = OUT / "angebote" / a["_slug"]
        ziel.mkdir(parents=True)
        (ziel / "index.html").write_text(angebotsseite(seite, a), encoding="utf-8")
    for feld, titel in (("impressum", "Impressum"), ("datenschutz", "Datenschutz")):
        if seite.get(feld):
            ziel = OUT / feld
            ziel.mkdir()
            (ziel / "index.html").write_text(rechtsseite(seite, titel, seite[feld]), encoding="utf-8")
    robots = "User-agent: *\nAllow: /\n" if seite["indexieren"] else "User-agent: *\nDisallow: /\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")
    print(f"Seite geschrieben nach {OUT.name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
