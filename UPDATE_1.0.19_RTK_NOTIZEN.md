# Mein Speiseplan v1.0.19 – Rezeptnotizen bei RTK-Import & Export

- Persönliche `notes` aus My Recipe Box `.rtk` werden unabhängig von `instructions` importiert.
- Im Rezepteditor gibt es jetzt ein eigenes Feld **Persönliche Notizen**.
- In der Rezeptansicht erscheinen Notizen separat von der Anleitung.
- RTK-Export gibt Notizen separat im `notes`-Feld aus (bereits vorhandener Exportpfad).
- Bereits gespeicherte Rezepte bleiben unverändert; früher falsch importierte Notizen lassen sich nicht nachträglich aus den ursprünglichen `.rtk`-Dateien rekonstruieren. Für diese Rezepte die Original-RTK erneut importieren (bestehende gleichnamige Rezepte werden übersprungen) oder Notizen manuell ergänzen.

## Installation

Vor dem Update Home-Assistant-Backup anlegen. Dateien nach `/config/custom_components/meal_planner/` kopieren, Home Assistant neu starten und Browser-Cache gegebenenfalls aktualisieren.

## Prüfung

1. Eine `.rtk` mit unterschiedlichen `instructions` und `notes` importieren.
2. Rezept öffnen: Anleitung und persönliche Notizen getrennt angezeigt.
3. Rezept bearbeiten und Notiz ändern.
4. Als `.rtk` exportieren, erneut in Testumgebung importieren: beide Felder müssen erhalten bleiben.

Dies ist eine Testversion; der Import in die originale My Recipe Box App wurde nicht in einer Live-Umgebung geprüft.
