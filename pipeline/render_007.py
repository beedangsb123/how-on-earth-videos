"""Video 007 — GTA 6 trend: "That broken bridge in the GTA 6 trailer? It's real." -> the Bahia Honda Rail Bridge and
Henry Flagler's Overseas Railroad to Key West (mega-build). Made 2026-11-24 on Bidhan's request (GTA 6 launched
19 Nov 2026). NO game footage, logos, fonts or characters: only real photos of the real place + our own graphics.
Structure: "Real or game?" quiz — F host (Sarah) asks the viewer and reveals, M contestant (Liam) always guesses
"game" and jokes.
NEW LOOK v5 "quiz show / map HUD" (different from 006 Art Deco):
 - slab(): dark glass headline slabs with a sunset-coral / aqua neon underline that wipes in
 - quiz(): REAL / GAME answer buttons, a pressed state and a big rotated REAL stamp on the reveal
 - pin(): generic map waypoint diamond + pulsing ring on the real photo; neon route over historic aerials
 - glitch(): RGB-split + slice-offset transition instead of shutter / whip
 - drawn cross-sections: shallow concrete arches vs deep-channel steel truss; the 1938 deck added ON TOP of the truss
Real media: see credits_007.txt. usage (work dir with meta.json, media/):
  python render_007.py stills <prefix> t1 t2 ...   |   python render_007.py full [a b out.mp4]"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish

Image.MAX_IMAGE_PIXELS = None
CORAL = hexc("FF6B5E"); AQUA = hexc("2EE6D6"); GLASS = (0.04, 0.06, 0.12); SUNG = hexc("FFC857"); GREEN = hexc("36D17A")
engine.CAP_ACCENT = AQUA


def finish(a, t, **kw):
    return _finish(haze(a, t), t, **kw)


meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]
END = 2.4
STARTS.append(_t); DURS.append(END)
TOTAL = _t + END
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix): return sorted(glob.glob(f"media*/{prefix}*"))[0]


HOOK = Photo(M("Florida_Keys_Scenic"), maxz=1.3)                       # NARA 7718464, PD
COLOUR = Photo(M("Aerial_photographs_of_Florida_MM00034362x"), maxz=1.3)  # Florida Keys Public Libraries, CC BY 2.0
RAIL = Photo(M("Aerial_photographs_of_Florida_MM00000353"), archival=True, maxz=1.3)  # Florida Keys Public Libraries, CC BY 2.0
PIGEON = Photo(M("Pigeon_Key"), archival=True, maxz=1.3)               # HAER, 1938, PD
SEVEN = Photo(M("Seven_Mile"), maxz=1.3)                               # US DOT, PD
TRUSS = Photo(M("Bahia_Honda_Rail_Bridge_FL1"), maxz=1.3)              # Acroterion, CC BY-SA 4.0
INSIDE = Photo(M("Old_Bahia_Honda"), maxz=1.3)                         # Kalman Venczel, CC BY-SA 3.0
PARKER = Photo(M("Parker_deck"), maxz=1.3)                             # Z22, CC BY-SA 4.0
ROAD = Photo(M("Bahia_Honda_Bridge_roadway"), maxz=1.3)                # postcard, PD
SAT = Photo(M("nasa_iss065e008077"), maxz=1.3)                         # NASA ISS, PD
P1 = Particles(90, 3)
TX = make_textures(7)
_BL = {}


def blurred(key, photo, f=(0.5, 0.5), dim=0.6):
    if key not in _BL: _BL[key] = blur(_finish(photo.kb(0, 1.0, 1.0, f, f), 0), 14, dim)
    return _BL[key]


def bg(c, key, photo, t, f=(0.5, 0.5), dim=0.6):
    to_ctx(c, haze(blurred(key, photo, f, dim), t, amt=30).astype(np.uint8))


def cam(c, z, cx=W / 2, cy=H / 2):
    c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)


def punch(t, at=0.0, amt=0.07):
    return 1 + amt * (1 - eout((t - at) / 0.35)) if t >= at else 1.0


def counter(t, v0, v1, dur, fmt="{:,}"):
    return fmt.format(int(round(lerp(v0, v1, eout(t / dur))))) if t > 0 else fmt.format(v0)


def zpt(p, z, cx=W / 2, cy=H / 2):  # where an image point lands after a centred zoom z
    return ((p[0] - cx) * z + cx, (p[1] - cy) * z + cy)


# ---------------- look v5: quiz show + map HUD ----------------
def slab(c, s, x, y, size, t, col=AQUA, fg=WHITE, maxw=940, sub=None):
    """dark glass headline slab; text slides up, neon underline wipes left->right"""
    if t <= 0: return
    w = text_w(c, s, size)
    if w > maxw - 70: size *= (maxw - 70) / w; w = maxw - 70
    k = eout(t / 0.28); bw, bh = w + 70, size * 1.42
    c.save(); c.translate(x, y + (1 - k) * 40)
    c.set_source_rgba(0, 0, 0, 0.35 * k); rrect(c, -bw / 2 + 8, -bh / 2 + 12, bw, bh, 18); c.fill()
    c.set_source_rgba(*GLASS, 0.86 * k); rrect(c, -bw / 2, -bh / 2, bw, bh, 18); c.fill()
    c.set_source_rgba(1, 1, 1, 0.10 * k); rrect(c, -bw / 2, -bh / 2, bw, bh * 0.45, 18); c.fill()
    u = eout((t - 0.08) / 0.35)
    if u > 0:
        for lw, a in ((18, 0.18), (10, 0.35), (5, 1.0)):
            c.set_source_rgba(*col, a); c.set_line_width(lw); c.move_to(-bw / 2 + 18, bh / 2 - 6); c.line_to(-bw / 2 + 18 + (bw - 36) * u, bh / 2 - 6); c.stroke()
    text(c, s, 0, size * 0.36, size, col=fg, alpha=k)
    c.restore()
    if sub and t > 0.25:
        a = ease((t - 0.25) / 0.25); sz = 42; sw = text_w(c, sub, sz) + 40
        c.save(); c.translate(x, y + bh / 2 + 46)
        c.set_source_rgba(*col, 0.95 * a); rrect(c, -sw / 2, -sz * 0.78, sw, sz * 1.3, 12); c.fill()
        text(c, sub, 0, sz * 0.25, sz, col=GLASS, alpha=a); c.restore()


def quiz(c, t, pressed=None, press_t=0.0, y=1000):
    """REAL / GAME answer buttons. pressed='GAME' lights it magenta-coral with a click squash."""
    if t <= 0: return
    for j, (lab, col) in enumerate((("REAL", GREEN), ("GAME", CORAL))):
        a = eout((t - j * 0.12) / 0.3)
        if a <= 0: continue
        x = 290 + j * 500; on = pressed == lab and press_t > 0
        sq = 1 - 0.08 * math.sin(math.pi * min(1, press_t / 0.18)) if on else 1
        c.save(); c.translate(x, y + (1 - a) * 80); c.scale(sq, sq)
        c.set_source_rgba(0, 0, 0, 0.4 * a); rrect(c, -200 + 10, -78 + 14, 400, 156, 78); c.fill()
        if on:
            for r, al in ((40, 0.12), (24, 0.2), (12, 0.35)):
                c.set_source_rgba(*col, al); rrect(c, -200 - r, -78 - r, 400 + 2 * r, 156 + 2 * r, 78 + r); c.fill()
        c.set_source_rgba(*(col if on else GLASS), 0.92 * a); rrect(c, -200, -78, 400, 156, 78); c.fill()
        c.set_source_rgba(*col, a); c.set_line_width(7); rrect(c, -200, -78, 400, 156, 78); c.stroke()
        text(c, lab, 0, 30, 84, col=GLASS if on else WHITE, alpha=a)
        c.restore()


def stamp(c, s, x, y, t, col=GREEN, size=170, ang=-0.12):
    """big rotated rubber-stamp reveal (slams in from 1.6x scale)"""
    if t <= 0: return
    k = min(1, t / 0.16); sc = lerp(1.6, 1.0, eout(k)); a = k
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(sc, sc)
    w = text_w(c, s, size) + 80; h = size * 1.3
    c.set_source_rgba(*col, 0.18 * a); rrect(c, -w / 2, -h / 2, w, h, 26); c.fill()
    c.set_source_rgba(*col, a); c.set_line_width(14); rrect(c, -w / 2, -h / 2, w, h, 26); c.stroke()
    c.set_line_width(4); rrect(c, -w / 2 + 16, -h / 2 + 16, w - 32, h - 32, 16); c.stroke()
    text(c, s, 0, size * 0.36, size, col=col, alpha=a, stroke=0)
    c.restore()


def pin(c, x, y, t, col=CORAL, lab=None):
    """generic map waypoint (diamond on a stem) + pulsing ground ring"""
    if t <= 0: return
    k = back(min(1, t / 0.35)); bob = 8 * math.sin(t * 4)
    for j in range(2):
        ph = (t * 0.8 + j * 0.5) % 1.0
        c.save(); c.translate(x, y); c.scale(1, 0.4); c.set_source_rgba(*col, 0.8 * (1 - ph)); c.set_line_width(6)
        c.arc(0, 0, 20 + 90 * ph, 0, 2 * math.pi); c.restore(); c.stroke()
    c.save(); c.translate(x, y - 120 * k + bob)
    c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(5); c.move_to(0, 0); c.line_to(0, 120 * k - bob - 10); c.stroke()
    c.rotate(math.pi / 4); s = 46 * k
    c.set_source_rgba(0, 0, 0, 0.4); c.rectangle(-s / 2 + 6, -s / 2 + 6, s, s); c.fill()
    c.set_source_rgb(*col); c.rectangle(-s / 2, -s / 2, s, s); c.fill()
    c.set_source_rgb(1, 1, 1); c.set_line_width(5); c.rectangle(-s / 2, -s / 2, s, s); c.stroke()
    c.restore()
    if lab and t > 0.3:
        a = ease((t - 0.3) / 0.25); sz = 38; w = text_w(c, lab, sz) + 36
        c.set_source_rgba(*GLASS, 0.85 * a); rrect(c, x - w / 2, y - 230 + bob, w, sz * 1.4, 12); c.fill()
        text(c, lab, x, y - 230 + bob + sz * 1.0, sz, col=col, alpha=a)


def glitch(surf, t, dur=0.22):
    """RGB-split + horizontal slice-offset transition for the first `dur` s of a scene"""
    if t >= dur: return
    surf.flush()
    a = np.ndarray((H, surf.get_stride() // 4, 4), np.uint8, surf.get_data())[:, :W, :3]
    k = 1 - eout(t / dur); sh = int(36 * k)
    if sh < 2: return
    src = a.copy()
    a[:, :, 2] = np.roll(src[:, :, 2], sh, axis=1)     # cairo BGRA: index 2 = red
    a[:, :, 0] = np.roll(src[:, :, 0], -sh, axis=1)    # blue
    rng = np.random.default_rng(int(t * 1000))
    for _ in range(6):
        y0 = int(rng.integers(0, H - 80)); hgt = int(rng.integers(20, 90)); dx = int(rng.integers(-80, 80) * k)
        a[y0:y0 + hgt] = np.roll(a[y0:y0 + hgt], dx, axis=1)
    surf.mark_dirty()


def sea(c, y0, t, y1=H + 20):
    """water body for the drawn sections: aqua -> deep blue gradient + drifting light ripples (no busy texture)"""
    g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgba(0, *hexc("39C6D6"), 0.92); g.add_color_stop_rgba(1, *hexc("0B3B6E"), 0.96)
    c.rectangle(-20, y0, W + 40, y1 - y0); c.set_source(g); c.fill()
    c.set_source_rgba(1, 1, 1, 0.35); c.set_line_width(4)
    for j in range(14):
        yy = y0 + 18 + j * 46
        if yy > y1: break
        x = (j * 173 + t * 60) % (W + 300) - 150
        c.move_to(x, yy); c.curve_to(x + 40, yy - 8, x + 80, yy + 8, x + 120, yy); c.stroke()


def depth_section(c, t, k_truss=1.0, labels=0.0):
    """cross-section: shallow water -> concrete arches; deepest channel -> long steel truss spans (simplified)"""
    bg(c, "seven", SEVEN, t, (0.5, 0.5), dim=0.55)
    sea_ = 760; c.save()
    c.restore(); sea(c, sea_, t)
    # seabed profile: shallow on the left, deep channel in the middle-right
    bed = [(-20, 1180), (260, 1180), (420, 1250), (520, 1560), (900, 1580), (1000, 1260), (1100, 1200)]
    c.move_to(*bed[0]); [c.line_to(*p) for p in bed[1:]]; c.line_to(1100, H + 20); c.line_to(-20, H + 20); c.close_path()
    c.save(); c.clip(); tex(c, TX["sand"], dy=t * 5); c.paint(); c.set_source_rgba(0.2, 0.15, 0.1, 0.25); c.paint(); c.restore()
    deck = 700
    # concrete arches over the shallows
    for x0 in (-40, 110, 260):
        c.set_source_rgb(*hexc("D8D2C4")); c.rectangle(x0, deck, 150, 30); c.fill()
        c.move_to(x0, deck + 30); c.curve_to(x0, deck + 140, x0 + 150, deck + 140, x0 + 150, deck + 30)
        c.line_to(x0 + 150, 1190); c.line_to(x0 + 128, 1190); c.curve_to(x0 + 120, deck + 120, x0 + 30, deck + 120, x0 + 22, 1190)
        c.line_to(x0, 1190); c.close_path(); c.set_source_rgb(*hexc("C9C2B2")); c.fill()
    # piers + steel truss spans over the deep channel
    for px in (410, 690, 970):
        c.set_source_rgb(*hexc("BDB6A6")); c.rectangle(px - 26, deck + 40, 52, 1600 - deck); c.fill()
    for j, (x0, x1) in enumerate(((410, 690), (690, 970))):
        kk = ease((k_truss - j * 0.35) / 0.6)
        if kk <= 0: continue
        top = deck - 170; c.save(); c.set_source_rgba(*hexc("B0502E"), kk); c.set_line_width(12)
        mid = (x0 + x1) / 2
        c.move_to(x0, deck); c.line_to(x1, deck); c.stroke()
        c.move_to(x0, deck); c.line_to(x0 + 50, top + 40); c.curve_to(mid - 60, top, mid + 60, top, x1 - 50, top + 40); c.line_to(x1, deck); c.stroke()
        c.set_line_width(7)
        for q in range(1, 6):
            xa = x0 + (x1 - x0) * q / 6; ya = top + 30 + 30 * abs(q - 3) / 3
            c.move_to(xa, deck); c.line_to(xa, ya); c.stroke()
            c.move_to(xa, deck); c.line_to(x0 + (x1 - x0) * (q + (1 if q < 3 else -1)) / 6, top + 40); c.stroke()
        c.restore()
    if labels > 0:
        a = ease(labels / 0.3)
        text(c, "SHALLOW", 140, 1150, 40, col=WHITE, stroke=8, alpha=a)
        text(c, "DEEPEST CHANNEL", 690, 1500, 44, col=SUNG, stroke=8, alpha=a)
    text(c, "(simplified, not to scale)", W / 2, 1650, 26, col=WHITE, stroke=6, alpha=0.8)


def deck_section(c, t, k_road=0.0, car_x=None, dim65=0.0):
    """end-on view of the truss: 1912 train INSIDE the truss -> 1938 road deck ON TOP, ~65 ft above the sea"""
    bg(c, "road", ROAD, t, (0.5, 0.5), dim=0.5)
    sea_ = 1560; sea(c, sea_, t)
    x0, x1, top, bot = 300, 780, 760, 1080
    c.set_source_rgb(*hexc("BDB6A6")); c.rectangle(470, bot, 140, sea_ - bot + 40); c.fill()           # pier
    c.set_source_rgba(0, 0, 0, 0.2); c.rectangle(470, bot, 30, sea_ - bot + 40); c.fill()
    c.save(); c.set_source_rgb(*hexc("B0502E")); c.set_line_width(14)
    c.rectangle(x0, top, x1 - x0, bot - top); c.stroke()
    c.move_to(x0, top); c.line_to(x1, bot); c.move_to(x1, top); c.line_to(x0, bot); c.stroke(); c.restore()
    # the 1912 train inside (fades as the road arrives)
    a = 1 - ease(k_road / 0.4)
    if a > 0:
        c.set_source_rgba(*hexc("2A2F3A"), a); rrect(c, 390, 860, 300, 200, 20); c.fill()
        c.set_source_rgba(1, 0.85, 0.5, a)
        for q in range(3): c.rectangle(415 + q * 90, 890, 70, 60); c.fill()
        text(c, "1912: TRAIN INSIDE", W / 2, 1230 - 0, 40, col=WHITE, stroke=8, alpha=a)
    if k_road > 0:
        kk = eout(k_road); dw = (x1 - x0 + 260) * kk
        c.set_source_rgb(*hexc("D8D2C4")); c.rectangle(W / 2 - dw / 2, top - 46, dw, 46); c.fill()
        c.set_source_rgb(*SUNG); c.set_line_width(5); c.set_dash([30, 24]); c.move_to(W / 2 - dw / 2, top - 23); c.line_to(W / 2 + dw / 2, top - 23); c.stroke(); c.set_dash([])
        if kk > 0.9: text(c, "1938: ROAD ON TOP", W / 2, 1230, 40, col=SUNG, stroke=8)
    if car_x is not None:  # a small car on the new deck
        c.save(); c.translate(car_x, top - 46)
        c.set_source_rgb(*CORAL); rrect(c, -70, -56, 140, 40, 10); c.fill(); rrect(c, -40, -86, 80, 36, 10); c.fill()
        c.set_source_rgb(0.1, 0.1, 0.12)
        for wx in (-42, 42): c.arc(wx, -14, 15, 0, 2 * math.pi); c.fill()
        c.restore()
    if dim65 > 0:
        a = ease(dim65 / 0.3); x = 900
        c.set_source_rgba(1, 1, 1, a); c.set_line_width(6)
        c.move_to(x, top - 46); c.line_to(x, sea_); c.stroke()
        for yy, d in ((top - 46, 1), (sea_, -1)):
            c.move_to(x - 22, yy + d * 30); c.line_to(x, yy); c.line_to(x + 22, yy + d * 30); c.stroke()
        c.set_source_rgba(*GLASS, 0.85 * a); rrect(c, x - 110, 1120, 220, 80, 14); c.fill()
        text(c, "65 FT", x, 1178, 52, col=SUNG, alpha=a)


def storm(c, t, x, y, r):
    """hurricane symbol (spiral bands) over the satellite view — no damage imagery"""
    c.save(); c.translate(x, y); c.rotate(-t * 1.6)
    for j in range(3):
        c.save(); c.rotate(j * 2 * math.pi / 3)
        c.move_to(0, 0)
        for q in range(40):
            a = q / 39 * 2.2; rr = r * q / 39
            c.line_to(math.cos(a) * rr, math.sin(a) * rr)
        c.set_source_rgba(1, 1, 1, 0.75); c.set_line_width(r * 0.16); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke(); c.restore()
    c.set_source_rgba(*GLASS, 0.9); c.arc(0, 0, r * 0.14, 0, 2 * math.pi); c.fill()
    c.restore()


# ---------------- scenes ----------------
GAP = (528, 1010)          # gap between the broken spans in HOOK at kb(f=(0.35, 0.5)), z = 1
PIG = [(0, 495), (270, 660), (540, 800), (810, 1050), (1080, 1320)]   # 1912 rail line across Pigeon Key (HAER, z=1)


def hook_frame(c, t, z=1.0):
    zz = lerp(1.0, 1.08, min(1, t / 3.0))
    a = HOOK.kb(0, zz, zz, (0.35, 0.5), (0.35, 0.5))
    c.save(); cam(c, z, W / 2, 1000); to_ctx(c, finish(a, t, vign=0.35)); c.restore()
    gx, gy = zpt(zpt(GAP, zz), z, W / 2, 1000)
    slab(c, "GTA 6 BRIDGE?", W / 2, 360, 104, t + 1, col=CORAL)
    pin(c, gx, gy, t - 0.4, col=CORAL, lab="REAL PLACE")
    if t > 2.1: stamp(c, "REAL", W / 2, 640, t - 2.1, col=GREEN, size=130)


def s0(c, t, d):  # F "That broken bridge in the GTA 6 trailer? It's real."
    hook_frame(c, t, z=punch(t, 1.2, 0.05))
    source_tag(c, "Photo: NARA (public domain) · Bahia Honda, Florida Keys", t - 0.3, y=1290, size=22)


def s1(c, t, d):  # M "Come on. Nobody builds half a bridge."
    a = COLOUR.kb(t / d, 1.0, 1.1, (0.45, 0.62), (0.45, 0.66)); to_ctx(c, finish(a, t, vign=0.35))
    slab(c, "HALF A BRIDGE?", W / 2, 400, 110, t - 0.6, col=CORAL)
    for x0, x1 in ((330, 560),):   # bracket the gap
        k = ease((t - 0.8) / 0.4); c.set_source_rgba(*CORAL, k); c.set_line_width(8)
        c.move_to(x0, 1180); c.line_to(x0, 1320); c.move_to(x1, 1180); c.line_to(x1, 1320); c.stroke()
        c.set_dash([16, 14]); c.move_to(x0, 1250); c.line_to(x1, 1250); c.stroke(); c.set_dash([])
    source_tag(c, "Photo: Florida Keys Public Libraries / CC BY 2.0", t - 0.2)


def s2(c, t, d):  # F "Real or game? A train that rode across the sea, all the way to Key West."
    a = RAIL.kb(t / d, 1.0, 1.1, (0.6, 0.4), (0.62, 0.38)); to_ctx(c, finish(a, t, archival=True, vign=0.4))
    slab(c, "REAL OR GAME?", W / 2, 380, 120, t - 0.05, col=SUNG)
    if t > 1.5: slab(c, "A TRAIN ACROSS THE SEA", W / 2, 560, 70, t - 1.5, col=AQUA)
    quiz(c, t - 0.4, y=1040)
    source_tag(c, "Photo: Florida Keys Public Libraries / CC BY 2.0", t - 0.3)


def s3(c, t, d):  # M "Game. Definitely game."
    a = RAIL.kb(1, 1.0, 1.1, (0.6, 0.4), (0.62, 0.38)); to_ctx(c, finish(a, t + 4, archival=True, vign=0.4))
    slab(c, "REAL OR GAME?", W / 2, 380, 120, 1.0, col=SUNG)
    quiz(c, 1.0, pressed="GAME", press_t=t - 0.05, y=1040)


def s4(c, t, d):  # F "Real. In 1912, the tracks ran more than a hundred miles out over open water."
    if t < 2.1:
        a = RAIL.kb(1, 1.0, 1.1, (0.6, 0.4), (0.62, 0.38)); to_ctx(c, finish(a, t + 5, archival=True, vign=0.4))
        quiz(c, 1.0, pressed="REAL", press_t=t, y=1040)
        stamp(c, "REAL", W / 2, 640, t - 0.05, col=GREEN)
        if t > 0.8: slab(c, "1912", W / 2, 380, 130, t - 0.8, col=SUNG)
    else:
        tt = t - 2.1; z = 1.3
        a = PIGEON.kb(tt / (d - 2.1), z, z * 1.05, (0.5, 0.5), (0.52, 0.5)); to_ctx(c, finish(a, tt, archival=True, vign=0.4))
        zz = lerp(1.0, 1.05, ease(tt / (d - 2.1)))
        slab(c, counter(tt - 0.6, 0, 100, 1.4) + "+ MILES", W / 2, 380, 120, tt - 0.05, col=AQUA, sub="OVER OPEN WATER")
        source_tag(c, "Photo: HAER, 1938 (PD) · Source: Florida Keys official history (fla-keys.com)", tt - 0.3, size=21)


def s5(c, t, d):  # M "Who signed off on that?"
    a = SEVEN.kb(t / d, 1.1, 1.2, (0.4, 0.5), (0.45, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
    slab(c, "WHO SIGNED OFF?!", W / 2, 400, 110, t - 0.05, col=CORAL)


def s6(c, t, d):  # F "A railroad boss with deep pockets. It took seven years, and people called it the eighth wonder of the world."
    if t < 2.4:
        a = SEVEN.kb(t / 2.4, 1.2, 1.3, (0.6, 0.45), (0.7, 0.45)); to_ctx(c, finish(a, t, vign=0.35))
        slab(c, "DEEP POCKETS", W / 2, 400, 110, t - 1.0, col=SUNG)
        source_tag(c, "Photo: US DOT (public domain)", t - 0.2)
    else:
        tt = t - 2.4; a = RAIL.kb(tt / (d - 2.4), 1.15, 1.3, (0.4, 0.3), (0.45, 0.35)); to_ctx(c, finish(a, tt, archival=True, vign=0.4))
        slab(c, counter(tt - 0.3, 0, 7, 0.8) + " YEARS", W / 2, 380, 130, tt - 0.05, col=AQUA)
        if tt > 2.2: stamp(c, "8TH WONDER", W / 2, 900, tt - 2.2, col=SUNG, size=110, ang=-0.08)
        if tt > 2.4: text(c, "OF THE WORLD", W / 2, 1050, 56, col=WHITE, stroke=10, alpha=ease((tt - 2.4) / 0.3))
        source_tag(c, "Source: Florida State Parks", tt - 0.4)


def s7(c, t, d):  # M "So why does that bridge look broken?"
    a = HOOK.kb(0, 1.25, 1.25, (0.35, 0.52), (0.35, 0.52)); c.save(); cam(c, 1 + 0.05 * t); to_ctx(c, finish(a, t, vign=0.35)); c.restore()
    slab(c, "WHY BROKEN?", W / 2, 400, 120, t - 0.05, col=CORAL)
    text(c, "?", 540, 1080, 260, col=CORAL, stroke=14, alpha=ease((t - 0.4) / 0.2))


def s8(c, t, d):  # F "Bahia Honda had the deepest channel on the route, so they built giant steel frames called trusses."
    if t < 2.4:
        depth_section(c, t, k_truss=0.0, labels=t - 0.9)
        slab(c, "BAHIA HONDA", W / 2, 380, 120, t - 0.05, col=AQUA)
        if t > 1.3: slab(c, "DEEPEST CHANNEL", W / 2, 560, 76, t - 1.3, col=SUNG)
    elif t < 4.6:
        tt = t - 2.4; depth_section(c, t, k_truss=ease(tt / 1.0) * 1.4, labels=1.0)
        slab(c, "STEEL FRAMES", W / 2, 380, 120, tt - 0.05, col=CORAL)
    else:
        tt = t - 4.6; a = INSIDE.kb(tt / (d - 4.6), 1.0, 1.12, (0.5, 0.5), (0.5, 0.45)); to_ctx(c, finish(a, tt, vign=0.35))
        slab(c, "= TRUSSES", W / 2, 380, 130, tt - 0.4, col=CORAL)
        source_tag(c, "Photo: Kalman Venczel / CC BY-SA 3.0 · Sources: Florida State Parks, HAER", tt - 0.2, size=21)


def s9(c, t, d):  # F "Then, in 1935, a hurricane ended the railroad."
    a = SAT.kb(t / d, 1.0, 1.15, (0.5, 0.5), (0.5, 0.5)); to_ctx(c, finish(a, t, vign=0.3))
    storm(c, t, 560, 900, 260 * ease(t / 0.8))
    slab(c, "1935", W / 2, 380, 130, t - 0.3, col=SUNG)
    if t > 1.4: slab(c, "THE RAILROAD ENDS", W / 2, 560, 76, t - 1.4, col=CORAL)
    source_tag(c, "Image: NASA ISS (PD) · symbol only · Source: Florida State Parks", t - 0.3, size=21)


def s10(c, t, d):  # F "Real or game? Cars driving on the roof of a train bridge."
    a = PARKER.kb(t / d, 1.0, 1.1, (0.5, 0.5), (0.55, 0.45)); to_ctx(c, finish(a, t, vign=0.35))
    slab(c, "REAL OR GAME?", W / 2, 380, 120, t - 0.05, col=SUNG)
    if t > 1.0: slab(c, "CARS ON THE ROOF?", W / 2, 560, 76, t - 1.0, col=AQUA)
    quiz(c, t - 0.3, y=1080)
    source_tag(c, "Photo: Z22 / CC BY-SA 4.0", t - 0.3)


def s11(c, t, d):  # M "Game. That's a cheat code."
    a = PARKER.kb(1, 1.0, 1.1, (0.5, 0.5), (0.55, 0.45)); to_ctx(c, finish(a, t + 4, vign=0.35))
    slab(c, "CHEAT CODE?", W / 2, 380, 120, t - 0.5, col=CORAL)
    quiz(c, 1.0, pressed="GAME", press_t=t - 0.05, y=1080)


def s12(c, t, d):  # F "Real! In 1938 they paved right over the top of the trusses. You drove sixty-five feet above the sea."
    if t < 1.6:
        a = PARKER.kb(1, 1.0, 1.1, (0.5, 0.5), (0.55, 0.45)); to_ctx(c, finish(a, t + 5, vign=0.35))
        quiz(c, 1.0, pressed="REAL", press_t=t, y=1080)
        stamp(c, "REAL!", W / 2, 700, t - 0.05, col=GREEN)
    elif t < 3.9:
        tt = t - 1.6; deck_section(c, tt, k_road=ease((tt - 0.4) / 1.2))
        slab(c, "1938", W / 2, 380, 130, tt - 0.05, col=SUNG)
        if tt > 1.0: slab(c, "ROAD ON TOP", W / 2, 560, 80, tt - 1.0, col=AQUA)
    else:
        tt = t - 3.9; deck_section(c, tt + 3, k_road=1.0, car_x=lerp(-100, 640, eout(tt / 1.6)), dim65=tt - 0.8)
        slab(c, "65 FT UP", W / 2, 380, 130, tt - 0.8, col=CORAL)
        source_tag(c, "Sources: Keys Weekly, Florida State Parks (simplified)", tt - 0.3, size=22)


def s13(c, t, d):  # M "My palms are sweating just hearing that."
    a = ROAD.kb(t / d, 1.05, 1.2, (0.5, 0.5), (0.5, 0.55)); to_ctx(c, finish(a, t, vign=0.35))
    slab(c, "SWEATY PALMS", W / 2, 400, 120, t - 0.3, col=CORAL)
    for j in range(5):   # sweat drops
        ph = (t * 1.2 + j / 5) % 1.0; x = 200 + j * 170
        c.set_source_rgba(*AQUA, 0.9 * (1 - ph)); c.arc(x, 700 + 300 * ph, 16, 0, 2 * math.pi); c.fill()
        c.move_to(x - 16, 700 + 300 * ph); c.line_to(x, 670 + 300 * ph); c.line_to(x + 16, 700 + 300 * ph); c.fill()
    source_tag(c, "Postcard: Bahia Honda Bridge roadway (PD)", t - 0.2)


def s14(c, t, d):  # F "A new bridge took over in 1972, and pieces of the old one were cut out so boats could pass safely."
    a = COLOUR.kb(t / d, 1.0, 1.08, (0.45, 0.6), (0.45, 0.62)); to_ctx(c, finish(a, t, vign=0.35))
    z = lerp(1.0, 1.08, ease(t / d))
    k = ease((t - 0.3) / 0.8)
    if k > 0:
        y = zpt((0, 975), z)[1]
        c.set_source_rgba(*AQUA, 0.9 * k); c.set_line_width(10); c.move_to(0, y - 28); c.line_to(W * k, y - 28); c.stroke()
        if t > 0.6: pin(c, *zpt((760, 960), z), t - 0.6, col=AQUA, lab="NEW BRIDGE · 1972")
    if t > 2.8:
        gx, gy = zpt((450, 1255), z); pin(c, gx, gy, t - 2.8, col=CORAL, lab="SPAN CUT OUT")
    slab(c, "1972", W / 2, 380, 130, t - 0.9, col=SUNG)
    if t > 4.4: slab(c, "SAFE FOR BOATS", W / 2, 560, 80, t - 4.4, col=AQUA)
    source_tag(c, "Photo: Florida Keys Public Libraries / CC BY 2.0 · Source: HAER", t - 0.3, size=22)


def s15(c, t, d):  # M "So the broken bridge in GTA 6..."
    hook_frame(c, 0.6 + t * 0.3, z=lerp(1.06, 1.0, eout(t / 0.6)))


def s16(c, t, d):  # F "Is a real, hundred-year-old wonder. And you can still walk on part of it."
    if t < 2.3:
        a = TRUSS.kb(t / 2.3, 1.0, 1.12, (0.5, 0.5), (0.45, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
        stamp(c, "REAL", W / 2, 720, t - 0.2, col=GREEN, size=150)
        slab(c, "100+ YEARS OLD", W / 2, 380, 110, t - 0.9, col=SUNG)
        source_tag(c, "Photo: Acroterion / CC BY-SA 4.0", t - 0.2)
    else:  # loop back to the hook image
        tt = t - 2.3; hook_frame(c, 0.4 + tt * 0.3, z=lerp(1.08, 1.0, eout(tt / 0.6)))
        slab(c, "YOU CAN STILL WALK IT", W / 2, 1150, 70, tt - 0.9, col=AQUA)


def s_end(c, t, d):
    a = SEVEN.kb(min(1, t / 3), 1.0, 1.08, (0.4, 0.5), (0.42, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
    end_card_logo(c, t, W / 2, 760, 270, LOGO)
    slab(c, "FOLLOW", W / 2, 1180, 120, t - 0.6, col=CORAL)
    if t > 1.0: text(c, "real places, real engineering", W / 2, 1330, 48, col=WHITE, stroke=8, alpha=ease((t - 1.0) / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s_end]
assert len(SCENES) == len(STARTS)
NO_GLITCH = (3, 11, 15)


def frame(c, gt, surf):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    c.save()
    if i > 0 and t < 0.3:
        z = 1 + 0.05 * (1 - eout(t / 0.3)); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[i](c, t, d)
    c.restore()
    badge(c, gt)
    if i < len(meta):
        captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))
    if i > 0 and i not in NO_GLITCH: glitch(surf, t)


def events():
    s = STARTS
    ev = [("boom", 0.0), ("pop", 0.3), ("thunk", 0.5), ("boom", 2.1)]
    ev += [("whoosh", x - 0.05) for x in s[1:] if x not in [s[i] for i in NO_GLITCH]]
    ev += [("pop", s[1] + 0.6), ("tick", s[1] + 0.8), ("tick", s[1] + 0.95)]
    ev += [("pop", s[2]), ("pop", s[2] + 0.4), ("pop", s[2] + 0.52), ("pop", s[2] + 1.5)]
    ev += [("thunk", s[3] + 0.05), ("ding", s[3] + 0.1)]
    ev += [("boom", s[4] + 0.05), ("pop", s[4] + 0.8)] + [("tick", s[4] + 2.7 + k * 0.12) for k in range(11)]
    ev += [("pop", s[5])] + [("pop", s[6] + 1.0), ("tick", s[6] + 2.7), ("tick", s[6] + 2.9), ("boom", s[6] + 4.6)]
    ev += [("pop", s[7] + 0.4), ("pop", s[8]), ("pop", s[8] + 1.3)] + [("clank", s[8] + 3.0 + k * 0.3) for k in range(4)] + [("pop", s[8] + 5.0)]
    ev += [("pop", s[9] + 0.3), ("pop", s[9] + 1.4)]
    ev += [("pop", s[10]), ("pop", s[10] + 0.3), ("pop", s[10] + 1.0), ("thunk", s[11] + 0.05), ("ding", s[11] + 0.1)]
    ev += [("boom", s[12] + 0.05), ("pop", s[12] + 1.6), ("clank", s[12] + 2.2), ("pop", s[12] + 2.6), ("thunk", s[12] + 4.7), ("pop", s[12] + 4.7)]
    ev += [("pop", s[13] + 0.3), ("pop", s[14] + 0.6), ("pop", s[14] + 0.9), ("pop", s[14] + 2.8), ("pop", s[14] + 4.4)]
    ev += [("boom", s[16] + 0.2), ("pop", s[16] + 0.9), ("thunk", s[16] + 2.3), ("pop", s[17] + 0.6)]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]:
            frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events(), "music_style": "default"}, open("events.json", "w"))
        a, b = (int(v) for v in sys.argv[2:4]) if len(sys.argv) > 3 else (0, int(math.ceil(TOTAL * FPS)))
        out = sys.argv[4] if len(sys.argv) > 4 else "video.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a, b):
            frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", a, b, "total", TOTAL)
