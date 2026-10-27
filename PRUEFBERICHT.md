# Mein Speiseplan 0.9.26 – statischer Prüfbericht

## Erfolgreich geprüfte Punkte

- **licenses.py:** Python syntax OK
- **__init__.py:** Python syntax OK
- **config_flow.py:** Python syntax OK
- **license_public_key.py:** Python syntax OK
- **const.py:** Python syntax OK
- **family-mobile.js:** JS syntax OK
- **panel.js:** JS syntax OK
- **Versionsabgleich:** manifest/frontend/backend 0.9.26
- **Admin-Schutz:** admin decorators present; HA runtime still needed
- **Speicherreihenfolge:** disk write before memory replacement
- **Datum Familienwünsche:** HA local date used

## Noch manuell in Home Assistant zu prüfen

1. Frische HACS-Installation und Update von 0.9.25 mit vollständigem Neustart.
2. Aktivierung jeder einzelnen gültigen PRO-Lizenz sowie ungültige Tokens und Gerätewechsel.
3. Familienansicht mit Admin, zugeordnetem Normalnutzer und gemeinsamem Nutzer in allen drei Modi; Fremdwünsche dürfen bei persönlicher Zuordnung nicht editierbar sein.
4. JSON-Export und Importvorschau sowie Wiederherstellung nach tatsächlichem Neustart.
5. Bring!-Export an echtes todo-Entity, Doppelversand und fehlerhafte Ziel-Entity.
6. Sprachwechsel und mobile Familienansicht in allen fünf Sprachen.
7. Bewusst fehlerhafter Speicherversuch darf aktive Daten nicht ersetzen.

**Hinweis:** Syntax- und Quellcodeprüfungen ersetzen keine Ende-zu-Ende-Tests in Home Assistant.
