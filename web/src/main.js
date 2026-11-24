import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ANNOTATIONS, GROUPS, TOUR, EQ, SCEN_NAMES } from './content.js';

// Fassung: index.html = Vollfassung (mit Erklärungen), index.html?aufgabe = Schülerfassung (ohne Lösungen)
const AUFGABE = new URLSearchParams(location.search).has('aufgabe');
document.body.classList.toggle('aufgabe', AUFGABE);

const $ = (id) => document.getElementById(id);
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const damp = (a, b, k, dt) => a + (b - a) * (1 - Math.exp(-k * dt));
const DEG = Math.PI / 180;

const TOUCH = matchMedia('(pointer: coarse)').matches;
const LOW = TOUCH || (navigator.hardwareConcurrency || 8) <= 4;

// ------------------------------------------------------------------ renderer / scene
const canvas = $('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: 'high-performance' });
const pixelRatio = Math.min(window.devicePixelRatio, LOW ? 1.5 : 2);
renderer.setPixelRatio(pixelRatio);
renderer.setSize(innerWidth, innerHeight, false);
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.0;

const BG = new THREE.Color('#060c18');
const scene = new THREE.Scene();
scene.background = BG;
scene.fog = new THREE.FogExp2(BG, 0.004);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.45;

const camera = new THREE.PerspectiveCamera(36, innerWidth / innerHeight, 0.2, 800);
camera.position.set(5, 20, 90);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.zoomToCursor = true;
controls.minDistance = 4;
controls.maxDistance = 110;
controls.screenSpacePanning = true;

scene.add(new THREE.HemisphereLight(0x9fc4ff, 0x120d10, 0.55));
const key = new THREE.DirectionalLight(0xfff0da, 2.2);
key.position.set(-25, 35, 30);
scene.add(key);
const rim = new THREE.DirectionalLight(0x6fb6ff, 1.4);
rim.position.set(30, 18, -40);
scene.add(rim);
const fill = new THREE.DirectionalLight(0xcfe2ff, 0.5);
fill.position.set(10, -20, 30);
scene.add(fill);

for (const l of scene.children) if (l.isLight) l.layers.enableAll();

(() => {
  const n = 1200, pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const r = THREE.MathUtils.randFloat(40, 130), th = Math.random() * Math.PI * 2, ph = Math.acos(THREE.MathUtils.randFloatSpread(2));
    pos.set([20 + r * Math.sin(ph) * Math.cos(th), r * Math.cos(ph) * 0.7, r * Math.sin(ph) * Math.sin(th)], i * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const m = new THREE.PointsMaterial({ size: 0.5, map: dotTexture('rgba(255,255,255,1)', 'rgba(255,255,255,0)'), color: 0x86b6e8, transparent: true, opacity: 0.32, depthWrite: false, blending: THREE.AdditiveBlending });
  const pts = new THREE.Points(g, m);
  pts.layers.enableAll();
  scene.add(pts);
})();

function dotTexture(inner, outer, size = 64) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const x = c.getContext('2d');
  const gr = x.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  gr.addColorStop(0, inner);
  gr.addColorStop(0.35, inner.replace(/[\d.]+\)$/, '.45)'));
  gr.addColorStop(1, outer);
  x.fillStyle = gr;
  x.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(c);
}

// ------------------------------------------------------------------ post-processing
const rt = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: LOW ? 2 : 4 });
const composer = new EffectComposer(renderer, rt);
composer.setPixelRatio(pixelRatio);
composer.setSize(innerWidth, innerHeight);
composer.addPass(new RenderPass(scene, camera));
let gtao = null;
if (!LOW) {
  gtao = new GTAOPass(scene, camera, innerWidth, innerHeight);
  gtao.updateGtaoMaterial({ radius: 0.4, distanceExponent: 1.4, thickness: 0.4, scale: 1.0, samples: 12 });
  gtao.blendIntensity = 0.6;
  composer.addPass(gtao);
}
const outline = new OutlinePass(new THREE.Vector2(innerWidth, innerHeight), scene, camera);
Object.assign(outline, { edgeStrength: 3.5, edgeGlow: 0.5, edgeThickness: 1.2, pulsePeriod: 0 });
outline.visibleEdgeColor.set('#ffb35c');
outline.hiddenEdgeColor.set('#3a2408');
composer.addPass(outline);
composer.addPass(new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.4, 0.5, 1.0));
composer.addPass(new OutputPass());

// ------------------------------------------------------------------ Zustand
const state = {
  playing: false, tourIdx: 0, tourT: 0, labels: true, arrows: false, eqs: false, so4: true, bubbles: true,
  world: 'versuch', selected: null, flight: null, zoomGoal: null, highlight: [], anode: false,
};
// Ablauf: scen = A/B/C, tau = Zeit im Ablauf, running, speed, loopPause
const proc = { scen: 'A', tau: 0, running: false, speed: 1, pause: 0, fast: false };
const nodes = {};
const meshes = [];
let meta = null;
const P = { A: [], B: [], C: [] };   // Teilchen je Ablauf

