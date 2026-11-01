# vhs-unterland-angebote

Statische Angebote-Website. Inhalte liegen in `angebote/*.json` und `seite.json`, gebaut wird mit `tools/build.py` (nur Python-Standardbibliothek), gehostet auf GitHub Pages.

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

- `indexieren` in `seite.json` auf `true` setzen, damit Suchmaschinen die Seite aufnehmen.
- Eigene Domain einrichten, bevor QR-Codes in den Druck gehen.
- `assets/logo.svg` ist aus einem 365-px-PNG nachgezeichnet. Bei Bedarf durch die Originaldatei ersetzen.
- Das Foto `assets/hero.jpg` ist KI-generiert.

Schrift: Inter Tight, SIL Open Font License (`assets/fonts/LICENSE-Inter-Tight.txt`).
