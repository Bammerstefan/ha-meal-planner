# Mein Speiseplan v1.0.3 – Rezeptimport (Testversion)

- Rezeptbuch PRO: Schaltfläche „Rezepte importieren“.
- My Recipe Box: `.rtk`-Datei (ZIP mit `recipes_*.json`) importieren. Bilder bleiben vorerst Symbolbilder.
- Webseiten: HTTPS-Link; liest JSON-LD `schema.org/Recipe`, sofern vorhanden. Keine Weiterleitungen, lokale/IP-Adressen blockiert; externe Webseiten können weitere Einschränkungen haben.
- Vorschau und Dublettenprüfung nach Rezeptname; bereits vorhandene Rezepte werden nicht überschrieben.
- Nur Home-Assistant-Administratoren mit gültiger Rezeptbuch-PRO-Lizenz dürfen die Vorschau abrufen.
- Vor dem Update bitte ein Backup der Speiseplandaten anlegen.
- Home Assistant nach dem Einspielen neu starten, Browser bei Bedarf neu laden.
- Import von Bildern, mehrere Webseitenrezepte sowie Mengenaufbereitung sind noch nicht vollständig unterstützt.
- Auf echtem HA-System noch nicht Ende-zu-Ende getestet. Teste zuerst mit einigen Export-Rezepten.
