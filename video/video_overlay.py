#!/usr/bin/env python3
"""Blendet Titel, Untertitel, Gleichungen, Zähler und Beschriftungen in die Blender-Einzelbilder ein
und erzeugt daraus video/verkupfern_1.mp4 bzw. verkupfern_2.mp4 (H.264, 1920×1080, 25 fps).

Aufruf (nach dem Rendern der Einzelbilder):
    blender -b blender/video1.blend -a        # → video/frames1/f_0001.png …
    python3 video/video_overlay.py 1          # → video/verkupfern_1.mp4
    (entsprechend mit 2)

Benötigt: Pillow, ffmpeg. Texte und Zeiten stehen in video/plan1.json / plan2.json (erzeugt von build_verkupfern.py).
"""
import json, os, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NR = next((a for a in sys.argv[1:] if a in ("1", "2")), "1")
PLAN = json.load(open(os.path.join(HERE, f"plan{NR}.json")))
FRAMES = os.path.join(HERE, f"frames{NR}")
OUT = os.path.join(HERE, f"verkupfern_{NR}.mp4")
LOGO = os.path.join(ROOT, "web", "lmg-tech-logo.png")
W, H = PLAN["size"]
FPS = PLAN["fps"]

FD = "/usr/share/fonts/truetype/dejavu/"
F = {
    "title": ImageFont.truetype(FD + "DejaVuSerif-Bold.ttf", 64),
    "sub": ImageFont.truetype(FD + "DejaVuSans.ttf", 32),
    "head": ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 34),
    "text": ImageFont.truetype(FD + "DejaVuSans.ttf", 29),
    "eyebrow": ImageFont.truetype(FD + "DejaVuSansMono.ttf", 20),
    "eq": ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", 30),
    "label": ImageFont.truetype(FD + "DejaVuSans.ttf", 24),
    "tag": ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", 20),
}
PANEL = (9, 17, 33, 205)
LINE = (160, 196, 235, 70)
ORANGE = (243, 154, 46, 255)
TEXT = (231, 238, 248, 255)
MUTED = (195, 208, 226, 255)


def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rounded(size, radius=22, fill=PANEL, outline=LINE):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius, fill=fill, outline=outline, width=2)
    return im


@lru_cache(None)
def caption_card(head, text, kind):
    if kind == "title":
        tw = max(F["title"].getlength(head), F["sub"].getlength(text)) + 120
        im = rounded((int(tw), 190), 28)
        d = ImageDraw.Draw(im)
        d.text((60, 24), "ELEKTROCHEMIE · KLASSE 9 · VERKUPFERN", font=F["eyebrow"], fill=ORANGE)
        d.text((60, 54), head, font=F["title"], fill=TEXT)
        d.text((60, 134), text, font=F["sub"], fill=MUTED)
        return im
    maxw = 1240
    lines = wrap(text, F["text"], maxw)
    h = 34 + 46 + len(lines) * 40 + 26
    im = rounded((maxw + 80, h))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 22, 5, h - 22], 3, fill=ORANGE)
    d.text((40, 26), head, font=F["head"], fill=TEXT)
    for k, ln in enumerate(lines):
        d.text((40, 80 + k * 40), ln, font=F["text"], fill=MUTED)
    return im


@lru_cache(None)
def eq_card(kicker, formula):
    w = int(max(F["eq"].getlength(formula), F["eyebrow"].getlength(kicker)) + 56)
    im = rounded((w, 100), 16, fill=(9, 17, 33, 220), outline=(255, 200, 140, 90))
    d = ImageDraw.Draw(im)
    d.text((28, 16), kicker.upper(), font=F["eyebrow"], fill=ORANGE)
    d.text((28, 46), formula, font=F["eq"], fill=(255, 243, 224, 255))
    return im


