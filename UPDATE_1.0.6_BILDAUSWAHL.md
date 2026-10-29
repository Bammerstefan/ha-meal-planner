# v1.0.6 – Bildauswahl beim Webseiten-Rezeptimport (Test)

- Mehrere Bildkandidaten aus schema.org/Recipe, OpenGraph, Twitter-Bild-Metadaten und HTML-Bildern.
- Bis zu sechs erfolgreich heruntergeladene Bildvorschauen pro Rezept.
- Vorschau mit Bildwahl, „Kein Bild übernehmen“ und optionalem eigenen Dateiupload.
- Weißer Hintergrund bei transparenten Bildern, JPG-Konvertierung auf maximal 900 px.
- Vorhandener RTK-Import, Lizenzprüfung und Dialog-Schließen-Schaltflächen erhalten.
- Sicherheitslimits: HTTPS, öffentliche DNS-Adressen, keine Redirects, maximal 900 KB je externem Bild, maximal 12 Kandidaten-Anfragen.

## Installation
1. Backup der vorhandenen Speiseplan-Daten und Integration erstellen.
2. `custom_components/meal_planner` aus dem ZIP in die Home-Assistant-Konfiguration kopieren.
3. Home Assistant neu starten und Browser-Cache der Oberfläche aktualisieren.
4. Rezept aus dem Internet importieren und Bildvorschau/Bildauswahl testen.

## Einschränkungen
Bilder, die die Seite blockiert, die weitergeleitet werden oder die vom Bildformat her nicht erkannt werden, können fehlen. Eine Bildanalyse zur sicheren automatischen Erkennung des Rezeptmotivs ist nicht enthalten. Die Funktion wurde syntaktisch geprüft, nicht in einer laufenden Home-Assistant-Instanz getestet.
