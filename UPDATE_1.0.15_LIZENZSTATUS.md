# Testupdate v1.0.15 – Online-Lizenzstatus

- Prüft alle 6 Stunden ausschließlich zufällige Lizenz-IDs über HTTPS bei bamlabs.at.
- Bei bestätigtem Status `revoked` bleibt die Lizenz gesperrt, auch offline.
- Bei bestätigtem Status `active` bleiben PRO-Funktionen bei einem Internetausfall bis 14 Tage nach der letzten erfolgreichen Prüfung nutzbar.
- Historische Lizenzen ohne serverseitigen Status (`unknown`) bleiben aus Kompatibilitätsgründen offline gültig.
- Ein **nach** Installation von License Manager v0.3.0 durchgeführter Gerätewechsel entzieht dem alten Schlüssel bei der nächsten erfolgreichen Statusprüfung die Gültigkeit.
- Nicht für echte Kunden aktivieren, bevor alle Tests abgeschlossen sind. Vorher Backups erstellen.
- Datenschutz: Lizenz-ID wird an BamLabs gesendet, IP-Adresse fällt beim Webserver an; Datenschutzerklärung entsprechend prüfen.
