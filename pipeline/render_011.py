"""Video 011 — Mount Everest (owner request, Bidhan 2026-11-26): "There are seashells at the top of Mount Everest."
How: the summit rock is ~450-million-year-old sea-floor limestone with trilobite / sea-lily / tiny-shellfish fossils;
India's plate slammed into Asia (~55 million years ago) and squeezed that sea floor 5.5 miles up; 2020 survey;
still rising ~4 in per century (slower than fingernails).
Structure NEW: "packing-list countdown" — Jessica (F) packs for Everest (1 snorkel, 2 tape measure, 3 patience) and gets
the punchlines; Bill (M) = dry geologist. Loop: the last line ("...the bottom of the sea") lands back on the hook.
NEW LOOK v8 "expedition kit" (different from 010 granite plates / dust bursts):
 - tag(): swinging kraft luggage-tag headlines on a string (pendulum settle)
 - checklist(): spiral notepad packing list with ticking boxes (the countdown device)
 - lift(): vertical "elevator" transition — the new scene pushes the old one up (it's a video about rock going UP)
 - rising_water(): wavy water line that floods the frame with real reef footage (sea floor <-> summit)
 - collision diagram (plates -> folded sea floor -> peak) with altitude ruler, tape measure, fingernail race meme
 - glacier-teal accent, summit-orange highlights
Media: credits_011.txt. usage (work dir with meta.json, media/, clip_reef/, clip_ama/):
  python render_011.py stills <prefix> t1 t2 ...   |   python render_011.py full [a b out.mp4]"""
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
TEAL = hexc("3FE0D0"); SUMMIT = hexc("FF8A3D"); KRAFT = hexc("D8B783"); PAPER = hexc("FBF6EA"); INK = hexc("1B2333")
RED = hexc("E5484D"); SEA = hexc("1C8FB8"); DEEP = hexc("0C3B5E"); ROCK = hexc("8A7F74"); GREEN = hexc("3DDC84")
engine.CAP_ACCENT = TEAL


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


KP = P("Close_Up_View_of_Mount_Everest", maxz=1.8)        # Bijay Chaurasia, CC BY-SA 4.0 (summit at 0.555, 0.095)
YB = P("Mount_Everest_a_close_view", maxz=1.3)            # Goutam1962, CC BY-SA 4.0 (summit at 0.35, 0.595)
ARG = P("Mount_Everest__Himalayas", maxz=1.3)             # Vyacheslav Argenberg, CC BY 4.0
SUN = P("Sunset_view_of_Everest", maxz=1.5)               # Nir B. Gurung, CC BY-SA 4.0 (Everest lit at 0.44, 0.44)
ISS = P("Himalayas", maxz=1.3)                            # NASA (PD), Himalaya from orbit
TRI = P("Fossil_Trilobite", maxz=1.2)                     # Gary Todd, CC0
CRI = P("Kaibab_Formation", maxz=1.2)                     # NPS, PD (crinoid columnals + brachiopod)
_ci = Image.open(M("Kaibab_Formation")).convert("RGB"); CRI_IM = _ci.crop((int(_ci.width * 0.12), 0, int(_ci.width * 0.88), _ci.height))
REEF = Clip("clip_reef"); AMA = Clip("clip_ama")         # Pixabay: Jackdrafahl reef, u_6cnilicef2 Ama Dablam timelapse
TX = make_textures(11)
_BL = {}


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


