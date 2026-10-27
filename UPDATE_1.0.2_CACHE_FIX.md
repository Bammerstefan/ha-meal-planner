# Mein Speiseplan 1.0.2 – Oberflächen-Cache-Fix

Die Korrektur der Familienmitglied-Speicherung aus v1.0.1 bleibt enthalten.
Die Weboberfläche wird nun mit einer neuen Datei-URL `/meal_planner/panel-1.0.2.js?v=1.0.2` registriert, sodass ältere Caches für `/meal_planner/panel.js` nicht mehr verwendet werden.

## Installation
1. Backup in Home Assistant erstellen.
2. Den Ordner `custom_components/meal_planner` aus diesem ZIP in den Home-Assistant-Ordner `/config/custom_components/` kopieren; Dateien überschreiben. Nicht den äußeren `ha-meal-planner-main`-Ordner kopieren.
3. Home Assistant vollständig neu starten.
4. Die Speiseplan-Seite in einem neuen privaten Browserfenster öffnen. Sie sollte „Oberfläche v1.0.2“ anzeigen.
5. Falls nicht: Test-URL `http(s)://DEIN-HA-HOST:8123/meal_planner/panel-1.0.2.js?v=1.0.2` aufrufen. Falls 404, wurde die neue Integration nicht korrekt installiert/geladen. Falls die JS-Datei erscheint, prüfen, ob das Panel weiterhin die alte Modul-URL registriert.

Das Update verändert keine gespeicherten Daten oder Lizenzen. Ein echter HA-Livetest war hier nicht möglich.
