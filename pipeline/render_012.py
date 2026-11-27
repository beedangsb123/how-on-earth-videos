"""Video 012 — Lake Victoria (owner request, Bidhan 2026-11-26) = the FIRST "How On Earth Weather" (Tuesday show).
"This lake makes its own thunderstorms. Every single night." How: by day the land heats faster -> lake breeze, storms over
land (afternoon); at night the land cools, the lake stays warm -> land breezes from every shore converge over the water
-> night storms (NASA Earth Observatory, Thiery et al. 2016). Lake flies (Chaoborus) swarm in billions, visible from
miles away. The lake dried out ~17,300 years ago and refilled ~14,700 years ago. Max depth ~81 m (Statue of Liberty +
pedestal 93 m would stick out). Drains only via the Nile at Jinja, Uganda.
Structure NEW: weather show — cheerful studio presenter (Sarah, F, explains) + fed-up field reporter live on the shore
(Joseph, M, reacts big and gets the punchlines). Loop: "Let me guess tomorrow's forecast..." -> hook.
NEW LOOK v9 "weather broadcast" (different from 011 luggage tags / lift transition):
 - wx_plate(): glassy navy broadcast plate with a lime radar stripe + drawn weather icon, slides in from the left
 - live_strap(): red LIVE box + name bar for the field reporter
 - radar(): procedural rain-radar blobs (green/yellow/red) over the REAL MODIS lake image, drifting
 - tiles(): 5-day forecast tiles that pop in and flip (storm, storm, storm... FLIES)
 - wind arrows (day: outward lake breeze, night: converging land breezes), heat/night grades, drawn lightning
 - radar-sweep transition: the next scene is revealed by a rotating radar wedge
 - drained-lake map (lake pixels replaced by cracked mud), depth cross-section with the Statue of Liberty cut-out
Media: credits_012.txt. usage (work dir with meta.json, media/, media2/, clip_storm/, clip_swarm/, clip_midge/):
  python render_012.py stills <prefix> t1 t2 ...   |   python render_012.py full [a b out.mp4]"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish
from clips import Clip

Image.MAX_IMAGE_PIXELS = None
LIME = hexc("A6F03C"); SKY = hexc("5EC8FF"); HEAT = hexc("FF8A3D"); NAVYG = hexc("0E1A3A"); INK = hexc("101828")
RED = hexc("E5484D"); PAPER = hexc("F4F7FB"); YEL = hexc("FFD23F"); MUD = hexc("B88A55"); WATER = hexc("2A7FBF")
engine.CAP_ACCENT = LIME


def finish(a, t, **kw):
    return _finish(haze(a, t), t, **kw)


meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]
END = 2.2
STARTS.append(_t); DURS.append(END)
TOTAL = _t + END


def wt(i, key, default):
    """start (s, within line i) of the first spoken word starting with `key` — visuals follow the VOICE"""
    for w in meta[i]["words"]:
        if w[0].lower().strip(".,!?'\"").startswith(key.lower()): return w[1]
    return default


LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix):
    fs = [f for f in sorted(glob.glob(f"media*/{prefix}*")) if os.path.getsize(f) > 0]
    return fs[0] if fs else None


def P(prefix, **kw):
    f = M(prefix); return Photo(f, **kw) if f else None


DAY = P("lake_day", maxz=1.6)                 # MODIS 2024-03-31, NASA GSFC (PD) — lake centre (0.53, 0.47)
DRY = P("lake_dry", maxz=1.6)                 # same image, lake pixels replaced by cracked mud (Pixabay: daeron)
REG = P("Lake_Victoria__Lake_Kyoga", maxz=1.5)  # MODIS 2016-03-19, Jeff Schmaltz NASA GSFC (PD) — lake (0.33, 0.74)
SHORE = P("Shores_of_Lake_Victoria", maxz=1.3)  # Jiame Josh, CC BY-SA 4.0 (Ssese Islands)
JINJA = P("Jinja_source", maxz=1.3)           # Dror Feitelson, CC BY-SA 3.0
MUDP = P("pixabay_dry_mud", maxz=1.3)         # Pixabay: daeron
STORM = Clip("clip_storm"); SWARM = Clip("clip_swarm"); MIDGE = Clip("clip_midge")   # Pixabay: adege, adege, Hans
ST_IM = Image.open(M("statue"))               # Daniel Schwen (PD), sky keyed out
TX = make_textures(12)
_BL = {}
LC = (0.53, 0.47); LR = (0.175, 0.245)        # lake centre / radii (fractions of the MODIS image)


def pt(photo, k, z0, z1, f0, f1, u, v):
    """screen position of image point (u, v) (fractions) for a Photo.kb() call with the same arguments"""
    e = ease(k); z = lerp(z0, z1, e); fx = lerp(f0[0], f1[0], e); fy = lerp(f0[1], f1[1], e)
    iw, ih = photo.im.width, photo.im.height
    cw = W * photo.maxz / z; ch = H * photo.maxz / z
    cx = min(max(fx * iw, cw / 2), iw - cw / 2); cy = min(max(fy * ih, ch / 2), ih - ch / 2)
    return (u * iw - (cx - cw / 2)) * W / cw, (v * ih - (cy - ch / 2)) * H / ch


def blurred(key, photo, f=(0.5, 0.5), dim=0.6, z=1.0):
    if key not in _BL: _BL[key] = blur(_finish(photo.kb(0, z, z, f, f), 0), 14, dim)
    return _BL[key]


def bg(c, key, photo, t, f=(0.5, 0.5), dim=0.6, z=1.0):
    to_ctx(c, haze(blurred(key, photo, f, dim, z), t, amt=30).astype(np.uint8))


def counter(t, v0, v1, dur, fmt="{:,}"):
    return fmt.format(int(round(lerp(v0, v1, eout(t / dur))))) if t > 0 else fmt.format(v0)


def surf_rgba(rgba):
    """HxWx4 float 0..1 (straight alpha) -> cairo ARGB32 surface (premultiplied BGRA)"""
    a = rgba[..., 3:4]; pm = np.concatenate([rgba[..., 2::-1] * a, a], 2)
    buf = np.ascontiguousarray((pm * 255).clip(0, 255).astype(np.uint8))
    h, w = buf.shape[:2]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    np.frombuffer(s.get_data(), np.uint8).reshape(h, s.get_stride() // 4, 4)[:, :w] = buf
    s.mark_dirty(); return s


# ---------------- generic stickers (from look v8, kept) ----------------
def stamp(c, s, x, y, t, col=RED, size=120, ang=-0.1):
    if t <= 0: return
    k = min(1, t / 0.16); sc = lerp(1.6, 1.0, eout(k))
    w = text_w(c, s, size) + 80
    if w > 980: size *= 980 / w; w = 980
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(sc, sc)
    h = size * 1.3
    c.set_source_rgba(*INK, 0.65 * k); rrect(c, -w / 2, -h / 2, w, h, 20); c.fill()
    c.set_source_rgba(*col, k); c.set_line_width(12); rrect(c, -w / 2, -h / 2, w, h, 20); c.stroke()
    text(c, s, 0, size * 0.36, size, col=col, alpha=k); c.restore()


def pill(c, s, x, y, size, t, bgc=INK, fg=LIME, alpha=0.88):
    if t <= 0: return
    a = ease(t / 0.25); w = text_w(c, s, size) + 50
    c.set_source_rgba(*bgc, alpha * a); rrect(c, x - w / 2, y - size * 0.85, w, size * 1.4, size * 0.7); c.fill()
    text(c, s, x, y + size * 0.3, size, col=fg, alpha=a)


def arrow(c, x0, y0, x1, y1, col, width=14, alpha=1):
    c.set_source_rgba(*col, alpha); c.set_line_width(width); c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()
    a = math.atan2(y1 - y0, x1 - x0); L = width * 2.6
    c.move_to(x1 + math.cos(a) * L * 0.6, y1 + math.sin(a) * L * 0.6)
    c.line_to(x1 + math.cos(a + 2.4) * L, y1 + math.sin(a + 2.4) * L); c.line_to(x1 + math.cos(a - 2.4) * L, y1 + math.sin(a - 2.4) * L)
    c.close_path(); c.fill()


# ---------------- look v9: weather icons ----------------
def sun(c, x, y, r, t, alpha=1):
    c.save(); c.translate(x, y); c.rotate(t * 0.6)
    c.set_source_rgba(*YEL, alpha); c.set_line_width(r * 0.16); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(10):
        a = k * math.pi / 5; c.move_to(math.cos(a) * r * 1.3, math.sin(a) * r * 1.3); c.line_to(math.cos(a) * r * 1.7, math.sin(a) * r * 1.7); c.stroke()
    c.set_line_cap(cairo.LINE_CAP_BUTT)
    g = cairo.RadialGradient(-r * 0.3, -r * 0.3, r * 0.1, 0, 0, r); g.add_color_stop_rgba(0, 1, 0.97, 0.7, alpha); g.add_color_stop_rgba(1, 1, 0.72, 0.15, alpha)
    c.set_source(g); c.arc(0, 0, r, 0, 2 * math.pi); c.fill(); c.restore()


def cloud(c, x, y, s, col=(0.93, 0.95, 1.0), alpha=1, dark=False, face=None, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    base = (0.42, 0.46, 0.56) if dark else col
    c.set_source_rgba(0, 0, 0, 0.25 * alpha)
    for (cx, cy, r) in ((-55, 10, 42), (0, -18, 58), (55, 8, 44), (0, 22, 46)): c.arc(cx + 6, cy + 10, r, 0, 2 * math.pi); c.fill()
    g = cairo.LinearGradient(0, -80, 0, 70); g.add_color_stop_rgba(0, *[min(1, v + 0.12) for v in base], alpha); g.add_color_stop_rgba(1, *[v * 0.82 for v in base], alpha)
    c.set_source(g)
    for (cx, cy, r) in ((-55, 10, 42), (0, -18, 58), (55, 8, 44), (0, 22, 46)): c.arc(cx, cy, r, 0, 2 * math.pi); c.fill()
    if face == "angry":   # original cartoon mood: frowning brows + eyes
        c.set_source_rgba(*INK, alpha); c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND)
        for sd in (-1, 1):
            c.move_to(sd * 42, -22); c.line_to(sd * 12, -8); c.stroke()
            c.arc(sd * 26, 8, 8, 0, 2 * math.pi); c.fill()
        c.arc(0, 44, 18, math.pi * 1.15, math.pi * 1.85); c.stroke(); c.set_line_cap(cairo.LINE_CAP_BUTT)
    c.restore()


def bolt(c, x0, y0, x1, y1, seed, alpha=1, width=7, col=(1, 0.97, 0.75)):
    """jagged lightning bolt with glow"""
    if alpha <= 0: return
    r = np.random.default_rng(seed); n = 9; pts = []
    for k in range(n + 1):
        f = k / n; jit = 0 if k in (0, n) else r.uniform(-1, 1) * 38
        pts.append((lerp(x0, x1, f) + jit, lerp(y0, y1, f)))
    for wdt, a in ((width * 5, 0.12), (width * 2.5, 0.3), (width, 1.0)):
        c.set_source_rgba(*col, a * alpha); c.set_line_width(wdt); c.set_line_join(cairo.LINE_JOIN_ROUND)
        for j, q in enumerate(pts): (c.move_to if j == 0 else c.line_to)(*q)
        c.stroke()
    c.set_line_join(cairo.LINE_JOIN_MITER)


def storm_icon(c, x, y, s, t, alpha=1):
    cloud(c, x, y, s, dark=True, alpha=alpha)
    c.save(); c.translate(x, y); c.scale(s, s)
    c.set_source_rgba(*YEL, alpha); c.move_to(-8, 40); c.line_to(22, 40); c.line_to(4, 78); c.line_to(26, 78); c.line_to(-18, 135); c.line_to(-4, 92); c.line_to(-24, 92); c.close_path(); c.fill()
    c.restore()


def moon(c, x, y, r, alpha=1):
    c.save(); c.set_source_rgba(1, 0.96, 0.82, alpha); c.arc(x, y, r, 0, 2 * math.pi); c.fill()
    c.set_operator(cairo.OPERATOR_OVER); c.set_source_rgba(*NAVYG, alpha); c.arc(x + r * 0.45, y - r * 0.25, r * 0.85, 0, 2 * math.pi); c.fill(); c.restore()


def fly(c, x, y, s, t, alpha=1):
    """original cartoon fly: buzzing wings, round body, big eyes"""
    c.save(); c.translate(x, y); c.scale(s, s)
    wf = 0.5 + 0.5 * math.sin(t * 60)
    c.set_source_rgba(0.85, 0.95, 1, 0.55 * alpha)
    for sd in (-1, 1):
        c.save(); c.translate(sd * 10, -16); c.rotate(sd * (0.5 + 0.4 * wf)); c.scale(0.55, 1.0); c.arc(0, -22, 22, 0, 2 * math.pi); c.restore(); c.fill()
    c.set_source_rgba(0.12, 0.12, 0.14, alpha); c.save(); c.scale(1.25, 1); c.arc(0, 0, 20, 0, 2 * math.pi); c.restore(); c.fill()
    c.set_source_rgba(0.7, 0.1, 0.1, alpha)
    for sd in (-1, 1): c.arc(sd * 13, -10, 9, 0, 2 * math.pi); c.fill()
    c.restore()


def thermo(c, x, y, lvl, col, label, alpha=1):
    c.set_source_rgba(*PAPER, 0.95 * alpha); rrect(c, x - 26, y - 420, 52, 430, 26); c.fill(); c.arc(x, y + 20, 46, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(*col, alpha); c.arc(x, y + 20, 34, 0, 2 * math.pi); c.fill(); c.rectangle(x - 13, y - 20 - 370 * lvl, 26, 380 * lvl); c.fill()
    pill(c, label, x, y + 120, 40, 1, fg=col)


# ---------------- look v9: broadcast graphics ----------------
def wx_plate(c, s, x, y, size, t, icon=None, col=LIME, sub=None, maxw=960):
    """glassy navy weather plate: slides in from the left with a lime radar stripe + weather icon"""
    if t <= 0: return
    w = text_w(c, s, size)
    iw = size * 1.5 if icon else 0
    if w + iw + 90 > maxw: size *= (maxw - iw - 90) / w; w = maxw - iw - 90; iw = size * 1.5 if icon else 0
    bw, bh = w + iw + 90, size * 1.6
    k = eout(t / 0.3); x0 = x - bw / 2 - (1 - k) * 700; y0 = y - bh / 2
    c.save(); c.set_source_rgba(0, 0, 0, 0.35 * k); rrect(c, x0 + 8, y0 + 12, bw, bh, 22); c.fill()
    g = cairo.LinearGradient(0, y0, 0, y0 + bh); g.add_color_stop_rgba(0, 0.12, 0.2, 0.42, 0.95 * k); g.add_color_stop_rgba(1, 0.05, 0.09, 0.22, 0.95 * k)
    c.set_source(g); rrect(c, x0, y0, bw, bh, 22); c.fill()
    c.set_source_rgba(1, 1, 1, 0.14 * k); rrect(c, x0 + 6, y0 + 5, bw - 12, bh * 0.42, 18); c.fill()
    c.set_source_rgba(*col, k); rrect(c, x0, y0, 16, bh, 8); c.fill()
    sw = (t * 0.7) % 1.6 - 0.3                                       # light sweep
    if 0 < sw < 1:
        c.save(); rrect(c, x0, y0, bw, bh, 22); c.clip()
        g2 = cairo.LinearGradient(x0 + sw * bw - 120, 0, x0 + sw * bw + 120, 0)
        g2.add_color_stop_rgba(0, 1, 1, 1, 0); g2.add_color_stop_rgba(0.5, 1, 1, 1, 0.18); g2.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.set_source(g2); c.paint(); c.restore()
    if icon:
        ix, iy = x0 + 30 + iw / 2, y
        if icon == "sun": sun(c, ix, iy, size * 0.36, t)
        elif icon == "storm": storm_icon(c, ix, iy - size * 0.18, size * 0.0075, t)
        elif icon == "moon": moon(c, ix, iy, size * 0.42)
        elif icon == "fly": fly(c, ix, iy, size * 0.019, t)
        elif icon == "cloud": cloud(c, ix, iy, size * 0.0075)
    text(c, s, x0 + 45 + iw + w / 2, y + size * 0.36, size, col=WHITE, alpha=k)
    c.restore()
    if sub and t > 0.3:
        a = ease((t - 0.3) / 0.25); sz = 38; sw_ = text_w(c, sub, sz) + 44
        c.set_source_rgba(*col, 0.95 * a); rrect(c, x - sw_ / 2, y + bh / 2 + 10, sw_, sz * 1.35, sz * 0.67); c.fill()
        text(c, sub, x, y + bh / 2 + 10 + sz * 0.98, sz, col=INK, alpha=a)


def live_strap(c, name, place, t, y=1235):
    if t <= 0: return
    k = eout(t / 0.3); x0 = 60 - (1 - k) * 600
    blink = 0.65 + 0.35 * (math.sin(t * 6) > 0)
    c.set_source_rgba(*RED, k); rrect(c, x0, y - 44, 150, 66, 10); c.fill()
    c.set_source_rgba(1, 1, 1, blink * k); c.arc(x0 + 28, y - 11, 9, 0, 2 * math.pi); c.fill()
    text(c, "LIVE", x0 + 88, y + 2, 36, col=WHITE, alpha=k)
    nw = max(text_w(c, name, 40), text_w(c, place, 28)) + 50
    c.set_source_rgba(1, 1, 1, 0.95 * k); rrect(c, x0 + 160, y - 44, nw, 66, 10); c.fill()
    text(c, name, x0 + 185, y + 2, 40, col=INK, align="left", alpha=k)
    c.set_source_rgba(*NAVYG, 0.9 * k); rrect(c, x0 + 160, y + 26, nw, 42, 8); c.fill()
    text(c, place, x0 + 185, y + 57, 28, col=LIME, align="left", alpha=k)


def tile(c, x, y, top, icon, val, t, hl=False, flip=0.0, w=176, h=250):
    """forecast tile; flip 0..1 = card turning (scaled in x), drawn back face after 0.5"""
    if t <= 0: return
    k = back(min(1, t / 0.3)); sx = abs(math.cos(flip * math.pi)) if flip > 0 else 1
    c.save(); c.translate(x, y + (1 - min(1, t / 0.3)) * 80); c.scale(max(0.02, sx) * k, k)
    c.set_source_rgba(0, 0, 0, 0.35); rrect(c, -w / 2 + 6, -h / 2 + 10, w, h, 22); c.fill()
    g = cairo.LinearGradient(0, -h / 2, 0, h / 2)
    if hl: g.add_color_stop_rgb(0, 0.55, 0.85, 0.25); g.add_color_stop_rgb(1, 0.25, 0.5, 0.1)
    else: g.add_color_stop_rgb(0, 0.16, 0.26, 0.52); g.add_color_stop_rgb(1, 0.06, 0.1, 0.25)
    c.set_source(g); rrect(c, -w / 2, -h / 2, w, h, 22); c.fill()
    c.set_source_rgba(1, 1, 1, 0.5); c.set_line_width(3); rrect(c, -w / 2, -h / 2, w, h, 22); c.stroke()
    text(c, top, 0, -h / 2 + 46, 34, col=LIME if not hl else INK)
    if icon == "storm": storm_icon(c, 0, 0, 0.62, t)
    elif icon == "sun": sun(c, 0, 5, 42, t)
    elif icon == "fly":
        for j, (fx, fy) in enumerate(((-30, -10), (28, 6), (-6, 34), (34, -30))): fly(c, fx + 6 * math.sin(t * 7 + j), fy + 5 * math.cos(t * 9 + j), 0.75, t + j)
    elif icon == "cloud": cloud(c, 0, 0, 0.6)
    text(c, val, 0, h / 2 - 26, 30 if len(val) < 9 else 24, col=WHITE if not hl else INK)
    c.restore()


def sweep(c, t, dur, draw_prev, draw_new):
    """radar-sweep transition: the new scene is revealed by a rotating wedge (with a lime beam edge)"""
    k = eout(t / dur); cx, cy = W / 2, H * 0.42
    draw_prev()
    c.save(); c.move_to(cx, cy); c.arc(cx, cy, 2400, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k); c.close_path(); c.clip()
    draw_new(); c.restore()
    a = -math.pi / 2 + 2 * math.pi * k
    c.set_source_rgba(*LIME, 0.9 * (1 - k)); c.set_line_width(10); c.move_to(cx, cy); c.line_to(cx + 2400 * math.cos(a), cy + 2400 * math.sin(a)); c.stroke()


# ---------------- radar / map helpers ----------------
_NZ = {}


def noise_field():
    if "n" not in _NZ:
        n = fbm(560, 400, octaves=5, seed=21, base=5); _NZ["n"] = (n - n.min()) / (n.max() - n.min())
    return _NZ["n"]


def radar(c, cx, cy, rx, ry, t, inten=1.0, mode="lake"):
    """procedural rain radar painted in an ellipse (mode lake) or in a ring around it (mode ring). inten 0..1"""
    if inten <= 0: return
    n = noise_field(); h, w = 240, 240
    ox = int(t * 14) % 160; oy = int(t * 9) % 160
    f = n[oy:oy + h, ox:ox + w]
    yy, xx = np.mgrid[0:h, 0:w]; d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    if mode == "lake": env = np.clip((1.0 - d) / 0.25, 0, 1)
    else: env = np.clip(1 - np.abs(d - 0.75) / 0.25, 0, 1) * (d > 0.45)
    v = f * env; thr = lerp(0.95, 0.42, inten); v = np.clip((v - thr) / 0.35, 0, 1)
    col = np.zeros((h, w, 4), np.float32)
    g = np.clip(v / 0.4, 0, 1); yv = np.clip((v - 0.35) / 0.3, 0, 1); rv = np.clip((v - 0.7) / 0.3, 0, 1)
    col[..., 0] = lerp(0.2, 1.0, yv) * (1 - rv) + 0.95 * rv
    col[..., 1] = lerp(0.85, 0.85, yv) * (1 - rv) + 0.2 * rv
    col[..., 2] = 0.2 * (1 - yv)
    col[..., 3] = np.where(v > 0, 0.25 + 0.5 * g, 0) * min(1, inten * 1.5)
    s = surf_rgba(col)
    sc_x = (rx * (1.0 if mode == "lake" else 1.7)) * 2 / w; sc_y = (ry * (1.0 if mode == "lake" else 1.7)) * 2 / h
    c.save(); c.translate(cx - w / 2 * sc_x, cy - h / 2 * sc_y); c.scale(sc_x, sc_y)
    c.set_source_surface(s, 0, 0); c.get_source().set_filter(cairo.FILTER_BILINEAR); c.paint(); c.restore()


def lake_map(c, t, k, z0, z1, f0, f1, night=0.0, dry=0.0, heat=0.0):
    """MODIS lake map (with optional dry overlay / heat / night grades). Returns (cx, cy, rx, ry) of the lake on screen."""
    a = DAY.kb(k, z0, z1, f0, f1)
    if dry > 0: a = a * (1 - dry) + DRY.kb(k, z0, z1, f0, f1) * dry
    if heat > 0: a = a * (1 - 0.25 * heat) + np.array([255, 120, 40], np.float32) * 0.25 * heat
    to_ctx(c, finish(a, t, vign=0.25, night=night))
    cx, cy = pt(DAY, k, z0, z1, f0, f1, *LC)
    ex, _ = pt(DAY, k, z0, z1, f0, f1, LC[0] + LR[0], LC[1]); _, ey = pt(DAY, k, z0, z1, f0, f1, LC[0], LC[1] + LR[1])
    if heat > 0:   # cool lake vs hot land: keep the lake blue-ish
        c.save(); c.translate(cx, cy); c.scale(ex - cx, ey - cy); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.set_source_rgba(*SKY, 0.18 * heat); c.fill()
    return cx, cy, ex - cx, ey - cy


def breeze(c, cx, cy, rx, ry, t, inward, alpha=1, n=10, col=None):
    """animated wind arrows: outward lake breeze (day) or inward land breezes converging (night)"""
    col = col or (SKY if inward else HEAT)
    for j in range(n):
        a = j * 2 * math.pi / n + 0.2
        ph = (t * 0.9 + j * 0.13) % 1
        r0, r1 = (1.75, 0.55) if inward else (0.75, 1.7)
        r_ = lerp(r0, r1, ph); r2 = lerp(r0, r1, min(1, ph + 0.18))
        x0, y0 = cx + math.cos(a) * rx * r_, cy + math.sin(a) * ry * r_
        x1, y1 = cx + math.cos(a) * rx * r2, cy + math.sin(a) * ry * r2
        arrow(c, x0, y0, x1, y1, col, width=11, alpha=alpha * math.sin(math.pi * ph))


def flashes(c, cx, cy, rx, ry, t, rate=1.6, seed=5, alpha=1):
    """random lightning bolts inside the lake ellipse"""
    for j in range(3):
        per = 1 / rate; ph = (t + j * per / 3) % per; idx = int((t + j * per / 3) / per)
        if ph < 0.18:
            r = np.random.default_rng(seed * 100 + idx * 7 + j)
            x = cx + r.uniform(-0.6, 0.6) * rx; y = cy + r.uniform(-0.5, 0.3) * ry
            a = alpha * (1 - ph / 0.18)
            c.set_source_rgba(1, 1, 0.9, 0.12 * a); c.arc(x, y + 60, 220, 0, 2 * math.pi); c.fill()
            bolt(c, x + r.uniform(-30, 30), y - 220, x, y + 120, int(r.integers(1e6)), alpha=a)


def rain(c, t, n=90, alpha=0.5, seed=4, slant=0.25):
    r = np.random.default_rng(seed); xs = r.uniform(-200, W + 200, n); sp = r.uniform(1400, 2200, n); off = r.uniform(0, H, n)
    c.set_source_rgba(0.85, 0.92, 1, alpha); c.set_line_width(3)
    for x, s, o in zip(xs, sp, off):
        y = (o + t * s) % (H + 200) - 100; xx = x + slant * y
        c.move_to(xx, y); c.line_to(xx + slant * 50, y + 50); c.stroke()


def flies_cloud(c, t, n=24, x0=100, x1=980, y0=500, y1=1200, s=0.55, alpha=1, seed=9):
    r = np.random.default_rng(seed); px = r.uniform(0, 1, n); py = r.uniform(0, 1, n); ph = r.uniform(0, 6.28, n)
    for j in range(n):
        x = lerp(x0, x1, px[j]) + 40 * math.sin(t * 2.3 + ph[j]); y = lerp(y0, y1, py[j]) + 30 * math.cos(t * 3.1 + ph[j] * 1.3)
        fly(c, x, y, s * (0.7 + 0.5 * py[j]), t + ph[j], alpha)


def clipframe(clip, t, speed=1.0, vign=0.3, night=0.0):
    return finish(clip.at(t, speed).astype(np.float32), t, vign=vign, night=night)


# ---------------- scenes ----------------
HK = dict(z0=1.05, z1=1.14, f0=(0.53, 0.47), f1=(0.53, 0.47))


def hook_map(c, t, k=None):
    kk = min(1, t / 4) if k is None else k
    return lake_map(c, t, kk, HK["z0"], HK["z1"], HK["f0"], HK["f1"], night=0.35)


def s0(c, t, d):   # F hook: "This lake makes its own thunderstorms. Every single night."
    cx, cy, rx, ry = hook_map(c, t)
    radar(c, cx, cy, rx, ry, t, inten=0.75 + 0.25 * ease(t / 2))
    flashes(c, cx, cy, rx, ry, t + 0.12, rate=1.5)
    wx_plate(c, "THIS LAKE MAKES", W / 2, 380, 70, t + 1.0, icon="storm")
    pk = back(min(1, (t + 0.4) / 0.3)); c.save(); c.translate(W / 2, 560); c.scale(pk, pk)
    text(c, "ITS OWN STORMS?!", 0, 0, 90, col=LIME, stroke=16); c.restore()
    pill(c, "LAKE VICTORIA, EVERY NIGHT", W / 2, 1200, 44, t + 1.0, fg=YEL)
    TN = wt(0, "night", 3.1)
    if t > TN - 0.1: moon(c, 880, 640, 56 * back(min(1, (t - TN + 0.1) / 0.3)))
    source_tag(c, "Satellite: NASA MODIS (PD) · radar: illustration", t - 0.3, y=1350, size=20)


def s1(c, t, d):   # M "[sighs] Yes. I'm standing in one."
    to_ctx(c, clipframe(STORM, t, night=0.15))
    rain(c, t, alpha=0.45)
    TS = wt(1, "standing", 1.1)
    if TS - 0.05 < t < TS + 0.35:
        a = 1 - (t - TS + 0.05) / 0.4; c.set_source_rgba(1, 1, 1, 0.35 * a); c.paint(); bolt(c, 640, 120, 560, 980, 77, alpha=a, width=9)
    live_strap(c, "JOSEPH", "LIVE . LAKE VICTORIA", t + 0.6)
    source_tag(c, "Storm footage (illustrative): adege / Pixabay", t - 0.3, y=1350, size=20)


def s2(c, t, d):   # F "Welcome to How On Earth Weather! Joseph is live at Lake Victoria."
    k = min(1, t / d); f0, f1 = (0.42, 0.55), (0.33, 0.72)
    a = REG.kb(k, 1.0, 1.35, f0, f1); to_ctx(c, finish(a, t, vign=0.25))
    wx_plate(c, "HOW ON EARTH WEATHER", W / 2, 400, 74, t - 0.05, icon="sun")
    TV = wt(2, "victoria", 3.0) - 0.1
    if t > TV:
        x, y = pt(REG, k, 1.0, 1.35, f0, f1, 0.33, 0.74)
        c.set_source_rgba(*LIME, 0.9); c.set_line_width(6); c.arc(x, y, 60 + 8 * math.sin(t * 6), 0, 2 * math.pi); c.stroke()
        pill(c, "LAKE VICTORIA", x, y - 110, 50, t - TV)
    TJ = wt(2, "joseph", 1.9) - 0.1
    if t > TJ: live_strap(c, "JOSEPH", "LIVE . LAKE VICTORIA", t - TJ)
    source_tag(c, "Satellite: Jeff Schmaltz, NASA MODIS (PD)", t - 0.3, y=1350, size=20)


def s3(c, t, d):   # M "Africa's biggest lake. Bigger than Lake Michigan... and moodier."
    a = SHORE.kb(min(1, t / d), 1.0, 1.12, (0.4, 0.5), (0.5, 0.55)); to_ctx(c, finish(a, t, vign=0.25))
    wx_plate(c, "AFRICA'S BIGGEST LAKE", W / 2, 400, 70, t - 0.05, col=YEL)
    TM = wt(3, "michigan", 1.6) - 0.1
    if t > TM:   # area comparison bars (Victoria > Michigan)
        k = eout((t - TM) / 0.6); x0 = 130
        c.set_source_rgba(*INK, 0.75); rrect(c, 90, 600, 900, 330, 26); c.fill()
        text(c, "SURFACE AREA", W / 2, 655, 38, col=LIME)
        for j, (lab, frac, col) in enumerate((("LAKE VICTORIA", 1.0, WATER), ("LAKE MICHIGAN", 0.965, hexc("7E8FA8")))):
            y = 730 + j * 110
            c.set_source_rgb(*col); rrect(c, x0, y - 40, 820 * frac * k, 80, 16); c.fill()
            text(c, lab, x0 + 24, y + 14, 38, col=WHITE, align="left")
    TD = wt(3, "moodier", 3.0) - 0.1
    if t > TD:
        s_ = back(min(1, (t - TD) / 0.3)); cloud(c, 800, 1080, 1.1 * s_, dark=True, face="angry")
        bolt(c, 780, 1140, 740, 1300, 3, alpha=0.6 + 0.4 * math.sin(t * 20))
    source_tag(c, "Photo: Jiame Josh / CC BY-SA 4.0 · area: Victoria ~60,000-69,000 km2 > Michigan ~58,000 km2", t - 0.3, y=1350, size=17)


MAPK = dict(z0=1.0, z1=1.06, f0=(0.53, 0.47), f1=(0.53, 0.47))


def s4(c, t, d):   # F "Here's the trick. By day, the land heats up faster, so storms pop up over land."
    TD = wt(4, "day", 0.9); TH = wt(4, "heats", 1.6); TS = wt(4, "storms", 3.4)
    heat = ease((t - TH) / 0.8)
    cx, cy, rx, ry = lake_map(c, t, min(1, t / d), MAPK["z0"], MAPK["z1"], MAPK["f0"], MAPK["f1"], heat=heat)
    if t > TH: breeze(c, cx, cy, rx, ry, t, inward=False, alpha=heat)
    if t > TS: radar(c, cx, cy, rx, ry, t, inten=ease((t - TS) / 0.6), mode="ring")
    if t > TS:
        for j, a in enumerate((0.3, 1.6, 2.9, 4.4, 5.5)):
            s_ = back(min(1, (t - TS - j * 0.08) / 0.3)) if t - TS - j * 0.08 > 0 else 0
            if s_ > 0: storm_icon(c, cx + math.cos(a) * rx * 1.45, cy + math.sin(a) * ry * 1.35 - 40, 0.55 * s_, t)
    wx_plate(c, "BY DAY: STORMS OVER LAND", W / 2, 400, 64, t - TD + 0.2, icon="sun", col=HEAT)
    if t > TH: pill(c, "LAND HEATS UP FASTER", W / 2, 1200, 46, t - TH, fg=HEAT)
    source_tag(c, "NASA Earth Observatory · storms peak over land ~4:30 pm", t - 0.3, y=1350, size=20)


def s5(c, t, d):   # M "[laughs] Perfect! So I just stay on the beach?"
    a = SHORE.kb(min(1, t / d), 1.15, 1.3, (0.3, 0.75), (0.32, 0.72)); to_ctx(c, finish(a, t, vign=0.25))
    sun(c, 860, 600, 70, t)
    TB = wt(5, "beach", 1.8) - 0.1
    if t > 0.2:   # beach umbrella pops up
        s_ = back(min(1, (t - 0.2) / 0.35)); c.save(); c.translate(330, 1110); c.scale(s_, s_); c.rotate(-0.12)
        c.set_source_rgb(*PAPER); c.set_line_width(10); c.move_to(0, -230); c.line_to(0, 120); c.stroke()
        for j in range(6):
            c.set_source_rgb(*((RED if j % 2 else PAPER))); c.move_to(0, -240)
            c.arc(0, -150, 210, math.pi + j * math.pi / 6, math.pi + (j + 1) * math.pi / 6); c.close_path(); c.fill()
        c.restore()
    live_strap(c, "JOSEPH", "LIVE . THE BEACH", t + 1)
    if t > TB: tile(c, 790, 930, "BEACH", "sun", "DRY", t - TB, hl=True)
    if t > TB + 0.7: stamp(c, "...FOR NOW", 760, 1150, t - TB - 0.7, col=YEL, size=56, ang=0.06)


def s6(c, t, d):   # F "Until night. The land cools off, but the lake stays warm."
    TN = wt(6, "night", 0.4); TC = wt(6, "cools", 1.3); TW = wt(6, "warm", 2.9)
    nt = 0.8 * ease((t - TN + 0.1) / 0.8)
    cx, cy, rx, ry = lake_map(c, t, 0.5 + 0.5 * min(1, t / d), MAPK["z0"], MAPK["z1"], MAPK["f0"], MAPK["f1"], night=nt)
    if t > TN: moon(c, 870, 620, 60 * back(min(1, (t - TN) / 0.3)))
    if t > TC: thermo(c, 170, 1060, lerp(0.75, 0.25, ease((t - TC) / 1.0)), SKY, "LAND", alpha=1)
    if t > TW - 0.2: thermo(c, 910, 1060, 0.8, HEAT, "LAKE", alpha=1)
    if t > TW: pill(c, "STAYS WARM", 900, 680, 40, t - TW, fg=HEAT)
    wx_plate(c, "BY NIGHT", W / 2, 400, 74, t - TN + 0.1, icon="moon", col=SKY)
    source_tag(c, "NASA Earth Observatory: water keeps its heat longer than land", t - 0.3, y=1350, size=20)


def s7(c, t, d):   # F "Breezes from every shore crash together over the water... and up it goes."
    TC = wt(7, "crash", 1.4); TU = wt(7, "up", 3.4)
    cx, cy, rx, ry = lake_map(c, t + 3, 1.0, MAPK["z0"], MAPK["z1"], MAPK["f0"], MAPK["f1"], night=0.8)
    breeze(c, cx, cy, rx, ry, t, inward=True, n=12)
    if t > TC:
        k = ease((t - TC) / 0.4); c.set_source_rgba(1, 1, 1, 0.5 * (1 - k)); c.arc(cx, cy, 80 + 200 * k, 0, 2 * math.pi); c.fill()
    if t > TU - 0.3:
        u = ease((t - TU + 0.3) / 0.8); radar(c, cx, cy, rx, ry, t, inten=u)
        cloud(c, cx, cy - 120 - 200 * u, 1.0 + 1.3 * u, dark=True, alpha=min(1, u * 1.5))
        flashes(c, cx, cy, rx, ry, t, rate=2.0, alpha=u)
    wx_plate(c, "LAND BREEZES CRASH TOGETHER", W / 2, 400, 60, t + 1, icon="moon", col=SKY)
    source_tag(c, "NASA Earth Observatory: land breezes converge over the lake at night", t - 0.3, y=1350, size=20)


def s8(c, t, d):   # M "[surprised] The whole coastline ganging up on one lake?!"
    cx, cy, rx, ry = lake_map(c, t + 6, 1.0, MAPK["z0"], MAPK["z1"], MAPK["f0"], MAPK["f1"], night=0.8)
    breeze(c, cx, cy, rx, ry, t + 3, inward=True, n=16, col=RED)
    radar(c, cx, cy, rx, ry, t + 3, inten=1.0); flashes(c, cx, cy, rx, ry, t + 3, rate=2.2)
    TG = wt(8, "ganging", 1.0) - 0.05
    stamp(c, "GANGING UP?!", W / 2, 420, t - TG, col=RED, size=100, ang=-0.05)
    live_strap(c, "JOSEPH", "LIVE . VERY WET", t + 1)


DAYS = ["MON", "TUE", "WED", "THU", "FRI"]


def s9(c, t, d):   # F "Every night. And the extended forecast... clouds of flies."
    bg(c, "night", DAY, t, (0.53, 0.47), dim=0.5, z=1.0)
    c.set_source_rgba(*NAVYG, 0.35); c.paint()
    TE = wt(9, "every", 0.1); TF = wt(9, "flies", 3.0) - 0.15; TX_ = wt(9, "extended", 1.3)
    wx_plate(c, "EXTENDED FORECAST", W / 2, 400, 70, t - TX_ + 0.2, icon="cloud")
    for j, dd in enumerate(DAYS):
        x = 130 + j * 205; y = 850 if j % 2 == 0 else 880
        x = W / 2 + (j - 2) * 200
        last = j == 4
        fl = ease((t - TF) / 0.35) if last else 0
        if last and fl > 0.5: tile(c, x, 860, dd, "fly", "FLIES", t - TE - j * 0.12, hl=True, flip=fl)
        else: tile(c, x, 860, dd, "storm", "STORM", t - TE - j * 0.12, flip=fl)
    if t > TF + 0.4: stamp(c, "CLOUDS OF FLIES", W / 2, 1160, t - TF - 0.4, col=LIME, size=70, ang=-0.04)


def s10(c, t, d):  # M "[surprised] I'm sorry... flies?!"
    to_ctx(c, clipframe(SWARM, t + 1))
    flies_cloud(c, t, n=10, s=0.7)
    TF = wt(10, "flies", 0.8) - 0.05
    stamp(c, "FLIES?!", W / 2, 760, t - TF, col=LIME, size=150, ang=0.07)
    live_strap(c, "JOSEPH", "LIVE . CONFUSED", t + 1)


def s11(c, t, d):  # F "Lake flies. Billions of them, in swarms you can see from miles away."
    TB = wt(11, "billions", 0.9); TM = wt(11, "miles", 3.4) - 0.1
    to_ctx(c, clipframe(MIDGE if t < TB + 1.2 else SWARM, t + 2))
    flies_cloud(c, t, n=int(8 + 22 * ease((t - TB) / 1.5)), s=0.45, seed=13)
    wx_plate(c, "LAKE FLIES", W / 2, 400, 74, t + 0.5, icon="fly", col=LIME)
    if t > TB: pill(c, "BILLIONS", W / 2, 700, 80, t - TB, fg=YEL)
    if t > TM:   # binoculars-ish distance bar
        k = eout((t - TM) / 0.5); c.set_source_rgba(*PAPER, 0.9); c.set_line_width(6)
        c.move_to(160, 1150); c.line_to(160 + 760 * k, 1150); c.stroke()
        for xx in (160, 160 + 760 * k): c.move_to(xx, 1125); c.line_to(xx, 1175); c.stroke()
        pill(c, "SEEN FROM MILES AWAY", W / 2, 1080, 44, t - TM, fg=LIME)
    source_tag(c, "Swarm footage (illustrative): Hans, adege / Pixabay · lake flies: Chaoborus (phantom midges)", t - 0.3, y=1350, size=18)


def s12(c, t, d):  # M "[sarcastic] Fantastic. Cloudy... with a chance of flies."  (own meme forecast card)
    bg(c, "swarm", SHORE, t, (0.5, 0.5), dim=0.45, z=1.0)
    TC = wt(12, "cloudy", 1.0) - 0.1; TF = wt(12, "flies", 2.6) - 0.1
    c.set_source_rgba(*INK, 0.85); rrect(c, 110, 560, 860, 620, 40); c.fill()
    c.set_source_rgba(*LIME, 1); c.set_line_width(6); rrect(c, 110, 560, 860, 620, 40); c.stroke()
    text(c, "TODAY'S FORECAST", W / 2, 640, 46, col=LIME)
    if t > TC:
        s_ = back(min(1, (t - TC) / 0.3)); cloud(c, W / 2, 830, 1.4 * s_)
        text(c, "CLOUDY", W / 2, 1000, 64, col=WHITE, alpha=min(1, (t - TC) / 0.2))
    if t > TF:
        flies_cloud(c, t, n=14, x0=250, x1=830, y0=880, y1=980, s=0.5, seed=4)
        pill(c, "CHANCE OF FLIES: HIGH", W / 2, 1100, 50, t - TF, fg=YEL, bgc=hexc("2A3A5A"))
    live_strap(c, "JOSEPH", "LIVE . NOT IMPRESSED", t + 1)


def s13(c, t, d):  # F "Could be worse. Seventeen thousand years ago, this lake was completely dry."
    TS = wt(13, "seventeen", 0.9) - 0.1; TD = wt(13, "dry", 3.9) - 0.3
    dry = ease((t - TS - 0.3) / max(0.6, TD - TS))
    cx, cy, rx, ry = lake_map(c, t, min(1, t / d), 1.0, 1.15, LC, LC, dry=dry)
    if t > TS:
        c.set_source_rgba(*hexc("C9A46A"), 0.15 * (1 - dry)); c.paint()
        wx_plate(c, counter(t - TS, 0, 17000, 1.2) + " YEARS AGO", W / 2, 400, 70, t - TS, icon="sun", col=YEL)
    if t > TD + 0.3: stamp(c, "COMPLETELY DRY", W / 2, 1150, t - TD - 0.3, col=YEL, size=80, ang=-0.05)
    source_tag(c, "Lake last dried out ~17,300 yrs ago (Verheyen et al. 2003) · map: illustration", t - 0.3, y=1350, size=19)


def s14(c, t, d):  # M "[curious] Dry? The whole thing?"
    a = MUDP.kb(min(1, t / d), 1.0, 1.15, (0.5, 0.5), (0.5, 0.55)); to_ctx(c, finish(a, t, vign=0.3))
    TW = wt(14, "whole", 0.6) - 0.05
    stamp(c, "THE WHOLE THING?!", W / 2, 760, t - TW, col=YEL, size=96, ang=0.05)
    live_strap(c, "JOSEPH", "LIVE . DISBELIEF", t + 1)
    source_tag(c, "Photo: daeron / Pixabay", t - 0.3, y=1350, size=20)


def s15(c, t, d):  # F "Gone, for over two thousand years. Then the rain came back."
    TT = wt(15, "two", 0.6); TR = wt(15, "rain", 2.3) - 0.1
    refill = ease((t - TR - 0.2) / 1.0)
    cx, cy, rx, ry = lake_map(c, t, min(1, t / d), 1.15, 1.05, LC, LC, dry=1 - refill)
    if t > TR: rain(c, t, n=110, alpha=0.5)
    if t < TR:
        wx_plate(c, "GONE...", W / 2, 400, 80, t + 0.5, icon="sun", col=YEL)
        if t > TT: pill(c, "2,000+ YEARS", W / 2, 1180, 64, t - TT, fg=YEL)
    else:
        wx_plate(c, "...THEN THE RAIN CAME BACK", W / 2, 400, 64, t - TR, icon="cloud", col=SKY)
    source_tag(c, "Dry ~17,300 to ~14,700 years ago (Verheyen et al. 2003) · map: illustration", t - 0.3, y=1350, size=19)


def s16(c, t, d):  # M "[laughs] So it's basically a giant puddle!"
    a = SHORE.kb(min(1, t / d), 1.0, 1.1, (0.55, 0.5), (0.6, 0.48)); to_ctx(c, finish(a, t, vign=0.25))
    TP = wt(16, "giant", 1.3) - 0.1
    if t > 0.2:   # rubber duck bobbing (original drawing)
        s_ = back(min(1, (t - 0.2) / 0.35)); bob = 10 * math.sin(t * 4)
        c.save(); c.translate(760, 1060 + bob); c.scale(s_, s_); c.rotate(0.08 * math.sin(t * 3))
        c.set_source_rgb(*YEL); c.save(); c.scale(1.5, 1); c.arc(0, 0, 70, 0, 2 * math.pi); c.restore(); c.fill()
        c.arc(55, -80, 50, 0, 2 * math.pi); c.fill()
        c.set_source_rgb(*HEAT); c.move_to(95, -85); c.line_to(140, -75); c.line_to(95, -62); c.close_path(); c.fill()
        c.set_source_rgb(0.1, 0.1, 0.1); c.arc(68, -92, 8, 0, 2 * math.pi); c.fill(); c.restore()
    stamp(c, "GIANT PUDDLE", W / 2, 560, t - TP, col=SKY, size=110, ang=-0.06)
    live_strap(c, "JOSEPH", "LIVE . DELIGHTED", t + 1)


def s17(c, t, d):  # F "Kind of! At its deepest, the Statue of Liberty's torch would stick out."
    bg(c, "shore", SHORE, t, (0.5, 0.45), dim=0.55, z=1.0)
    TD = wt(17, "deepest", 0.9) - 0.1; TS = wt(17, "statue", 1.8) - 0.1; TO = wt(17, "stick", 3.4) - 0.1
    x0, x1, ytop, ybed = 90, 990, 520, 1260   # cross-section panel; scale: 93 m = (ybed - y93)
    y93 = 560; ppm = (ybed - y93) / 93.0; y81 = ybed - 81 * ppm
    c.save(); rrect(c, x0, ytop - 40, x1 - x0, ybed - ytop + 110, 30); c.clip()
    g = cairo.LinearGradient(0, ytop, 0, ybed); g.add_color_stop_rgba(0, 0.55, 0.75, 0.95, 0.85); g.add_color_stop_rgba(1, 0.2, 0.35, 0.55, 0.85)
    c.set_source(g); c.paint()
    wl = lerp(ybed, y81, ease((t - TD) / 0.7)) if t > TD else ybed
    c.set_source_rgba(*WATER, 0.55); c.rectangle(x0, wl, x1 - x0, ybed - wl); c.fill()
    c.set_source_rgba(1, 1, 1, 0.8); c.set_line_width(4)
    for xx in range(x0, x1, 30): c.move_to(xx, wl + 5 * math.sin(xx / 15 + t * 4)); c.line_to(xx + 15, wl + 5 * math.sin((xx + 15) / 15 + t * 4)); c.stroke()
    c.set_source_rgb(*MUD); c.rectangle(x0, ybed, x1 - x0, 200); c.fill()
    c.restore()
    if t > TS:   # pedestal (drawn) + statue cut-out, rising into place
        k = eout((t - TS) / 0.6); off = (1 - k) * 500
        ped_h = 47 * ppm; sx = 560
        c.save(); c.rectangle(x0, ytop - 60, x1 - x0, ybed - ytop + 60); c.clip()
        c.set_source_rgb(*hexc("A89C8A")); c.rectangle(sx - 95, ybed - ped_h + off, 190, ped_h); c.fill()
        c.set_source_rgb(*hexc("8C8170")); c.rectangle(sx - 120, ybed - ped_h + off, 240, 24); c.fill()
        st_h = 46 * ppm; sc = st_h / ST_IM.height; sw = ST_IM.width * sc
        key = "st%d" % int(st_h)
        if key not in _BL: _BL[key] = cairo.ImageSurface.create_from_png(M("statue"))
        c.save(); c.translate(sx - sw / 2 + 10, ybed - ped_h - st_h + off + 6); c.scale(sc, sc); c.set_source_surface(_BL[key], 0, 0); c.paint(); c.restore()
        c.restore()
        c.set_source_rgba(*WATER, 0.45); c.rectangle(x0, max(wl, y81), x1 - x0, ybed - max(wl, y81)); c.fill()   # water in front
    # ruler
    c.set_source_rgba(*PAPER, 1); c.set_line_width(5); c.move_to(150, ybed); c.line_to(150, y93); c.stroke()
    for m_, lab in ((0, "0"), (81, "81 m"), (93, "93 m")):
        yy = ybed - m_ * ppm; c.move_to(130, yy); c.line_to(170, yy); c.stroke()
        if t > TD: text(c, lab, 185, yy + 12, 32, col=WHITE, align="left", stroke=6)
    if t > TD: pill(c, "DEEPEST: ~81 m (266 ft)", 330, y81 + 60, 34, t - TD, fg=SKY)
    if t > TS + 0.4: pill(c, "STATUE + PEDESTAL: 93 m (305 ft)", W / 2, ytop - 10, 34, t - TS - 0.4, fg=YEL)
    if t > TO: glow_torch = pill(c, "STICKS OUT!", 820, y93 + 40, 44, t - TO, fg=LIME)
    source_tag(c, "Statue: Daniel Schwen (PD), NPS 305 ft · lake depth ~80-84 m (Britannica)", t - 0.3, y=1350, size=19)


def s18(c, t, d):  # F "All that water leaves in Uganda... to start the Nile."
    a = JINJA.kb(min(1, t / d), 1.0, 1.12, (0.45, 0.5), (0.43, 0.45)); to_ctx(c, finish(a, t, vign=0.25))
    TU = wt(18, "uganda", 1.3) - 0.1; TN = wt(18, "nile", 3.3) - 0.1
    wx_plate(c, "JINJA, UGANDA", W / 2, 400, 74, t - TU, icon="sun", col=LIME)
    if t > TN:
        k = eout((t - TN) / 0.6)
        arrow(c, 300, 1150, lerp(300, 820, k), lerp(1150, 980, k), LIME, width=20)
        pill(c, "THE NILE STARTS HERE", W / 2, 1200, 50, t - TN, fg=YEL)
    source_tag(c, "Photo: Dror Feitelson / CC BY-SA 3.0 · the Nile is the lake's only outlet", t - 0.3, y=1350, size=20)


def s19(c, t, d):  # M "So the Nile starts... next to my storm. [sighs] Let me guess tomorrow's forecast..."
    to_ctx(c, clipframe(STORM, t + 3, night=0.15))
    rain(c, t, alpha=0.45)
    TS = wt(19, "storm", 1.4); TG = wt(19, "guess", 2.6) - 0.1
    if TS - 0.05 < t < TS + 0.35:
        a = 1 - (t - TS + 0.05) / 0.4; c.set_source_rgba(1, 1, 1, 0.3 * a); c.paint(); bolt(c, 380, 150, 470, 900, 31, alpha=a, width=9)
    live_strap(c, "JOSEPH", "LIVE . STILL WET", t + 1)
    if t > TG:
        fl = ease((t - TG - 0.4) / 0.35)
        if fl > 0.5: tile(c, W / 2, 780, "TOMORROW", "storm", "STORMS", t - TG, hl=True, flip=fl, w=300, h=340)
        else: tile(c, W / 2, 780, "TOMORROW", "cloud", "???", t - TG, flip=fl, w=300, h=340)
    source_tag(c, "Storm footage (illustrative): adege / Pixabay", t - 0.3, y=1350, size=20)


def s_end(c, t, d):
    cx, cy, rx, ry = lake_map(c, t, min(1, t / 3), 1.05, 1.1, LC, LC, night=0.45)
    radar(c, cx, cy, rx, ry, t, inten=0.7)
    end_card_logo(c, t, W / 2, 760, 270, LOGO)
    wx_plate(c, "FOLLOW", W / 2, 1150, 100, t - 0.4, icon="sun")
    if t > 0.9: text(c, "a new wonder, explained daily", W / 2, 1360, 44, col=WHITE, stroke=8, alpha=ease((t - 0.9) / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s_end]
assert len(SCENES) == len(STARTS), (len(SCENES), len(STARTS))
NO_SWEEP = (7, 8, 15)   # continuous scenes (same map continues): no transition
SW = 0.35


def frame(c, gt, surf):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*NAVYG); c.paint()
    if i > 0 and i not in NO_SWEEP and t < SW:
        sweep(c, t, SW, lambda: SCENES[i - 1](c, DURS[i - 1] + t, DURS[i - 1]), lambda: SCENES[i](c, t, d))
    else:
        SCENES[i](c, t, d)
    badge(c, gt)
    if i < len(meta):
        captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    ev = [("thunder", 0.15), ("crack", 0.2), ("pop", s[0] + 0.05)]
    ev += [("whoosh", x - 0.05) for k, x in enumerate(s[1:], 1) if k not in NO_SWEEP]
    ev += [("crack", s[1] + wt(1, "standing", 1.1)), ("thunder", s[1] + wt(1, "standing", 1.1))]
    ev += [("ding", s[2] + 0.1), ("pop", s[2] + wt(2, "joseph", 1.9)), ("pop", s[2] + wt(2, "victoria", 3.0))]
    ev += [("pop", s[3] + 0.1), ("tick", s[3] + wt(3, "michigan", 1.6)), ("thunk", s[3] + wt(3, "moodier", 3.0)), ("thunder", s[3] + wt(3, "moodier", 3.0) + 0.1)]
    ev += [("pop", s[4] + wt(4, "day", 0.9)), ("pop", s[4] + wt(4, "storms", 3.4)), ("thunder", s[4] + wt(4, "storms", 3.4) + 0.2)]
    ev += [("pop", s[5] + 0.2), ("ding", s[5] + wt(5, "beach", 1.8)), ("thunk", s[5] + wt(5, "beach", 1.8) + 0.7)]
    ev += [("pop", s[6] + wt(6, "night", 0.4)), ("tick", s[6] + wt(6, "cools", 1.3)), ("ding", s[6] + wt(6, "warm", 2.9))]
    ev += [("boom", s[7] + wt(7, "crash", 1.4)), ("thunder", s[7] + wt(7, "up", 3.4)), ("crack", s[7] + wt(7, "up", 3.4) + 0.3)]
    ev += [("thunk", s[8] + wt(8, "ganging", 1.0)), ("thunder", s[8] + 1.6)]
    ev += [("pop", s[9] + wt(9, "every", 0.1) + k * 0.12) for k in range(5)] + [("buzz", s[9] + wt(9, "flies", 3.0)), ("pop", s[9] + wt(9, "flies", 3.0) + 0.4)]
    ev += [("scratch", s[10] + 0.05), ("thunk", s[10] + wt(10, "flies", 0.8)), ("buzz", s[10] + wt(10, "flies", 0.8) + 0.1)]
    ev += [("pop", s[11] + wt(11, "billions", 0.9)), ("buzz", s[11] + wt(11, "billions", 0.9) + 0.2), ("ding", s[11] + wt(11, "miles", 3.4))]
    ev += [("pop", s[12] + wt(12, "cloudy", 1.0)), ("buzz", s[12] + wt(12, "flies", 2.6)), ("trombone", s[12] + DURS[12] - 0.5)]
    ev += [("scratch", s[13] + wt(13, "seventeen", 0.9) - 0.15)] + [("tick", s[13] + wt(13, "seventeen", 0.9) + k * 0.1) for k in range(10)] + [("thunk", s[13] + wt(13, "dry", 3.9))]
    ev += [("thunk", s[14] + wt(14, "whole", 0.6))]
    ev += [("pop", s[15] + wt(15, "two", 0.6)), ("thunder", s[15] + wt(15, "rain", 2.3))]
    ev += [("pop", s[16] + 0.2), ("thunk", s[16] + wt(16, "giant", 1.3))]
    ev += [("bubble", s[17] + wt(17, "deepest", 0.9)), ("clank", s[17] + wt(17, "statue", 1.8) + 0.3), ("ding", s[17] + wt(17, "stick", 3.4))]
    ev += [("pop", s[18] + wt(18, "uganda", 1.3)), ("pop", s[18] + wt(18, "nile", 3.3))]
    ev += [("crack", s[19] + wt(19, "storm", 1.4)), ("thunder", s[19] + wt(19, "storm", 1.4)), ("pop", s[19] + wt(19, "guess", 2.6)), ("ding", s[19] + wt(19, "guess", 2.6) + 0.5)]
    ev += [("boom", s[20]), ("pop", s[20] + 0.4)]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]:
            frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    elif sys.argv[1] == "beats":
        for i in range(len(STARTS)): print(i, round(STARTS[i], 2), round(DURS[i], 2), meta[i]["cap"] if i < len(meta) else "END")
    else:
        json.dump({"total": TOTAL, "events": events(), "music_style": "weather"}, open("events.json", "w"))
        a, b = (int(v) for v in sys.argv[2:4]) if len(sys.argv) > 3 else (0, int(math.ceil(TOTAL * FPS)))
        out = sys.argv[4] if len(sys.argv) > 4 else "video.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a, b):
            frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", a, b, "total", TOTAL)
