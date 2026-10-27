# Installation & erster Start · V1.0.0

1. Vollständiges Home-Assistant-Backup erstellen.
2. Repository `https://github.com/Bammerstefan/ha-meal-planner` in HACS als benutzerdefinierte **Integration** hinzufügen, falls es nicht bereits vorhanden ist.
3. Mein Speiseplan installieren, Home Assistant vollständig neu starten.
4. Einstellungen → Geräte & Dienste → Integration hinzufügen → **Mein Speiseplan**.
5. In der Seitenleiste Speiseplan öffnen. Bei alter Anzeige Browser hart neu laden (Strg+F5).
6. In **QR & Module** die Installationskennung kontrollieren. PRO nur bei gültiger Lizenz aktivieren.
7. Zum Test zunächst Rezept, Wochenplan und Einkaufsliste anlegen; Familienhandyansicht bei Bedarf mit normalem HA-Benutzer testen.

## Update von v0.9.26

Vorher Sicherung erstellen. Dateien aus dem v1.0.0-Paket ersetzen, GitHub-Release `v1.0.0` auf dem aktualisierten Commit erstellen, HACS-Version herunterladen, HA neu starten, Cache aktualisieren. **Nur das Label/Manifest hochzählen genügt nicht.** Alle Frontend- und Backend-Dateien müssen zusammenpassen.

## Gerätewechsel

1. Alte Lizenzinformationen und Datenexport sichern, zusätzlich volles HA-Backup.
2. Auf neuer Installation Speiseplan einrichten, Kennung notieren.
3. JSON-Datenimport mit Vorschau und Bestätigung durchführen.
4. Beim Anbieter neuen signierten PRO-Schlüssel für die **neue** Kennung anfordern.
5. Neue Lizenz aktivieren; alle Module und Familienzugänge testen.

Lizenzsignierschlüssel und Generator sind nicht Teil des öffentlich verteilten Pakets.
