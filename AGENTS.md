# Website von Teclai Consulting

Statische Website von Nicole Teclai. Die Inhalte liegen als JSON-Dateien im Repo. Du wirst meist von Nicole gebeten, ein Angebot anzulegen, zu ändern oder offline zu nehmen. Sie ist keine Entwicklerin: Antworte auf Deutsch, kurz und ohne Technikbegriffe.

## Was du ändern darfst

Für normale Aufträge nur diese Dateien:

- `angebote/<name>.json`: ein Angebot pro Datei
- `bilder/`: Bilder zu Angeboten (jpg, png, webp)
- `seite.json`: Texte der Startseite, Stichworte, Kontakt-Adresse, Impressum und Datenschutz

Nur diese Änderungen gehen automatisch live. Layout, Skripte und Workflows nur ändern, wenn ausdrücklich verlangt, und Nicole dann sagen, dass Benedikt das freigeben muss.

## Ablauf

1. Bei Änderungen zuerst die vorhandene Datei in `angebote/` suchen und nur die betroffenen Felder ändern.
2. `python3 tools/build.py --check` ausführen. Die Prüfung muss fehlerfrei sein, sonst den Fehler beheben.
3. Pull Request öffnen und Nicole in einem Satz sagen, was sich ändert. Nach dem Öffnen geht es automatisch live, normalerweise innerhalb von zwei Minuten.

## Regeln für Inhalte

- Nichts erfinden. Termine, Preise, Orte und Anmeldelinks nur übernehmen, wenn Nicole sie genannt hat. Fehlt etwas, das Feld weglassen und am Ende nachfragen.
- Texte von Nicole nicht umschreiben, außer sie bittet darum. Rechtschreibung darfst du korrigieren.
- Die Seite spricht junge Leute mit «du» an.
- Keine internen Notizen in die Texte schreiben. Alles in den Dateien ist öffentlich.
- Keine Passwörter, Zugangsdaten oder personenbezogenen Daten von Teilnehmenden ins Repo.
- Zum Offline-Nehmen `status` auf `entwurf` setzen und die Datei nicht löschen, außer Nicole verlangt das ausdrücklich.

## Aufbau eines Angebots

Dateiname: nur Kleinbuchstaben, Ziffern und Bindestriche, ohne Umlaute, zum Beispiel `angebote/crashkurs-word-excel-outlook.json`. Der Dateiname wird zum Link der Seite und sollte später nicht mehr geändert werden, weil Plakate und QR-Codes darauf zeigen können.

Pflichtfelder:

- `status`: `online` oder `entwurf`
- `titel`: höchstens 90 Zeichen
- `teaser`: ein bis zwei Sätze, höchstens 200 Zeichen
- `kategorie`: kurz, zum Beispiel `Computer & Office`. Vorhandene Kategorien wiederverwenden.
- `beschreibung`: Liste von Absätzen

Optionale Felder:

- `zeit`: zum Beispiel `2 Samstagvormittage, 9–13 Uhr`
- `termine`: Liste im Format `JJJJ-MM-TT`. Nach dem letzten Termin verschwindet das Angebot von der Startseite.
- `ort`, `preis`: kurzer Text
- `anmelde_link`: muss mit `https://` beginnen. Ohne Link öffnet der Knopf eine Mail an `kontakt_email` aus `seite.json`. Ist auch die nicht eingetragen, erscheint kein Knopf.
- `bild`: Dateiname aus `bilder/`, dazu `bild_text` mit einer kurzen Bildbeschreibung
- `inhalte`: Liste aus Einträgen mit `titel` und `text`, erscheint als «Das erwartet dich»
- `abschluss`: ein Absatz am Ende

Andere Felder sind nicht erlaubt. HTML wird nicht ausgeführt, nur reiner Text. `angebote/crashkurs-word-excel-outlook.json` ist ein vollständiges Beispiel.
