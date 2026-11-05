# Mein Speiseplan v1.0.18 – RTK-Export (Testversion)

## Neu
Im **Rezeptbuch PRO**: „📤 Als My Recipe Box (.rtk) exportieren“.
Exportiert Rezepte, Zutaten, Zubereitung, Portionszahl, Kategorien, Quell-URL und – soweit vorhanden – eigene Fotos in ein ZIP-basiertes `.rtk`-Archiv gemäß [öffentlicher RTK-Spezifikation](https://github.com/cmonapp/rtk-format).

- Rezeptdaten bleiben lokal in Home Assistant. Es erfolgt kein Upload an BamLabs.
- Bis 500 Rezepte, höchstens 100 MB Exportarchiv.
- Der Export ist für Benutzer mit Home-Assistant-Administratorrechten und aktiver Rezeptbuch-PRO-Lizenz verfügbar.
- Keine Änderung an Rezepten, Wochenplänen, Einkaufslisten oder Lizenzen.
- Keine automatisierte vollständige Sicherung: Wochenpläne und Einkaufslisten werden nicht exportiert; dafür die bestehende JSON-Sicherung nutzen.

## Installation
ZIP-Ordner `custom_components/meal_planner` über die bestehende Integration kopieren; Home Assistant vollständig neu starten, anschließend die Webseite/App neu laden.
HACS-Installationen erhalten dieses ZIP nicht automatisch als Release, bis v1.0.18 im GitHub-Repository veröffentlicht wird.

## Test
Erstelle ein Testrezept mit Zutaten, Anleitung, Kategorie und Foto, exportiere `.rtk`, prüfe danach den Import in der echten My-Recipe-Box-App. Die Spezifikation wurde berücksichtigt, ein App-End-to-End-Test ist noch offen.
