# Mein Speiseplan 1.0.1 – Korrektur Familie PRO

## Behobener Fehler
Beim Anlegen von Familienmitgliedern konnte der Klick auf **Speichern** auf lokalen Home-Assistant-Adressen über HTTP scheinbar wirkungslos bleiben. Ursache: `crypto.randomUUID()` benötigt im Browser normalerweise einen sicheren Kontext (HTTPS oder localhost), ist bei `http://192.168...` nicht zuverlässig verfügbar. Die Erzeugung von Datensatz-IDs erfolgt jetzt über `crypto.getRandomValues()` (soweit vorhanden) und einen Fallback. Andere Aktionen mit dieser ID-Erzeugung (Wunsch, Rezept, Wochenvorlage) profitieren ebenfalls. Fehler beim Klick werden nun in der Benutzeroberfläche angezeigt.

## Installieren
1. Home Assistant: **Mein Speiseplan → Einstellungen → QR & Module → Daten sichern (JSON)** (optional, zusätzlich vollständiges Home-Assistant-Backup empfohlen).
2. ZIP entpacken. Den Ordner `custom_components/meal_planner` auf dein Home-Assistant-Konfigurationsverzeichnis unter `custom_components/meal_planner` kopieren und vorhandene Programmdateien **überschreiben**. Keine anderen Verzeichnisse wie `.storage` löschen.
3. **Home Assistant neu starten** (Einstellungen → System → Neu starten).
4. Die Seite im Browser hart neu laden (Strg+F5) bzw. auf der Oberfläche **Oberfläche neu laden**.
5. Unter **Familie PRO → Person hinzufügen** das Speichern testen.

Die Änderung ersetzt keine gespeicherten Rezepte, Familienmitglieder oder Lizenzinformationen. Keine neue Lizenz notwendig.

Dies ist ein Code-Fix mit JS-Syntaxprüfung und Python-Kompilierprüfung, kein Live-Test auf deiner Installation.
