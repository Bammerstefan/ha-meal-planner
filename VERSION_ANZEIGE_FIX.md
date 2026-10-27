# Korrektur Versionsanzeige 1.0.1

Der Fehler beim Speichern neuer Familienmitglieder bleibt behoben.
Die JavaScript-Oberfläche zeigte irrtümlich weiterhin `1.0.0`, obwohl das Backend bereits `1.0.1` meldete.
Im korrigierten `www/panel.js` steht jetzt ebenfalls `1.0.1`.

Installation: `custom_components/meal_planner` in das Home-Assistant-Konfigurationsverzeichnis kopieren und bestehende Dateien überschreiben. Home Assistant neu starten, dann die Seite mit Strg+F5 neu laden. Gegebenenfalls Browser-Cache für die Seite löschen. Vorher Backup empfohlen. Bestehende gespeicherte Daten und Lizenzen werden von diesem Dateiaustausch nicht zurückgesetzt.