// ------------------------------------------------------------------ Laden
const loader = new GLTFLoader();
const metaP = fetch('models/meta.json').then((r) => r.json());
loader.load('models/verkupfern.glb', async (gltf) => {
  meta = await metaP;
  setup(gltf);
  $('loadBar').style.width = '100%';
  $('loader').classList.add('done');
}, (e) => {
  if (e.total) {
    const p = Math.round((e.loaded / e.total) * 100);
    $('loadBar').style.width = p + '%';
    $('loadPct').textContent = p + ' %';
  }
}, (err) => { $('loadPct').textContent = 'Fehler beim Laden: ' + err.message; });

// ------------------------------------------------------------------ Aufbau
const TRANSPARENT = { Glas: 0.12, Loesung: 0.55, TLoesung: 0.08, Blase: 0.6 };
let MAT = {};   // Materialien der Teilchen nach Zustand

function physical(src) {
  const name = src.name;
  const tr = TRANSPARENT[name];
  const m = new THREE.MeshPhysicalMaterial({
    name, color: src.color.clone(), roughness: Math.max(0.2, src.roughness ?? 0.5), metalness: src.metalness ?? 0,
    clearcoat: ['Cu2', 'Fe2', 'Elektron', 'Glas', 'CuAtom'].includes(name) ? 0.6 : 0.1, clearcoatRoughness: 0.3,
    emissive: src.emissive?.clone() ?? new THREE.Color(0), emissiveIntensity: src.emissiveIntensity ?? 1,
    transparent: tr != null, opacity: tr ?? 1, depthWrite: tr == null,
  });
  if (name === 'Glas') { m.side = THREE.DoubleSide; m.roughness = 0.05; }
  if (name === 'Loesung') { m.emissive.set('#123e6e'); m.emissiveIntensity = 1; }
  if (name === 'Pol' || name.startsWith('Pfeil')) m.emissiveIntensity = 0.15;
  return m;
}

// Zwei Welten auf getrennten Ebenen (Layer 0 = Versuch, 1 = Teilchenebene bei x = 40): die Kamera sieht immer nur eine
function layerOf(o) {
  const c = o.geometry.boundingSphere ? o.geometry.boundingSphere.center.clone().applyMatrix4(o.matrixWorld) : o.position;
  return c.x > 20 ? 1 : 0;
}
function register(o) {
  o.geometry.computeBoundingBox();
  o.geometry.computeBoundingSphere();
  o.updateMatrixWorld(true);
  o.layers.set(o.userData.layer ?? layerOf(o));
  o.children.forEach((c) => c.layers.set(o.layers.mask === 2 ? 1 : 0));
  o.userData = { ...o.userData, base: o.material.color?.clone(), baseEmissive: o.material.emissive?.clone(), ann: null };
  meshes.push(o);
}

function setup(gltf) {
  const root = gltf.scene;
  scene.add(root);
  root.traverse((o) => { if (o.name) nodes[o.name] = o; });
  root.traverse((o) => {
    if (!o.isMesh) return;
    o.material = physical(o.material);
    if (o.material.transparent) o.renderOrder = o.name === 'Glas' || o.name === 'Becherglas' ? 32 : 30;
    if (/^(V_|Z_|Inst_)/.test(o.name)) { o.visible = false; return; }
    register(o);
  });
  nodes.Loesung.renderOrder = 30;
  nodes.Becherglas.renderOrder = 31;
  nodes.T_Loesung.userData.noPick = true;

  for (const [name, def] of Object.entries(meta.instances)) {
    const p = nodes[def.proto];
    const im = new THREE.InstancedMesh(p.geometry, p.material.clone(), def.pos.length);
    const mtx = new THREE.Matrix4();
    def.pos.forEach((q, i) => im.setMatrixAt(i, mtx.makeTranslation(q[0], q[1], q[2])));
    im.instanceMatrix.needsUpdate = true;
    im.computeBoundingSphere();
    im.userData.layer = def.pos[0][0] > 20 ? 1 : 0;
    im.name = name;
    scene.add(im);
    nodes[name] = im;
    register(im);
  }

  // Teilchen-Materialien nach Zustand: 1 Cu, 2 Cu²⁺, 3 Fe, 4 Fe²⁺, 5 e⁻, 6 SO₄²⁻
  const proto = nodes.V_Atom.material;
  const mk = (hex, emis = 0) => { const m = proto.clone(); m.color.set(hex); m.emissive.set(hex); m.emissiveIntensity = emis; m.metalness = 0.2; return m; };
  MAT = { 1: mk(meta.colors.cu, 0.05), 2: mk(meta.colors.cu2, 0.18), 3: mk(meta.colors.fe), 4: mk(meta.colors.fe2, 0.1), 5: nodes.V_e.material, 6: nodes.V_SO4.material };
  MAT[1].metalness = 0.5;
  const SIGN = { 2: nodes.Z_2plus, 4: nodes.Z_2plus, 5: nodes.Z_minus, 6: nodes.Z_2minus };
  const NAME = { 1: 'P_Cu', 2: 'P_Cu2', 3: 'P_Fe', 4: 'P_Fe2', 5: 'P_e', 6: 'P_SO4' };
  for (const [sc, def] of Object.entries(meta.scenarios)) {
    def.tracks.forEach((tr, i) => {
      const geo = tr.kind === 'e' ? nodes.V_e.geometry : tr.kind === 'so4' ? nodes.V_SO4.geometry : nodes.V_Atom.geometry;
      const m = new THREE.Mesh(geo, MAT[tr.kind === 'e' ? 5 : tr.kind === 'so4' ? 6 : 2]);
      const signs = {};
      for (const [st, z] of Object.entries(SIGN)) {
        if (!tr.keys.some((k) => String(k[4]) === st)) continue;
        if (!signs[z.name]) {
          const s = new THREE.Mesh(z.geometry, z.material);
          s.visible = false;
          m.add(s);
          signs[z.name] = s;
        }
      }
      m.visible = false;
      m.name = `${sc}_${i}`;
      m.userData.layer = 1;
      Object.values(signs).forEach((s) => s.layers.set(1));
      scene.add(m);
      register(m);
      P[sc].push({ tr, m, signs, state: -1, kind: tr.kind });
    });
  }
  P.SIGN = SIGN;
  P.NAME = NAME;

  // Blasen am Nagel (nur Versuch, mit Strom)
  P.bubbles = [];
  for (let i = 0; i < 16; i++) {
    const b = new THREE.Mesh(nodes.V_Blase.geometry, nodes.V_Blase.material);
    b.scale.setScalar(0.8 + 0.6 * (i % 3) / 2);
    b.renderOrder = 33;
    b.layers.set(0);
    scene.add(b);
    P.bubbles.push(b);
  }

  for (const n of ['Pfeil_e_rot_A', 'Pfeil_e_gelb_A', 'Pfeil_Cu_A', 'Pfeil_e_gelb_C', 'Pfeil_e_rot_C', 'Pfeil_Cu_C']) nodes[n].userData.noPick = true;
  for (const a of ANNOTATIONS) a.list = meshesFor(a);
  for (const o of meshes) o.userData.ann = annotationForName(o.name);

  buildUI();
  computeHome();
  goToStep(0, { instant: true });
  camera.position.copy(state.flight.toPos).sub(state.flight.toTarget).multiplyScalar(1.8).add(state.flight.toTarget);
  state.flight.fromPos.copy(camera.position);
}

