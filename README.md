# Verkupfern von Eisen – interaktives 3D-Modell

3D-Modell zum Versuch „Verkupfern von Eisen“ (Elektrochemie, Klasse 9). Es passt zum Infotext (Abschnitt 6) und zu Aufgabenblatt 1 des Unterrichtsmoduls (die liegen nicht im Repo) und ist im Stil der Modelle `BLENDERgehirn` und `BLENDERlithiumakku` gebaut.

**Online:** https://wil318.github.io/BLENDERverkupfern/ · Schülerfassung: https://wil318.github.io/BLENDERverkupfern/?aufgabe

- **Versuch:** 150-ml-Becherglas mit Kupfersulfat-Lösung, Eisennagel am Minuspol (gelbes Kabel), Kupferblech am Pluspol (rotes Kabel), Doppel-Krokodilklemmen, 4,5-V-Flachbatterie (kurzer Anschluss = Pluspol).
- **Teilchenebene:** Nageloberfläche (Fe), Kupferblech (Cu), Lösung mit Cu²⁺ und SO₄²⁻, Elektronen nur in Drähten und Batterie.
- **Drei Abläufe:** mit Strom, ohne Strom (A3) und falsch gepolt. Ein Zähler zeigt Cu²⁺ und Fe²⁺ in Lösung sowie abgeschiedenes und abgelöstes Kupfer.
- **Rundgang** mit 9 Stationen (die letzte ist optional: Anode und Kathode).
- **Zwei Fassungen** über die Adresse:
  - `index.html` ist die **Vollfassung** mit Erklärungen, Gleichungen und Pfeilen, zur Besprechung.
  - `index.html?aufgabe` ist die **Schülerfassung**. Sie hat dieselben Stationen, aber nur Beobachtungsaufträge und Fragen, ohne Gleichungen, Pfeile und Deutung. Sie eignet sich für den QR-Code auf dem Arbeitsblatt.
- **Videos:**
  - `video/verkupfern_1.mp4` (92 s): Verkupfern mit Strom
  - `video/verkupfern_2.mp4` (64 s): ohne Strom und falsch gepolt

## Lokal ansehen

```bash
python3 serve.py
```

Dann http://127.0.0.1:5175 öffnen (Schülerfassung: http://127.0.0.1:5175/?aufgabe). Three.js wird per Import-Map von jsDelivr geladen, beim ersten Aufruf ist also Internet nötig.

## Bauen

```bash
./build.sh            # Modell, Vorschaubilder, Icons (≈ 5 s)
./build.sh --video    # zusätzlich beide Videos (≈ 30–40 min)
```

`blender/build_verkupfern.py` (Blender 4.0.2) baut die Szene, berechnet die Teilchen-Spuren der drei Abläufe und exportiert sie nach `web/models/meta.json`. Viewer und Videos nutzen dieselben Spuren.
Gemeinsame Bausteine mit dem Akku-Modell stehen in `blender/helpers.py`. Die Texte der App stehen in `web/src/content.js`.
