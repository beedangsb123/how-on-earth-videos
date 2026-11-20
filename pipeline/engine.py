"""How On Earth render engine v2 (video 002+).
Shared helpers: procedural textures (numpy fBm -> cairo), camera, particles, kinetic captions
with gold keywords, colour-wipe transitions (never black), labels, counters, badge, end card.
Rules baked in (PLAYBOOK "Making it NOT boring" + "Platform flags to avoid"):
 - every frame is filled edge to edge with texture (no flat bands, no fades to black)
 - captions 1-3 words, pop-in, CAPS/number words gold
"""
import cairo, math, random, numpy as np
from PIL import Image

W, H, FPS = 1080, 1920, 30


def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def eout(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def back(t):  # overshoot pop
    t = max(0.0, min(1.0, t)); s = 1.70158; t -= 1; return t * t * ((s + 1) * t + s) + 1
def lerp(a, b, t): return a + (b - a) * t
def lerpc(c1, c2, t): return tuple(lerp(a, b, t) for a, b in zip(c1, c2))
def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

NAVY, MID, BLUE, ORANGE, GOLD = map(hexc, ["0B1026", "1B2B5C", "3E5C9A", "F28C38", "FFC857"])
WHITE = (1, 1, 1)


# ---------------- textures ----------------
def fbm(h, w, octaves=6, seed=0, base=4):
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o
        g = rng.random((max(2, n * h // w), n)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += amp * np.asarray(im, np.float32) / 255; tot += amp; amp *= 0.55
    out /= tot; out = (out - out.min()) / (out.max() - out.min() + 1e-6); return out


def to_surface(rgb):
    """rgb float array HxWx3 in 0..1 -> cairo ImageSurface"""
    h, w, _ = rgb.shape
    a = np.empty((h, w, 4), np.uint8)
    a[..., 0] = np.clip(rgb[..., 2] * 255, 0, 255); a[..., 1] = np.clip(rgb[..., 1] * 255, 0, 255)
    a[..., 2] = np.clip(rgb[..., 0] * 255, 0, 255); a[..., 3] = 255
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    stride = s.get_stride(); buf = s.get_data()
    np.ndarray((h, stride // 4, 4), np.uint8, buf)[:, :w, :] = a
    s.mark_dirty(); return s


def ramp(n, stops):
    """n: 0..1 array; stops list of (pos, (r,g,b))"""
    out = np.zeros(n.shape + (3,), np.float32)
    for i in range(3):
        out[..., i] = np.interp(n, [p for p, _ in stops], [c[i] for _, c in stops])
    return out


def make_textures(seed=1):
    T = {}
    hh, ww = H, W
    y = np.linspace(0, 1, hh)[:, None] * np.ones((1, ww))
    # sky: blue top -> warm horizon, with clouds
    n = fbm(hh, ww, 6, seed, 3)
    sky = ramp(y, [(0, hexc("3C6FB4")), (0.25, hexc("6E9BD0")), (0.4, hexc("F2B27A")), (1, hexc("F7C98E"))])
    cl = np.clip((n - 0.45) * 2.2, 0, 1)[..., None]
    T["sky"] = to_surface(sky * (1 - 0.55 * cl) + 0.55 * cl * np.array([1, 0.97, 0.93]))
    # rock: banded warm brown volcanic rock
    n1 = fbm(hh, ww, 7, seed + 1, 6); n2 = fbm(hh, ww, 5, seed + 2, 2)
    strata = 0.5 + 0.5 * np.sin(y * 140 + n2 * 9)
    v = np.clip(0.55 * n1 + 0.25 * strata + 0.2 * n2, 0, 1)
    T["rock"] = to_surface(ramp(v, [(0, hexc("4A2E22")), (0.35, hexc("7A4A32")), (0.6, hexc("A8693F")), (0.8, hexc("C98E58")), (1, hexc("E2B07A"))]))
    # concrete: pale grey-beige with speckle
    sp = np.random.default_rng(seed + 3).random((hh, ww)).astype(np.float32)
    v = 0.7 * fbm(hh, ww, 6, seed + 4, 5) + 0.3 * sp
    T["concrete"] = to_surface(ramp(v, [(0, hexc("9C968C")), (0.5, hexc("CFC8BB")), (1, hexc("ECE6DA"))]))
    # water: teal/blue ripples
    v = fbm(hh, ww, 6, seed + 5, 8)
    rip = 0.5 + 0.5 * np.sin(y * 260 + v * 12)
    T["water"] = to_surface(ramp(0.6 * v + 0.4 * rip, [(0, hexc("1C5F7A")), (0.5, hexc("2F8FA8")), (0.85, hexc("6CC4CF")), (1, hexc("D8F4F2"))]))
    # terrain for maps
    v = fbm(hh, ww, 7, seed + 6, 4)
    T["terrain"] = to_surface(ramp(v, [(0, hexc("5E7B3E")), (0.4, hexc("8D9A55")), (0.6, hexc("C2A36A")), (0.8, hexc("A9744A")), (1, hexc("EAD7A8"))]))
    # sand (dry riverbed)
    v = fbm(hh, ww, 6, seed + 7, 10)
    T["sand"] = to_surface(ramp(v, [(0, hexc("B98B57")), (1, hexc("E8C88E"))]))
    # blueprint / x-ray background
    v = fbm(hh, ww, 6, seed + 8, 3)
    T["xray"] = to_surface(ramp(v, [(0, hexc("123A6B")), (0.5, hexc("1D5A9A")), (1, hexc("3D86C6"))]))
    return T


def tex(c, surf, dx=0, dy=0, alpha=1.0):
    p = cairo.SurfacePattern(surf); p.set_extend(cairo.EXTEND_REFLECT)
    m = cairo.Matrix(); m.translate(-dx, -dy); p.set_matrix(m)
    c.set_source(p)
    return p


def fill_tex(c, surf, dx=0, dy=0, alpha=1.0):
    """fill current path with texture"""
    tex(c, surf, dx, dy)
    if alpha >= 1: c.fill()
    else:
        c.save(); c.clip(); c.paint_with_alpha(alpha); c.restore()


def paint_tex(c, surf, dx=0, dy=0, alpha=1.0, pad=400):
    c.rectangle(-pad, -pad, W + 2 * pad, H + 2 * pad); fill_tex(c, surf, dx, dy, alpha)


def rrect(c, x, y, w, h, r):
    c.new_sub_path(); c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.close_path()


# ---------------- text ----------------
def fam(s): return "Montserrat" if set(s) & set("ṉṟṯ") else "Poppins"


def text(c, s, x, y, size, col=WHITE, align="center", alpha=1, stroke=0, weight=cairo.FONT_WEIGHT_BOLD):
    c.select_font_face(fam(s), cairo.FONT_SLANT_NORMAL, weight); c.set_font_size(size)
    ext = c.text_extents(s)
    xx = x - ext.x_advance / 2 if align == "center" else (x - ext.x_advance if align == "right" else x)
    c.move_to(xx, y); c.text_path(s)
    if stroke:
        c.set_source_rgba(0, 0, 0, 0.85 * alpha); c.set_line_width(stroke); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgba(*col, alpha); c.fill(); return ext.x_advance


def text_w(c, s, size):
    c.select_font_face(fam(s), cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    return c.text_extents(s).x_advance


def pop_text(c, s, x, y, size, t, col=GOLD, stroke=12, maxw=900):
    """big text that pops in with overshoot at t>=0"""
    if t <= 0: return
    w = text_w(c, s, size)
    if w > maxw: size *= maxw / w
    k = back(t / 0.35)
    c.save(); c.translate(x, y); c.scale(k, k); text(c, s, 0, 0, size, col=col, stroke=stroke, alpha=min(1, t / 0.12)); c.restore()


def label(c, s, y, t, x=W / 2, size=46, bg=GOLD, fg=NAVY):
    if t <= 0: return
    a = min(1, t / 0.2); k = back(t / 0.35)
    w = text_w(c, s, size) + 64; h = size + 34
    c.save(); c.translate(x, y + h / 2); c.scale(k, k)
    c.set_source_rgba(0, 0, 0, 0.35 * a); rrect(c, -w / 2 + 6, -h / 2 + 8, w, h, h / 2); c.fill()
    c.set_source_rgba(*bg, a); rrect(c, -w / 2, -h / 2, w, h, h / 2); c.fill()
    text(c, s, 0, size * 0.36, size, col=fg, alpha=a); c.restore()


def badge(c):
    c.save()
    w = text_w(c, "HOW ON EARTH?", 36) + 40
    c.set_source_rgba(*NAVY, 0.55); rrect(c, W / 2 - w / 2, 196, w, 58, 29); c.fill()
    text(c, "HOW ON EARTH?", W / 2, 238, 36, col=GOLD); c.restore()


# ---------------- captions ----------------
def chunks(cap, dur):
    words = cap.split(); out = []; cur = []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[-1] in ".,?!" or (len(cur) >= 2 and len(" ".join(cur)) > 16):
            out.append(cur); cur = []
    if cur: out.append(cur)
    tot = sum(len(" ".join(x)) + 4 for x in out); t = 0; res = []
    for x in out:
        d = dur * (len(" ".join(x)) + 4) / tot; res.append((t, t + d, x)); t += d
    return res


def is_key(w):
    core = w.strip(".,?!'\"")
    return (core.isupper() and len(core) > 1) or any(ch.isdigit() for ch in core)


def captions(c, cap, dur, t, y=1440):
    ch = chunks(cap, dur)
    for i, (a, b, ws) in enumerate(ch):
        if a <= t < b or (t >= b and i == len(ch) - 1):
            k = back((t - a) / 0.18)
            size = 84
            words = [w if is_key(w) else w for w in ws]
            full = " ".join(words)
            tw = text_w(c, full, size)
            if tw > 880: size *= 880 / tw; tw = 880
            c.save(); c.translate(W / 2, y); c.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
            x = -tw / 2
            for w in words:
                col = GOLD if is_key(w) else WHITE
                disp = w
                adv = text(c, disp, x, 0, size, col=col, align="left", stroke=16)
                x += adv + text_w(c, " ", size)
            c.restore(); return


# ---------------- particles ----------------
class Particles:
    def __init__(self, n, seed=0):
        r = random.Random(seed); self.p = [(r.random(), r.random(), r.random(), r.random()) for _ in range(n)]

    def dust(self, c, t, col=(1, 0.95, 0.85), alpha=0.5, speed=40, size=3):
        for a, b, s, ph in self.p:
            x = (a * W + math.sin(t * 0.7 + ph * 6) * 30) % W
            y = (b * H - t * speed * (0.5 + s)) % H
            c.set_source_rgba(*col, alpha * (0.4 + 0.6 * abs(math.sin(t * 2 + ph * 9))))
            c.arc(x, y, size * (0.5 + s), 0, 2 * math.pi); c.fill()

    def steam(self, c, t, x0, x1, y0, rise=500, alpha=0.35, col=(1, 1, 1)):
        for a, b, s, ph in self.p:
            life = (t * (0.25 + 0.2 * s) + ph) % 1.0
            x = lerp(x0, x1, a) + math.sin(life * 6 + ph * 7) * 40 * life
            y = y0 - life * rise * (0.6 + s)
            r = 18 + 90 * life * (0.5 + s)
            c.set_source_rgba(*col, alpha * math.sin(math.pi * life) * (0.5 + 0.5 * b))
            c.arc(x, y, r, 0, 2 * math.pi); c.fill()

    def sparks(self, c, t, x, y, alpha=1):
        for a, b, s, ph in self.p[:40]:
            life = (t * 2.5 + ph) % 1.0
            ang = a * 2 * math.pi; d = life * 120 * (0.5 + s)
            c.set_source_rgba(1, lerp(0.95, 0.5, life), 0.3, alpha * (1 - life))
            c.arc(x + math.cos(ang) * d, y + math.sin(ang) * d - 40 * life, 4 * (1 - life) + 1, 0, 2 * math.pi); c.fill()


def glow_stroke(c, path_fn, col, width, alpha=1, layers=4):
    for i in range(layers, 0, -1):
        path_fn(); c.set_source_rgba(*col, alpha * 0.12); c.set_line_width(width + i * width * 0.9); c.stroke()
    path_fn(); c.set_source_rgba(*col, alpha); c.set_line_width(width); c.stroke()


def wipe(c, t, col=GOLD, dur=0.22):
    """diagonal colour band sweeping across at a scene start (replaces fades to black)"""
    if t >= dur: return
    k = t / dur; x = lerp(-700, W + 700, k)
    c.save(); c.move_to(x - 260, -100); c.line_to(x + 260, -100); c.line_to(x - 140, H + 100); c.line_to(x - 660, H + 100); c.close_path()
    c.set_source_rgba(*col, 0.85); c.fill(); c.restore()


def thermal_rgb(h):
    """h 0 (cool blue) .. 1 (hot yellow-white)"""
    stops = [(0, (0.18, 0.45, 0.85)), (0.35, (0.55, 0.2, 0.6)), (0.6, (0.9, 0.25, 0.15)), (0.8, (1.0, 0.55, 0.1)), (1, (1.0, 0.92, 0.5))]
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if h <= p1: return lerpc(c0, c1, (h - p0) / (p1 - p0))
    return stops[-1][1]
