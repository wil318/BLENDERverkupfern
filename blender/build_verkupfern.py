"""
Verkupfern von Eisen – prozeduraler Blender-Aufbau, Export für den Three.js-Viewer und zwei Videos.

Zwei „Welten“ in einer Szene:
  * Versuch (Makro, 1 Einheit = 1 cm): 150-ml-Becherglas mit Kupfersulfat-Lösung, Eisennagel (links, Minuspol,
    gelbes Kabel) und Kupferblech (rechts, Pluspol, rotes Kabel), Doppel-Krokodilklemmen, 4,5-V-Flachbatterie.
  * Teilchenebene (stark vergrößert, Schema wie beim Akku) bei x = +40: Nageloberfläche (Fe), Kupferblech (Cu),
    Lösung mit Cu²⁺ und SO₄²⁻, Drähte und Batterie.

Drei Abläufe (Szenarien), als Teilchen-Spuren berechnet und in meta.json exportiert (Viewer und Video nutzen dieselben):
  A = mit Strom (richtig gepolt), B = ohne Strom (A3), C = falsch gepolt.

Koordinaten (Blender): +X rechts, +Y vom Betrachter weg, +Z oben. three.js: (x, z, -y).

Aufruf:
    blender -b --factory-startup --python blender/build_verkupfern.py -- [--no-render] [--video1 | --video2]
"""
import bpy, math, json, os, sys, time
import numpy as np
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
import helpers
importlib.reload(helpers)
from helpers import (srgb, make_mat, coll, make_object, uvsphere, box, rbox, cyl, cone, merge, instances,
                     text_object, catmull, resample, polyline, smooth01, MATS, COLL)

T0 = time.time()
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DO_RENDER = "--no-render" not in ARGS
VIDEO = 1 if "--video1" in ARGS else 2 if "--video2" in ARGS else 0
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLB_PATH = os.path.join(ROOT, "web/models/verkupfern.glb")
META_PATH = os.path.join(ROOT, "web/models/meta.json")
BLEND_PATH = os.path.join(ROOT, "blender/verkupfern.blend" if not VIDEO else f"blender/video{VIDEO}.blend")
RENDER_PATH = os.path.join(ROOT, "web/img/render.jpg")
ICON_DIR = os.path.join(ROOT, "web/icons")
for p in (GLB_PATH, BLEND_PATH, RENDER_PATH, ICON_DIR + "/x", os.path.join(ROOT, "video/x")):
    os.makedirs(os.path.dirname(p), exist_ok=True)


def log(*a):
    print(f"[kupfer {time.time() - T0:6.1f}s]", *a, flush=True)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
MATS.clear()
COLL.clear()

# --------------------------------------------------------------------------------------
# Farben (Übergabe Abschnitt 6, an das Akku-Modell angelehnt)
# --------------------------------------------------------------------------------------
C = {
    "elektron": "#d8432f",       # Akku: #c0392b, etwas heller
    "cu2": "#38c6d9",            # Cu²⁺ hellblau/türkis
    "cu": "#b87333",             # Kupfer
    "fe": "#8a8d91",             # Eisen
    "fe2": "#a9d9a0",            # Fe²⁺ blassgrün
    "so4": "#cfc9a6",            # Sulfat, gelblich-grau
    "loesung": "#2f86e0",        # Kupfersulfat-Lösung (Makro)
    "loesung_t": "#8cc4ee",      # Lösung (Teilchenebene), wie Akku-Elektrolyt
    "glas": "#dfeaf3",
    "kabel_rot": "#c8312a", "kabel_gelb": "#e8c22c",
    "batterie": "#1d1f22", "messing": "#c9b26a",
    "klemme": "#b9bec5", "buchse": "#26282b",
    "pol": "#c3cddb",
    "pfeil_e": "#e0503f", "pfeil_cu": "#38c6d9",
}

M = {
    "Glas": make_mat("Glas", C["glas"], rough=0.22, alpha=0.10, coat=0.0),
    "Loesung": make_mat("Loesung", C["loesung"], rough=0.7, alpha=0.26, emit=0.18),
    "Eisen": make_mat("Eisen", C["fe"], rough=0.35, metal=0.7),
    "NagelUnten": make_mat("NagelUnten", C["fe"], rough=0.35, metal=0.7),
    "Kupfer": make_mat("Kupfer", C["cu"], rough=0.3, metal=0.75),
    "BlechUnten": make_mat("BlechUnten", C["cu"], rough=0.3, metal=0.75),
    "Klemme": make_mat("Klemme", C["klemme"], rough=0.3, metal=0.8),
    "Buchse": make_mat("Buchse", C["buchse"], rough=0.5),
    "KabelRot": make_mat("KabelRot", C["kabel_rot"], rough=0.45, coat=0.3),
    "KabelGelb": make_mat("KabelGelb", C["kabel_gelb"], rough=0.45, coat=0.3),
    "Batterie": make_mat("Batterie", C["batterie"], rough=0.55),
    "Messing": make_mat("Messing", C["messing"], rough=0.3, metal=0.8),
    "Schrift": make_mat("Schrift", "#e7eef8", rough=0.5),
    "Pol": make_mat("Pol", C["pol"], rough=0.4, emit=0.3),
    "Blase": make_mat("Blase", "#eef6ff", rough=0.05, alpha=0.55, coat=1.0),
    # Teilchenebene
    "TLoesung": make_mat("TLoesung", C["loesung_t"], rough=0.15, alpha=0.07),
    "Rueckwand": make_mat("Rueckwand", "#16324f", rough=0.6),
    "Behaelter": make_mat("Behaelter", "#7a9cb5", rough=0.3),
    "FeAtom": make_mat("FeAtom", C["fe"], rough=0.35, metal=0.4),
    "CuAtom": make_mat("CuAtom", C["cu"], rough=0.3, metal=0.5, coat=0.3),
    "Cu2": make_mat("Cu2", C["cu2"], rough=0.3, coat=0.6, emit=0.15),
    "Fe2": make_mat("Fe2", C["fe2"], rough=0.3, coat=0.6, emit=0.1),
    "SO4": make_mat("SO4", C["so4"], rough=0.45),
    "Elektron": make_mat("Elektron", C["elektron"], rough=0.3, coat=0.5, emit=0.5),
    "Zeichen": make_mat("Zeichen", "#13202f", rough=0.5),
    "ZeichenHell": make_mat("ZeichenHell", "#ffffff", rough=0.5, emit=0.3),
    "PfeilE": make_mat("PfeilE", C["pfeil_e"], rough=0.35, emit=0.6),
    "PfeilCu": make_mat("PfeilCu", C["pfeil_cu"], rough=0.35, emit=0.6),
}
for _n in ("Loesung", "TLoesung"):
    M[_n].blend_method = "HASHED"   # Eevee: zuverlässige Sortierung im Glas (BLEND würde vom Glas überdeckt)


# --------------------------------------------------------------------------------------
# Zusätzliche Geometrie: Drehkörper, Schlauch entlang einer Kurve
# --------------------------------------------------------------------------------------
def lathe(profile, seg=64, center=(0, 0, 0)):
    """profile: Liste (r, z) von außen unten nach …; ergibt geschlossenen Ring-Drehkörper."""
    V, F = [], []
    n = len(profile)
    for k in range(seg):
        a = 2 * math.pi * k / seg
        for r, z in profile:
            V.append((center[0] + r * math.cos(a), center[1] + r * math.sin(a), center[2] + z))
    for k in range(seg):
        k2 = (k + 1) % seg
        for i in range(n - 1):
            F.append((k * n + i, k2 * n + i, k2 * n + i + 1, k * n + i + 1))
    return np.array(V, float), F