# ---------------- look v8: expedition kit ----------------
def tag(c, s, x, y, size, t, col=KRAFT, fg=INK, sub=None, maxw=900):
    """kraft luggage tag on a string: drops in and swings to rest (damped pendulum about the string point)"""
    if t <= 0: return
    w = text_w(c, s, size)
    if w > maxw - 150: size *= (maxw - 150) / w; w = maxw - 150
    bw, bh = w + 150, size * 1.55
    k = min(1, t / 0.2); ang = 0.22 * math.exp(-3.2 * t) * math.cos(9 * t)
    px, py = x - bw / 2 + 30, y - bh / 2 - 70             # string anchor (above the hole)
    c.save(); c.translate(px, py - (1 - eout(k)) * 60); c.rotate(ang); c.translate(-px, -py)
    hx, hy = x - bw / 2 + 52, y                           # grommet
    c.set_source_rgba(0.95, 0.93, 0.88, 0.9 * k); c.set_line_width(4)
    c.move_to(px, py); c.curve_to(px + 10, py + 30, hx - 10, hy - 30, hx, hy); c.stroke()
    x0 = x - bw / 2; x1 = x + bw / 2; y0 = y - bh / 2; y1 = y + bh / 2; nk = bh * 0.32
    def shape():
        c.move_to(x0 + nk, y0); c.line_to(x1 - 14, y0); c.arc(x1 - 14, y0 + 14, 14, -math.pi / 2, 0)
        c.line_to(x1, y1 - 14); c.arc(x1 - 14, y1 - 14, 14, 0, math.pi / 2); c.line_to(x0 + nk, y1)
        c.line_to(x0, y1 - nk); c.line_to(x0, y0 + nk); c.close_path()
    c.set_source_rgba(0, 0, 0, 0.35 * k); c.save(); c.translate(10, 14); shape(); c.fill(); c.restore()
    shape(); c.save(); c.clip(); c.set_source_rgba(*col, k); c.paint()
    tex(c, TX["concrete"], dx=x * 0.2, dy=y * 0.3); c.paint_with_alpha(0.10 * k)
    g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgba(0, 1, 1, 1, 0.25); g.add_color_stop_rgba(1, 0, 0, 0, 0.12)
    c.set_source(g); c.paint(); c.restore()
    c.set_source_rgba(*INK, 0.35 * k); c.set_line_width(2.5); c.set_dash([10, 7]); shape(); c.stroke(); c.set_dash([])
    c.set_source_rgba(*SUMMIT, k); c.arc(hx, hy, 15, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(*INK, k); c.arc(hx, hy, 8, 0, 2 * math.pi); c.fill()
    text(c, s, x + 30, y + size * 0.36, size, col=fg, alpha=k)
    c.restore()
    if sub and t > 0.3:
        a = ease((t - 0.3) / 0.25); sz = 40; sw = text_w(c, sub, sz) + 44
        c.save(); c.translate(x + 30, y + bh / 2 + 46)
        c.set_source_rgba(*INK, 0.9 * a); rrect(c, -sw / 2, -sz * 0.82, sw, sz * 1.35, sz * 0.67); c.fill()
        text(c, sub, 0, sz * 0.27, sz, col=TEAL, alpha=a); c.restore()


ITEMS = ["SNORKEL", "TAPE MEASURE", "PATIENCE"]


def checklist(c, t, n_shown, ticks, x=W / 2, y=760, hl=None):
    """spiral notepad 'EVEREST PACKING LIST' with the countdown items; ticks[i] = time since item i was ticked"""
    k = eout(t / 0.35); w, h = 820, 700; y = y + (1 - k) * 260
    c.save(); c.translate(x, y); c.rotate(-0.035)
    c.set_source_rgba(0, 0, 0, 0.4); rrect(c, -w / 2 + 14, -h / 2 + 20, w, h, 18); c.fill()
    c.set_source_rgb(*PAPER); rrect(c, -w / 2, -h / 2, w, h, 18); c.fill()
    c.save(); rrect(c, -w / 2, -h / 2, w, h, 18); c.clip(); tex(c, TX["concrete"]); c.paint_with_alpha(0.05); c.restore()
    c.set_source_rgba(0.35, 0.55, 0.85, 0.35); c.set_line_width(2)
    for j in range(9): yy = -h / 2 + 170 + j * 62; c.move_to(-w / 2 + 20, yy); c.line_to(w / 2 - 20, yy); c.stroke()
    c.set_source_rgba(*RED, 0.6); c.move_to(-w / 2 + 110, -h / 2 + 90); c.line_to(-w / 2 + 110, h / 2 - 10); c.stroke()
    for j in range(9):   # spiral rings
        rx = -w / 2 + 70 + j * 85
        c.set_source_rgba(0.75, 0.77, 0.8, 1); c.set_line_width(7); c.arc(rx, -h / 2 + 6, 17, math.pi * 0.95, math.pi * 2.05); c.stroke()
    text(c, "EVEREST PACKING LIST", 0, -h / 2 + 115, 54, col=INK)
    for i in range(n_shown):
        yy = -h / 2 + 250 + i * 150; a = ease((t - 0.25 - 0.12 * i) / 0.3) if hl is None or i < hl else 1
        bx = -w / 2 + 150
        if hl == i:
            c.set_source_rgba(*TEAL, 0.25); rrect(c, bx - 30, yy - 70, w - 200, 110, 14); c.fill()
        c.set_source_rgba(*INK, a); c.set_line_width(6); rrect(c, bx, yy - 50, 64, 64, 8); c.stroke()
        text(c, f"{i + 1}. {ITEMS[i]}", bx + 100, yy + 2, 64, col=INK, align="left", alpha=a)
        tk = ticks[i] if i < len(ticks) else None
        if tk is not None and tk > 0:
            e = eout(tk / 0.25); c.set_source_rgba(*GREEN, 1); c.set_line_width(13); c.set_line_cap(cairo.LINE_CAP_ROUND)
            p0 = (bx + 8, yy - 20); p1 = (bx + 28, yy + 4); p2 = (bx + 84, yy - 66)
            c.move_to(*p0)
            if e < 0.4: c.line_to(lerp(p0[0], p1[0], e / 0.4), lerp(p0[1], p1[1], e / 0.4))
            else: c.line_to(*p1); c.line_to(lerp(p1[0], p2[0], (e - 0.4) / 0.6), lerp(p1[1], p2[1], (e - 0.4) / 0.6))
            c.stroke(); c.set_line_cap(cairo.LINE_CAP_BUTT)
    c.restore()


def shell(c, x, y, s, t=0.0, col=(1.0, 0.86, 0.72)):
    """original scallop-shell icon (fan of ribs)"""
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(0.15 * math.sin(t * 3))
    c.set_source_rgba(0, 0, 0, 0.35); c.arc(4, 6, 46, math.pi, 2 * math.pi); c.fill()
    c.move_to(-46, 0); c.arc(0, 0, 46, math.pi, 2 * math.pi); c.line_to(14, 16); c.line_to(-14, 16); c.close_path()
    c.set_source_rgb(*col); c.fill_preserve(); c.set_source_rgba(*SUMMIT, 1); c.set_line_width(3); c.stroke()
    for j in range(7):
        a = math.pi + (j + 0.5) * math.pi / 7; c.move_to(0, 12); c.line_to(44 * math.cos(a), 44 * math.sin(a)); c.stroke()
    c.restore()


def sea_lily(c, x, y, s, t):
    """original drawing of a crinoid ('sea lily'): segmented stalk + cup + feathery arms swaying"""
    c.save(); c.translate(x, y); c.scale(s, s)
    sw = 10 * math.sin(t * 1.8)
    c.set_source_rgb(*hexc("E9C9A0")); c.set_line_width(14)
    c.move_to(0, 0); c.curve_to(10, -90, -10, -160, sw, -230); c.stroke()
    c.set_source_rgba(0.55, 0.35, 0.2, 0.8); c.set_line_width(3)
    for k in range(12): yy = -k * 19; c.move_to(-8, yy); c.line_to(8, yy); c.stroke()
    c.set_source_rgb(*hexc("F2A65A")); c.arc(sw, -238, 20, 0, 2 * math.pi); c.fill()
    for j in range(7):
        ang = -math.pi / 2 + (j - 3) * 0.32 + 0.05 * math.sin(t * 2 + j); L = 110
        ex, ey = sw + math.cos(ang) * L, -250 + math.sin(ang) * L
        c.set_source_rgb(*hexc("F2A65A")); c.set_line_width(7); c.move_to(sw, -250); c.line_to(ex, ey); c.stroke()
        c.set_line_width(3)
        for q in range(1, 8):
            px, py = lerp(sw, ex, q / 8), lerp(-250, ey, q / 8)
            for sd in (-1, 1): c.move_to(px, py); c.line_to(px + sd * 14 * math.cos(ang + 1.57), py + sd * 14 * math.sin(ang + 1.57)); c.stroke()
    c.restore()


def glow_ring(c, x, y, t, r=70, col=TEAL):
    for j in range(3):
        ph = (t * 1.2 + j / 3) % 1
        c.set_source_rgba(*col, 0.7 * (1 - ph)); c.set_line_width(5); c.arc(x, y, r * (0.4 + ph), 0, 2 * math.pi); c.stroke()


def crab(c, x, y, s, t):
    """original cartoon crab with a tiny backpack (the 'very lost crab')"""
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-0.35)
    leg = math.sin(t * 14) * 8
    c.set_source_rgb(*hexc("E0503C")); c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for sd in (-1, 1):
        for j in range(3):
            c.move_to(sd * 40, 10 + j * 12); c.line_to(sd * (78 + j * 6), 30 + j * 16 + (leg if (j + (sd > 0)) % 2 else -leg)); c.stroke()
        c.move_to(sd * 42, -10); c.line_to(sd * 70, -48); c.stroke()
        c.arc(sd * 76, -62, 20, 0, 2 * math.pi); c.fill()
    c.set_source_rgb(*hexc("F0644A")); c.save(); c.scale(1.3, 0.85); c.arc(0, 10, 46, 0, 2 * math.pi); c.restore(); c.fill()
    c.set_source_rgb(*hexc("2F6FB0")); rrect(c, -30, -36, 60, 44, 10); c.fill()          # backpack
    c.set_source_rgb(*hexc("FFD54A")); c.rectangle(-30, -20, 60, 6); c.fill()
    for sd in (-1, 1):
        c.set_source_rgb(1, 1, 1); c.move_to(sd * 16, -12); c.line_to(sd * 18, -40); c.set_line_width(5); c.stroke()
        c.arc(sd * 18, -46, 10, 0, 2 * math.pi); c.fill(); c.set_source_rgb(0.05, 0.05, 0.1); c.arc(sd * 19, -46, 5, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(0.6, 0.85, 1, 0.9 * (0.5 + 0.5 * math.sin(t * 5)))              # sweat drop
    c.move_to(58, -70); c.curve_to(48, -52, 68, -52, 58, -70); c.fill()
    c.set_line_cap(cairo.LINE_CAP_BUTT); c.restore()


def snorkel_mask(c, x, y, s, t):
    c.save(); c.translate(x, y + 10 * math.sin(t * 2.5)); c.scale(s, s); c.rotate(-0.12)
    c.set_source_rgb(*hexc("FFB020")); c.set_line_width(16); c.move_to(80, 10); c.line_to(80, -150); c.curve_to(80, -175, 110, -175, 110, -150); c.stroke()
    c.set_source_rgb(*hexc("1B6FB8")); rrect(c, -110, -50, 220, 110, 50); c.fill()
    c.set_source_rgba(0.75, 0.93, 1, 0.9); rrect(c, -90, -34, 80, 76, 30); c.fill(); rrect(c, 10, -34, 80, 76, 30); c.fill()
    c.set_source_rgba(1, 1, 1, 0.8); c.arc(-60, -14, 10, 0, 2 * math.pi); c.fill(); c.arc(40, -14, 10, 0, 2 * math.pi); c.fill()
    c.restore()


def tape_measure(c, x, ybase, ytop, k, t, label=None):
    """yellow tape measure extending up from a case at the bottom"""
    yt = lerp(ybase, ytop, eout(k))
    c.set_source_rgb(*hexc("FFD23F")); c.rectangle(x - 24, yt, 48, ybase - yt); c.fill()
    c.set_source_rgba(0.1, 0.1, 0.1, 1); c.set_line_width(3)
    y = ybase
    j = 0
    while y > yt:
        L = 30 if j % 5 == 0 else 14; c.move_to(x - 24, y); c.line_to(x - 24 + L, y); c.stroke(); y -= 22; j += 1
    c.set_source_rgb(*hexc("C9CDD3")); c.rectangle(x - 34, yt - 10, 68, 14); c.fill()     # hook
    c.set_source_rgb(*hexc("E5484D")); rrect(c, x - 90, ybase - 10, 180, 150, 30); c.fill()
    c.set_source_rgb(*hexc("2A2F3A")); c.arc(x, ybase + 65, 40, 0, 2 * math.pi); c.fill()
    if label and k > 0.95:
        c.set_source_rgba(*INK, 0.9); rrect(c, x + 50, yt - 10, text_w(c, label, 50) + 40, 80, 14); c.fill()
        text(c, label, x + 70, yt + 47, 50, col=hexc("FFD23F"), align="left")


def rising_water(c, t, level_y, clip_frame, amp=18):
    """fill everything below a wavy line with real reef footage (tinted), white foam on the line"""
    c.save()
    c.move_to(0, H + 10); c.line_to(0, level_y)
    for xx in range(0, W + 30, 30): c.line_to(xx, level_y + amp * math.sin(xx / 70 + t * 4) + 6 * math.sin(xx / 23 - t * 7))
    c.line_to(W, H + 10); c.close_path(); c.clip()
    s = to_surface(clip_frame.astype(np.float32) / 255); c.set_source_surface(s, 0, 0); c.paint()
    c.set_source_rgba(*SEA, 0.25); c.paint()
    c.restore()
    c.set_source_rgba(1, 1, 1, 0.85); c.set_line_width(6)
    for xx in range(0, W + 30, 30):
        yy = level_y + amp * math.sin(xx / 70 + t * 4) + 6 * math.sin(xx / 23 - t * 7)
        (c.move_to if xx == 0 else c.line_to)(xx, yy)
    c.stroke()


def bubbles(c, t, n=24, seed=3, x0=80, x1=1000, y0=1700, alpha=0.7):
    r = np.random.default_rng(seed)
    for j in range(n):
        bx = x0 + r.random() * (x1 - x0); sp = 120 + r.random() * 160; ph = r.random()
        y = y0 - ((t * sp + ph * 1600) % 1500); rr = 6 + r.random() * 14
        c.set_source_rgba(0.85, 0.97, 1, alpha); c.set_line_width(3); c.arc(bx + 12 * math.sin(t * 3 + j), y, rr, 0, 2 * math.pi); c.stroke()


def fish(c, x, y, s, t, col=(1.0, 0.6, 0.2), flip=1):
    c.save(); c.translate(x, y); c.scale(s * flip, s); w_ = math.sin(t * 10) * 6
    c.set_source_rgb(*col); c.save(); c.scale(1.6, 1); c.arc(0, 0, 26, 0, 2 * math.pi); c.restore(); c.fill()
    c.move_to(-36, 0); c.line_to(-66, -22 + w_); c.line_to(-66, 22 + w_); c.close_path(); c.fill()
    c.set_source_rgb(1, 1, 1); c.arc(22, -6, 7, 0, 2 * math.pi); c.fill(); c.set_source_rgb(0, 0, 0); c.arc(24, -6, 3.5, 0, 2 * math.pi); c.fill()
    c.restore()


def stamp(c, s, x, y, t, col=RED, size=120, ang=-0.1):
    if t <= 0: return
    k = min(1, t / 0.16); sc = lerp(1.6, 1.0, eout(k))
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(sc, sc)
    w = text_w(c, s, size) + 80; h = size * 1.3
    c.set_source_rgba(*INK, 0.6 * k); rrect(c, -w / 2, -h / 2, w, h, 20); c.fill()
    c.set_source_rgba(*col, k); c.set_line_width(12); rrect(c, -w / 2, -h / 2, w, h, 20); c.stroke()
    text(c, s, 0, size * 0.36, size, col=col, alpha=k); c.restore()


def pill(c, s, x, y, size, t, bgc=INK, fg=TEAL, alpha=0.9):
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


# ---------------- collision diagram (illustrative) ----------------
def collision(c, t, phase, rise=0.0):
    """illustrative cross-section: an ocean between INDIA (left) and ASIA (right); its sea-floor layer (teal, fossil
    dots) crumples into folds as the plates close (phase 0..1), then is pushed up into a peak (rise 0..1).
    Returns (peak x, peak top y, base y)."""
    bg(c, "iss", ISS, t, (0.5, 0.5), dim=0.45, z=1.1)
    x0, x1, yb = 70, 1010, 1230; yc = yb - 150; mid = (x0 + x1) / 2
    c.save(); rrect(c, x0 - 20, 330, x1 - x0 + 40, 960, 30); c.clip()
    g = cairo.LinearGradient(0, 330, 0, 1290); g.add_color_stop_rgba(0, 0.62, 0.8, 0.98, 0.6); g.add_color_stop_rgba(1, 0.12, 0.22, 0.38, 0.6)
    c.set_source(g); c.paint()
    p = ease(phase); gap = lerp(420, 0, p); ix = mid - gap / 2; ax = mid + gap / 2
    c.set_source_rgba(*hexc("7A3A22"), 0.95); c.rectangle(x0 - 20, yb, x1 - x0 + 40, 80); c.fill()          # mantle
    if gap > 4:   # the ocean between the continents
        c.set_source_rgba(*SEA, 0.85); c.rectangle(ix, yc - 10, gap, 130); c.fill()
        c.set_source_rgba(1, 1, 1, 0.6); c.set_line_width(4)
        for xx in np.arange(ix, ax, 26): c.move_to(xx, yc - 10 + 4 * math.sin(xx / 9 + t * 5)); c.line_to(xx + 13, yc - 10 + 4 * math.sin((xx + 13) / 9 + t * 5)); c.stroke()
    for (xa, xb, lab, col) in ((x0 - 20, ix, "INDIA", hexc("C9A46A")), (ax, x1 + 20, "ASIA", hexc("A88E6E"))):
        c.set_source_rgb(*col); c.rectangle(xa, yc, xb - xa, yb - yc); c.fill()
        c.save(); c.rectangle(xa, yc, xb - xa, yb - yc); c.clip(); tex(c, TX["rock"], dx=xa); c.paint_with_alpha(0.25); c.restore()
        if xb - xa > 200: text(c, lab, (xa + xb) / 2 + (-40 if lab == "INDIA" else 40), yb - 50, 56, col=INK)
    # sea-floor layer: length is conserved, so it crumples as the gap closes
    r = ease(rise); half = lerp(max(gap / 2, 0) + 60, 150, p) + 230 * r; top = yc + 110 - (110 + 500) * r
    amp = 60 * p * (1 - 0.6 * r); n = 5
    def surf_y(u):   # u in -1..1 across the layer
        base = yc + 110 - (yc + 110 - top) * max(0.0, 1 - abs(u) ** 1.2) if r > 0 else yc + 110
        return base - amp * abs(math.sin((u + 1) * math.pi * n / 2)) * (1 - 0.7 * r)
    pts = [(mid + u * half, surf_y(u)) for u in np.linspace(-1, 1, 61)]
    if r > 0:   # rock body of the mountain under the draped layer
        c.move_to(mid - half - 40, yc + 2)
        for (xx, yy) in pts: c.line_to(xx, yy + 18)
        c.line_to(mid + half + 40, yc + 2); c.close_path()
        c.save(); c.clip_preserve(); c.set_source_rgb(*ROCK); c.fill(); tex(c, TX["rock"]); c.paint_with_alpha(0.3)
        c.set_source_rgba(*hexc("1E8A80"), 0.7); c.set_line_width(7)       # folded layers inside the mountain
        for k in range(1, 4):
            for j, u in enumerate(np.linspace(-0.85, 0.85, 40)):
                xx = mid + u * half * (1 - 0.18 * k); yy = surf_y(u) + 70 * k + 28 * math.sin(u * 9 + k)
                (c.move_to if j == 0 else c.line_to)(xx, yy)
            c.stroke()
        c.restore()
    c.set_source_rgb(*TEAL); c.set_line_width(34); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for j, q in enumerate(pts): (c.move_to if j == 0 else c.line_to)(*q)
    c.stroke(); c.set_line_cap(cairo.LINE_CAP_BUTT); c.set_line_join(cairo.LINE_JOIN_MITER)
    for j in range(3, 58, 6):
        xx, yy = pts[j]; shell(c, xx, yy - 4, 0.22, t)                                   # fossils ride along
    if r > 0.95: glow_ring(c, mid, top, t, r=60, col=hexc("FFD23F"))
    c.restore()
    text(c, "SEA-FLOOR LAYER (with fossils)", mid, 1335, 30, col=TEAL, stroke=8)
    if p < 1 and r == 0:
        a = 1 - ease((phase - 0.85) / 0.15)
        arrow(c, ix - 260, yc + 70, ix - 70, yc + 70, SUMMIT, width=18, alpha=a)
        text(c, "NORTH", ix - 170, yc + 30, 34, col=SUMMIT, stroke=8, alpha=a)
    return mid, top, yc + 110


def lift(c, t, i, draw_prev, dur=0.3):
    """vertical 'elevator' transition: the new scene pushes the previous one up and out"""
    k = eout(t / dur)
    c.save(); c.translate(0, -H * k); draw_prev(); c.restore()
    c.translate(0, H * (1 - k))


# ---------------- scenes ----------------
HK = dict(z0=1.55, z1=1.68, f0=(0.555, 0.2), f1=(0.555, 0.18))


def hook_frame(c, t, k=None):
    kk = min(1, t / 4) if k is None else k
    a = KP.kb(kk, HK["z0"], HK["z1"], HK["f0"], HK["f1"]); to_ctx(c, finish(a, t, vign=0.25))
    return pt(KP, kk, HK["z0"], HK["z1"], HK["f0"], HK["f1"], 0.555, 0.105)


def shells_at(c, sx, sy, t, n=5):
    for j in range(n):
        tt = t - j * 0.12
        if tt <= 0: continue
        ang = -math.pi / 2 + (j - (n - 1) / 2) * 0.55; d = 120 + 25 * (j % 2)
        e = back(min(1, tt / 0.3)); shell(c, sx + math.cos(ang) * d * e, sy + 60 + math.sin(ang) * d * e * 0.6 + 80, 0.9 * e, tt)


def s0(c, t, d):   # M hook
    sx, sy = hook_frame(c, t)
    TS = wt(0, "seashells", 0.4)
    if t > TS - 0.1: glow_ring(c, sx, sy + 40, t); shells_at(c, sx, sy, t - TS + 0.1)
    tag(c, "SEASHELLS UP HERE?!", W / 2, 1130, 92, t + 1.0, sub="TOP OF MOUNT EVEREST")
    source_tag(c, "Photo: Bijay Chaurasia / CC BY-SA 4.0", t - 0.3, y=1360, size=20)


def s1(c, t, d):   # F lost crab
    z0, z1, f = 1.25, 1.35, (0.56, 0.3)
    a = KP.kb(min(1, t / d), z0, z1, f, f); to_ctx(c, finish(a, t, vign=0.25))
    sx, sy = pt(KP, min(1, t / d), z0, z1, f, f, 0.555, 0.105)
    k = ease((t - 0.6) / max(1, d - 1.0))
    crab(c, lerp(900, sx + 60, k), lerp(1250, sy + 140, k), 1.1, t)
    TC = wt(1, "crab", 3.0)
    tag(c, "A VERY LOST CRAB?", W / 2, 1120 - 700 * 0, 84, t - TC + 0.1, col=hexc("FFD9A0"))


def s2(c, t, d):   # M "Nobody carried them. The summit used to be sea floor."
    z0, z1, f0, f1 = 1.0, 1.12, (0.37, 0.55), (0.36, 0.58)
    a = YB.kb(min(1, t / d), z0, z1, f0, f1); to_ctx(c, finish(a, t, vign=0.25))
    sx, sy = pt(YB, min(1, t / d), z0, z1, f0, f1, 0.35, 0.6)
    tag(c, "NOBODY CARRIED THEM", W / 2, 420, 70, t - 0.15)
    TS = wt(2, "sea", 1.8) - 0.15
    if t > TS:
        lv = lerp(H + 40, sy - 60, eout((t - TS) / 0.9))
        rising_water(c, t, lv, REEF.at(t))
        if t > TS + 0.6: pill(c, "SUMMIT = OLD SEA FLOOR", W / 2, 1180, 58, t - TS - 0.6)
    source_tag(c, "Photo: Goutam1962 / CC BY-SA 4.0 · Reef: Jackdrafahl / Pixabay", t - 0.3, y=1360, size=20)


def s3(c, t, d):   # F item one: snorkel
    bg(c, "arg", ARG, t, (0.5, 0.4), dim=0.55, z=1.05)
    T1 = wt(3, "snorkel", 3.5)
    checklist(c, t, 1, [t - T1 + 0.05], hl=0 if t > T1 else None)
    if t > T1 - 0.1: snorkel_mask(c, 820, 1060, 0.9 * back(min(1, (t - T1 + 0.1) / 0.3)), t)
    tag(c, "ITEM 1", 250, 330, 60, t - 0.1, col=TEAL)


def s4(c, t, d):   # M "450 million years late"
    to_ctx(c, finish(REEF.at(t + 0.5).astype(np.float32), t, vign=0.3))
    c.set_source_rgba(*DEEP, 0.25); c.paint()
    TN = wt(4, "four", 1.1)
    # rewinding clock
    cx, cy, r = W / 2, 760, 170
    c.set_source_rgba(*INK, 0.75); c.arc(cx, cy, r + 20, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(*TEAL, 1); c.set_line_width(8); c.arc(cx, cy, r, 0, 2 * math.pi); c.stroke()
    sp = -t * 9 if t > TN else -t * 1.5
    for L, w_, a_ in ((r * 0.75, 10, sp), (r * 0.5, 14, sp / 12)):
        c.set_line_width(w_); c.set_source_rgb(*PAPER); c.move_to(cx, cy); c.line_to(cx + L * math.sin(a_), cy - L * math.cos(a_)); c.stroke()
    text(c, "REWIND", cx, cy + r + 70, 44, col=TEAL, stroke=8)
    if t > TN:
        pill(c, counter(t - TN, 0, 450, 1.3) + " MILLION YEARS AGO", W / 2, 1180, 56, t - TN, fg=hexc("FFD23F"))
    tag(c, "YOU'RE LATE", W / 2, 380, 84, t - wt(4, "late", 3.0) + 0.1, col=hexc("FFB5A0"))
    source_tag(c, "Summit limestone ~450-470 million yrs old · IUGS, Montana State Univ.", t - 0.3, y=1360, size=20)


def s5(c, t, d):   # M "Back then, this rock was mud in a warm, shallow sea."
    to_ctx(c, finish(REEF.at(t + 4.5).astype(np.float32), t, vign=0.3))
    bubbles(c, t, n=16, alpha=0.5)
    tag(c, "MUD + WARM SHALLOW SEA", W / 2, 400, 66, t - 0.1, col=hexc("BEEFEA"))
    TW = wt(5, "warm", 2.0)
    if t > TW:   # thermometer
        k = eout((t - TW) / 0.6); x, y0 = 170, 1150
        c.set_source_rgba(*PAPER, 0.95); rrect(c, x - 26, y0 - 420, 52, 430, 26); c.fill(); c.arc(x, y0 + 20, 46, 0, 2 * math.pi); c.fill()
        c.set_source_rgb(*RED); c.arc(x, y0 + 20, 34, 0, 2 * math.pi); c.fill(); c.rectangle(x - 13, y0 - 20 - 330 * k, 26, 340 * k); c.fill()
    TSH = wt(5, "shallow", 2.6)
    if t > TSH: pill(c, "SHALLOW", 760, 1000, 60, t - TSH, fg=TEAL)
    source_tag(c, "Source: IUGS Geoheritage 'The Ordovician rocks of Mount Everest'", t - 0.3, y=1360, size=20)


def s6(c, t, d):   # M "Trilobites, sea lilies, tiny shellfish. Their fossils are still up there."
    TL = wt(6, "sea", 1.0); TF = wt(6, "tiny", 1.8); TU = wt(6, "still", 3.2)
    if t < TU - 0.1:
        a = TRI.kb(min(1, t / d), 1.0, 1.12, (0.5, 0.45), (0.5, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
        tag(c, "TRILOBITE", W / 2, 360, 74, t - 0.05, col=hexc("FFD9A0"))
        if t > TL:   # polaroid inset: crinoid columnals
            k = back(min(1, (t - TL) / 0.3)); c.save(); c.translate(780, 900); c.rotate(0.08); c.scale(k, k)
            c.set_source_rgba(0, 0, 0, 0.4); c.rectangle(-210 + 10, -200 + 14, 420, 440); c.fill()
            c.set_source_rgb(*PAPER); c.rectangle(-210, -200, 420, 440); c.fill()
            c.set_source_rgb(*hexc("0E4B6E")); c.rectangle(-190, -182, 380, 350); c.fill()
            sea_lily(c, 0, 150, 1.0, t)
            text(c, "SEA LILY (crinoid)", 0, 215, 36, col=INK); c.restore()
        if t > TF:
            for j in range(6): shell(c, 150 + j * 70, 1180 - 30 * (j % 2), 0.55 * back(min(1, (t - TF - j * 0.06) / 0.25)) if t - TF - j * 0.06 > 0 else 0.001, t)
            pill(c, "TINY SHELLFISH", 330, 1060, 44, t - TF, fg=hexc("FFD23F"))
        source_tag(c, "Trilobite: Gary Todd (CC0) · Crinoid: NPS (PD) · examples, not Everest's own", t - 0.3, y=1360, size=19)
    else:
        tt = t - TU + 0.1; sx, sy = hook_frame(c, tt * 0.3 + 0.5, k=0.6)
        glow_ring(c, sx, sy + 120, tt, r=110); tag(c, "STILL UP THERE", W / 2, 1100, 84, tt)
        source_tag(c, "Fossils in the summit limestone: Montana State Univ., IUGS", tt - 0.2, y=1360, size=20)


def s7(c, t, d):   # F "The highest rock on Earth... is an old aquarium?!"
    sx, sy = hook_frame(c, t + 2, k=min(1, 0.6 + t / 8))
    TA = wt(7, "aquarium", 2.5) - 0.1
    k = ease((t - TA) / 0.35)
    if k > 0:   # glass tank drawn around the summit, water inside
        x0, y0, x1, y1 = 110, sy - 120, 970, sy + 700
        c.save(); c.rectangle(x0, y0 + 90, x1 - x0, y1 - y0 - 90); c.clip(); c.set_source_rgba(*SEA, 0.35 * k); c.paint(); c.restore()
        bubbles(c, t, n=14, x0=x0 + 40, x1=x1 - 40, y0=y1, alpha=0.6 * k)
        for j, (fx, fy, col) in enumerate(((0.3, 0.45, (1, 0.55, 0.15)), (0.7, 0.62, (1, 0.85, 0.2)), (0.45, 0.8, (0.3, 0.8, 1)))):
            xx = x0 + (x1 - x0) * ((fx + t * 0.08 * (1 if j % 2 else -1)) % 1); fish(c, xx, y0 + (y1 - y0) * fy, 1.1 * k, t + j, col, 1 if j % 2 else -1)
        c.set_source_rgba(0.85, 0.97, 1, 0.9 * k); c.set_line_width(12); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.stroke()
        c.set_source_rgba(1, 1, 1, 0.25 * k); c.rectangle(x0 + 30, y0 + 20, 40, y1 - y0 - 40); c.fill()
        c.set_source_rgb(*INK); c.rectangle(x0 - 20, y1, x1 - x0 + 40, 40); c.fill()
    tag(c, "HIGHEST ROCK ON EARTH", W / 2, 1200, 66, t - 0.1)
    if t > TA + 0.25: stamp(c, "AQUARIUM?!", W / 2, 430, t - TA - 0.25, col=SUMMIT, size=110)


def s8(c, t, d):   # M "Pretty much. Then India showed up."
    a = ISS.kb(min(1, t / d), 1.0, 1.15, (0.5, 0.5), (0.5, 0.6)); to_ctx(c, finish(a, t, vign=0.3))
    TI = wt(8, "india", 1.3) - 0.1
    if t > TI:
        k = eout((t - TI) / 0.6); arrow(c, W / 2, 1700 - 400 * k, W / 2, 1250 - 400 * k, SUMMIT, width=26)
        tag(c, "...THEN INDIA SHOWED UP", W / 2, 420, 70, t - TI)
    source_tag(c, "Himalaya from orbit: NASA (PD)", t - 0.3, y=1360, size=20)


def s9(c, t, d):   # F "India... the country?"
    a = ISS.kb(1, 1.15, 1.15, (0.5, 0.6), (0.5, 0.6)); to_ctx(c, finish(a, t, vign=0.3))
    c.set_source_rgba(*INK, 0.35); c.paint()
    tag(c, "...THEN INDIA SHOWED UP", W / 2, 420, 70, t + 2)
    stamp(c, "THE COUNTRY?", W / 2, 900, t - wt(9, "country", 0.8) + 0.05, col=TEAL, size=110, ang=0.06)


def s10(c, t, d):  # M "The plate! It drifted north and slammed into Asia, about 55 million years ago."
    TS = wt(10, "slammed", 2.0)
    ph = 0.75 * ease((t - 0.3) / max(0.5, TS - 0.3)) + 0.25 * ease((t - TS) / 0.4)
    collision(c, t, ph)
    tag(c, "THE PLATE!", W / 2, 420, 84, t - 0.05, col=hexc("FFD9A0"))
    if t > TS: stamp(c, "CRUNCH", 760, 760, t - TS, col=SUMMIT, size=90, ang=0.1)
    TF = wt(10, "fifty-five", 3.6)
    if t > TF: pill(c, "~55 MILLION YEARS AGO", W / 2, 560, 52, t - TF, fg=hexc("FFD23F"))
    source_tag(c, "Diagram (simplified) · Source: IUGS Geoheritage", t - 0.3, y=1275, x=90, size=20)


def s11(c, t, d):  # M "That sea floor got squeezed, folded and shoved up... five and a half miles."
    TSH = wt(11, "shoved", 2.4); TFV = wt(11, "five", 3.4)
    rise = ease((t - TSH + 0.2) / max(0.6, TFV - TSH + 1.0))
    mid, top, yb = collision(c, t + 3, 1.0, rise=rise)
    if rise > 0:
        x = 150; c.set_source_rgba(*PAPER, 1); c.set_line_width(7); c.move_to(x, yb); c.line_to(x, top); c.stroke()
        for yy in (yb, top): c.move_to(x - 22, yy); c.line_to(x + 22, yy); c.stroke()
        c.set_dash([10, 8]); c.set_line_width(3); c.move_to(x, top); c.line_to(mid, top); c.stroke(); c.set_dash([])
    if t > TFV:
        pill(c, "5.5 MILES UP", 790, top + 40, 54, t - TFV, fg=hexc("FFD23F"))
    lab = "SQUEEZED" if t < wt(11, "folded", 1.6) else ("FOLDED" if t < TSH else "SHOVED UP")
    tag(c, lab, W / 2, 420, 84, t - 0.05, col=hexc("BEEFEA"))
    source_tag(c, "Diagram (simplified) · summit 8,848.86 m = 5.5 mi", t - 0.3, y=1275, x=90, size=20)


def s12(c, t, d):  # F item two: tape measure
    bg(c, "sun", SUN, t, (0.44, 0.45), dim=0.6, z=1.0)
    T2 = wt(12, "tape", 1.2)
    checklist(c, t + 1, 2, [9, t - T2 + 0.05], hl=1 if t > T2 else None)
    tag(c, "ITEM 2", 250, 330, 60, t - 0.1, col=TEAL)
    TC = wt(12, "changing", 3.5)
    if t > TC: stamp(c, "IT KEEPS CHANGING?", W / 2, 1250, t - TC, col=SUMMIT, size=64, ang=-0.05)


def s13(c, t, d):  # M "Mostly better measuring. But it really is rising... about four inches a century."
    z0, z1, f0, f1 = 1.55, 1.65, (0.36, 0.78), (0.36, 0.78)
    k_ = min(1, t / d); a = YB.kb(k_, z0, z1, f0, f1); to_ctx(c, finish(a, t, vign=0.25))
    sx, sy = pt(YB, k_, z0, z1, f0, f1, 0.35, 0.595)
    tape_measure(c, sx - 160, 1780, sy - 6, min(1, t / 0.9), t, label="8,848.86 m")
    c.set_source_rgba(1, 1, 1, 0.7); c.set_line_width(3); c.set_dash([10, 8]); c.move_to(sx - 160, sy - 6); c.line_to(sx, sy - 6); c.stroke(); c.set_dash([])
    if t > 0.9: pill(c, "2020 SURVEY: NEPAL + CHINA", W / 2, 420, 46, t - 0.9, fg=hexc("FFD23F"))
    TR = wt(13, "rising", 2.3)
    if t > TR:
        bob = 14 * math.sin(t * 6); arrow(c, sx + 200, sy + 200 + bob, sx + 200, sy + 30 + bob, GREEN, width=16)
        TF = wt(13, "four", 3.4)
        if t > TF: tag(c, "+4 INCHES / CENTURY", W / 2, 1010, 72, t - TF, col=hexc("C9F7D9"))
    source_tag(c, "Photo: Goutam1962 / CC BY-SA 4.0 · NPR, Britannica (2020) · EarthDate (10 cm/century)", t - 0.3, y=1310, size=18)


def s14(c, t, d):  # F fingernail race (own meme format)
    bg(c, "kp2", KP, t, (0.55, 0.3), dim=0.45, z=1.2)
    tag(c, "RACE TO 4 INCHES", W / 2, 380, 76, t - 0.05, col=hexc("FFD9A0"))
    TN = wt(14, "fingernails", 2.0)
    lanes = (("EVEREST", 640, 100, ROCK, "100 YEARS"), ("FINGERNAIL", 900, 2.4, hexc("FFB5C0"), "~2.5 YEARS"))
    x0, x1 = 140, 900
    c.set_source_rgba(*PAPER, 0.9); c.set_line_width(6); c.set_dash([18, 12]); c.move_to(x1, 540); c.line_to(x1, 1010); c.stroke(); c.set_dash([])
    text(c, "4 IN", x1, 530, 40, col=PAPER, stroke=8)
    tr = max(0.0, t - TN + 0.4)
    for (lab, y, yrs, col, fin) in lanes:
        prog = min(1, tr / (0.9 * yrs / 2.4)) if yrs < 10 else min(1, tr * 0.012)
        c.set_source_rgba(*INK, 0.75); rrect(c, x0 - 20, y - 70, x1 - x0 + 40, 140, 24); c.fill()
        c.set_source_rgb(*col); rrect(c, x0, y - 50, max(30, (x1 - x0) * prog), 100, 18); c.fill()
        text(c, lab, x0 + 20, y + 16, 44, col=INK if prog > 0.45 else PAPER, align="left")
        if prog >= 1: pill(c, fin, W / 2, y + 120, 40, tr - 0.9, fg=GREEN)
        elif lab == "EVEREST" and tr > 1.0: pill(c, fin + "...", 560, y + 120, 40, tr - 1.0, fg=hexc("FFD23F"))
    if tr > 1.2: stamp(c, "WINNER", 760, 1150, tr - 1.2, col=GREEN, size=80, ang=-0.08)
    source_tag(c, "Nails ~3.5 mm/month (Yaemsiri 2010, BioNumbers) · Everest ~10 cm/century (EarthDate)", t - 0.3, y=1360, size=19)


def s15(c, t, d):  # F item three: patience
    bg(c, "sun", SUN, t, (0.44, 0.45), dim=0.6, z=1.0)
    T3 = wt(15, "patience", 0.8)
    checklist(c, t + 1, 3, [9, 9, t - T3 + 0.05], hl=2 if t > T3 else None)
    if t > T3 - 0.1:   # hourglass
        k = back(min(1, (t - T3 + 0.1) / 0.3)); c.save(); c.translate(860, 1080); c.scale(k, k); c.rotate(0.1 * math.sin(t * 2))
        c.set_source_rgb(*KRAFT); c.rectangle(-70, -110, 140, 18); c.fill(); c.rectangle(-70, 92, 140, 18); c.fill()
        c.set_source_rgba(0.85, 0.95, 1, 0.85); c.move_to(-55, -92); c.line_to(55, -92); c.line_to(6, 0); c.line_to(55, 92); c.line_to(-55, 92); c.line_to(-6, 0); c.close_path(); c.fill()
        c.set_source_rgb(*hexc("E8C27A")); c.move_to(-40, 92); c.line_to(40, 92); c.line_to(0, 40); c.close_path(); c.fill(); c.restore()
    tag(c, "ITEM 3", 250, 330, 60, t - 0.1, col=TEAL)


def s16(c, t, d):  # M "Lots. India's still pushing. So next time someone says they climbed Everest..."
    TSO = wt(16, "so", 2.4) - 0.15
    if t < TSO:
        to_ctx(c, finish(AMA.at(t, speed=1.0).astype(np.float32), t, vign=0.3))
        TP = wt(16, "pushing", 1.4)
        if t > TP - 0.2:
            for j, xx in enumerate((300, 540, 780)):
                ph = (t * 1.5 + j * 0.3) % 1; arrow(c, xx, 1350 - ph * 120, xx, 1220 - ph * 120, SUMMIT, width=14, alpha=1 - ph)
            tag(c, "STILL PUSHING", W / 2, 420, 84, t - TP + 0.2, col=hexc("FFD9A0"))
        source_tag(c, "Himalaya timelapse (Ama Dablam): u_6cnilicef2 / Pixabay", t - 0.3, y=1360, size=20)
    else:
        tt = t - TSO; a = SUN.kb(min(1, tt / max(1, d - TSO)), 1.2, 1.35, (0.44, 0.45), (0.44, 0.42)); to_ctx(c, finish(a, tt, vign=0.3))
        TC = wt(16, "climbed", 3.6)
        if t > TC: tag(c, "\"I CLIMBED EVEREST!\"", W / 2, 420, 76, t - TC, col=hexc("FFFFFF"))
        source_tag(c, "Photo: Nir B. Gurung / CC BY-SA 4.0", tt - 0.3, y=1360, size=20)


def s17(c, t, d):  # F "...tell them they walked on the bottom of the sea."  -> loops to the hook
    sx, sy = hook_frame(c, t)
    TB = wt(17, "bottom", 1.8) - 0.3
    lv = lerp(H + 40, sy - 40, eout((t - TB) / 1.0)) if t > TB else H + 40
    if t > TB: rising_water(c, t, lv, REEF.at(t + 2))
    if t > TB + 0.6:
        bubbles(c, t, n=18, alpha=0.6); shells_at(c, sx, sy, t - TB - 0.6)
    tag(c, "BOTTOM OF THE SEA", W / 2, 1130, 92, t - wt(17, "walked", 0.9) + 0.1, col=hexc("BEEFEA"))


def s_end(c, t, d):
    a = SUN.kb(min(1, t / 3), 1.0, 1.06, (0.44, 0.45), (0.44, 0.45)); to_ctx(c, finish(a, t, vign=0.3))
    end_card_logo(c, t, W / 2, 760, 270, LOGO)
    tag(c, "FOLLOW", W / 2, 1180, 110, t - 0.4, col=TEAL)
    if t > 0.9: text(c, "a new wonder, explained daily", W / 2, 1360, 44, col=WHITE, stroke=8, alpha=ease((t - 0.9) / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s_end]
assert len(SCENES) == len(STARTS), (len(SCENES), len(STARTS))
NO_LIFT = (5, 9, 11, 17)   # continuous scenes (same footage/diagram/photo continues): no transition


def frame(c, gt, surf):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    c.save()
    if i > 0 and i not in NO_LIFT and t < 0.3:
        lift(c, t, i, lambda: SCENES[i - 1](c, DURS[i - 1] - 0.01, DURS[i - 1]))
    SCENES[i](c, t, d)
    c.restore()
    badge(c, gt)
    if i < len(meta):
        captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    ev = [("boom", 0.0), ("pop", s[0] + wt(0, "seashells", 0.4)), ("bubble", s[0] + wt(0, "seashells", 0.4) + 0.1)]
    ev += [("whoosh", x - 0.05) for k, x in enumerate(s[1:], 1) if k not in NO_LIFT]
    ev += [("pop", s[1] + wt(1, "crab", 3.0))]
    ev += [("pop", s[2] + 0.15), ("splash", s[2] + wt(2, "sea", 1.8)), ("bubble", s[2] + wt(2, "sea", 1.8) + 0.4)]
    ev += [("pop", s[3] + 0.3), ("ding", s[3] + wt(3, "snorkel", 3.5)), ("pop", s[3] + wt(3, "snorkel", 3.5) + 0.1)]
    ev += [("scratch", s[4] + wt(4, "four", 1.1) - 0.15)] + [("tick", s[4] + wt(4, "four", 1.1) + k * 0.1) for k in range(10)] + [("thunk", s[4] + wt(4, "late", 3.0))]
    ev += [("bubble", s[5] + 0.3), ("pop", s[5] + wt(5, "warm", 2.0)), ("pop", s[5] + wt(5, "shallow", 2.6))]
    ev += [("pop", s[6] + 0.05), ("pop", s[6] + wt(6, "sea", 1.0)), ("pop", s[6] + wt(6, "tiny", 1.8)), ("boom", s[6] + wt(6, "still", 3.2))]
    ev += [("bubble", s[7] + wt(7, "aquarium", 2.5) - 0.1), ("thunk", s[7] + wt(7, "aquarium", 2.5) + 0.25)]
    ev += [("boom", s[8] + wt(8, "india", 1.3) - 0.1)]
    ev += [("scratch", s[9] + 0.05), ("thunk", s[9] + wt(9, "country", 0.8))]
    ev += [("crack", s[10] + wt(10, "slammed", 2.0)), ("boom", s[10] + wt(10, "slammed", 2.0)), ("pop", s[10] + wt(10, "fifty-five", 3.6))]
    ev += [("drill", s[11] + wt(11, "squeezed", 0.6)), ("thunk", s[11] + wt(11, "folded", 1.6)), ("boom", s[11] + wt(11, "shoved", 2.4)), ("ding", s[11] + wt(11, "five", 3.4) + 0.3)]
    ev += [("pop", s[12] + 1.0), ("ding", s[12] + wt(12, "tape", 1.2)), ("clank", s[12] + wt(12, "tape", 1.2) + 0.3), ("thunk", s[12] + wt(12, "changing", 3.5))]
    ev += [("clank", s[13] + 0.1), ("pop", s[13] + 0.9), ("pop", s[13] + wt(13, "rising", 2.3)), ("ding", s[13] + wt(13, "four", 3.4))]
    T14 = s[14] + wt(14, "fingernails", 2.0) - 0.4
    ev += [("pop", s[14] + 0.05)] + [("tick", T14 + k * 0.12) for k in range(8)] + [("ding", T14 + 0.95), ("trombone", T14 + 1.3)]
    ev += [("pop", s[15] + 0.3), ("ding", s[15] + wt(15, "patience", 0.8))]
    ev += [("pop", s[16] + wt(16, "pushing", 1.4)), ("whoosh", s[16] + wt(16, "so", 2.4) - 0.15), ("pop", s[16] + wt(16, "climbed", 3.6))]
    ev += [("splash", s[17] + wt(17, "bottom", 1.8) - 0.3), ("bubble", s[17] + wt(17, "bottom", 1.8)), ("boom", s[18]), ("pop", s[18] + 0.4)]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]:
            frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    elif sys.argv[1] == "beats":
        for i in range(len(STARTS)): print(i, round(STARTS[i], 2), round(DURS[i], 2), meta[i]["cap"] if i < len(meta) else "END")
    else:
        json.dump({"total": TOTAL, "events": events(), "music_style": "eastasia"}, open("events.json", "w"))
        a, b = (int(v) for v in sys.argv[2:4]) if len(sys.argv) > 3 else (0, int(math.ceil(TOTAL * FPS)))
        out = sys.argv[4] if len(sys.argv) > 4 else "video.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a, b):
            frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", a, b, "total", TOTAL)