const matchName = (p, name) => (p.endsWith('_') ? name.startsWith(p) : name === p);
function annotationForName(name) {
  for (const a of ANNOTATIONS) for (const p of a.meshes) if (matchName(p, name)) return a;
  return null;
}
function meshesFor(a) { return meshes.filter((o) => a.meshes.some((p) => matchName(p, o.name))); }
const annById = (id) => ANNOTATIONS.find((a) => a.id === id);

// ------------------------------------------------------------------ Kamera
function computeHome() {
  const aspect = innerWidth / innerHeight;
  state.distScale = aspect >= 1.45 ? 1 : 1.45 / aspect;
}
function viewToPose(v) {
  const t = new THREE.Vector3().fromArray(v.t || [0, 0, 0]);
  const d = Math.min(v.d * state.distScale, controls.maxDistance * 0.95);
  const az = v.az * DEG, el = v.el * DEG;
  const p = new THREE.Vector3(Math.cos(el) * Math.sin(az), Math.sin(el), Math.cos(el) * Math.cos(az)).multiplyScalar(d).add(t);
  return { pos: p, target: t };
}
function flyTo(pos, target, dur = 1.6) {
  state.flight = { fromPos: camera.position.clone(), fromTarget: controls.target.clone(), toPos: pos.clone(), toTarget: target.clone(), t: 0, dur };
}
const HOME = { versuch: { az: -18, el: 14, d: 42, t: [4.6, 5.6, 0] }, teilchen: { az: 0, el: 6, d: 36, t: [40, 4.4, 0] } };
function resetView() {
  const v = TOUR[state.tourIdx].view;
  const p = viewToPose(worldOfView(v) === state.world ? v : HOME[state.world]);
  flyTo(p.pos, p.target);
}
const worldOfView = (v) => (v.t[0] > 20 ? 'teilchen' : 'versuch');
function focusOn(a) {
  const box = new THREE.Box3();
  for (const o of a.list) if (o.visible) box.expandByObject(o);
  if (box.isEmpty()) return;
  const c = box.getCenter(new THREE.Vector3());
  const r = box.getSize(new THREE.Vector3()).length() * 0.5;
  const dir = camera.position.clone().sub(controls.target).normalize();
  const dist = clamp((r / Math.sin((camera.fov * DEG) / 2)) * 1.1, 6, 50);
  flyTo(c.clone().addScaledVector(dir, dist), c, 1.2);
}
canvas.addEventListener('pointerdown', () => { state.flight = null; state.zoomGoal = null; });
canvas.addEventListener('wheel', () => { state.flight = null; state.zoomGoal = null; }, { passive: true });

function setWorld(w, fly = true) {
  state.world = w;
  camera.layers.set(w === 'teilchen' ? 1 : 0);
  ray.layers.set(w === 'teilchen' ? 1 : 0);
  $('worldBtn').textContent = w === 'versuch' ? 'Teilchen' : 'Versuch';
  $('worldBtn').title = w === 'versuch' ? 'Zur Teilchenebene wechseln (T)' : 'Zum Versuch wechseln (T)';
  if (fly) {
    const v = TOUR[state.tourIdx].view;
    const p = viewToPose(worldOfView(v) === w ? v : HOME[w]);
    flyTo(p.pos, p.target, 1.8);
  }
}

