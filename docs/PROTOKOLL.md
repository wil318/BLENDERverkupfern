# Protokoll – 3D-Modell „Verkupfern von Eisen“

## 24.11.2026

### Auftrag und Grundlage
- Eine Blender-Animation zum Verkupfern von Eisen, passend zur Akku-Animation (`BLENDERlithiumakku`).
- Grundlagen:
  - `Chemie-Modul-Elektrochemie-neu/UEBERGABE-Blender-Verkupfern.md`
  - Infotext Abschnitt 6 (`Infotexte-…_korrigiert.odt`)
  - `Aufgabenblatt-1-Verkupfern_korrigiert.odt`, `Loesungsblatt-1-Verkupfern.odt`
  - `Aufbauhilfe-Verkupfern_korrigiert.odt` (Fotos)

### Entscheidungen im Planungsgespräch
| Frage | Entscheidung |
| --- | --- |
| Ausgabe | Web-App + Video, eigener Ordner `BLENDERverkupfern` |
| Fassungen | wie beim Gehirn über die Adresse: `index.html` = Vollfassung (zeigt alles direkt), `?aufgabe` = Schülerfassung ohne Lösungen |
| Ansichten | Versuch (Makro, nach den Fotos) + Teilchenebene |
| Umfang | mit Strom, ohne Strom (A3), falsch gepolt; SO₄²⁻ und Gasbläschen (beide abschaltbar) |
| Gegenstand | Eisennagel (wie Infotext Abb. 2) |
| Anode/Kathode | optionale letzte Station |
| Videos | zwei: Hauptvideo (mit Strom, 92 s) + Zusatzvideo (ohne Strom, falsch gepolt, 64 s) |
| Ionenwanderung | Cu²⁺ zittern ungeordnet und driften zum Nagel (wie Infotext); Hinweis s. u. |
| Gasbläschen | nur im Versuch, Hinweis „Wasserstoff aus der Säure“, keine H⁺-Teilchen und keine H₂-Gleichung |
| Batterie | undurchsichtig; Elektronen verschwinden am Pluspol und kommen am Minuspol heraus |
| Energie | keine Aussage über gespeicherte Energie |
| Ohne Strom / falsch gepolt | Zähler zeigt sinkende Cu²⁺-Zahl bzw. Fe²⁺, Lösungsfarbe ändert sich nur leicht |

### Umsetzung
- **Versuch:**
  - Becherglas mit Lösung bis 6,3 cm Höhe; Nagel links, Blech rechts (Minus links wie beim Akku und in Infotext-Abb. 2).
  - Rotes Kabel vom Kupferblech zum kurzen Anschluss (+), gelbes Kabel vom Nagel zum langen Anschluss (−), wie auf den Fotos.
  - Für „falsch gepolt“ eine zweite, umgedrehte Batterie: Dort führt das gelbe Kabel zum kurzen Anschluss.
- **Teilchenebene** bei x = 40: Fe-Gitter (Nageloberfläche), Cu-Gitter (Blech), Lösung, Drähte, Batterie.
- **Elektronen als Kette:** Im ersten Entwurf liefen die Elektronen einzeln 3 s über den Draht. Dadurch schwankte die Zahl der Cu²⁺ zwischen 6 und 7: Am Blech war das Atom schon gelöst, am Nagel aber noch nicht abgeschieden.
  - Jetzt stehen die Elektronen als Kette in den Drähten. Bei jedem Schritt rücken alle gleichzeitig um zwei Plätze weiter.
  - Im selben Moment wird am Blech ein Cu-Atom zu Cu²⁺ und am Nagel ein Cu²⁺ zu Cu.
  - Die Zahl der Cu²⁺ bleibt exakt 6. Das passt auch fachlich: Der Strom fließt im ganzen Kreis gleichzeitig.
- **Abläufe (Spuren in `meta.json`):**
  - A: 8 Schritte. Ein Ion, das sich am Blech gelöst hat, wandert danach durch die Lösung und scheidet sich später am Nagel ab.
  - B: 5 Schritte. Ein Fe-Atom gibt 2 e⁻ direkt an ein Cu²⁺ an der Oberfläche ab. Cu setzt sich locker und unregelmäßig ab, Fe²⁺ geht in Lösung.
  - C: 5 Schritte. Ein Fe-Atom wird zu Fe²⁺, die Elektronen laufen über das gelbe Kabel in die Batterie und am roten Kabel zum Blech, wo sich Cu abscheidet.
- **Zähler:**
  - A: Cu²⁺ bleibt bei 6, abgeschieden = abgelöst.
  - B und C: Cu²⁺ sinkt von 8 auf 3, Fe²⁺ steigt von 0 auf 5.
  - In der Schülerfassung sind nur Cu²⁺ und Fe²⁺ zu sehen, damit A2 c nicht vorweggenommen wird.
- **Export:** GLB 0,44 MB. Der lokale Blender hat kein Draco; die Gitter laufen deshalb als Instanzen.
- Im Viewer liegen die beiden Welten auf getrennten Kamera-Ebenen, man sieht also immer nur eine.
- **Videos:**
  - Die Szenen `blender/video1.blend` und `video2.blend` werden mit Eevee gerendert (1080p, 25 fps).
  - Texte, Gleichungen, Zähler und Beschriftungen setzt `video/video_overlay.py` ein.

### Hinweise für die Lehrkraft: bewusste Vereinfachungen
1. **Wanderung der Cu²⁺:** In der schwefelsauren Lösung tragen vor allem H⁺ und SO₄²⁻ den Strom. Die Cu²⁺-Ionen gelangen größtenteils durch Diffusion zum Nagel. Das Modell zeigt eine Drift zum Nagel, wie der Infotext („bewegen sich zum Minuspol“).
2. **Gasbläschen** zeigt das Modell nur im Versuch. H⁺ und die Gleichung 2 H⁺ + 2 e⁻ → H₂ fehlen, weil sie nicht im Infotext stehen.
3. **Batterie:** Im Inneren fließen keine Elektronen wie im Draht. Die Batterie ist deshalb undurchsichtig („pumpt“ die Elektronen).
4. **Maßstab:** Die Teilchenebene ist extrem vergrößert, das Gitter ist schematisch (kein echtes Kristallgitter). Wasser und Hydrathüllen fehlen.
5. **Zeitraffer:** Wenige Ionen und Schritte stehen für sehr viele. Im Versuch werden der Nagel kupferfarben und das Blech übertrieben dünner (bzw. bei falscher Polung dicker).
6. **Energie:** Das Modell sagt nichts über gespeicherte Energie. Mit Kupfer-Anode heben sich die Teilgleichungen auf (siehe Übergabe, Abschnitt 3).
7. **Ohne Strom:** Das Kupfer setzt sich im Modell locker und unregelmäßig ab („schwammig“). Die Löcher im Eisen sind klein dargestellt.

### Offen
- Stationstexte (Voll- und Schülerfassung) von der Lehrkraft prüfen lassen (`web/src/content.js`).
- iPad-Test; Veröffentlichung (GitHub Pages) und QR-Code für die Schülerfassung später.