def tube(points, r, seg=14):
    P = np.asarray(points, float)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    ref = np.array([0, 0, 1.0]) if abs(T[0][2]) < 0.9 else np.array([1.0, 0, 0])
    N = np.cross(T[0], ref); N /= np.linalg.norm(N)
    V, F = [], []
    for i, (p, t) in enumerate(zip(P, T)):
        N = N - np.dot(N, t) * t
        N /= np.linalg.norm(N)
        B = np.cross(t, N)
        for k in range(seg):
            a = 2 * math.pi * k / seg
            V.append(p + r * (math.cos(a) * N + math.sin(a) * B))
    for i in range(len(P) - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            F.append((i * seg + k, i * seg + k2, (i + 1) * seg + k2, (i + 1) * seg + k))
    return np.array(V), F


# ======================================================================================
# 1) VERSUCH (Makro)
# ======================================================================================
NAIL_X, SHEET_X = -1.5, 1.6
LIQ = 6.3                     # Füllhöhe
BEAKER_R, BEAKER_H = 3.1, 9.0
BAT = dict(x=10.5, y=1.5, w=6.2, d=2.2, h=6.5)
TAB_MINUS = (BAT["x"] - 1.9, BAT["y"], BAT["h"])   # langer Anschluss = Minuspol (links)
TAB_PLUS = (BAT["x"] + 1.9, BAT["y"], BAT["h"])    # kurzer Anschluss = Pluspol (rechts)

make_object("Becherglas", *lathe([(BEAKER_R - 0.12, 0.3), (BEAKER_R - 0.12, BEAKER_H), (BEAKER_R + 0.06, BEAKER_H),
                                  (BEAKER_R, BEAKER_H - 0.05), (BEAKER_R, 0.05), (BEAKER_R - 0.05, 0.0), (0.0, 0.0)][::-1]),
            M["Glas"], "Versuch")
make_object("Loesung", *lathe([(0, 0.3), (BEAKER_R - 0.13, 0.3), (BEAKER_R - 0.13, LIQ), (0, LIQ)], 64), M["Loesung"], "Versuch")

# Eisennagel: unterer Teil (in der Lösung, wird kupferfarben) und oberer Teil
make_object("Nagel_unten", *merge(cone((NAIL_X, 0, 1.4), (NAIL_X, 0, 0.8), 0.22, 20), cyl((NAIL_X, 0, 1.4), (NAIL_X, 0, LIQ + 0.05), 0.22, 20)),
            M["NagelUnten"], "Versuch")
make_object("Nagel_oben", *merge(cyl((NAIL_X, 0, LIQ + 0.05), (NAIL_X, 0, 9.9), 0.22, 20), cyl((NAIL_X, 0, 9.9), (NAIL_X, 0, 10.05), 0.5, 28)),
            M["Eisen"], "Versuch")
# Kupferblech
make_object("Kupferblech_unten", *box((SHEET_X, 0, (1.3 + LIQ) / 2), (0.07, 2.3, LIQ - 1.3)), M["BlechUnten"], "Versuch", smooth=False)
make_object("Kupferblech_oben", *box((SHEET_X, 0, (LIQ + 10.0) / 2), (0.07, 2.3, 10.0 - LIQ)), M["Kupfer"], "Versuch", smooth=False)


# Doppel-Krokodilklemmen am Rand (außen auf dem Glasrand, innen eine Klemme mit Kabelbuchse)
def double_clip(name, side):
    s = side
    rim = BEAKER_R * s
    obj_x = NAIL_X if s < 0 else SHEET_X
    parts = [
        rbox((rim, 0, BEAKER_H - 0.2), (0.55, 0.9, 1.3), 0.08),                       # Klemme auf dem Rand
        rbox(((rim + obj_x) / 2, 0, BEAKER_H + 0.55), (abs(rim - obj_x) + 0.3, 0.5, 0.22), 0.06),  # Verbindungssteg
        rbox((obj_x, 0, 10.05 if s < 0 else 9.75), (0.55, 0.7, 0.9), 0.08),          # innere Klemme hält Nagel/Blech
    ]
    make_object(name, *merge(*parts), M["Klemme"], "Versuch")
    make_object(name + "_Buchse", *cyl((obj_x, 0, 10.4), (obj_x, 0, 10.9), 0.17, 18), M["Buchse"], "Versuch")
    return (obj_x, 0, 10.9)


plug_l = double_clip("Klemme_Nagel", -1)
plug_r = double_clip("Klemme_Blech", 1)
make_object("Stecker_gelb", *cyl(plug_l, (plug_l[0], 0, 11.7), 0.2, 18), M["KabelGelb"], "Versuch")
make_object("Stecker_rot", *cyl(plug_r, (plug_r[0], 0, 11.7), 0.2, 18), M["KabelRot"], "Versuch")

# 4,5-V-Flachbatterie mit kurzem (+) und langem (−) Anschluss.
# „A“: richtig angeschlossen (langer Anschluss links → gelbes Kabel zum Nagel).
# „C“: Batterie umgedreht (kurzer Anschluss = Pluspol links → gelbes Kabel, Nagel am Pluspol).
def battery(tag, flipped):
    cn = f"Batterie{tag}"
    xl, xr = BAT["x"] - 1.9, BAT["x"] + 1.9
    x_long, x_short = (xr, xl) if flipped else (xl, xr)
    make_object(f"Batterie{tag}", *rbox((BAT["x"], BAT["y"], BAT["h"] / 2), (BAT["w"], BAT["d"], BAT["h"]), 0.35), M["Batterie"], cn)
    text_object(f"Batterie{tag}_Schrift", "4,5 V", 0.9, (BAT["x"], BAT["y"] - BAT["d"] / 2 - 0.02, BAT["h"] * 0.55), cn, M["Schrift"], bold=True)
    bend = -0.5 if flipped else 0.5
    make_object(f"Batterie{tag}_Fahne_lang", *merge(box((x_long, BAT["y"], BAT["h"] + 0.9), (0.7, 0.05, 1.8)), box((x_long + bend, BAT["y"], BAT["h"] + 1.78), (1.0, 0.05, 0.05))),
                M["Messing"], cn, smooth=False)
    make_object(f"Batterie{tag}_Fahne_kurz", *box((x_short, BAT["y"], BAT["h"] + 0.45), (0.7, 0.05, 0.9)), M["Messing"], cn, smooth=False)
    cm = (x_long, BAT["y"], BAT["h"] + 1.5)
    cp = (x_short, BAT["y"], BAT["h"] + 0.75)
    make_object(f"Batterie{tag}_Klemme_minus", *rbox(cm, (0.45, 0.5, 1.0), 0.07), M["Klemme"], cn)
    make_object(f"Batterie{tag}_Klemme_plus", *rbox(cp, (0.45, 0.5, 1.0), 0.07), M["Klemme"], cn)
    left, right = (cp, cm) if flipped else (cm, cp)   # links endet das gelbe, rechts das rote Kabel
    cy = catmull([(plug_l[0], 0, 11.7), (plug_l[0], 0, 13.2), (2.0, 0.6, 14.6), (left[0] - 0.3, 1.2, left[2] + 4.5), (left[0], BAT["y"], left[2] + 0.5)], 14)
    cr = catmull([(plug_r[0], 0, 11.7), (plug_r[0], 0, 12.6), (6.0, 0.4, 13.0), (right[0] - 0.2, 1.3, right[2] + 3.2), (right[0], BAT["y"], right[2] + 0.5)], 14)
    make_object(f"Kabel{tag}_gelb", *tube(cy, 0.13), M["KabelGelb"], cn)
    make_object(f"Kabel{tag}_rot", *tube(cr, 0.13), M["KabelRot"], cn)
    return cy, cr, cm, cp


CABLE_Y, CABLE_R, clip_m, clip_p = battery("", False)
CABLE_YC, CABLE_RC, clip_mC, clip_pC = battery("C", True)
TAB_MINUS = clip_m
TAB_PLUS = clip_p
log("Versuch aufgebaut")

# ======================================================================================
# 2) TEILCHENEBENE (Schema, stark vergrößert)
# ======================================================================================
OFF = np.array([40.0, 0.0, 3.0])
R_AT, R_E, R_SO4 = 0.28, 0.16, 0.3
GY = [-1.8, -1.2, -0.6, 0.0, 0.6, 1.2, 1.8]
GZ = [round(-4.2 + 0.6 * k, 2) for k in range(14)]
FE_X = [-9.0, -8.4, -7.8]
CU_X = [7.2, 7.8, 8.4, 9.0]
BOX = dict(x0=-9.6, x1=9.6, y=2.4, z0=-4.6, z1=4.2)
WIRE_Z = 7.3
BAT_T = dict(w=4.6, d=1.6, h=1.8)
TERM_L, TERM_R = np.array([-2.6, 0, WIRE_Z]), np.array([2.6, 0, WIRE_Z])
WIRE_L = [np.array([-8.4, 0, 3.4]), np.array([-8.4, 0, WIRE_Z]), TERM_L]
WIRE_R = [np.array([8.1, 0, 3.4]), np.array([8.1, 0, WIRE_Z]), TERM_R]


def W(p):
    return np.asarray(p, float) + OFF


# reagierende Atome (eigene Spuren, nicht im Gitter)
A_SITES = [(-1.8, 1.8), (-1.2, -0.6), (-1.8, -2.4), (-1.2, 3.0), (-1.8, 0.6), (-1.2, -3.0), (-1.8, -1.2), (-1.2, 1.2)]
A_DISS = [(-1.8, -1.8), (-1.2, 1.2), (-1.8, 2.4), (-1.2, -1.2), (-1.8, 0.0), (-1.2, 3.0), (-1.8, -3.0), (-1.2, -2.4)]
FE_REACT = [(-1.8, 2.4), (-1.8, 0.0), (-1.8, -2.4), (-1.2, 1.2), (-1.2, -1.2)]
C_SITES = [(-1.8, 1.8), (-1.2, -0.6), (-1.8, -1.2), (-1.2, 2.4), (-1.8, 0.0)]

fe_all = [(x, y, z) for x in FE_X for y in GY for z in GZ]
cu_all = [(x, y, z) for x in CU_X for y in GY for z in GZ]
fe_react_pos = [(-7.8, y, z) for y, z in FE_REACT]
cu_diss_pos = [(7.2, y, z) for y, z in A_DISS]
key3 = lambda p: (round(p[0], 2), round(p[1], 2), round(p[2], 2))
fe_rest = [p for p in fe_all if key3(p) not in {key3(q) for q in fe_react_pos}]
cu_rest = [p for p in cu_all if key3(p) not in {key3(q) for q in cu_diss_pos}]

make_object("T_Loesung", *box(W((0, 0, (BOX["z0"] + BOX["z1"]) / 2)), (BOX["x1"] - BOX["x0"], 2 * BOX["y"], BOX["z1"] - BOX["z0"])), M["TLoesung"], "Teilchen", smooth=False)
make_object("T_Rueckwand", *box(W((0, BOX["y"] - 0.02, (BOX["z0"] + BOX["z1"]) / 2)), (BOX["x1"] - BOX["x0"], 0.04, BOX["z1"] - BOX["z0"])), M["Rueckwand"], "Teilchen", smooth=False)
x0, x1, yb, z0, z1 = BOX["x0"], BOX["x1"], BOX["y"], BOX["z0"], BOX["z1"]
edges = []
for sy in (-yb, yb):
    edges += [((x0, sy, z0), (x1, sy, z0)), ((x0, sy, z1), (x1, sy, z1)), ((x0, sy, z0), (x0, sy, z1)), ((x1, sy, z0), (x1, sy, z1))]
for sx in (x0, x1):
    for sz in (z0, z1):
        edges.append(((sx, -yb, sz), (sx, yb, sz)))
make_object("T_Behaelter", *merge(*[cyl(W(a), W(b), 0.045, 10) for a, b in edges]), M["Behaelter"], "Teilchen")

# Drähte und Batterie (Teilchenebene)
make_object("T_Draht_gelb", *merge(*[cyl(W(a), W(b), 0.1, 14) for a, b in zip(WIRE_L, WIRE_L[1:])],
                                   (uvsphere(0.1, 14, 8)[0] + W(WIRE_L[1]), uvsphere(0.1, 14, 8)[1])), M["KabelGelb"], "TStrom")
make_object("T_Draht_rot", *merge(*[cyl(W(a), W(b), 0.1, 14) for a, b in zip(WIRE_R, WIRE_R[1:])],
                                  (uvsphere(0.1, 14, 8)[0] + W(WIRE_R[1]), uvsphere(0.1, 14, 8)[1])), M["KabelRot"], "TStrom")
make_object("T_Batterie", *rbox(W((0, 0, WIRE_Z)), (BAT_T["w"], BAT_T["d"], BAT_T["h"]), 0.2), M["Batterie"], "TStrom")
text_object("T_Batterie_Schrift", "4,5 V", 0.55, W((0, -BAT_T["d"] / 2 - 0.02, WIRE_Z)), "TStrom", M["Schrift"], bold=True)
text_object("T_Pol_A_minus", "−", 0.9, W((-1.75, -BAT_T["d"] / 2 - 0.02, WIRE_Z)), "TStrom", M["Pol"], bold=True)
text_object("T_Pol_A_plus", "+", 0.9, W((1.75, -BAT_T["d"] / 2 - 0.02, WIRE_Z)), "TStrom", M["Pol"], bold=True)
text_object("T_Pol_C_plus", "+", 0.9, W((-1.75, -BAT_T["d"] / 2 - 0.02, WIRE_Z)), "TFalsch", M["Pol"], bold=True)
text_object("T_Pol_C_minus", "−", 0.9, W((1.75, -BAT_T["d"] / 2 - 0.02, WIRE_Z)), "TFalsch", M["Pol"], bold=True)


def arrow(name, p0, p1, r, head, mat, collection):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    V, F = merge(cyl(p0, p1 - d * head * 1.6, r, 14), cone(p1 - d * head * 1.7, p1, head, 22))
    return make_object(name, V, F, mat, collection)


# Pfeile (Vollfassung): Elektronen in den Drähten, Cu²⁺ in der Lösung – für A; C nutzt eigene
arrow("Pfeil_e_rot_A", W((9.0, -0.6, 4.2)), W((9.0, -0.6, 6.6)), 0.09, 0.26, M["PfeilE"], "PfeileA")
arrow("Pfeil_e_gelb_A", W((-9.3, -0.6, 6.6)), W((-9.3, -0.6, 4.2)), 0.09, 0.26, M["PfeilE"], "PfeileA")
arrow("Pfeil_Cu_A", W((3.0, -2.0, -5.4)), W((-3.0, -2.0, -5.4)), 0.1, 0.3, M["PfeilCu"], "PfeileA")
arrow("Pfeil_e_gelb_C", W((-9.3, -0.6, 4.2)), W((-9.3, -0.6, 6.6)), 0.09, 0.26, M["PfeilE"], "PfeileC")
arrow("Pfeil_e_rot_C", W((9.0, -0.6, 6.6)), W((9.0, -0.6, 4.2)), 0.09, 0.26, M["PfeilE"], "PfeileC")
arrow("Pfeil_Cu_C", W((-3.0, -2.0, -5.4)), W((3.0, -2.0, -5.4)), 0.1, 0.3, M["PfeilCu"], "PfeileC")

# Gitter (im Viewer als Instanzen)
sph_at = uvsphere(R_AT, 16, 10)
INSTANCES = {
    "T_Fe_voll": ("Inst_Fe", sph_at, M["FeAtom"], [W(p) for p in fe_all]),
    "T_Fe_rest": ("Inst_Fe", sph_at, M["FeAtom"], [W(p) for p in fe_rest]),
    "T_Cu_voll": ("Inst_Cu", sph_at, M["CuAtom"], [W(p) for p in cu_all]),
    "T_Cu_rest": ("Inst_Cu", sph_at, M["CuAtom"], [W(p) for p in cu_rest]),
}
make_object("Inst_Fe", *sph_at, M["FeAtom"], "Vorlagen")
make_object("Inst_Cu", *sph_at, M["CuAtom"], "Vorlagen")

# Vorlagen der beweglichen Teilchen + Ladungszeichen (Zeichen liegt vorn: −Y = three +z)
for nm, r, mat in (("V_Atom", R_AT, M["CuAtom"]), ("V_e", R_E, M["Elektron"]), ("V_SO4", R_SO4, M["SO4"])):
    make_object(nm, *uvsphere(r, 22, 14), mat, "Vorlagen")
for nm, body, r, mat in (("Z_2plus", "2+", R_AT, M["Zeichen"]), ("Z_minus", "−", R_E, M["ZeichenHell"]), ("Z_2minus", "2−", R_SO4, M["Zeichen"])):
    o = text_object(nm, body, r * (1.0 if body != "−" else 1.6), (0, -r * 0.98, 0), "Vorlagen", mat, bold=True, extrude=0.01)
make_object("V_Blase", *uvsphere(0.07, 12, 8), M["Blase"], "Vorlagen")
bpy.context.view_layer.update()
for o in list(COLL["Vorlagen"].objects):
    if o.name.startswith("Z_"):          # Lage in die Geometrie übernehmen (Viewer klont nur die Geometrie)
        o.data.transform(o.matrix_world)
        o.location = (0, 0, 0)
        o.rotation_euler = (0, 0, 0)

# ======================================================================================
# 3) ABLÄUFE: Spuren der Teilchen (Zeit τ in Sekunden, Zustand je Schlüssel)
# ======================================================================================
# Zustände: 0 unsichtbar, 1 Cu-Atom, 2 Cu²⁺, 3 Fe-Atom, 4 Fe²⁺, 5 Elektron, 6 SO₄²⁻
rng = np.random.default_rng(7)


class Track:
    def __init__(self, kind):
        self.kind = kind          # "atom" | "e" | "so4"
        self.keys = []

    def add(self, t, p, s):
        self.keys.append((round(float(t), 3), np.asarray(p, float).copy(), int(s)))

    def at(self, t):
        K = self.keys
        if t <= K[0][0]:
            return K[0][1], K[0][2]
        for a, b in zip(K, K[1:]):
            if a[0] <= t < b[0]:
                k = (t - a[0]) / (b[0] - a[0]) if b[0] > a[0] else 0
                return a[1] + (b[1] - a[1]) * k, a[2]
        return K[-1][1], K[-1][2]


def clampbox(p):
    p = np.array(p, float)
    p[1] = np.clip(p[1], -2.0, 2.0)
    p[2] = np.clip(p[2], -4.1, 3.6)
    return p


def wander(tr, p0, p1, t0, t1, state, amp=0.22, step=0.5):
    """Ungeordnete Zitterbewegung mit Drift von p0 nach p1."""
    if t1 <= t0:
        return
    n = max(1, int((t1 - t0) / step))
    for k in range(n + 1):
        u = k / n
        p = np.asarray(p0) + (np.asarray(p1) - np.asarray(p0)) * u
        if 0 < k < n:
            p = p + rng.normal(0, amp, 3) * np.array([1, 0.8, 1])
        tr.add(t0 + (t1 - t0) * u, clampbox(p), state)


def glide(tr, p0, p1, t0, t1, state, n=8):
    for k in range(n + 1):
        u = smooth01(k / n)
        tr.add(t0 + (t1 - t0) * k / n, np.asarray(p0) + (np.asarray(p1) - np.asarray(p0)) * u, state)


def along(tr, P, t0, t1, state=5):
    n = len(P)
    for k in range(0, n, 3):
        tr.add(t0 + (t1 - t0) * k / (n - 1), P[k], state)
    tr.add(t1, P[-1], state)


def epath(points):
    return resample(polyline([np.asarray(p, float) for p in points], 0.05), 60)


def electron(tr, seg1, seg2, ts, t_bat=1.3, t_hide=0.3, t2=1.5):
    """Elektron: Weg 1 (bis Batterie-Anschluss), unsichtbar in der Batterie, Weg 2 (bis zum Ziel)."""
    tr.add(0, seg1[0], 0)
    tr.add(ts - 0.01, seg1[0], 0)
    along(tr, seg1, ts, ts + t_bat)
    if seg2 is None:
        tr.add(ts + t_bat + 0.01, seg1[-1], 0)
        return ts + t_bat
    tr.add(ts + t_bat + 0.01, seg1[-1], 0)
    tr.add(ts + t_bat + t_hide - 0.01, seg2[0], 0)
    along(tr, seg2, ts + t_bat + t_hide, ts + t_bat + t_hide + t2)
    tr.add(ts + t_bat + t_hide + t2 + 0.01, seg2[-1], 0)
    return ts + t_bat + t_hide + t2


def so4_tracks(T, drift):
    pos = [(-3.0, 1.4, 0.2), (-1.0, -0.4, -2.8), (0.8, 1.5, 2.8), (2.4, -1.0, -0.8), (4.2, 0.6, 1.8), (-4.6, 1.2, -3.0)]
    out = []
    for p in pos:
        tr = Track("so4")
        wander(tr, p, np.array(p) + np.array([drift, 0, 0]), 0, T, 6, amp=0.2, step=0.6)
        out.append(tr)
    return out


ED = 1.2            # Dauer eines Reaktionsschritts (s)
S0 = np.array([8.1, 0, 3.4])    # Eintritt in den roten Draht (Blech)
N0 = np.array([-8.4, 0, 3.4])   # Austritt aus dem gelben Draht (Nagel)


def conveyor(events, forward=True, n=16):
    """Elektronenkette im Stromkreis: Alle Elektronen in Drähten rücken bei jedem Schritt gleichzeitig um zwei Plätze weiter.
    forward: Blech → rot → Batterie → gelb → Nagel (mit Strom); sonst umgekehrt (falsch gepolt)."""
    red = resample(polyline([S0, WIRE_R[1], TERM_R], 0.05), 120)
    yel = resample(polyline([TERM_L, WIRE_L[1], N0], 0.05), 120)
    L1 = float(np.sum(np.linalg.norm(np.diff(red, axis=0), axis=1)))
    L2 = float(np.sum(np.linalg.norm(np.diff(yel, axis=0), axis=1)))
    gap = 1.2
    Lt = L1 + gap + L2
    d = Lt / n

    def point(sv):
        sv = sv % Lt
        if not forward:
            sv = Lt - sv
        if sv <= L1:
            return red[min(int(sv / L1 * (len(red) - 1)), len(red) - 1)], True
        if sv <= L1 + gap:
            return None, False
        u = (sv - L1 - gap) / L2
        return yel[min(int(u * (len(yel) - 1)), len(yel) - 1)], True

    def shift(t):
        sh = 0.0
        for t0 in events:
            sh += 2 * d * smooth01((t - t0) / ED)
        return sh

    tracks = []
    times = [0.0]
    for t0 in events:
        times += [t0 + ED * k / 8 for k in range(9)]
    times.append(events[-1] + ED + 30)
    for k in range(n):
        tr = Track("e")
        last = None
        for t in times:
            sv = k * d + 0.5 * d + shift(t)
            p, vis = point(sv)
            wrap = int(sv // Lt)
            if p is None:
                p = last if last is not None else S0
            if last is not None and wrap != getattr(tr, "_w", wrap):
                tr.add(t - 0.001, last, 0)        # Übergang Nagel → Blech unsichtbar
            tr._w = wrap
            tr.add(t, p, 5 if vis else 0)
            last = p
        tracks.append(tr)
    return tracks


def feeder(p0, p1, t0, n=2):
    """zwei Elektronen von p0 nach p1 im Zeitraum eines Reaktionsschritts"""
    out = []
    for k in range(n):
        e = Track("e")
        off = np.array([0, 0.18 * (k - 0.5), 0.18 * (0.5 - k)])
        e.add(0, p0, 0)
        e.add(t0 - 0.01, p0 + off, 0)
        glide(e, np.asarray(p0) + off, np.asarray(p1) + off * 0.3, t0, t0 + ED, 5, 6)
        e.add(t0 + ED + 0.01, p1, 0)
        out.append(e)
    return out


def scenario_A():
    """Mit Strom: Im selben Moment gibt am Blech ein Cu-Atom 2 e⁻ ab (→ Cu²⁺) und nimmt am Nagel ein Cu²⁺ 2 e⁻ auf (→ Cu)."""
    T = 32.0
    events = [3.0 + 3.6 * i for i in range(8)]
    pool = [(-4.8, -0.9, 1.4), (-3.6, 0.8, -1.8), (-2.0, -1.2, 2.6), (-0.6, 1.0, -0.4), (1.4, -0.6, 1.0), (3.2, 0.9, -2.6)]
    diss = []
    for j, (y, z) in enumerate(A_DISS):
        tr = Track("atom")
        p = np.array([7.2, y, z])
        tr.add(0, p, 1)
        tm = events[j] + ED / 2
        tr.add(tm - 0.01, p, 1)
        tr.add(tm, p, 2)
        tr.add(events[j] + ED, p, 2)
        glide(tr, p, (5.4, y * 0.6, z), events[j] + ED, events[j] + ED + 1.4, 2, 5)
        diss.append((tr, events[j] + ED + 1.4, np.array([5.4, y * 0.6, z])))
    queue = [(Track("atom"), 0.0, np.array(p)) for p in pool] + diss
    for tr, _, p in queue[:6]:
        tr.add(0, p, 2)
    elist = conveyor(events, True)
    for i, t0 in enumerate(events):
        tr, born, p = queue[i]
        y, z = A_SITES[i]
        site = np.array([-7.2, y, z])
        appr = np.array([-5.6, y * 0.5, z])
        wander(tr, p, appr, born, t0 - 2.2, 2)
        glide(tr, appr, site, t0 - 2.2, t0, 2)
        tr.add(t0 + ED / 2 - 0.01, site, 2)
        tr.add(t0 + ED / 2, site, 1)
        tr.add(T, site, 1)
        dy, dz = A_DISS[i]
        elist += feeder(np.array([7.2, dy, dz]), S0, t0)
        elist += feeder(N0, site, t0)
    for tr, born, p in queue[8:]:
        wander(tr, p, p + np.array([-(T - born) * 0.28, 0, 0]), born, T, 2)
    atoms = [q[0] for q in queue]
    return dict(T=T, tracks=atoms + elist + so4_tracks(T, 1.6), events=events)


def scenario_B():
    """Ohne Strom: Fe-Atom gibt 2 e⁻ direkt an ein Cu²⁺ an der Oberfläche ab; Fe²⁺ geht in Lösung, Cu setzt sich locker ab."""
    T = 26.0
    events = [1.0 + 4.6 * j for j in range(5)]
    pool = [(-4.6, -1.0, 2.2), (-3.4, 0.6, -0.4), (-5.0, -1.4, -2.0), (-2.2, -0.8, 1.0), (-4.0, 1.0, -3.0),
            (-0.4, 0.4, 2.6), (1.6, -0.8, -1.4), (3.4, 0.9, 0.6)]
    tracks = []
    ions = [Track("atom") for _ in pool]
    for tr, p in zip(ions, pool):
        tr.add(0, p, 2)
    for j, t0 in enumerate(events):
        y, z = FE_REACT[j]
        fe = Track("atom")
        fp = np.array([-7.8, y, z])
        fe.add(0, fp, 3)
        tc = t0 + 3.4
        tr = ions[j]
        contact = np.array([-7.18, y + 0.15, z + 0.35])
        wander(tr, pool[j], (-5.4, y * 0.5, z + 0.3), 0 if j == 0 else events[j - 1], t0 + 0.8, 2)
        glide(tr, (-5.4, y * 0.5, z + 0.3), contact, t0 + 0.8, t0 + 2.5, 2)
        tr.add(tc - 0.01, contact, 2)
        loose = contact + np.array([0.25 + rng.uniform(0, 0.35), rng.uniform(-0.3, 0.3), rng.uniform(-0.25, 0.25)])
        tr.add(tc, contact, 1)
        glide(tr, contact, loose, tc + 0.02, tc + 0.8, 1, 4)
        tr.add(T, loose, 1)
        for k in range(2):
            e = Track("e")
            ts = t0 + 2.6 + 0.3 * k
            e.add(0, fp, 0)
            e.add(ts - 0.01, fp, 0)
            glide(e, fp + np.array([0.25, 0, 0]), contact, ts, ts + 0.5, 5, 5)
            e.add(ts + 0.51, contact, 0)
            tracks.append(e)
        fe.add(tc - 0.01, fp, 3)
        fe.add(tc, fp, 4)
        glide(fe, fp, fp + np.array([1.4, -0.2, -0.5]), tc, tc + 1.2, 4, 5)
        wander(fe, fp + np.array([1.4, -0.2, -0.5]), np.array([-3.6 + 1.1 * j, rng.uniform(-1, 1), z * 0.6]), tc + 1.2, T, 4)
        tracks.append(fe)
    for j in range(5, len(pool)):
        wander(ions[j], pool[j], np.array(pool[j]) + np.array([-1.0, 0, 0]), 0, T, 2)
    return dict(T=T, tracks=ions + tracks + so4_tracks(T, 0.0), events=events)


def scenario_C():
    """Falsch gepolt: Im selben Moment gibt am Nagel ein Fe-Atom 2 e⁻ ab (→ Fe²⁺) und nimmt am Blech ein Cu²⁺ 2 e⁻ auf (→ Cu)."""
    T = 26.0
    events = [3.0 + 4.4 * j for j in range(5)]
    pool = [(4.6, -1.0, 2.0), (3.4, 0.6, -0.6), (5.0, -1.4, -2.2), (2.2, -0.8, 1.2), (4.0, 1.0, -3.0),
            (0.4, 0.4, 2.6), (-1.6, -0.8, -1.4), (-3.4, 0.9, 0.6)]
    ions = [Track("atom") for _ in pool]
    for tr, p in zip(ions, pool):
        tr.add(0, p, 2)
    tracks = conveyor(events, False)
    for j, t0 in enumerate(events):
        y, z = FE_REACT[j]
        fe = Track("atom")
        fp = np.array([-7.8, y, z])
        fe.add(0, fp, 3)
        fe.add(t0 + ED / 2 - 0.01, fp, 3)
        fe.add(t0 + ED / 2, fp, 4)
        fe.add(t0 + ED, fp, 4)
        glide(fe, fp, fp + np.array([1.4, -0.2, 0.3]), t0 + ED, t0 + ED + 1.2, 4, 5)
        wander(fe, fp + np.array([1.4, -0.2, 0.3]), np.array([-4.0 + 0.9 * j, rng.uniform(-1, 1), z * 0.6]), t0 + ED + 1.2, T, 4)
        tracks.append(fe)
        cy, cz = C_SITES[j]
        site = np.array([6.6, cy, cz])
        tr = ions[j]
        appr = np.array([5.0, cy * 0.5, cz])
        wander(tr, pool[j], appr, 0 if j == 0 else events[j - 1], t0 - 2.2, 2)
        glide(tr, appr, site, t0 - 2.2, t0, 2)
        tr.add(t0 + ED / 2 - 0.01, site, 2)
        tr.add(t0 + ED / 2, site, 1)
        tr.add(T, site, 1)
        tracks += feeder(fp, N0, t0)
        tracks += feeder(S0, site, t0)
    for j in range(5, len(pool)):
        wander(ions[j], pool[j], np.array(pool[j]) + np.array([1.0, 0, 0]), 0, T, 2)
    return dict(T=T, tracks=ions + tracks + so4_tracks(T, -1.2), events=events)


SCEN = {"A": scenario_A(), "B": scenario_B(), "C": scenario_C()}
for k, sc in SCEN.items():
    for tr in sc["tracks"]:
        tr.keys.sort(key=lambda x: x[0])


def counters(sc):
    out = []
    for t in np.arange(0, sc["T"] + 0.001, 0.1):
        st = [tr.at(t) for tr in sc["tracks"] if tr.kind == "atom"]
        cu2 = sum(1 for p, s in st if s == 2)
        fe2 = sum(1 for p, s in st if s == 4)
        dep = sum(1 for p, s in st if s == 1 and p[0] < 0)
        on_sheet = sum(1 for p, s in st if s == 1 and p[0] > 6.4 and p[0] < 7.0)
        diss = sum(1 for tr in sc["tracks"] if tr.kind == "atom" and tr.keys[0][2] == 1 and tr.keys[0][1][0] > 0
                   and any(k[2] == 2 and k[0] <= t + 1e-6 for k in tr.keys))
        row = [round(float(t), 1), cu2, fe2, dep + on_sheet, diss]
        if not out or out[-1][1:] != row[1:]:
            out.append(row)
    return out


log("Abläufe berechnet:", {k: len(v["tracks"]) for k, v in SCEN.items()})


# --------------------------------------------------------------------------------------
# Export für den Viewer
# --------------------------------------------------------------------------------------
def to_three(p):
    p = np.asarray(p, float)
    return [round(float(p[0]), 3), round(float(p[2]), 3), round(float(-p[1]), 3)]


ANCHORS = {
    # Versuch
    "nagel": (NAIL_X, -0.2, 4.0), "blech": (SHEET_X, -1.2, 5.0), "loesung": (0.3, -2.9, 2.0), "becherglas": (-2.6, -1.8, 8.6),
    "batterie": (BAT["x"], BAT["y"] - 1.1, 4.5), "pol_minus": TAB_MINUS[:2] + (TAB_MINUS[2] + 0.9,), "pol_plus": TAB_PLUS[:2] + (TAB_PLUS[2] + 0.9,),
    "kabel_gelb": tuple(CABLE_Y[len(CABLE_Y) // 2]), "kabel_rot": tuple(CABLE_R[len(CABLE_R) // 2]),
    "klemme": (-BEAKER_R, -0.5, BEAKER_H + 0.5), "blasen": (NAIL_X + 0.2, -0.3, 2.2),
    # Teilchenebene
    "t_nagel": tuple(W((-8.4, -2.0, 3.9))), "t_blech": tuple(W((8.1, -2.0, 3.9))), "t_loesung": tuple(W((0.6, -2.4, -3.6))),
    "t_batterie": tuple(W((0, -0.8, WIRE_Z + 1.0))), "t_draht_gelb": tuple(W((-5.5, 0, WIRE_Z))), "t_draht_rot": tuple(W((5.5, 0, WIRE_Z))),
    "eq_links": tuple(W((-5.0, 0, 5.6))), "eq_rechts": tuple(W((5.0, 0, 5.6))), "eq_mitte": tuple(W((0, 0, -6.3))),
    "t_e_gelb": tuple(W((-9.9, -0.6, 5.4))), "t_e_rot": tuple(W((9.6, -0.6, 5.4))), "t_cu_pfeil": tuple(W((0, -2.0, -5.0))),
}
stats = {"blender": bpy.app.version_string, "objects": sum(1 for o in bpy.data.objects if o.type == "MESH")}


def export_tracks(sc):
    out = []
    for tr in sc["tracks"]:
        keys = []
        last = None
        for t, p, s in tr.keys:
            k = [t] + to_three(p + OFF) + [s]
            if last is None or k[1:] != last[1:] or True:
                keys.append(k)
            last = k
        out.append({"kind": tr.kind, "keys": keys})
    return out


meta = {
    "units": "Versuch: 1 Einheit = 1 cm; Teilchenebene stark vergrößert (bei x = 40). three.js: +x rechts, +y oben, +z zum Betrachter",
    "states": {"0": "unsichtbar", "1": "Cu", "2": "Cu²⁺", "3": "Fe", "4": "Fe²⁺", "5": "e⁻", "6": "SO₄²⁻"},
    "scenarios": {k: {"T": v["T"], "events": v["events"], "tracks": export_tracks(v), "counters": counters(v)} for k, v in SCEN.items()},
    "instances": {g: {"proto": v[0], "pos": [to_three(p) for p in v[3]]} for g, v in INSTANCES.items()},
    "colors": {k: C[k] for k in ("cu", "cu2", "fe", "fe2", "so4", "elektron", "loesung")},
    "macro": {"nail": to_three((NAIL_X, 0, 0)), "sheet": to_three((SHEET_X, 0, 0)), "liquid": LIQ},
    "anchors": {k: to_three(v) for k, v in ANCHORS.items()},
    "stats": stats,
}
if not VIDEO:
    with open(META_PATH, "w") as fh:
        json.dump(meta, fh, ensure_ascii=False, separators=(",", ":"))
    for o in bpy.data.objects:
        o.select_set(o.type == "MESH" and o.name not in INSTANCES)
    bpy.ops.export_scene.gltf(filepath=GLB_PATH, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                              export_cameras=False, export_lights=False, export_animations=False, export_extras=False)
    log(f"GLB {os.path.getsize(GLB_PATH) / 1e6:.2f} MB, meta {os.path.getsize(META_PATH) / 1e6:.2f} MB")

# Gitter auch in Blender (für Video/Vorschau)
for g, (proto, geo, mat, pos) in INSTANCES.items():
    make_object(g, *instances(geo, pos), mat, "Gitter")

# --------------------------------------------------------------------------------------
# Licht, Welt, Kamera
# --------------------------------------------------------------------------------------
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (*srgb("#060c18"), 1)
bg.inputs["Strength"].default_value = 1.0


def light(name, kind, loc, energy, color, size=10.0, target=(0, 0, 1.5)):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = srgb(color)
    if kind == "AREA":
        ld.size = size
    lo = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return lo


light("Key_V", "AREA", (-12, -24, 24), 7000, "#fff0da", 14, (4, 0, 5))
light("Rim_V", "AREA", (16, 18, 16), 4000, "#6fb6ff", 12, (4, 0, 5))
light("Fill_V", "AREA", (8, -20, 0), 1500, "#cfe2ff", 12, (4, 0, 5))
light("Key_T", "AREA", (24, -26, 22), 9000, "#fff0da", 16, tuple(OFF))
light("Rim_T", "AREA", (58, 20, 14), 5000, "#6fb6ff", 14, tuple(OFF))
light("Fill_T", "AREA", (46, -22, -10), 1500, "#cfe2ff", 14, tuple(OFF))

scene.render.engine = "BLENDER_EEVEE"
ee = scene.eevee
ee.taa_render_samples = 48
ee.use_gtao = True
ee.gtao_distance = 1.0
ee.use_bloom = True
ee.bloom_threshold = 1.1
ee.bloom_intensity = 0.05
ee.use_soft_shadows = True
ee.use_ssr = True
ee.use_ssr_refraction = True
scene.view_settings.view_transform = "AgX"

cam_data = bpy.data.cameras.new("Kamera")
cam_data.lens = 50
cam_data.clip_end = 500
cam = bpy.data.objects.new("Kamera", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_target = bpy.data.objects.new("Kameraziel", None)
scene.collection.objects.link(cam_target)
tc = cam.constraints.new("TRACK_TO")
tc.target = cam_target
tc.track_axis = "TRACK_NEGATIVE_Z"
tc.up_axis = "UP_Y"


def orbit(az, el, d, target):
    t = Vector(target)
    a, e = math.radians(az), math.radians(el)
    return t + Vector((d * math.cos(e) * math.sin(a), -d * math.cos(e) * math.cos(a), d * math.sin(e)))


def set_view(az, el, d, target):
    cam_target.location = target
    cam.location = orbit(az, el, d, target)


for c_ in ("Vorlagen",):
    for o in COLL[c_].objects:
        o.hide_render = True
        o.hide_viewport = True
for c_ in ("PfeileA", "PfeileC", "TFalsch", "BatterieC"):
    for o in COLL[c_].objects:
        o.hide_render = True

VIEW_MACRO = (-18, 16, 40, (5.0, 0, 5.5))
VIEW_PART = (0, 6, 34, tuple(OFF + np.array([0, 0, 1.3])))

# ======================================================================================
# 4) VIDEO (Drehbuch, Keyframes) – nur mit --video1 / --video2
# ======================================================================================
FPS = 25


def setup_particles(sc, tag):
    """Objekte für die Spuren eines Szenarios: je Teilchen eine Kugel je Erscheinung (Atom/Ion/e⁻/SO₄²⁻)."""
    objs = []
    for i, tr in enumerate(sc["tracks"]):
        if tr.kind == "e":
            o = make_object(f"{tag}_e{i}", *uvsphere(R_E, 18, 10), M["Elektron"], "Video")
            s = text_object(f"{tag}_e{i}_Z", "−", R_E * 1.6, (0, 0, 0), "Video", M["ZeichenHell"], bold=True, extrude=0.01, rot=(0, 0, 0))
            looks = {5: (o, s)}
        elif tr.kind == "so4":
            o = make_object(f"{tag}_s{i}", *uvsphere(R_SO4, 18, 10), M["SO4"], "Video")
            s = text_object(f"{tag}_s{i}_Z", "2−", R_SO4, (0, 0, 0), "Video", M["Zeichen"], bold=True, extrude=0.01, rot=(0, 0, 0))
            looks = {6: (o, s)}
        else:
            looks = {}
            for st, mat, sign in ((1, M["CuAtom"], None), (2, M["Cu2"], "2+"), (3, M["FeAtom"], None), (4, M["Fe2"], "2+")):
                if not any(k[2] == st for k in tr.keys):
                    continue
                o = make_object(f"{tag}_a{i}_{st}", *uvsphere(R_AT, 20, 12), mat, "Video")
                s = text_object(f"{tag}_a{i}_{st}_Z", sign, R_AT, (0, 0, 0), "Video", M["Zeichen"], bold=True, extrude=0.01, rot=(0, 0, 0)) if sign else None
                looks[st] = (o, s)
        for st, (o, s) in looks.items():
            if s:
                s.parent = o
                s.location = (0, 0, 0)
                # Zeichen vor der Kugel, immer zur Kamera
                me = s.data
                for v in me.vertices:
                    v.co.z += (R_AT if tr.kind == "atom" else R_E if tr.kind == "e" else R_SO4) * 0.98
                t = s.constraints.new("TRACK_TO")
                t.target = cam
                t.track_axis = "TRACK_Z"
                t.up_axis = "UP_Y"
        objs.append((tr, looks))
    return objs


def key_particles(objs, frame, tau, visible=True):
    for tr, looks in objs:
        p, st = tr.at(tau)
        p = p + OFF
        for s_, (o, sg) in looks.items():
            on = visible and s_ == st
            o.location = p
            o.keyframe_insert("location", frame=frame)
            o.hide_render = not on
            o.keyframe_insert("hide_render", frame=frame)
            if sg:
                sg.hide_render = not on
                sg.keyframe_insert("hide_render", frame=frame)


def interp(keys, t):
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * ((t - t0) / (t1 - t0) if t1 > t0 else 0)
    return keys[-1][1] if t > keys[-1][0] else keys[0][1]


def cam_at(CK, t):
    for a, b in zip(CK, CK[1:]):
        if a[0] <= t <= b[0]:
            k = smooth01((t - a[0]) / (b[0] - a[0]))
            v = [a[i] + (b[i] - a[i]) * k for i in (1, 2, 3)]
            return v + [Vector(a[4]).lerp(Vector(b[4]), k)]
    a = CK[-1]
    return [a[1], a[2], a[3], Vector(a[4])]


def set_vis(objs, frame, on):
    for o in objs:
        if o.hide_render != (not on) or frame == 1:
            o.hide_render = not on
            o.keyframe_insert("hide_render", frame=frame)


def mat_color(mat, frame, hexa, hexb, k):
    b = mat.node_tree.nodes["Principled BSDF"]
    ca, cb = np.array(srgb(hexa)), np.array(srgb(hexb))
    b.inputs["Base Color"].default_value = (*(ca + (cb - ca) * k), 1)
    b.inputs["Base Color"].keyframe_insert("default_value", frame=frame)


def bubbles_setup(n=14):
    out = []
    for i in range(n):
        o = make_object(f"Blase_{i}", *uvsphere(0.06 + 0.03 * (i % 3), 12, 8), M["Blase"], "Video")
        out.append(o)
    return out


def bubbles_key(bub, frame, t, on):
    for i, o in enumerate(bub):
        ph = (t * 0.45 + i / len(bub)) % 1.0
        z = 1.2 + ph * (LIQ - 1.3)
        ang = i * 2.4
        o.location = (NAIL_X + 0.22 * math.cos(ang) + 0.05 * math.sin(t * 3 + i), 0.22 * math.sin(ang), z)
        o.keyframe_insert("location", frame=frame)
        o.hide_render = not (on and ph < 0.97)
        o.keyframe_insert("hide_render", frame=frame)


if VIDEO:
    plan = {"fps": FPS, "size": [1920, 1080], "video": VIDEO}
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
    coll_vis = lambda name: list(COLL[name].objects)
    T_STROM = coll_vis("TStrom")
    T_FALSCH = coll_vis("TFalsch")
    PF_A, PF_C = coll_vis("PfeileA"), coll_vis("PfeileC")
    G = {n: bpy.data.objects[n] for n in INSTANCES}
    batt_objs = list(COLL["Batterie"].objects)
    battC_objs = list(COLL["BatterieC"].objects)
    blech_objs = [bpy.data.objects[n] for n in ("Stecker_gelb", "Stecker_rot", "Klemme_Blech", "Klemme_Blech_Buchse", "Kupferblech_oben", "Kupferblech_unten")]
    nail_lo, sheet_lo = bpy.data.objects["Nagel_unten"], bpy.data.objects["Kupferblech_unten"]
    bub = bubbles_setup()
    if VIDEO == 1:
        DUR = 92.0
        objsA = setup_particles(SCEN["A"], "A")
        # (t, τ) für die Teilchenebene, (t, p) Fortschritt im Versuch (Zeitraffer)
        TAU = [(0, 0), (26, 0), (82, SCEN["A"]["T"]), (92, SCEN["A"]["T"])]
        PMAC = [(0, 0), (13, 0), (22, 1), (92, 1)]
        CK = [(0, -30, 18, 48, (5.0, 0, 6.0)), (6, -16, 14, 40, (5.0, 0, 5.5)), (12, -16, 14, 40, (5.0, 0, 5.5)),
              (15, -34, 8, 17, (-0.2, 0, 4.2)), (22, -22, 6, 16, (-0.2, 0, 4.2)),
              (25, 0, 6, 36, tuple(OFF + np.array([0, 0, 1.3]))), (32, 0, 6, 34, tuple(OFF + np.array([0, 0, 1.3]))),
              (35, 18, 8, 15, tuple(OFF + np.array([-6.5, 0, 0]))), (50, 24, 8, 14, tuple(OFF + np.array([-6.5, 0, 0]))),
              (53, -18, 8, 15, tuple(OFF + np.array([6.5, 0, 0]))), (66, -24, 8, 14, tuple(OFF + np.array([6.5, 0, 0]))),
              (69, 0, 6, 34, tuple(OFF + np.array([0, 0, 1.3]))), (92, 8, 8, 36, tuple(OFF + np.array([0, 0, 1.3])))]
        plan["captions"] = [
            (0.4, 5.6, "Verkupfern von Eisen", "Ein Beispiel für eine erzwungene Redoxreaktion", "title"),
            (6.0, 12.6, "Der Versuch", "Der Eisennagel hängt am Minuspol (gelbes Kabel), das Kupferblech am Pluspol (rotes Kabel) einer 4,5-V-Batterie. Beide tauchen in blaue Kupfersulfat-Lösung.", ""),
            (13.0, 23.4, "Nach etwa 10 Minuten (Zeitraffer)", "Der Nagel überzieht sich mit Kupfer. Das Kupferblech ist kaum verändert, die Lösung bleibt blau. Am Nagel steigen Gasbläschen auf (Wasserstoff aus der Säure).", ""),
            (24.0, 33.0, "Die Teilchenebene (stark vergrößert)", "Links die Oberfläche des Eisennagels, rechts das Kupferblech, dazwischen die Lösung mit Kupfer-Ionen Cu²⁺ und Sulfat-Ionen SO₄²⁻.", ""),
            (33.5, 51.0, "Am Eisennagel (Minuspol): Reduktion", "Ein Cu²⁺-Ion nimmt zwei Elektronen auf und wird zu einem Kupfer-Atom, das auf dem Nagel haften bleibt. Cu²⁺ ist der Elektronenakzeptor.", ""),
            (51.5, 67.0, "Am Kupferblech (Pluspol): Oxidation", "Ein Kupfer-Atom gibt zwei Elektronen ab und geht als Cu²⁺-Ion in Lösung. Cu ist der Elektronendonator. Das Blech wird dabei langsam dünner.", ""),
            (67.5, 80.0, "Die Lösung bleibt blau", "Für jedes Cu²⁺, das am Nagel zu Kupfer wird, löst sich am Blech ein Kupfer-Atom als Cu²⁺. Die Zahl der Cu²⁺-Ionen bleibt gleich.", ""),
            (80.5, 92.0, "Merke", "Elektronen fließen nur durch Drähte und Batterie, nie durch die Lösung. Die Batterie „pumpt“ sie vom Kupferblech zum Nagel: eine erzwungene Redoxreaktion (Elektrolyse).", ""),
        ]
        plan["equations"] = [(34.0, 92.0, ("Minuspol · Reduktion", "Cu²⁺ + 2 e⁻ → Cu"), ("Pluspol · Oxidation", "Cu → Cu²⁺ + 2 e⁻"))]
        plan["counter"] = [(67.5, 92.0, "A")]
        LABELS = [(6.5, 12.6, "Eisennagel (Minuspol)", "nagel"), (6.5, 12.6, "Kupferblech (Pluspol)", "blech"),
                  (7.0, 12.6, "Kupfersulfat-Lösung", "loesung"), (7.5, 12.6, "4,5-V-Batterie", "batterie"),
                  (8.0, 12.6, "Minuspol (langer Anschluss)", "pol_minus"), (8.0, 12.6, "Pluspol (kurzer Anschluss)", "pol_plus"),
                  (16.0, 23.0, "Gasbläschen", "blasen"),
                  (26.0, 33.0, "Eisennagel (Minuspol)", "t_nagel"), (26.0, 33.0, "Kupferblech (Pluspol)", "t_blech"),
                  (26.5, 33.0, "Lösung", "t_loesung"), (27.0, 33.0, "Batterie", "t_batterie")]
        SEGMENTS = [(0, DUR, "A")]
    else:
        DUR = 64.0
        objsB = setup_particles(SCEN["B"], "B")
        objsC = setup_particles(SCEN["C"], "C")
        TB = [(0, 0), (15, 0), (36, SCEN["B"]["T"]), (64, SCEN["B"]["T"])]
        TC = [(0, 0), (44, 0), (62, SCEN["C"]["T"]), (64, SCEN["C"]["T"])]
        PB = [(0, 0), (4.5, 0), (10, 1), (64, 1)]
        PC = [(0, 0), (37.5, 0), (43, 1), (64, 1)]
        CK = [(0, -14, 14, 22, (0, 0, 5.0)), (4, -30, 8, 18, (-0.4, 0, 4.4)), (10, -18, 6, 16, (-0.4, 0, 4.2)),
              (13, 0, 6, 34, tuple(OFF + np.array([0, 0, 1.3]))), (16, 18, 8, 15, tuple(OFF + np.array([-6.0, 0, 0]))),
              (34, 26, 8, 14, tuple(OFF + np.array([-6.0, 0, 0]))), (36.5, -16, 14, 40, (5.0, 0, 5.5)), (43, -10, 12, 36, (4.0, 0, 5.0)),
              (45.5, 0, 6, 34, tuple(OFF + np.array([0, 0, 1.3]))), (62, 8, 8, 34, tuple(OFF + np.array([0, 0, 1.3]))), (64, 8, 8, 34, tuple(OFF + np.array([0, 0, 1.3])))]
        plan["captions"] = [
            (0.4, 4.2, "Zum Vergleich", "Verkupfern ohne Strom – und falsch gepolt", "title"),
            (4.5, 12.6, "Ohne Strom", "Ein Eisennagel hängt ohne Batterie in der Kupfersulfat-Lösung. Auch er überzieht sich mit Kupfer, aber die Schicht ist schwammig und haftet schlecht.", ""),
            (13.0, 36.0, "Ohne Strom: Das Eisen gibt die Elektronen ab", "Eisen ist unedler als Kupfer. Ein Eisen-Atom gibt zwei Elektronen direkt an ein Cu²⁺-Ion ab. Kupfer setzt sich locker ab, das Fe²⁺-Ion geht in Lösung – der Nagel löst sich an. Die Reaktion läuft freiwillig ab.", ""),
            (36.5, 44.6, "Falsch gepolt", "Jetzt hängt der Nagel am Pluspol und das Kupferblech am Minuspol.", ""),
            (45.0, 64.0, "Falsch gepolt: Der Nagel löst sich auf", "Die Batterie zieht Elektronen vom Nagel ab: Eisen-Atome geben Elektronen ab und gehen als Fe²⁺ in Lösung. Am Kupferblech scheidet sich Kupfer ab.", ""),
        ]
        plan["equations"] = [(16.0, 36.0, ("Oxidation · Nagel", "Fe → Fe²⁺ + 2 e⁻"), ("Reduktion · an der Nageloberfläche", "Cu²⁺ + 2 e⁻ → Cu")),
                             (46.0, 64.0, ("Nagel am Pluspol · Oxidation", "Fe → Fe²⁺ + 2 e⁻"), ("Blech am Minuspol · Reduktion", "Cu²⁺ + 2 e⁻ → Cu"))]
        plan["total"] = [(22.0, 36.0, "Gesamt (freiwillig):  Fe + Cu²⁺ → Fe²⁺ + Cu")]
        plan["counter"] = [(16.0, 36.0, "B"), (46.0, 64.0, "C")]
        LABELS = [(5.0, 12.6, "Eisennagel", "nagel"),
                  (14.0, 20.0, "Nageloberfläche (Eisen)", "t_nagel"),
                  (38.0, 44.6, "Nagel jetzt am Pluspol", "nagel"), (38.0, 44.6, "Blech jetzt am Minuspol", "blech")]
        SEGMENTS = [(0, 36.25, "B"), (36.25, DUR, "C")]
    NF = int(DUR * FPS)
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, NF
    from bpy_extras.object_utils import world_to_camera_view
    W_, H_ = 1920, 1080
    per = []
    prev_seg = None
    for f in range(1, NF + 1):
        t = (f - 1) / FPS
        seg = [s for s in SEGMENTS if s[0] <= t < s[1] or (t >= s[1] and s is SEGMENTS[-1])][0][2]
        az, el, d_, tg = cam_at(CK, t)
        cam_target.location = tg
        cam_target.keyframe_insert("location", frame=f)
        cam.location = orbit(az, el, d_, tg)
        cam.keyframe_insert("location", frame=f)
        if VIDEO == 1:
            tau = interp(TAU, t); p = interp(PMAC, t)
            key_particles(objsA, f, tau)
            on_b = 13 <= t <= 24
        else:
            if seg == "B":
                tau = interp(TB, t); p = interp(PB, t)
                key_particles(objsB, f, tau, True)
                key_particles(objsC, f, 0, False)
            else:
                tau = interp(TC, t); p = interp(PC, t)
                key_particles(objsB, f, 0, False)
                key_particles(objsC, f, tau, True)
            on_b = False
        if seg != prev_seg:
            # Sichtbarkeit je Szenario
            set_vis(T_STROM, f, seg in ("A", "C"))
            set_vis([o for o in T_STROM if o.name.startswith("T_Pol_A")], f, seg == "A")
            set_vis(T_FALSCH, f, seg == "C")
            set_vis(PF_A, f, seg == "A")
            set_vis(PF_C, f, seg == "C")
            set_vis([G["T_Fe_voll"]], f, seg == "A")
            set_vis([G["T_Fe_rest"]], f, seg in ("B", "C"))
            set_vis([G["T_Cu_rest"]], f, seg == "A")
            set_vis([G["T_Cu_voll"]], f, seg == "C")
            set_vis(batt_objs, f, seg == "A")
            set_vis(battC_objs, f, seg == "C")
            set_vis(blech_objs, f, seg in ("A", "C"))
            prev_seg = seg
        if f % 3 == 1 or f == NF:
            if seg == "A":
                mat_color(M["NagelUnten"], f, C["fe"], C["cu"], smooth01(p))
                mat_color(M["Loesung"], f, C["loesung"], C["loesung"], 0)
            elif seg == "B":
                mat_color(M["NagelUnten"], f, C["fe"], "#5a3420", smooth01(p))
                mat_color(M["Loesung"], f, C["loesung"], "#5c9fd4", smooth01(p))
            else:
                mat_color(M["NagelUnten"], f, C["fe"], "#6d6a66", smooth01(p))
                mat_color(M["Loesung"], f, C["loesung"], "#4f9cc8", smooth01(p))
            sc_ = 1 - 0.35 * smooth01(p) if seg == "C" else 1.0
            nail_lo.scale = (sc_, sc_, 1)
            nail_lo.location = (NAIL_X * (1 - sc_), 0, 0)
            nail_lo.keyframe_insert("scale", frame=f)
            nail_lo.keyframe_insert("location", frame=f)
            sh = 1 - 0.25 * smooth01(p) if seg == "A" else 1.0 + (0.6 * smooth01(p) if seg == "C" else 0)
            sheet_lo.scale = (sh, 1, 1)
            sheet_lo.location = (SHEET_X * (1 - sh), 0, 0)
            sheet_lo.keyframe_insert("scale", frame=f)
            sheet_lo.keyframe_insert("location", frame=f)
        bubbles_key(bub, f, t, on_b)
        # Bildschirm-Positionen für Beschriftungen + Zähler
        row = {"t": round(t, 3), "seg": seg, "tau": round(tau, 3)}
        active = [L for L in LABELS if L[0] - 0.1 <= t <= L[1] + 0.1]
        if active:
            scene.frame_set(f)
            pos = {}
            for (_, _, text, anc) in active:
                v = world_to_camera_view(scene, cam, Vector(ANCHORS[anc]))
                pos[text] = [round(v.x * W_, 1), round((1 - v.y) * H_, 1), round(v.z, 2)]
            row["pos"] = pos
        per.append(row)
    for o in bpy.data.objects:
        ad = o.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                const = fc.data_path in ("hide_render",)
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT" if const else "LINEAR"
    plan["labels"] = [{"t0": a, "t1": b, "text": c, "anchor": d} for a, b, c, d in LABELS]
    plan["per_frame"] = per
    plan["frames"] = NF
    plan["counters"] = {k: counters(SCEN[k]) for k in SCEN}
    with open(os.path.join(ROOT, f"video/plan{VIDEO}.json"), "w") as fh:
        json.dump(plan, fh, ensure_ascii=False, separators=(",", ":"))
    scene.render.filepath = os.path.join(ROOT, f"video/frames{VIDEO}/f_")
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.frame_set(1)
    log("Video", VIDEO, "animiert:", NF, "Bilder")
else:
    # Standbild (Vorschau): Teilchenebene im Szenario A mitten im Ablauf, dazu Versuch zum Vergleich
    for o in COLL["TFalsch"].objects:
        o.hide_render = True
    bpy.data.objects["T_Fe_rest"].hide_render = True
    bpy.data.objects["T_Cu_voll"].hide_render = True
    objsA = setup_particles(SCEN["A"], "A") if DO_RENDER else []
    if DO_RENDER:
        key_particles(objsA, 1, 14.2)
        bub = bubbles_setup()
        bubbles_key(bub, 1, 3.0, True)
        mat_color(M["NagelUnten"], 1, C["fe"], C["cu"], 0.8)
        scene.frame_set(1)
        scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
        scene.render.image_settings.file_format = "JPEG"
        scene.render.image_settings.quality = 88
        set_view(*VIEW_PART)
        scene.render.filepath = RENDER_PATH
        bpy.ops.render.render(write_still=True)
        set_view(*VIEW_MACRO)
        scene.render.filepath = RENDER_PATH.replace("render.jpg", "versuch.jpg")
        bpy.ops.render.render(write_still=True)
        log("Vorschaubilder gerendert")
        set_view(-8, 10, 13, (0, 0, 5.0))
        scene.render.resolution_x = scene.render.resolution_y = 1024
        scene.render.image_settings.file_format = "PNG"
        icon_master = os.path.join(ICON_DIR, "icon-1024.png")
        scene.render.filepath = icon_master
        bpy.ops.render.render(write_still=True)
        for sz in (512, 192, 180):
            img = bpy.data.images.load(icon_master)
            img.scale(sz, sz)
            img.filepath_raw = os.path.join(ICON_DIR, f"icon-{sz}.png")
            img.file_format = "PNG"
            img.save()
            bpy.data.images.remove(img)
        log("Icons gerendert")

bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH, compress=True)
log("fertig:", BLEND_PATH)