@lru_cache(None)
def pill(text, font_key="label", border=(160, 196, 235, 150), color=TEXT):
    f = F[font_key]
    w = int(f.getlength(text) + 30)
    hh = 40 if font_key == "label" else 32
    im = Image.new("RGBA", (w, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, hh - 1], hh // 2, fill=(6, 12, 24, 215), outline=border, width=2)
    d.text((15, (hh - f.size) // 2 - 2), text, font=f, fill=color)
    return im


def fade(t, t0, t1, ramp=0.45):
    if t < t0 or t > t1:
        return 0.0
    return max(0.0, min(1.0, (t - t0) / ramp, (t1 - t) / ramp))


def paste(base, im, xy, alpha):
    if alpha <= 0.01:
        return
    if alpha < 0.99:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda a: int(a * alpha)))
    base.alpha_composite(im, (int(xy[0]), int(xy[1])))


@lru_cache(None)
def counter_card(sc, cu2, fe2, dep, dis):
    rows = [("Cu²⁺ in Lösung", cu2)]
    if sc != "A":
        rows.append(("Fe²⁺ in Lösung", fe2))
    rows += [("Cu abgeschieden", dep)] + ([("Cu abgelöst", dis)] if sc == "A" else [])
    im = rounded((360, 30 + 40 * len(rows)), 16, fill=(9, 17, 33, 220))
    d = ImageDraw.Draw(im)
    for k, (lab, v) in enumerate(rows):
        d.text((24, 16 + 40 * k), lab, font=F["label"], fill=MUTED)
        d.text((320, 16 + 40 * k), str(v), font=F["head"], fill=(127, 227, 240, 255) if lab.startswith("Cu²⁺") else TEXT, anchor="ra")
    return im


logo = None
if os.path.exists(LOGO):
    logo = Image.open(LOGO).convert("RGBA").resize((72, 72), Image.LANCZOS)
    m = Image.new("L", logo.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 71, 71], 16, fill=255)
    logo.putalpha(m)


def compose(k, fr):
    t = fr["t"]
    src = os.path.join(FRAMES, f"f_{k + 1:04d}.png")
    base = Image.open(src).convert("RGBA")
    if logo:
        paste(base, logo, (W - 72 - 40, H - 72 - 36), 0.9)
    # Untertitel / Titel
    for t0, t1, head, text, kind in PLAN["captions"]:
        a = fade(t, t0, t1)
        if a:
            im = caption_card(head, text, kind)
            y = (H - im.height) // 2 - 40 if kind == "title" else H - im.height - 40
            paste(base, im, ((W - im.width) // 2, y), a)
    # Gleichungen oben links / rechts
    for t0, t1, left, right in PLAN["equations"]:
        a = fade(t, t0, t1, 0.6)
        if a:
            il, ir = eq_card(*left), eq_card(*right)
            paste(base, il, (60, 40), a)
            paste(base, ir, (W - ir.width - 60, 40), a)
    # Gesamtgleichung (Video 2)
    for t0, t1, text in PLAN.get("total", []):
        a = fade(t, t0, t1, 0.6)
        if a:
            im = eq_card("Gesamtgleichung", text.split(":", 1)[-1].strip())
            paste(base, im, ((W - im.width) // 2, 40), a)
    # Zähler (oben rechts unter der Gleichung)
    for t0, t1, sc in PLAN.get("counter", []):
        a = fade(t, t0, t1, 0.5)
        if a:
            rows = PLAN["counters"][sc]
            r = rows[0]
            for row in rows:
                if row[0] <= fr["tau"] + 1e-6:
                    r = row
            paste(base, counter_card(sc, r[1], r[2], r[3], r[4]), (W - 420, 160), a)
    # Beschriftungen an projizierten Punkten
    pos = fr.get("pos", {})
    for L in PLAN["labels"]:
        a = fade(t, L["t0"], L["t1"], 0.4)
        p = pos.get(L["text"])
        if not a or not p or p[2] <= 0:
            continue
        im = pill(L["text"])
        d = ImageDraw.Draw(base)
        x, y = p[0], p[1]
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(243, 154, 46, int(255 * a)))
        paste(base, im, (x + 14, y - im.height - 4), a)
    return base.convert("RGB")


def main():
    frames = PLAN["per_frame"]
    missing = [k for k in range(len(frames)) if not os.path.exists(os.path.join(FRAMES, f"f_{k + 1:04d}.png"))]
    if missing:
        sys.exit(f"Es fehlen {len(missing)} Einzelbilder (z. B. f_{missing[0] + 1:04d}.png). Erst rendern: blender -b blender/video{NR}.blend -a")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", "hqdn3d=8:6:10:8", "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k, fr in enumerate(frames):
        ff.stdin.write(compose(k, fr).tobytes())
        if k % 250 == 0:
            print(f"{k}/{len(frames)}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("fertig:", OUT, f"{os.path.getsize(OUT) / 1e6:.1f} MB")


if __name__ == "__main__":
    if "--test" in sys.argv:
        # Einzelbilder zur Kontrolle: python3 video_overlay.py 1 --test 3 22 31 …
        for ts in sys.argv[sys.argv.index("--test") + 1:]:
            k = int(float(ts) * FPS)
            compose(k, PLAN["per_frame"][k]).save(os.path.join(HERE, f"test{NR}_{float(ts):05.1f}.jpg"), quality=88)
    else:
        main()
