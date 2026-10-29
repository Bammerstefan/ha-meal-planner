# Update 1.0.7 – My Recipe Box Import

- Maximale RTK-Dateigröße von 5 MB auf 20 MB angehoben (Oberfläche, WebSocket-Endpunkt, Importer).
- Sicherheitsgrenze für entpackte Inhalte: 100 MB insgesamt; für einzelne Rezeptlisten 12 MB.
- Sonstige Funktionen aus v1.0.6 bleiben unverändert.

Achtung: Sehr große Dateiübertragungen können zusätzlich an der WebSocket-Nachrichtengröße von Home Assistant scheitern; falls 20 MB nicht übertragen werden können, ist eine in Blöcke aufgeteilte Upload-Lösung nötig.
