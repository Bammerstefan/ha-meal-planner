# Mein Speiseplan v1.0.10 – stabilerer Rezeptimport (TEST)

- RTK bis 80 MB: Übertragung in Blöcken; Vorschau wird in Seiten zu 10 Rezepten übertragen.
- Alle erkannten Rezepte werden in der Importvorschau gezeigt (bisher nur 100 sichtbar).
- Import verarbeitet 5 Rezepte pro Speicherdurchgang und zeigt einen Fortschrittsbalken.
- Bilder werden unabhängig von den Rezeptdaten als JPEG in `.storage/meal_planner_images` gespeichert.
- Gespeicherte Bilder werden nur über authentifizierte Admin-WebSocket-Kommandos geladen.
- Rezeptlisten verwenden Bildreferenzen, dadurch bleiben gespeicherte Rezeptdaten kleiner.
- Vorhandene Daten und PRO-Lizenzen werden nicht umgeschrieben.

## Installation

1. Vollständiges Home-Assistant-Backup anfertigen.
2. ZIP entpacken und `custom_components/meal_planner` nach `/config/custom_components/meal_planner` kopieren.
3. Home Assistant neu starten und Speiseplan im Browser neu laden.
4. Zuerst 2–3 Rezepte mit Bildern importieren und Speicherung prüfen. Danach große RTK-Datei testen.

## Grenzen und Hinweise

- Für bereits vorhandene, eingebettete Bilder findet noch keine automatische Migration statt; vorhandene Bilder bleiben erhalten.
- Die Bilddateien sind Teil einer Home-Assistant-Vollsicherung; ein reiner JSON-Export aus dem Speiseplan umfasst diese ausgelagerten Dateien noch nicht.
- Nach einem Importabbruch können bereits erfolgreich gespeicherte Teilgruppen vorhanden sein. Vor erneutem Start die Rezeptliste prüfen.
- Unbenutzte importierte Bilddateien werden noch nicht automatisch aufgeräumt.
- Die Verarbeitung großer Archive kann bei wenig RAM trotz kleinerer Nachrichten an Grenzen stoßen.
- Syntaxprüfung und synthetische Importtests ersetzen keinen End-to-End-Test mit einer echten 50-MB-RTK-Datei.