// ------------------------------------------------------------------ Ablauf
function setScenario(sc, from = 0) {
  proc.scen = sc;
  if (from != null) proc.tau = from;
  proc.pause = 0;
  document.querySelectorAll('[data-scen]').forEach((b) => b.classList.toggle('on', b.dataset.scen === sc));
  $('procName').textContent = SCEN_NAMES[sc];
  for (const s of ['A', 'B', 'C']) for (const p of P[s]) if (s !== sc) p.m.visible = false;
  // Sichtbarkeit je Ablauf
  const show = (names, on) => names.forEach((n) => { if (nodes[n]) nodes[n].visible = on; });
  const strom = sc !== 'B';
  show(['T_Draht_gelb', 'T_Draht_rot', 'T_Batterie', 'T_Batterie_Schrift'], strom);
  show(['T_Pol_A_minus', 'T_Pol_A_plus'], sc === 'A');
  show(['T_Pol_C_plus', 'T_Pol_C_minus'], sc === 'C');
  show(['T_Fe_voll'], sc === 'A');
  show(['T_Fe_rest'], sc !== 'A');
  show(['T_Cu_rest'], sc === 'A');
  show(['T_Cu_voll'], sc === 'C');
  for (const o of meshes) {
    if (/^Batterie(_|$)/.test(o.name) || /^Kabel_/.test(o.name)) o.visible = sc === 'A';
    else if (/^BatterieC/.test(o.name) || /^KabelC_/.test(o.name)) o.visible = sc === 'C';
    else if (/^(Stecker_|Klemme_Blech|Kupferblech_)/.test(o.name)) o.visible = strom;
  }
  updateArrows();
  updateRunButton();
}
function updateArrows() {
  const on = state.arrows && !AUFGABE;
  for (const n of ['Pfeil_e_rot_A', 'Pfeil_e_gelb_A', 'Pfeil_Cu_A']) nodes[n].visible = on && proc.scen === 'A';
  for (const n of ['Pfeil_e_gelb_C', 'Pfeil_e_rot_C', 'Pfeil_Cu_C']) nodes[n].visible = on && proc.scen === 'C';
}
function updateRunButton() {
  $('btnRun').textContent = proc.running ? '❚❚ Pause' : '▶ Start';
  $('btnRun').classList.toggle('on', proc.running);
  $('btnFast').classList.toggle('on', proc.fast);
}
function stopTour() {
  if (!state.playing) return;
  state.playing = false;
  $('play').classList.add('paused');
}

function stepProcess(dt) {
  const T = meta.scenarios[proc.scen].T;
  if (proc.pause > 0) {
    proc.pause -= dt;
    if (proc.pause <= 0) proc.tau = 0;
    return;
  }
  if (!proc.running) return;
  proc.tau += dt * proc.speed * (proc.fast ? 3 : 1);
  if (proc.tau >= T) { proc.tau = T; proc.pause = 2.0; }
}

function evalTrack(keys, t, out) {
  let lo = 0, hi = keys.length - 1;
  if (t <= keys[0][0]) { out.set(keys[0][1], keys[0][2], keys[0][3]); return keys[0][4]; }
  if (t >= keys[hi][0]) { out.set(keys[hi][1], keys[hi][2], keys[hi][3]); return keys[hi][4]; }
  while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (keys[mid][0] <= t) lo = mid; else hi = mid; }
  const a = keys[lo], b = keys[hi];
  const k = b[0] > a[0] ? (t - a[0]) / (b[0] - a[0]) : 0;
  out.set(a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k, a[3] + (b[3] - a[3]) * k);
  return a[4];
}

