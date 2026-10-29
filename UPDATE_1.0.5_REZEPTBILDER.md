# Version 1.0.5 – Rezeptfotos aus dem Web

Beim Import einer Rezeptwebseite wird das erste Bild aus schema.org/Recipe ausgewählt. Ein HTTPS-Bild wird nur von öffentlich erreichbaren Hosts ohne Weiterleitungen geladen, auf eine maximale Größe begrenzt und als eingebettetes Bild in der Rezeptvorschau bereitgestellt. Im Browser wird das Bild auf max. 900 Pixel verkleinert und als JPEG im bestehenden Rezept-Datenformat gespeichert.

Falls die Seite kein Bild bereitstellt, es blockiert oder ein nicht unterstütztes Format liefert, bleibt das Standardsymbol aktiv. Bereits vorhandene Rezepte werden nicht überschrieben.

**Testversion:** Bitte vorher ein Backup erstellen. Installation: Inhalt der ZIP-Datei wie bisher in die HA-Integration übernehmen, Home Assistant neu starten und Browsercache aktualisieren.
