// Inhalte: Bauteile/Teilchen (Info-Panel), Rundgang-Stationen in zwei Fassungen.
//   Vollfassung (index.html): Erklärungen, Gleichungen, Pfeile – zur Besprechung.
//   Schülerfassung (index.html?aufgabe): gleiche Stationen und Nummern, nur Beobachtungsaufträge und Fragen (passend zu Blatt 1, A1–A3).
// Bezug: Infotext Abschnitt 4, 5, 6 und 9 (optional), Aufgabenblatt 1 „Verkupfern von Eisen“.

export const GROUPS = [
  ['Versuch', ['nagel', 'blech', 'loesung', 'batterie', 'kabel', 'klemmen']],
  ['Teilchen', ['fe', 'cu', 'cu2', 'fe2', 'so4', 'elektron']],
];

// text = Vollfassung, aufgabe = Schülerfassung (ohne Deutung)
export const ANNOTATIONS = [
  {
    id: 'nagel', title: 'Eisennagel', kicker: 'Gegenstand aus Eisen', color: '#9aa0a8', anchor: 'nagel', world: 'versuch',
    meshes: ['Nagel_'],
    text: 'Der Nagel ist mit dem Minuspol der Batterie verbunden (gelbes Kabel). An ihm scheidet sich Kupfer ab: Er wird kupferfarben.',
    aufgabe: 'Der Nagel wurde vorher geschmirgelt und mit Brennspiritus entfettet. Er hängt an einer Doppel-Krokodilklemme und ist über das gelbe Kabel mit der Batterie verbunden.',
    facts: [['Pol', 'Minuspol (−)'], ['Kabel', 'gelb'], ['vorher', 'geschmirgelt, entfettet']],
    factsAufgabe: [['Kabel', 'gelb'], ['vorher', 'geschmirgelt, entfettet']],
  },
  {
    id: 'blech', title: 'Kupferblech', kicker: 'Cu', color: '#c98a55', anchor: 'blech', world: 'versuch',
    meshes: ['Kupferblech_'],
    text: 'Das Kupferblech ist mit dem Pluspol verbunden (rotes Kabel). Es gibt Kupfer-Ionen an die Lösung ab und wird dabei langsam dünner.',
    aufgabe: 'Das Kupferblech wurde vorher geschmirgelt. Es ist über das rote Kabel mit der Batterie verbunden.',
    facts: [['Pol', 'Pluspol (+)'], ['Kabel', 'rot'], ['nach dem Versuch', 'kaum verändert, etwas dünner']],
    factsAufgabe: [['Kabel', 'rot']],
  },
  {
    id: 'loesung', title: 'Saure Kupfersulfat-Lösung', kicker: 'Cu²⁺ und SO₄²⁻', color: '#2f86e0', anchor: 'loesung', world: 'versuch',
    meshes: ['Loesung', 'Becherglas'],
    text: 'Die Lösung enthält Kupfer-Ionen (Cu²⁺) und Sulfat-Ionen (SO₄²⁻). Die Cu²⁺-Ionen färben sie blau. Sie ist schwefelsauer und ätzend.',
    aufgabe: 'Die Lösung enthält Kupfer-Ionen (Cu²⁺) und Sulfat-Ionen (SO₄²⁻). Die Cu²⁺-Ionen färben sie blau. Sie ist schwefelsauer und ätzend.',
    facts: [['Farbe', 'blau (durch Cu²⁺)'], ['Gefahr', 'ätzend'], ['Gefäß', 'Becherglas 150 ml']],
  },
  {
    id: 'batterie', title: '4,5-V-Flachbatterie', kicker: 'Stromquelle', color: '#c9b26a', anchor: 'batterie', world: 'versuch',
    meshes: ['Batterie', 'Batterie_', 'BatterieC', 'BatterieC_'],
    text: 'Die Batterie „pumpt“ Elektronen: Am Minuspol (langer Anschluss) drückt sie Elektronen in das gelbe Kabel, am Pluspol (kurzer Anschluss) zieht sie Elektronen aus dem roten Kabel ab.',
    aufgabe: 'Eine 4,5-V-Flachbatterie hat zwei Messing-Anschlüsse: Der kurze Anschluss ist der Pluspol, der lange der Minuspol.',
    facts: [['kurzer Anschluss', 'Pluspol (+)'], ['langer Anschluss', 'Minuspol (−)'], ['Spannung', '4,5 V']],
    factsAufgabe: [['kurzer Anschluss', 'Pluspol (+)'], ['langer Anschluss', 'Minuspol (−)']],
  },
  {
    id: 'kabel', title: 'Kabel', kicker: 'rot und gelb', color: '#e8c22c', anchor: 'kabel_gelb', world: 'versuch',
    meshes: ['Kabel_', 'KabelC_', 'Stecker_'],
    text: 'Rotes Kabel: Pluspol → Kupferblech. Gelbes Kabel: Minuspol → Eisennagel. Durch die Kabel fließen die Elektronen – durch die Lösung fließen keine Elektronen.',
    aufgabe: 'Rotes Kabel: Pluspol → Kupferblech. Gelbes Kabel: Minuspol → Eisennagel. So ist es auch auf der Aufbauhilfe zu sehen.',
    facts: [['rot', 'Pluspol → Kupferblech'], ['gelb', 'Minuspol → Eisennagel']],
  },
  {
    id: 'klemmen', title: 'Doppel-Krokodilklemmen', kicker: 'Halterung', color: '#b9bec5', anchor: 'klemme', world: 'versuch',
    meshes: ['Klemme_'],
    text: 'Zwei Doppel-Krokodilklemmen sitzen einander gegenüber am Rand des Becherglases. Die Klemme mit dem Kabelanschluss hängt innen und hält Nagel bzw. Blech. Die Klemmen sollen nicht in die Lösung tauchen.',
    aufgabe: 'Zwei Doppel-Krokodilklemmen sitzen einander gegenüber am Rand des Becherglases. Die Klemme mit dem Kabelanschluss hängt innen und hält Nagel bzw. Blech. Die Klemmen sollen nicht in die Lösung tauchen.',
    facts: [['Anzahl', '2'], ['Kabelanschluss', 'innen']],
  },
  // ---------------------------------------------------------------- Teilchen
  {
    id: 'fe', title: 'Eisen-Atome', kicker: 'Fe', color: '#8a8d91', anchor: 't_nagel', world: 'teilchen',
    meshes: ['T_Fe_', 'P_Fe'],
    text: 'Die Oberfläche des Nagels besteht aus Eisen-Atomen. Mit Strom bleiben sie erhalten, weil die Batterie die Elektronen liefert. Ohne Strom oder bei falscher Polung geben sie Elektronen ab und gehen als Fe²⁺ in Lösung.',
    aufgabe: 'Die Oberfläche des Nagels besteht aus Eisen-Atomen (Fe).',
    facts: [['Teilchen', 'Atom, ungeladen'], ['Redoxreihe', 'unedler als Kupfer']],
    factsAufgabe: [['Teilchen', 'Atom, ungeladen']],
  },
  {
    id: 'cu', title: 'Kupfer-Atome', kicker: 'Cu', color: '#b87333', anchor: 't_blech', world: 'teilchen',
    meshes: ['T_Cu_', 'P_Cu'],
    text: 'Das Kupferblech besteht aus Kupfer-Atomen. Abgeschiedene Kupfer-Atome bilden auf dem Nagel die Kupferschicht.',
    aufgabe: 'Das Kupferblech besteht aus Kupfer-Atomen (Cu). Kupfer-Atome sind ungeladen.',
    facts: [['Teilchen', 'Atom, ungeladen'], ['Farbe im Modell', 'kupfer']],
    factsAufgabe: [['Teilchen', 'Atom, ungeladen']],
  },
  {
    id: 'cu2', title: 'Kupfer-Ionen', kicker: 'Cu²⁺', color: '#38c6d9', anchor: 'dyn:cu2', world: 'teilchen',
    meshes: ['P_Cu2'],
    text: 'Kupfer(II)-Ionen sind zweifach positiv geladen und frei beweglich. Sie färben die Lösung blau. Am Minuspol nimmt ein Cu²⁺ zwei Elektronen auf und wird zu einem Kupfer-Atom.',
    aufgabe: 'Kupfer(II)-Ionen sind zweifach positiv geladen und in der Lösung frei beweglich. Sie färben die Lösung blau.',
    facts: [['Ladung', '2+'], ['Farbe der Lösung', 'blau'], ['im Modell', 'türkis, „2+“']],
    factsAufgabe: [['Ladung', '2+'], ['im Modell', 'türkis, „2+“']],
  },
  {
    id: 'fe2', title: 'Eisen-Ionen', kicker: 'Fe²⁺', color: '#a9d9a0', anchor: 'dyn:fe2', world: 'teilchen',
    meshes: ['P_Fe2'],
    text: 'Fe²⁺-Ionen entstehen nur ohne Strom oder bei falscher Polung: Dann gibt ein Eisen-Atom zwei Elektronen ab und geht in Lösung. Der Nagel wird angegriffen.',
    aufgabe: 'Eisen(II)-Ionen sind zweifach positiv geladen. Im Modell sind sie blassgrün.',
    facts: [['Ladung', '2+'], ['im Modell', 'blassgrün, „2+“']],
  },
  {
    id: 'so4', title: 'Sulfat-Ionen', kicker: 'SO₄²⁻', color: '#cfc9a6', anchor: 'dyn:so4', world: 'teilchen',
    meshes: ['P_SO4'],
    text: 'Sulfat-Ionen sind zweifach negativ geladen. Sie reagieren hier nicht, wandern aber langsam zum Pluspol. Mit „SO₄²⁻“ kannst du sie ausblenden.',
    aufgabe: 'Sulfat-Ionen sind zweifach negativ geladen. Mit „SO₄²⁻“ kannst du sie ausblenden.',
    facts: [['Ladung', '2−'], ['im Modell', 'gelblich-grau, „2−“']],
  },
  {
    id: 'elektron', title: 'Elektronen', kicker: 'e⁻', color: '#e0503f', anchor: 'dyn:e', world: 'teilchen',
    meshes: ['P_e'],
    text: 'Elektronen fließen nur durch Drähte und Batterie, nie durch die Lösung. Für ein Kupfer-Atom braucht es zwei Elektronen.',
    aufgabe: 'Elektronen sind negativ geladen. Beobachte, wo sie entstehen und wohin sie fließen.',
    facts: [['Ladung', '−1'], ['Weg', 'nur Drähte und Batterie'], ['pro Cu-Atom', '2 e⁻']],
    factsAufgabe: [['Ladung', '−1']],
  },
];