const counts = { cu2: 0, fe2: 0, dep: 0, dis: 0 };
const C_NAIL = new THREE.Color(), C_FE = new THREE.Color('#8a8d91'), C_CU = new THREE.Color('#b87333'), C_SPONGE = new THREE.Color('#5a3420');
const C_SOL = new THREE.Color('#2f86e0'), C_SOL_B = new THREE.Color('#5c9fd4'), C_SOL_C = new THREE.Color('#4f9cc8');
function updateParticles(time) {
  const sc = proc.scen, def = meta.scenarios[sc];
  const tau = proc.tau;
  for (const p of P[sc]) {
    const st = evalTrack(p.tr.keys, tau, p.m.position);
    const vis = st !== 0 && (st !== 6 || state.so4);
    p.m.visible = vis;
    if (st !== p.state) {
      p.state = st;
      if (MAT[st]) p.m.material = MAT[st];
      p.m.name = P.NAME[st] || p.m.name;
      p.m.userData.ann = annotationForName(p.m.name);
      const want = P.SIGN[st]?.name;
      for (const [n, s] of Object.entries(p.signs)) s.visible = n === want;
    }
    for (const s of Object.values(p.signs)) if (s.visible) s.quaternion.copy(camera.quaternion);
  }
  // Zähler
  const rows = def.counters;
  let r = rows[0];
  for (const row of rows) { if (row[0] <= tau + 1e-6) r = row; else break; }
  counts.cu2 = r[1]; counts.fe2 = r[2]; counts.dep = r[3]; counts.dis = r[4];

  // Versuch: Fortschritt des Nagels/Blechs/der Lösung
  const k = clamp(tau / def.T, 0, 1);
  const nm = nodes.Nagel_unten.material, sm = nodes.Loesung.material;
  if (sc === 'A') { nm.color.copy(C_FE).lerp(C_CU, k); sm.color.copy(C_SOL); }
  else if (sc === 'B') { nm.color.copy(C_FE).lerp(C_SPONGE, k); sm.color.copy(C_SOL).lerp(C_SOL_B, k); }
  else { nm.color.copy(C_FE).lerp(C_NAIL.set('#6d6a66'), k); sm.color.copy(C_SOL).lerp(C_SOL_C, k); }
  const nail = nodes.Nagel_unten, nx = meta.macro.nail[0];
  const sn = sc === 'C' ? 1 - 0.35 * k : 1;
  nail.scale.set(sn, 1, sn);
  nail.position.set(nx * (1 - sn), 0, 0);
  const sheet = nodes.Kupferblech_unten, sx = meta.macro.sheet[0];
  const ss = sc === 'A' ? 1 - 0.25 * k : sc === 'C' ? 1 + 0.6 * k : 1;
  sheet.scale.set(ss, 1, 1);
  sheet.position.set(sx * (1 - ss), 0, 0);
  // Gasbläschen
  const bOn = state.bubbles && sc === 'A' && proc.running && tau > 0.5;
  const liq = meta.macro.liquid;
  P.bubbles.forEach((b, i) => {
    const ph = (time * 0.45 + i / P.bubbles.length) % 1;
    const a = i * 2.4;
    b.visible = bOn && ph < 0.97;
    b.position.set(nx + 0.22 * Math.cos(a) + 0.05 * Math.sin(time * 3 + i), 1.2 + ph * (liq - 1.3), -0.22 * Math.sin(a));
  });
}

