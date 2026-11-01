#!/usr/bin/env python3
"""Erzeugt das Teclai-Logo als SVG mit echten Pfaden aus Inter Tight 900. Braucht fonttools und brotli."""
import pathlib
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "marke"
BLAU, LIME, INK, WEISS = "#1048E6", "#D4FF3A", "#111114", "#FFFFFF"
SCHWER = TTFont(ROOT / "assets/fonts/inter-tight-900.woff2")
MITTEL = TTFont(ROOT / "assets/fonts/inter-tight-500.woff2")


def glyphen(font, text, groesse, x, y, sperrung=0.0):
    """Liefert SVG-Pfad und Endposition. y ist die Grundlinie, SVG-Achse zeigt nach unten."""
    menge, cmap, teile = font.getGlyphSet(), font.getBestCmap(), []
    s = groesse / font["head"].unitsPerEm
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(menge, ntos=lambda v: f"{v:.2f}")
        menge[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        teile.append(pen.getCommands())
        x += menge[name].width * s + sperrung * groesse
    return "".join(teile), x - sperrung * groesse


def funke(cx, cy, r):
    k = r * 0.13
    return (f"M{cx:.2f} {cy - r:.2f}C{cx + k:.2f} {cy - k:.2f} {cx + k:.2f} {cy - k:.2f} {cx + r:.2f} {cy:.2f}"
            f"C{cx + k:.2f} {cy + k:.2f} {cx + k:.2f} {cy + k:.2f} {cx:.2f} {cy + r:.2f}"
            f"C{cx - k:.2f} {cy + k:.2f} {cx - k:.2f} {cy + k:.2f} {cx - r:.2f} {cy:.2f}"
            f"C{cx - k:.2f} {cy - k:.2f} {cx - k:.2f} {cy - k:.2f} {cx:.2f} {cy - r:.2f}Z")


def logo(tecl, ai, unterzeile):
    g, base, spr, r = 200.0, 200.0, -0.022, 42.0
    d1, x = glyphen(SCHWER, "tecl", g, 0, base, spr)
    d2, ende_a = glyphen(SCHWER, "a", g, x + spr * g, base, spr)
    x_i = ende_a + spr * g
    d3, ende = glyphen(SCHWER, "\u0131", g, x_i, base)
    mitte_i = x_i + (ende - x_i) / 2
    teile = [f'<path fill="{tecl}" d="{d1}"/>', f'<path fill="{ai}" d="{d2}{d3}{funke(mitte_i, base - 162, r)}"/>']
    _, ende_u = glyphen(MITTEL, "consulting", 40.0, 0, 0, 0.012)
    d4, _ = glyphen(MITTEL, "consulting", 40.0, ende - ende_u, base + 62, 0.012)
    teile.append(f'<path fill="{unterzeile}" d="{d4}"/>')
    breite, hoehe = mitte_i + r + 4, base + 82
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -8 {breite + 4:.2f} {hoehe:.2f}">'
            f'<title>Teclai Consulting</title>{"".join(teile)}</svg>')


def icon():
    b, g = 512, 430.0
    s = g / SCHWER["head"].unitsPerEm
    t_breite = SCHWER.getGlyphSet()[SCHWER.getBestCmap()[ord("t")]].width * s
    d, _ = glyphen(SCHWER, "t", g, (b - t_breite) / 2 - 34, 430)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {b} {b}"><title>Teclai Consulting</title>'
            f'<rect width="{b}" height="{b}" rx="112" fill="{BLAU}"/><path fill="{WEISS}" d="{d}"/>'
            f'<path fill="{LIME}" d="{funke(388, 142, 88)}"/></svg>')


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    varianten = {
        "logo-auf-blau": (WEISS, LIME, WEISS),
        "logo-auf-weiss": (INK, BLAU, INK),
        "logo-auf-lime": (INK, BLAU, INK),
        "logo-schwarz": (INK, INK, INK),
        "logo-weiss": (WEISS, WEISS, WEISS),
    }
    for name, farben in varianten.items():
        (OUT / f"{name}.svg").write_text(logo(*farben))
    (OUT / "icon.svg").write_text(icon())
    print("ok", sorted(p.name for p in OUT.iterdir()))