// Gleichungen an den Elektroden (nur Vollfassung)
export const EQ = {
  A: { links: ['Minuspol · Reduktion', 'Cu²⁺ + 2 e⁻ → Cu'], rechts: ['Pluspol · Oxidation', 'Cu → Cu²⁺ + 2 e⁻'] },
  B: { links: ['Oxidation · Nagel', 'Fe → Fe²⁺ + 2 e⁻'], rechts: ['Reduktion · an der Nageloberfläche', 'Cu²⁺ + 2 e⁻ → Cu'],
    mitte: ['Gesamt · freiwillig', 'Fe + Cu²⁺ → Fe²⁺ + Cu'] },
  C: { links: ['Nagel am Pluspol · Oxidation', 'Fe → Fe²⁺ + 2 e⁻'], rechts: ['Blech am Minuspol · Reduktion', 'Cu²⁺ + 2 e⁻ → Cu'] },
};

export const SCEN_NAMES = { A: 'Mit Strom', B: 'Ohne Strom', C: 'Falsch gepolt' };

// Ansichten (three.js): az 0 = frontal, el Höhe, d Abstand, t Zielpunkt. Teilchenebene liegt bei x = 40.
const V_VERSUCH = { az: -18, el: 14, d: 42, t: [4.6, 5.6, 0] };
const V_GLAS = { az: -8, el: 10, d: 20, t: [0, 4.4, 0] };
const V_TEIL = { az: 0, el: 6, d: 36, t: [40, 4.4, 0] };
const V_NAGEL = { az: 20, el: 8, d: 15, t: [33.5, 3.0, 0] };
const V_BLECH = { az: -20, el: 8, d: 15, t: [46.5, 3.0, 0] };