// ------------------------------------------------------------------ UI
const hotspots = [];
const tags = [];
function buildUI() {
  const list = $('partList');
  let n = 0;
  GROUPS.forEach(([label, ids]) => {
    list.insertAdjacentHTML('beforeend', `<li class="grp">${label}</li>`);
    for (const id of ids) {
      const a = annById(id);
      a.no = ++n;
      const li = document.createElement('li');
      li.innerHTML = `<button data-id="${a.id}"><span class="n">${String(a.no).padStart(2, '0')}</span><span class="dot" style="background:${a.color}"></span><span>${a.title}</span></button>`;
      li.firstChild.addEventListener('click', () => select(a.id, true));
      list.appendChild(li);
    }
  });
  $('partCount').textContent = `· ${n}`;
  $('indexToggle').addEventListener('click', () => {
    const c = $('index').classList.toggle('collapsed');
    $('indexToggle').setAttribute('aria-expanded', String(!c));
  });
  if (innerWidth < 1100 || innerHeight < 760) $('index').classList.add('collapsed');
  if (AUFGABE) $('eyebrow').textContent = 'Elektrochemie · Klasse 9 · Aufgabenfassung';

  const host = $('hotspots');
  for (const a of ANNOTATIONS) {
    const el = document.createElement('button');
    el.className = 'hs';
    el.style.setProperty('--c', a.color);
    el.setAttribute('aria-label', a.title);
    el.innerHTML = `<span class="ring">${a.no}</span><span class="lbl">${a.title}</span>`;
    el.addEventListener('click', (ev) => { ev.stopPropagation(); select(a.id); });
    host.appendChild(el);
    hotspots.push({ a, el, pos: new THREE.Vector3() });
  }

  const mkTag = (cls, html, get, show) => {
    const el = document.createElement('div');
    el.className = 'tag gone ' + cls;
    el.innerHTML = `<span>${html}</span>`;
    host.appendChild(el);
    const t = { el, get, show, span: el.firstChild };
    tags.push(t);
    return t;
  };
  const A = (k) => (v) => v.fromArray(meta.anchors[k]);
  const arrowsOn = () => state.arrows && !AUFGABE && state.world === 'teilchen';
  mkTag('e', 'e⁻', A('t_e_gelb'), () => arrowsOn() && proc.scen !== 'B');
  mkTag('e', 'e⁻', A('t_e_rot'), () => arrowsOn() && proc.scen !== 'B');
  mkTag('cu', 'Cu²⁺', A('t_cu_pfeil'), () => arrowsOn() && proc.scen !== 'B');
  const anode = (k, isBlech) => {
    const t = mkTag('big anode', 'Anode', (v) => v.fromArray(meta.anchors[k]).add(new THREE.Vector3(0, 1.0, 0)),
      () => state.anode && !AUFGABE && state.world === 'teilchen' && proc.scen === 'A');
    t.el.classList.toggle('anode', isBlech);
    t.el.classList.toggle('kathode', !isBlech);
    t.span.textContent = isBlech ? 'Anode · Oxidation' : 'Kathode · Reduktion';
  };
  anode('t_blech', true);
  anode('t_nagel', false);
  for (const side of ['links', 'rechts', 'mitte']) {
    const el = document.createElement('div');
    el.className = 'eqbox gone ' + side;
    el.innerHTML = '<div><small></small><strong></strong></div>';
    host.appendChild(el);
    const t = { el, get: A('eq_' + side), show: () => state.eqs && !AUFGABE && state.world === 'teilchen' && !!EQ[proc.scen][side], box: true };
    t.update = () => {
      const [k, f] = EQ[proc.scen][side];
      el.querySelector('small').textContent = k;
      el.querySelector('strong').textContent = f;
    };
    tags.push(t);
  }

  buildTimeline();
  $('play').addEventListener('click', togglePlay);
  $('scrub').addEventListener('input', () => {
    const v = +$('scrub').value / 1000;
    const i = Math.floor(v);
    if (i !== state.tourIdx) goToStep(i);
    state.tourT = (v - i) * TOUR[state.tourIdx].seconds;
  });
  $('phasePrev').addEventListener('click', () => step(-1));
  $('phaseNext').addEventListener('click', () => step(1));
  document.querySelectorAll('[data-scen]').forEach((b) => b.addEventListener('click', () => {
    stopTour();
    setScenario(b.dataset.scen, 0);
    proc.running = true;
    proc.speed = 1;
    updateRunButton();
  }));
  $('btnRun').addEventListener('click', () => {
    stopTour();
    if (proc.tau >= meta.scenarios[proc.scen].T) proc.tau = 0;
    proc.running = !proc.running;
    if (!proc.speed) proc.speed = 1;
    proc.pause = 0;
    updateRunButton();
  });
  $('btnReset').addEventListener('click', () => { proc.tau = 0; proc.pause = 0; });
  $('btnFast').addEventListener('click', () => { proc.fast = !proc.fast; updateRunButton(); });

  chip('worldBtn', () => setWorld(state.world === 'versuch' ? 'teilchen' : 'versuch'));
  chip('so4', () => { state.so4 = !state.so4; setChip('so4', state.so4); });
  chip('bubbles', () => { state.bubbles = !state.bubbles; setChip('bubbles', state.bubbles); });
  chip('arrows', () => setArrows(!state.arrows));
  chip('eqs', () => setEqs(!state.eqs));
  chip('labels', () => {
    state.labels = !state.labels;
    setChip('labels', state.labels);
    $('hotspots').classList.toggle('hide-labels', !state.labels);
  });
  $('reset').addEventListener('click', resetView);
  $('infoClose').addEventListener('click', () => select(null));
  $('infoFocus').addEventListener('click', () => state.selected && focusOn(state.selected));
  const cycle = (d) => {
    const order = [...ANNOTATIONS].sort((x, y) => x.no - y.no);
    const i = state.selected ? order.indexOf(state.selected) : -1;
    select(order[(i + d + order.length) % order.length].id, true);
  };
  $('infoPrev').addEventListener('click', () => cycle(-1));
  $('infoNext').addEventListener('click', () => cycle(1));

  const slider = $('zoomSlider');
  slider.addEventListener('input', () => { state.zoomGoal = sliderToDist(+slider.value); state.sliderActive = true; state.flight = null; });
  slider.addEventListener('change', () => { state.sliderActive = false; });
  $('zoomIn').addEventListener('click', () => { state.flight = null; state.zoomGoal = clamp(currentDist() / 1.5, controls.minDistance, controls.maxDistance); });
  $('zoomOut').addEventListener('click', () => { state.flight = null; state.zoomGoal = clamp(currentDist() * 1.5, controls.minDistance, controls.maxDistance); });

  addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
    if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
    if (e.key === 'Escape') select(null);
    if (e.key === 'ArrowRight') step(1);
    if (e.key === 'ArrowLeft') step(-1);
    if (e.key === 't' || e.key === 'T') $('worldBtn').click();
    if (!AUFGABE && (e.key === 'p' || e.key === 'P')) setArrows(!state.arrows);
    if (!AUFGABE && (e.key === 'g' || e.key === 'G')) setEqs(!state.eqs);
    if (e.key === '+' || e.key === '=') $('zoomIn').click();
    if (e.key === '-') $('zoomOut').click();
  });

  let down = null;
  canvas.addEventListener('pointerdown', (e) => { down = { x: e.clientX, y: e.clientY }; });
  canvas.addEventListener('pointerup', (e) => {
    if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6) return;
    const hit = pick(e.clientX, e.clientY);
    select(hit ? hit.id : null);
  });
  if (!TOUCH) {
    let raf = 0;
    canvas.addEventListener('pointermove', (e) => {
      if (raf || e.buttons) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const a = pick(e.clientX, e.clientY);
        const tip = $('hoverTip');
        tip.classList.toggle('on', !!a);
        canvas.style.cursor = a ? 'pointer' : '';
        if (a) {
          tip.textContent = a.title;
          tip.style.transform = `translate(${e.clientX + 14}px, ${e.clientY + 12}px)`;
        }
      });
    });
  }
}

function buildTimeline() {
  const ticks = $('ticks');
  ticks.innerHTML = '';
  TOUR.forEach((s, i) => {
    const x = (i / TOUR.length) * 100;
    ticks.insertAdjacentHTML('beforeend', `<i style="left:${x}%"></i><span style="left:${x + 50 / TOUR.length}%">${i + 1}</span>`);
  });
  $('phaseTrack').innerHTML = TOUR.map(() => '<i style="--w:1"><b></b></i>').join('');
  $('scrub').max = String(TOUR.length * 1000 - 1);
}

