"""Gemeinsame Bausteine (aus build_akku.py übernommen): Materialien, Objekte, Geometrie, Text, Kurven."""
import bpy, math, os
import numpy as np

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


MATS = {}


def make_mat(name, hexcol, rough=0.45, alpha=1.0, emit=0.0, metal=0.0, coat=0.0, trans=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    col = srgb(hexcol)
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*col, 1)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
        m.shadow_method = "NONE"
        m.show_transparent_back = False
    m.diffuse_color = (*col, alpha)
    MATS[name] = m
    return m


COLL = {}


def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COLL[name] = c
    return COLL[name]


def make_object(name, V, F, mat, collection, smooth=True, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata(np.asarray(V, dtype=np.float64).tolist(), [], [list(map(int, f)) for f in F])
    me.update(calc_edges=True)
    me.validate()
    me.polygons.foreach_set("use_smooth", [smooth] * len(me.polygons))
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    coll(collection).objects.link(o)
    return o


# --------------------------------------------------------------------------------------
# Geometrie-Bausteine (numpy, ohne bpy.ops)
# --------------------------------------------------------------------------------------
def uvsphere(r, seg=24, rings=14):
    V = [(0, 0, r)]
    for i in range(1, rings):
        th = math.pi * i / rings
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            V.append((r * math.sin(th) * math.cos(ph), r * math.sin(th) * math.sin(ph), r * math.cos(th)))
    V.append((0, 0, -r))
    F = []
    for j in range(seg):
        F.append((0, 1 + j, 1 + (j + 1) % seg))
    for i in range(rings - 2):
        a, b = 1 + i * seg, 1 + (i + 1) * seg
        for j in range(seg):
            F.append((a + j, b + j, b + (j + 1) % seg, a + (j + 1) % seg))
    last = len(V) - 1
    a = 1 + (rings - 2) * seg
    for j in range(seg):
        F.append((a + j, last, a + (j + 1) % seg))
    return np.array(V, float), F


def box(c, s):
    cx, cy, cz = c
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    V = [(cx + x * hx, cy + y * hy, cz + z * hz) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    F = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return np.array(V, float), F


def rbox(c, s, r=0.12, seg=4):
    """Quader mit abgerundeten Kanten (über eine Kugel mit verschobenen Hälften)."""
    V, F = uvsphere(r, seg * 4, seg * 2 + 1)
    V = V.copy()
    for k in range(3):
        h = s[k] / 2 - r
        V[:, k] = np.where(V[:, k] > 1e-9, V[:, k] + h, np.where(V[:, k] < -1e-9, V[:, k] - h, V[:, k]))
    V += np.array(c)
    return V, F


def cyl(p0, p1, r, seg=16, caps=True):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d)
    d /= L
    a = np.array([1, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(d, a); u /= np.linalg.norm(u)
    v = np.cross(d, u)
    V, F = [], []
    for k in range(seg):
        ph = 2 * math.pi * k / seg
        o = r * (math.cos(ph) * u + math.sin(ph) * v)
        V += [p0 + o, p1 + o]
    for k in range(seg):
        k2 = (k + 1) % seg
        F.append((2 * k, 2 * k2, 2 * k2 + 1, 2 * k + 1))
    if caps:
        V += [p0, p1]
        c0, c1 = 2 * seg, 2 * seg + 1
        for k in range(seg):
            k2 = (k + 1) % seg
            F.append((c0, 2 * k2, 2 * k))
            F.append((c1, 2 * k + 1, 2 * k2 + 1))
    return np.array(V, float), F


def cone(p0, p1, r, seg=24):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0; d /= np.linalg.norm(d)
    a = np.array([0, 0, 1]) if abs(d[2]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(d, a); u /= np.linalg.norm(u)
    v = np.cross(d, u)
    V = [p0 + r * (math.cos(2 * math.pi * k / seg) * u + math.sin(2 * math.pi * k / seg) * v) for k in range(seg)]
    V += [p1, p0]
    F = [(k, (k + 1) % seg, seg) for k in range(seg)] + [((k + 1) % seg, k, seg + 1) for k in range(seg)]
    return np.array(V, float), F


def merge(*parts):
    Vs, Fs, off = [], [], 0
    for V, F in parts:
        Vs.append(np.asarray(V, float))
        Fs += [tuple(i + off for i in f) for f in F]
        off += len(V)
    return np.concatenate(Vs), Fs


def instances(proto, positions):
    V0, F0 = proto
    return merge(*[(V0 + np.array(p), F0) for p in positions])


def text_object(name, body, size, loc, collection, mat, bold=False, extrude=0.02, rot=(math.pi / 2, 0, 0), align="CENTER"):
    cu = bpy.data.curves.new(name + "_c", "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "CENTER"
    fp = FONT_BOLD if bold else FONT_REG
    if os.path.exists(fp):
        cu.font = bpy.data.fonts.load(fp, check_existing=True)
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    me.name = name
    me.materials.clear()
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    coll(collection).objects.link(o)
    return o


def catmull(points, samples=24):
    P = np.array(points, float)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, samples, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return np.array(out)


def resample(P, n):
    P = np.asarray(P, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, P[:, k]) for k in range(3)], axis=1)


def polyline(points, step=0.05):
    out = []
    for a, b in zip(points, points[1:]):
        a, b = np.array(a, float), np.array(b, float)
        k = max(2, int(np.linalg.norm(b - a) / step))
        out += [a + (b - a) * t for t in np.linspace(0, 1, k, endpoint=False)]
    out.append(np.array(points[-1], float))
    return np.array(out)


def smooth01(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


