# teclai-consulting

Website von Teclai Consulting (Nicole Teclai). Statische Seite. Inhalte liegen in `angebote/*.json` und `seite.json`, gebaut wird mit `tools/build.py` (nur Python-Standardbibliothek), gehostet auf GitHub Pages.

- Für Nicole: [ANLEITUNG.md](ANLEITUNG.md)
- Für Agents: [AGENTS.md](AGENTS.md)

```bash
python3 tools/build.py --check
```

```bash
python3 tools/build.py
```

## Ablauf

Codex Cloud in ChatGPT öffnet einen Pull Request. `angebot-freigeben.yml` prüft ihn. Ändert er nur Inhalte und besteht die Prüfung, wird er automatisch gemergt und `veroeffentlichen.yml` gestartet. Andere Änderungen bleiben offen. Schlägt die Prüfung beim Veröffentlichen fehl, bleibt die alte Seite online.

## Vor dem offiziellen Start

- `kontakt_email`, `impressum` und `datenschutz` in `seite.json` eintragen.
- `indexieren` in `seite.json` auf `true` setzen, damit Suchmaschinen die Seite aufnehmen. Das geht erst mit ausgefülltem Impressum und Datenschutz.
- Eigene Domain einrichten, bevor QR-Codes in den Druck gehen.
- Das Foto `bilder/crashkurs.jpg` ist KI-generiert und zeigt nicht Nicole.

## Logo

`assets/marke/` enthält das Logo als SVG in allen Farbvarianten, dazu PNGs und das Icon. Erzeugt mit `tools/logo.py` (braucht fonttools und brotli). Die Marke nutzt Blau `#1048E6`, Limette `#D4FF3A` und Fast-Schwarz `#111114`.

Schrift: Inter Tight, SIL Open Font License (`assets/fonts/LICENSE-Inter-Tight.txt`).