// proc: scen = Ablauf, from = Startzeit (null = weiterlaufen), speed = Zeitfaktor, loop = am Ende neu beginnen
export const TOUR = [
  {
    id: 'aufbau', kicker: 'Versuch', title: 'Der Versuchsaufbau', seconds: 14, view: V_VERSUCH, proc: { scen: 'A', from: 0, speed: 0 },
    highlight: ['nagel', 'blech', 'batterie', 'kabel'],
    text: 'Der Eisennagel hängt am Minuspol (langer Anschluss, gelbes Kabel), das Kupferblech am Pluspol (kurzer Anschluss, rotes Kabel) einer 4,5-V-Batterie. ' +
      'Beide tauchen in blaue, schwefelsaure Kupfersulfat-Lösung. Die Lösung wird erst zum Schluss eingefüllt.',
    aufgabe: 'Sieh dir den Aufbau an und vergleiche mit deinem Versuch. Welcher Gegenstand ist mit welchem Pol der Batterie verbunden? Woran erkennst du Plus- und Minuspol der Batterie?',
  },
  {
    id: 'zeitraffer', kicker: 'Versuch · Zeitraffer', title: 'Nach etwa 10 Minuten', seconds: 14, view: V_GLAS, proc: { scen: 'A', from: 0, speed: 2.6 },
    highlight: ['nagel', 'blech', 'loesung'],
    text: 'Der Nagel überzieht sich mit einer rotbraunen Kupferschicht. Das Kupferblech ist kaum verändert, die Lösung bleibt blau. ' +
      'Am Nagel steigen kleine Gasbläschen auf: Wasserstoff aus der sauren Lösung.',
    aufgabe: 'Beobachte im Zeitraffer den Nagel, das Kupferblech und die Lösung. Vergleiche mit deiner Beobachtungstabelle: Was verändert sich, was nicht?',
  },
  {
    id: 'teilchen', kicker: 'Teilchenebene', title: 'Ein Blick auf die Teilchen', seconds: 16, view: V_TEIL, proc: { scen: 'A', from: 0, speed: 1 },
    highlight: ['fe', 'cu', 'cu2'],
    text: 'Stark vergrößert: links die Oberfläche des Eisennagels, rechts das Kupferblech, dazwischen die Lösung mit Cu²⁺- und SO₄²⁻-Ionen. ' +
      'Oben verbinden die Drähte beide Elektroden mit der Batterie.',
    aufgabe: 'Links siehst du die Oberfläche des Nagels, rechts das Kupferblech. Welche Teilchen findest du in der Lösung? Tippe sie an.',
  },
  {
    id: 'nagel', kicker: 'Am Eisennagel', title: 'Minuspol: Reduktion', seconds: 18, view: V_NAGEL, proc: { scen: 'A', from: null, speed: 1 },
    highlight: ['cu2', 'elektron'],
    text: 'Die Batterie drückt Elektronen in den Nagel. Ein Cu²⁺-Ion an der Oberfläche nimmt zwei Elektronen auf und wird zu einem Kupfer-Atom, das haften bleibt. ' +
      'Cu²⁺ ist der Elektronenakzeptor. Die Kupferschicht wächst.',
    eq: [['Minuspol', 'Cu²⁺ + 2 e⁻ → Cu'], ['', 'Reduktion: Aufnahme von Elektronen']],
    aufgabe: 'Beobachte ein Cu²⁺-Ion, das zum Nagel kommt. Wie viele Elektronen kommen dort an, und was wird aus dem Ion? Ergänze in A1 die Spalte „am Eisengegenstand“.',
  },
  {
    id: 'blech', kicker: 'Am Kupferblech', title: 'Pluspol: Oxidation', seconds: 18, view: V_BLECH, proc: { scen: 'A', from: null, speed: 1 },
    highlight: ['cu', 'elektron'],
    text: 'Die Batterie zieht Elektronen aus dem Kupferblech ab. Ein Kupfer-Atom gibt zwei Elektronen ab und geht als Cu²⁺-Ion in Lösung. ' +
      'Kupfer ist der Elektronendonator. Das Blech wird dabei langsam dünner.',
    eq: [['Pluspol', 'Cu → Cu²⁺ + 2 e⁻'], ['', 'Oxidation: Abgabe von Elektronen']],
    aufgabe: 'Beobachte die Oberfläche des Kupferblechs. Was geschieht mit einem Kupfer-Atom, und wohin fließen die Elektronen? Ergänze in A1 die Spalte „am Kupferblech“.',
  },
  {
    id: 'blau', kicker: 'Die Lösung', title: 'Die Lösung bleibt blau', seconds: 18, view: V_TEIL, proc: { scen: 'A', from: null, speed: 1.4 },
    highlight: ['cu2'],
    text: 'Für jedes Cu²⁺-Ion, das am Nagel zu Kupfer wird, löst sich am Blech ein Kupfer-Atom als Cu²⁺. Die Zahl der Cu²⁺-Ionen bleibt gleich – die Lösung bleibt blau. ' +
      'Es scheidet sich genauso viel Kupfer ab, wie sich löst. Die Elektronen fließen nur durch Drähte und Batterie, nie durch die Lösung.',
    eq: [['Minuspol', 'Cu²⁺ + 2 e⁻ → Cu'], ['Pluspol', 'Cu → Cu²⁺ + 2 e⁻']],
    aufgabe: 'Zähle die Cu²⁺-Ionen in der Lösung (Anzeige oben rechts) über eine Weile. Was fällt dir auf? Nutze das für A2 b) und c).',
  },
  {
    id: 'ohne', kicker: 'Vergleich (A3)', title: 'Ohne Strom', seconds: 26, view: V_NAGEL, proc: { scen: 'B', from: 0, speed: 1 },
    highlight: ['fe', 'fe2', 'cu2'],
    text: 'Ohne Batterie: Eisen ist unedler als Kupfer und gibt seine Elektronen leichter ab. Ein Eisen-Atom gibt zwei Elektronen direkt an ein Cu²⁺-Ion ab. ' +
      'Kupfer setzt sich locker ab, das Fe²⁺-Ion geht in Lösung – der Nagel löst sich an. Die Reaktion läuft freiwillig ab. Die Zahl der Cu²⁺ sinkt.',
    eq: [['Oxidation', 'Fe → Fe²⁺ + 2 e⁻'], ['Reduktion', 'Cu²⁺ + 2 e⁻ → Cu'], ['Gesamt', 'Fe + Cu²⁺ → Fe²⁺ + Cu']],
    aufgabe: 'Jetzt hängt der Nagel ohne Batterie in der Lösung. Woher kommen die Elektronen für die Cu²⁺-Ionen? Welche neuen Teilchen entstehen? Vergleiche mit dem Verkupfern mit Strom (A3 c).',
  },
  {
    id: 'falsch', kicker: 'Falsch gepolt', title: 'Der Nagel löst sich auf', seconds: 26, view: V_TEIL, proc: { scen: 'C', from: 0, speed: 1 },
    highlight: ['fe', 'fe2'],
    text: 'Die Batterie ist falsch herum angeschlossen: Der Nagel hängt am Pluspol. Die Batterie zieht Elektronen aus dem Nagel ab – Eisen-Atome gehen als Fe²⁺ in Lösung. ' +
      'Am Kupferblech (jetzt Minuspol) scheidet sich Kupfer ab. Deshalb muss der Gegenstand an den Minuspol!',
    eq: [['Nagel (+)', 'Fe → Fe²⁺ + 2 e⁻ (Oxidation)'], ['Blech (−)', 'Cu²⁺ + 2 e⁻ → Cu (Reduktion)']],
    aufgabe: 'Hier ist die Batterie falsch herum angeschlossen. Beobachte den Nagel und das Kupferblech. Erkläre damit den Hinweis auf dem Aufgabenblatt: „…sonst löst er sich auf!“',
  },
  {
    id: 'anode', kicker: 'Vertiefung (optional)', title: 'Anode und Kathode', seconds: 18, view: V_TEIL, proc: { scen: 'A', from: 0, speed: 1 },
    highlight: [], anode: true,
    text: 'An – Ox – Ab: An der Anode findet die Oxidation statt, dort werden Elektronen abgegeben. Kat – Red – Auf: An der Kathode findet die Reduktion statt. ' +
      'Beim Verkupfern ist das Kupferblech (Pluspol) die Anode und der Nagel (Minuspol) die Kathode. Bei einer Elektrolyse ist die Anode also der Pluspol.',
    eq: [['Anode', 'Kupferblech (Pluspol): Cu → Cu²⁺ + 2 e⁻'], ['Kathode', 'Nagel (Minuspol): Cu²⁺ + 2 e⁻ → Cu']],
    aufgabe: 'Merkhilfe: An – Ox – Ab und Kat – Red – Auf. Welche Elektrode ist beim Verkupfern die Anode, welche die Kathode?',
  },
];
