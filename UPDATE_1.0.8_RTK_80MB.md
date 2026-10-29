# v1.0.8 – RTK-Import bis 80 MB (TEST)

- RTK-Dateien werden in Blöcken von 192 KiB über den Home-Assistant-WebSocket übertragen.
- Einzelnachrichten bleiben klein; serverseitige temporäre Dateien werden nach Abschluss oder Fehler gelöscht.
- Max. Archivgröße: 80 MB; max. entpackter Archivinhalt: 350 MB.
- My Recipe Box RTK-Fotos werden weiterhin nicht übernommen.
- Bitte vor Installation Backup erstellen und Testimport durchführen.
- Home Assistant neu starten und Browsercache aktualisieren.
