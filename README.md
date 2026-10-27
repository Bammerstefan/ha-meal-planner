# Mein Speiseplan · Version 1.0.0

**Home Assistant HACS integration for meal planning / Home-Assistant-Speiseplan-Integration.**

> Release candidate for a first public version. The existing v0.9.26 installation has been tested by the project owner, including backup/restore, PRO activation and family mobile access. A full external security audit, independent new-installation test and legal review have **not** been conducted.

## Funktionen · Features

| Kostenlos / Free | Zusatzmodule / Optional PRO |
|---|---|
| Wochenplan für Mittag- und Abendessen / Weekly lunch and dinner planning | Einkaufsliste PRO / Shopping list PRO |
| Grundlegende Rezepte / Basic recipes | Rezeptbuch PRO / Recipe book PRO |
| Grundlegende Einkaufsliste / Basic shopping list | Familienmodul PRO / Family PRO |

Weitere Funktionen je nach freigeschaltetem Modul: Rezeptfotos, Kochmodus, Wochenvorlagen, Portionsberechnung, Vorräte und Resteküche, Bring!-Übertragung über Home-Assistant-To-do-Listen sowie mobile Familienwünsche. Some features depend on the corresponding PRO license and Home Assistant integration configuration.

Oberflächensprachen / UI languages: Deutsch, English, Italiano, Français, Español. User-created content is not translated automatically.

## Installation mit HACS / Install using HACS

1. Sicherung von Home Assistant erstellen / Back up Home Assistant.
2. HACS öffnen; falls das Repository nicht gelistet ist, als **benutzerdefiniertes Repository** vom Typ *Integration* hinzufügen: `https://github.com/Bammerstefan/ha-meal-planner`.
3. **Mein Speiseplan** installieren und Home Assistant neu starten / Install and restart Home Assistant.
4. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach „Mein Speiseplan“ suchen und die Integration einrichten / Add the integration under Settings → Devices & Services.
5. In der Home-Assistant-Seitenleiste **Speiseplan** öffnen; gegebenenfalls Strg+F5 / Open the sidebar panel; hard-refresh if necessary.

### Manuelle Installation / Manual installation

`custom_components/meal_planner/` in Home Assistants Konfigurationsordner nach `/config/custom_components/meal_planner/` kopieren, Home Assistant neu starten und die Integration einrichten. `hacs.json` wird nur für HACS benötigt.

## Lizenzaktivierung / PRO activation

Die kostenlosen Funktionen können ohne Lizenz genutzt werden. PRO erfordert einen gültigen, an die **Installationskennung** gebundenen signierten Lizenzschlüssel. Im Speiseplan **QR & Module** öffnen, Kennung ablesen und gekauften Lizenzschlüssel eingeben. Die Module heißen intern `shopping_pro`, `recipes_pro`, `family_pro`.

Free functionality needs no key. PRO activation uses a signed license tied to the installation ID. Copy the installation ID from QR & Modules and enter a valid license there.

**Gerätewechsel / Device migration:** JSON-Sicherungen enthalten nicht die Lizenzen. Bei neuer Installationskennung wird ein neuer, vom Anbieter ausgestellter Schlüssel benötigt. Die bisherige Offline-Lizenz lässt sich auf einer alten Installation ohne zentralen Lizenzserver nicht technisch widerrufen.

## Datensicherung / Backup & restore

Unter **QR & Module** eine JSON-Sicherung exportieren. Vor einem Import unbedingt auch ein vollständiges Home-Assistant-Backup anfertigen. Der JSON-Import ersetzt die Speiseplandaten; die integrierte Vorschau zeigt die betroffenen Daten. Installationskennung und Lizenzen sind getrennt gespeichert und **nicht** im JSON-Export enthalten.

Export a JSON backup from QR & Modules. Make a full Home Assistant backup before importing. Import **replaces** meal-planner data; licenses and the installation ID are stored separately.

## Familie / Family access

Drei Modi: gemeinsamer Zugang, persönlich zugeordnete HA-Benutzer, gemischter Betrieb. Normale Familienkonten benötigen einen Home-Assistant-Login; Administrationsrechte sollen nicht erforderlich sein. Benutzerrechte vor einem öffentlichen Betrieb an der eigenen HA-Installation prüfen. Shared, personal, and mixed account modes are supported.

## Einkaufsliste / Shopping list integration

Bring! kann über die Home-Assistant-Integration als To-do-Ziel eingebunden werden. Die separate offizielle Bring!-Integration muss dafür eingerichtet sein. Übertragungen bitte zunächst mit einer Testliste prüfen. Bring! is not bundled or endorsed by this project.

## Fehler und Support / Reporting issues

Fehlerbericht über <https://github.com/Bammerstefan/ha-meal-planner/issues> mit Home-Assistant-Version, Integrationsversion, genauen Schritten und ggf. anonymisierten Logs. **Keine Lizenzschlüssel, persönlichen Rezeptdaten oder Zugangsdaten veröffentlichen.**

## Hinweise zur Lizenzierung / Licensing notice

Der Quellcode ist derzeit unter der im Repository vorhandenen **MIT License** veröffentlicht. Diese Lizenz gestattet unter ihren Bedingungen ausdrücklich auch Nutzung, Änderung und Weiterverbreitung des Quellcodes. Die PRO-Freischaltung ist eine technische Zugangskontrolle, keine Einschränkung der MIT-Rechte am publizierten Code. Vor kommerziellem Vertrieb rechtliche Ausgestaltung, Endkundenbedingungen, Markenverwendung und Datenschutz prüfen; bestehende Rechte an bereits veröffentlichtem MIT-Code bleiben erhalten.

See `RELEASE_CHECKLIST.md` for remaining release gates. No private signing key or license generator should be committed to this repository.