function chip(id, fn) { $(id).addEventListener('click', fn); }
function setChip(id, on) {
  $(id).classList.toggle('on', on);
  $(id).setAttribute('aria-pressed', String(on));
}
function setArrows(on) { state.arrows = on; setChip('arrows', on); updateArrows(); }
function setEqs(on) { state.eqs = on; setChip('eqs', on); }

const ray = new THREE.Raycaster();
const ndc = new THREE.Vector2();
function pickables() { return meshes.filter((o) => o.visible && o.userData.ann && !o.userData.noPick); }
function pick(x, y) {
  ndc.set((x / innerWidth) * 2 - 1, -(y / innerHeight) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const hits = ray.intersectObjects(pickables(), false);
  return hits.length ? hits[0].object.userData.ann : null;
}

function select(id, fly = false) {
  const a = id ? annById(id) : null;
  state.selected = a;
  document.querySelectorAll('#partList button').forEach((b) => b.classList.toggle('active', b.dataset.id === id));
  hotspots.forEach((h) => h.el.classList.toggle('active', h.a === a));
  outline.selectedObjects = a ? a.list.filter((o) => o.visible && !o.isInstancedMesh) : highlightObjects();
  if (a) outline.visibleEdgeColor.set(a.color);
  const info = $('info');
  if (!a) { info.classList.remove('open'); info.setAttribute('aria-hidden', 'true'); return; }
  info.style.setProperty('--c', a.color);
  $('infoKicker').textContent = a.kicker;
  $('infoTitle').textContent = a.title;
  $('infoText').textContent = AUFGABE ? a.aufgabe : a.text;
  const facts = AUFGABE ? (a.factsAufgabe || a.facts) : a.facts;
  $('infoFacts').innerHTML = (facts || []).map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
  info.classList.add('open');
  info.setAttribute('aria-hidden', 'false');
  if (a.world !== state.world) setWorld(a.world, !fly);
  if (fly) focusOn(a);
}
function highlightObjects() {
  return state.highlight.length && state.highlight.length < 4
    ? state.highlight.flatMap((h) => h.list.filter((o) => o.visible && !o.isInstancedMesh && !/^(A|B|C)_/.test(o.name)))
    : [];
}

// ------------------------------------------------------------------ Rundgang
function goToStep(i, { instant = false } = {}) {
  state.tourIdx = ((i % TOUR.length) + TOUR.length) % TOUR.length;
  state.tourT = 0;
  const s = TOUR[state.tourIdx];
  $('phaseNo').textContent = String(state.tourIdx + 1).padStart(2, '0');
  $('phaseStep').textContent = s.kicker;
  const h3 = $('phaseTitle');
  h3.textContent = s.title;
  h3.classList.remove('swap');
  void h3.offsetWidth;
  h3.classList.add('swap');
  $('phaseText').textContent = AUFGABE ? s.aufgabe : s.text;
  const host = $('reveal');
  host.replaceChildren();
  if (!AUFGABE && s.eq) {
    const box = document.createElement('div');
    box.className = 'rbox';
    for (const [k, f] of s.eq) {
      const row = document.createElement('div');
      row.className = 'rrow' + (/[→]/.test(f) ? ' f' : '');
      row.innerHTML = '<b></b><span></span>';
      row.children[0].textContent = k;
      row.children[1].textContent = f;
      box.append(row);
    }
    host.append(box);
  }
  const pr = s.proc;
  setScenario(pr.scen, pr.from != null ? pr.from : (proc.scen === pr.scen ? null : 0));
  proc.speed = pr.speed || 0;
  proc.running = pr.speed > 0;
  updateRunButton();
  state.anode = !!s.anode;
  // Vollfassung: Gleichungen und Pfeile in der Teilchenebene direkt zeigen
  if (!AUFGABE) { setEqs(worldOfView(s.view) === 'teilchen'); setArrows(worldOfView(s.view) === 'teilchen' && s.id !== 'anode'); }
  state.highlight = (s.highlight || []).map(annById);
  setWorld(worldOfView(s.view), false);
  select(null);
  outline.visibleEdgeColor.set(state.highlight[0]?.color || '#ffb84d');
  const p = viewToPose(s.view);
  if (instant) {
    state.flight = { fromPos: p.pos.clone(), fromTarget: p.target.clone(), toPos: p.pos, toTarget: p.target, t: 0, dur: 2.4 };
    controls.target.copy(p.target);
  } else flyTo(p.pos, p.target, 1.8);
}
function step(d) { goToStep(state.tourIdx + d); }
function togglePlay() {
  state.playing = !state.playing;
  $('play').classList.toggle('paused', !state.playing);
  $('play').setAttribute('aria-label', state.playing ? 'Pause' : 'Rundgang abspielen');
}

// ------------------------------------------------------------------ Zoom
const currentDist = () => camera.position.distanceTo(controls.target);
const sliderToDist = (v) => controls.minDistance * Math.pow(controls.maxDistance / controls.minDistance, 1 - v / 1000);
const distToSlider = (d) => 1000 * (1 - Math.log(d / controls.minDistance) / Math.log(controls.maxDistance / controls.minDistance));

// ------------------------------------------------------------------ Schleife
const clock = new THREE.Clock();
let frame = 0;
const _v = new THREE.Vector3(), _w = new THREE.Vector3();

function tick() {
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;
  frame++;
  if (meta) {
    const s = TOUR[state.tourIdx];
    if (state.playing) {
      state.tourT += dt;
      if (state.tourT >= s.seconds) goToStep(state.tourIdx + 1);
    }
    const prog = (state.tourIdx + Math.min(state.tourT / s.seconds, 1)) / TOUR.length;
    const scrub = $('scrub');
    if (document.activeElement !== scrub) scrub.value = String(Math.round(prog * TOUR.length * 1000));
    scrub.style.setProperty('--p', (prog * 100).toFixed(2) + '%');
    $('phaseTrack').querySelectorAll('b').forEach((b, i) => {
      b.style.width = (i < state.tourIdx ? 100 : i > state.tourIdx ? 0 : Math.min(state.tourT / s.seconds, 1) * 100) + '%';
    });
    stepProcess(dt);
    updateParticles(time);
    const pulseT = 0.5 + 0.5 * Math.sin(time * 3.2);
    for (const o of meshes) {
      const u = o.userData, m = o.material;
      if (!u.ann || !m.emissive || /^(A|B|C)_/.test(o.name) || o.name === 'Loesung') continue;
      if (state.highlight.includes(u.ann)) m.emissive.copy(m.color).multiplyScalar(0.05 + 0.1 * pulseT);
      else if (u.baseEmissive) m.emissive.copy(u.baseEmissive);
    }
    if (!state.selected) outline.selectedObjects = highlightObjects();
  }
  if (state.flight) {
    const f = state.flight;
    f.t += dt / f.dur;
    const k = easeInOut(Math.min(f.t, 1));
    camera.position.lerpVectors(f.fromPos, f.toPos, k);
    controls.target.lerpVectors(f.fromTarget, f.toTarget, k);
    if (f.t >= 1) state.flight = null;
  } else if (state.zoomGoal) {
    const d = currentDist();
    const nd = damp(d, state.zoomGoal, 8, dt);
    camera.position.sub(controls.target).setLength(nd).add(controls.target);
    if (Math.abs(nd - state.zoomGoal) < 0.01) state.zoomGoal = null;
  }
  controls.update();
  if (meta) {
    updateHotspots();
    updateTags();
    if (!state.sliderActive) $('zoomSlider').value = String(Math.round(distToSlider(currentDist())));
    if (frame % 6 === 0) updateReadout();
  }
  composer.render();
  requestAnimationFrame(tick);
}

function updateReadout() {
  const T = meta.scenarios[proc.scen].T;
  $('procBar').style.width = (100 * proc.tau / T).toFixed(1) + '%';
  $('cCu2').textContent = counts.cu2;
  $('cFe2').textContent = counts.fe2;
  $('cDep').textContent = counts.dep;
  $('cDis').textContent = counts.dis;
}

function anchorPos(a, out) {
  const k = a.anchor;
  if (k.startsWith('dyn:')) {
    const want = { 'dyn:cu2': 2, 'dyn:fe2': 4, 'dyn:so4': 6, 'dyn:e': 5 }[k];
    const p = P[proc.scen].find((q) => q.state === want && q.m.visible);
    if (!p) return null;
    return out.copy(p.m.position).add(_w.set(0, 0.45, 0));
  }
  return out.fromArray(meta.anchors[k]);
}

function project(pos) {
  _v.copy(pos).project(camera);
  if (_v.z > 1 || Math.abs(_v.x) > 1.1 || Math.abs(_v.y) > 1.1) return null;
  return [(_v.x * 0.5 + 0.5) * innerWidth, (-_v.y * 0.5 + 0.5) * innerHeight];
}

function updateHotspots() {
  for (const h of hotspots) {
    let gone = h.a.world !== state.world;
    if (!gone && state.highlight.length && !state.highlight.includes(h.a) && state.selected !== h.a) gone = true;
    if (!gone && h.a.id === 'fe2' && !counts.fe2) gone = true;
    if (!gone && h.a.id === 'so4' && !state.so4) gone = true;
    if (!gone && ['blech', 'batterie', 'kabel'].includes(h.a.id) && proc.scen === 'B') gone = true;
    const p = !gone && anchorPos(h.a, h.pos);
    const xy = p && project(h.pos);
    if (!xy) gone = true;
    h.el.classList.toggle('gone', gone);
    if (!gone) h.el.style.transform = `translate(${xy[0].toFixed(1)}px, ${xy[1].toFixed(1)}px)`;
  }
}

function updateTags() {
  for (const t of tags) {
    let show = t.show();
    if (show) {
      t.update?.();
      t.get(_w);
      const xy = project(_w);
      if (xy) t.el.style.transform = `translate(${xy[0].toFixed(1)}px, ${xy[1].toFixed(1)}px)`;
      else show = false;
    }
    t.el.classList.toggle('gone', !show);
  }
}

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight, false);
  composer.setSize(innerWidth, innerHeight);
  gtao?.setSize(innerWidth, innerHeight);
  computeHome();
});
document.addEventListener('gesturestart', (e) => e.preventDefault());
requestAnimationFrame(tick);
window.__kupfer = { state, proc, goToStep, setScenario, counts, nodes };

if ('serviceWorker' in navigator) {
  addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
