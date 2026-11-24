"""Video 008 — Strait of Hormuz (Bidhan's decision 2026-11-23): STRICTLY NEUTRAL geography + shipping logistics in the
"Press the button" what-if format. No conflict, no militaries, no governments, no blame; the button is a thought
experiment. Narrator M (Roger) + F (Matilda) who presses the button.
NEW LOOK v6 "logistics infographic" (different from 007's quiz/HUD):
 - pill(): white rounded headline pills with an orange block that slide in from the right
 - big arcade button() with an "ARE YOU SURE?" dialog gag, press / un-press animation
 - schematic lanes map (inbound / buffer / outbound) with moving tanker icons, pipeline bypass schematic, barrel bars,
   tanker queue — all clearly marked "schematic"
 - zoomblur(): radial zoom-blur punch transition
Real media: NASA ISS / Gemini photos (PD), tanker photos (CC). usage: python render_008.py stills p t.. | full [a b out]"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish

ORANGE2 = hexc("FF8A00"); INK = hexc("101828"); SEA = hexc("2F7FB8"); SAND = hexc("D9C29A"); RED = hexc("E5322D"); OK = hexc("2FBF71")
engine.CAP_ACCENT = ORANGE2


def finish(a, t, **kw): return _finish(haze(a, t), t, **kw)


meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]
END = 3.0
STARTS.append(_t); DURS.append(END)
TOTAL = _t + END
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix): return sorted(glob.glob(f"media*/{prefix}*"))[0]


class Sat:
    def __init__(self, path):
        self.im = Image.open(path).convert("RGB")

    def view(self, cx, cy, s):
        hw, hh = W / 2 / s, H / 2 / s; box = (cx - hw, cy - hh, cx + hw, cy + hh)
        a = np.asarray(self.im.resize((W, H), Image.BILINEAR, box=box), np.float32)
        return a, (lambda x, y: ((x - cx) * s + W / 2, (y - cy) * s + H / 2))


ISS = Sat(M("nasa_iss008e12570"))          # NASA ISS Expedition 8, PD — Gulf, Iran coast, Musandam peninsula
STRAIT = (1870, 1533)                      # the narrow gap in ISS image px
GEM = Photo(M("nasa_s04-37-716"), maxz=1.3)                 # NASA Gemini 4 (1965) photo of the strait, PD
FJORD = Photo(M("nasa_iss063e002679"), maxz=1.3)            # NASA ISS, Musandam coast, PD
T1 = Photo(M("Oil_Tanker_in_North_Sea"), maxz=1.3)          # ImagePerson, CC BY 4.0
T2 = Photo(M("Solomon_Sea"), maxz=1.3)                      # ITookSomePhotos, CC BY-SA 4.0
T3 = Photo(M("Chemical_Oil"), maxz=1.3)                     # Frans Berkelaar, CC BY 2.0
T4 = Photo(M("Oil_tanker__gas"), maxz=1.3)                  # Jernej Furman, CC BY 2.0
P1 = Particles(80, 5)
_BL = {}


def blurred(key, photo, f=(0.5, 0.5), dim=0.55):
    if key not in _BL: _BL[key] = blur(_finish(photo.kb(0, 1.0, 1.0, f, f), 0), 16, dim)
    return _BL[key]


def bg(c, key, photo, t, f=(0.5, 0.5), dim=0.55):
    to_ctx(c, haze(blurred(key, photo, f, dim), t, amt=30).astype(np.uint8))


def counter(t, v0, v1, dur, fmt="{:,}"):
    return fmt.format(int(round(lerp(v0, v1, eout(t / dur))))) if t > 0 else fmt.format(v0)


def iss(c, t, s, cy=1520, cx=1870):
    a, mp = ISS.view(cx, cy, s); to_ctx(c, finish(a, t, vign=0.3)); return mp


# ---------------- look v6: logistics infographic ----------------
def pill(c, s, x, y, size, t, col=ORANGE2, maxw=940, sub=None):
    if t <= 0: return
    w = text_w(c, s, size)
    if w > maxw - 110: size *= (maxw - 110) / w; w = maxw - 110
    k = eout(t / 0.3); bw, bh = w + 110, size * 1.4
    c.save(); c.translate(x + (1 - k) * W * 0.8, y)
    c.set_source_rgba(0, 0, 0, 0.35); rrect(c, -bw / 2 + 8, -bh / 2 + 12, bw, bh, bh / 2); c.fill()
    c.set_source_rgb(1, 1, 1); rrect(c, -bw / 2, -bh / 2, bw, bh, bh / 2); c.fill()
    c.save(); rrect(c, -bw / 2, -bh / 2, bw, bh, bh / 2); c.clip(); c.set_source_rgb(*col); c.rectangle(-bw / 2, -bh / 2, 40, bh); c.fill(); c.restore()
    text(c, s, 20, size * 0.36, size, col=INK)
    c.restore()
    if sub and t > 0.25:
        a = ease((t - 0.25) / 0.25); sz = 42; sw = text_w(c, sub, sz) + 40
        c.set_source_rgba(*INK, 0.9 * a); rrect(c, x - sw / 2, y + bh / 2 + 12, sw, sz * 1.35, 14); c.fill()
        text(c, sub, x, y + bh / 2 + 12 + sz * 1.0, sz, col=ORANGE2, alpha=a)


def zoomblur(surf, t, dur=0.2):
    if t >= dur: return
    k = 1 - eout(t / dur)
    if k < 0.08: return
    surf.flush()
    a = np.ndarray((H, surf.get_stride() // 4, 4), np.uint8, surf.get_data())[:, :W, :3]
    im = Image.fromarray(a[:, :, ::-1].copy()); acc = np.asarray(im, np.float32)
    for z in (1.03, 1.06, 1.09):
        zz = 1 + (z - 1) * k; cw, ch = W / zz, H / zz
        acc = acc + np.asarray(im.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2)), np.float32)
    a[...] = (acc / 4)[:, :, ::-1].astype(np.uint8); surf.mark_dirty()


def button(c, x, y, s, press=0.0, t=0.0, label="PRESS"):
    """big arcade button on a steel base; press 0..1 pushes the cap down"""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.set_source_rgba(0, 0, 0, 0.4); c.save(); c.scale(1, 0.42); c.arc(10, 330, 300, 0, 2 * math.pi); c.restore(); c.fill()
    g = cairo.LinearGradient(-260, 0, 260, 0); g.add_color_stop_rgb(0, 0.35, 0.38, 0.42); g.add_color_stop_rgb(0.5, 0.82, 0.84, 0.88); g.add_color_stop_rgb(1, 0.3, 0.32, 0.36)
    c.rectangle(-260, 40, 520, 90); c.set_source(g); c.fill()
    c.save(); c.scale(1, 0.38); c.arc(0, 340, 260, 0, 2 * math.pi); c.restore(); c.set_source(g); c.fill()
    c.save(); c.scale(1, 0.38); c.arc(0, 105, 260, 0, 2 * math.pi); c.restore(); c.set_source_rgb(0.9, 0.91, 0.93); c.fill()
    dy = 60 * press
    c.set_source_rgb(0.55, 0.08, 0.06); c.rectangle(-190, -40 + dy, 380, 80 - dy); c.fill()
    c.save(); c.scale(1, 0.38); c.arc(0, 105, 190, 0, math.pi); c.restore(); c.fill()
    g2 = cairo.RadialGradient(-60, -90 + dy, 10, 0, -40 + dy, 200); g2.add_color_stop_rgb(0, 1, 0.55, 0.5); g2.add_color_stop_rgb(1, *RED)
    c.save(); c.scale(1, 0.38); c.arc(0, (-40 + dy) / 0.38, 190, 0, 2 * math.pi); c.restore(); c.set_source(g2); c.fill()
    text(c, label, 0, -30 + dy, 54, col=WHITE, stroke=0)
    if press > 0.6:
        for j in range(8):
            a = j * math.pi / 4 + 0.2; r0, r1 = 240, 240 + 70 * min(1, (press - 0.6) / 0.4)
            c.set_source_rgba(*ORANGE2, 0.9); c.set_line_width(10); c.move_to(math.cos(a) * r0, math.sin(a) * r0 * 0.5 - 40); c.line_to(math.cos(a) * r1, math.sin(a) * r1 * 0.5 - 40); c.stroke()
    c.restore()


def dialog(c, t, x=W / 2, y=760):
    """'ARE YOU SURE?' pop-up gag"""
    if t <= 0: return
    k = back(min(1, t / 0.3)); c.save(); c.translate(x, y); c.scale(k, k)
    c.set_source_rgba(0, 0, 0, 0.4); rrect(c, -330 + 10, -130 + 14, 660, 260, 26); c.fill()
    c.set_source_rgb(1, 1, 1); rrect(c, -330, -130, 660, 260, 26); c.fill()
    c.set_source_rgb(*ORANGE2); rrect(c, -330, -130, 660, 70, 26); c.fill(); c.rectangle(-330, -90, 660, 30); c.fill()
    text(c, "WHAT-IF MODE", 0, -82, 34, col=WHITE)
    text(c, "ARE YOU SURE?", 0, 10, 60, col=INK)
    for j, (lab, col) in enumerate((("YES", OK), ("NO", (0.6, 0.62, 0.66)))):
        bx = -150 + j * 300; c.set_source_rgb(*col); rrect(c, bx - 110, 50, 220, 60, 30); c.fill()
        text(c, lab, bx, 93, 34, col=WHITE)
    c.restore()


def tanker_icon(c, x, y, s, col=(0.85, 0.3, 0.2)):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(-60, -10); c.line_to(50, -10); c.line_to(64, 0); c.line_to(50, 10); c.line_to(-60, 10); c.close_path()
    c.set_source_rgb(*col); c.fill()
    c.set_source_rgb(1, 1, 1); c.rectangle(-58, -7, 16, 14); c.fill()
    c.set_source_rgba(1, 1, 1, 0.6)
    for k in range(4): c.rectangle(-36 + k * 20, -4, 12, 8); c.fill()
    c.restore()


def lanes_map(c, t, k=1.0, flow=True, stop=0.0, queue=0.0):
    """SCHEMATIC strait: north + south coasts pinching in, inbound lane / buffer / outbound lane, tanker icons"""
    g = cairo.LinearGradient(0, 300, 0, H); g.add_color_stop_rgb(0, *hexc("1D5E91")); g.add_color_stop_rgb(1, *hexc("123F66"))
    c.set_source(g); c.paint()
    for j in range(16):                                   # ripples (edge texture)
        y = 330 + j * 100 + 10 * math.sin(t + j); x = (j * 210 + t * 40) % (W + 200) - 100
        c.set_source_rgba(1, 1, 1, 0.12); c.set_line_width(4); c.move_to(x, y); c.curve_to(x + 40, y - 8, x + 80, y + 8, x + 120, y); c.stroke()
    cy = 1000
    def coast(sign):
        c.move_to(-20, cy + sign * 900)
        for x in range(-20, W + 60, 60):
            pinch = 1 - 0.75 * math.exp(-((x - 540) / 260) ** 2)
            c.line_to(x, cy + sign * (230 + 520 * pinch) + 18 * math.sin(x / 37))
        c.line_to(W + 20, cy + sign * 900); c.close_path()
    for sign in (-1, 1):
        coast(sign); c.set_source_rgb(*SAND); c.fill_preserve(); c.set_source_rgba(0.45, 0.35, 0.2, 1); c.set_line_width(4); c.stroke()
    # lanes (inbound top, buffer, outbound bottom)
    a = ease(k)
    for yy, col, lab in ((cy - 120, OK, "IN · 2 MI"), (cy, (1, 1, 1), "BUFFER · 2 MI"), (cy + 120, ORANGE2, "OUT · 2 MI")):
        c.set_source_rgba(*col, 0.25 * a); c.rectangle(-20, yy - 55, W + 40, 110); c.fill()
        c.set_source_rgba(*col, 0.9 * a); c.set_line_width(3); c.set_dash([24, 16]); c.move_to(-20, yy - 55); c.line_to(W + 20, yy - 55); c.stroke(); c.set_dash([])
        text(c, lab, 150, yy + 14, 32, col=WHITE, stroke=6, alpha=a)
    if flow:
        sp = 1 - stop
        for j in range(5):
            ph = ((t * 0.12 * sp + j / 5) % 1.0)
            tanker_icon(c, lerp(-80, W + 80, ph), cy - 120, 1.1, col=OK)
            tanker_icon(c, lerp(W + 80, -80, ph), cy + 120, 1.1, col=ORANGE2)
    if queue > 0:                                        # tankers stacking up outside the strait
        n = int(14 * queue)
        for j in range(n):
            col_ = j % 5; row = j // 5
            tanker_icon(c, 100 + row * 130 + (col_ % 2) * 30, 720 + col_ * 140, 0.9, col=(0.9, 0.55, 0.15))
    text(c, "schematic, not to scale", W / 2, 1650, 28, col=WHITE, stroke=6, alpha=0.85)


def pipes(c, t, k):
    """schematic bypass: two overland pipelines around the strait + capacity bars"""
    lanes_map(c, t, k=0.4, flow=False)
    for j, (pts, lab) in enumerate((([(-20, 200), (300, 330), (540, 560), (780, 330), (W + 20, 200)], "PIPELINE 1"),
                                    ([(-20, 235), (300, 380), (540, 605), (780, 380), (W + 20, 235)], "PIPELINE 2"))):
        kk = ease((k - j * 0.3) / 0.6)
        if kk <= 0: continue
        neon_path(c, pts, kk, col=ORANGE2, width=12, t=t)
        text(c, lab, 540, pts[2][1] - 40 - (1 - j) * 50, 30, col=WHITE, stroke=6, alpha=kk)


def bars(c, t, k, y=760):
    """20 million barrels/day normal flow vs ~2.6 million spare pipeline room (EIA 2024)"""
    rows = (("NORMAL FLOW", 20.0, ORANGE2, "~20M BARRELS/DAY"), ("SPARE PIPELINE ROOM", 2.6, OK, "~2.6M"))
    for j, (lab, v, col, tag) in enumerate(rows):
        a = ease((k - j * 0.2) / 0.3)
        if a <= 0: continue
        yy = y + j * 230; x0, w = 110, 860
        c.set_source_rgba(*INK, 0.88 * a); rrect(c, x0 - 30, yy - 80, w + 60, 200, 24); c.fill()
        text(c, lab, x0, yy - 16, 40, col=WHITE, align="left", alpha=a)
        c.set_source_rgba(1, 1, 1, 0.15 * a); c.rectangle(x0, yy + 14, w, 64); c.fill()
        c.set_source_rgba(*col, a); c.rectangle(x0, yy + 14, max(8, w * v / 20 * eout((k - j * 0.2) / 0.8)), 64); c.fill()
        text(c, tag, x0 + w, yy - 16, 36, col=col, align="right", alpha=a)


def fifth(c, x, y, r, k):
    """pie: one fifth of world oil use"""
    c.set_source_rgba(*INK, 0.85); c.arc(x, y, r + 16, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(1, 1, 1, 0.25); c.arc(x, y, r, 0, 2 * math.pi); c.fill()
    c.move_to(x, y); c.arc(x, y, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * 0.2 * eout(k)); c.close_path(); c.set_source_rgb(*ORANGE2); c.fill()
    text(c, "1/5", x, y + 30, 90, col=WHITE, stroke=10)


def eiffel_vs(c, t, k):
    """tanker silhouette lying next to an Eiffel Tower silhouette of about the same size (Chevron: ~336 m tanker)"""
    a = ease(k); y0 = 1150; L = 760; x0 = 160
    c.set_source_rgba(*INK, 0.75 * a); rrect(c, 80, 560, 920, 720, 30); c.fill()
    # Eiffel tower (height L) drawn lying on its side? keep upright but scaled to L/2 with a scale bar
    tx = 820; th = 560 * a
    c.save(); c.set_source_rgba(1, 1, 1, a); c.set_line_width(6)
    c.move_to(tx - 90, y0); c.line_to(tx - 12, y0 - th); c.line_to(tx + 12, y0 - th); c.line_to(tx + 90, y0); c.stroke()
    c.move_to(tx - 60, y0 - th * 0.3); c.line_to(tx + 60, y0 - th * 0.3); c.move_to(tx - 35, y0 - th * 0.6); c.line_to(tx + 35, y0 - th * 0.6); c.stroke()
    c.arc(tx, y0, 50, math.pi, 2 * math.pi); c.stroke(); c.restore()
    # tanker stood on its end next to it, same height
    c.save(); c.translate(560, y0); c.rotate(-math.pi / 2); c.scale(th / 124 if th > 1 else 0.01, 1.6)
    tanker_icon(c, 2, 0, 1.0, col=ORANGE2); c.restore()
    text(c, "TANKER", 560, y0 + 60, 36, col=ORANGE2, alpha=a); text(c, "EIFFEL TOWER", tx, y0 + 60, 36, col=WHITE, alpha=a)
    text(c, "≈ 330 m", W / 2, 640, 54, col=WHITE, alpha=a)


# ---------------- scenes ----------------
def hook_frame(c, t, z=1.0):
    s = 2.0 * z * (1 + 0.04 * min(1, t / 5))
    mp = iss(c, t, s)
    x, y = mp(*STRAIT)
    ring_marker(c, x, y, t + 0.5, col=ORANGE2, r=24)
    k = ease((t - 0.3) / 0.6)
    if k > 0:   # gap ruler between the two coasts
        x0, y0 = mp(1855, 1600); x1, y1 = mp(1885, 1470)
        c.set_source_rgba(1, 1, 1, k); c.set_line_width(6); c.move_to(x0, y0); c.line_to(lerp(x0, x1, k), lerp(y0, y1, k)); c.stroke()
    pill(c, "OIL'S BUSIEST DOORWAY", W / 2, 360, 76, t + 1)
    pill(c, "21 MILES WIDE", W / 2, 500, 96, t + 1, col=RED)


def s0(c, t, d):  # M hook
    hook_frame(c, t, z=1 + 0.05 * (1 - eout((t - 1.2) / 0.35)) if t > 1.2 else 1.0)
    source_tag(c, "Image: NASA ISS (PD) · Source: US EIA", t - 0.3, y=1290)


def s1(c, t, d):  # F "21 miles? That's a commute, not an ocean."
    a = GEM.kb(t / d, 1.1, 1.2, (0.55, 0.55), (0.55, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
    pill(c, "21 MILES?", W / 2, 400, 110, t - 0.05, col=RED)
    if t > 0.9: pill(c, "= A COMMUTE", W / 2, 560, 80, t - 0.9)
    source_tag(c, "Photo: NASA Gemini 4, 1965 (PD)", t - 0.2)


def s2(c, t, d):  # M lanes: two in, two out, two-mile gap
    lanes_map(c, t, k=(t - 1.3) / 0.8)
    pill(c, "EVEN TIGHTER LANES", W / 2, 400, 84, t - 0.1)
    source_tag(c, "Source: US EIA (2-mile lanes, 2-mile buffer)", t - 1.0, y=1290)


def s3(c, t, d):  # F "For ships that big?"
    a = T1.kb(t / d, 1.1, 1.2, (0.5, 0.5), (0.52, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
    pill(c, "SHIPS THAT BIG?", W / 2, 400, 100, t - 0.05, col=RED)
    source_tag(c, "Photo: ImagePerson / CC BY 4.0", t - 0.1)


def s4(c, t, d):  # M tankers ~ Eiffel Tower
    if t < 1.2:
        a = T2.kb(t / 1.2, 1.0, 1.1, (0.5, 0.5), (0.55, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
        pill(c, "THE BIGGEST TANKERS", W / 2, 400, 84, t - 0.05)
        source_tag(c, "Photo: ITookSomePhotos / CC BY-SA 4.0", t - 0.1)
    else:
        tt = t - 1.2; bg(c, "t2", T2, tt); eiffel_vs(c, tt, tt / 0.8)
        pill(c, "≈ EIFFEL TOWER", W / 2, 400, 96, tt - 0.9, col=RED)
        source_tag(c, "Sources: Britannica (~330 m), Chevron", tt - 0.4, y=1350)


def s5(c, t, d):  # F "So what does this big red button do?"
    bg(c, "gem", GEM, t, (0.55, 0.55)); P1.dust(c, t, alpha=0.2)
    button(c, W / 2, 1000, 1.0, t=t)
    pill(c, "THE BIG RED BUTTON", W / 2, 400, 90, t - 0.6, col=RED)


def s6(c, t, d):  # M "It's a what-if. Press it, and for one day, no ship gets through."
    bg(c, "gem", GEM, t + 3, (0.55, 0.55))
    button(c, W / 2, 1050, 0.85, t=t)
    dialog(c, t - 0.3, y=700)
    if t > 2.0: pill(c, "1 DAY · NO SHIPS", W / 2, 400, 96, t - 2.0, col=RED)
    else: pill(c, "WHAT-IF", W / 2, 400, 110, t - 0.05)


def s7(c, t, d):  # F "Pressing it."
    bg(c, "gem", GEM, t + 6, (0.55, 0.55))
    sh = 10 * math.sin(t * 70) * (1 if 0.2 < t < 0.5 else 0)
    c.save(); c.translate(sh, 0); button(c, W / 2, 1050, 0.85, press=ease(t / 0.25), t=t); c.restore()
    pill(c, "PRESSED", W / 2, 400, 120, t - 0.05, col=RED)


def s8(c, t, d):  # M "Normally, about 20 million barrels of oil pass through here every day."
    lanes_map(c, t + 8, k=1.0, stop=ease(t / 1.0))
    pill(c, counter(t - 0.5, 0, 20, 1.4) + " MILLION", W / 2, 400, 110, t - 0.05, sub="BARRELS A DAY, NORMALLY")
    source_tag(c, "Source: US EIA (2024 average)", t - 0.6, y=1290)


def s9(c, t, d):  # F "Every single day?"
    lanes_map(c, t + 12, k=1.0, stop=1.0)
    pill(c, "EVERY DAY?!", W / 2, 400, 120, t - 0.05, col=RED)


def s10(c, t, d):  # M "Around a fifth of all the oil the world uses. And there's no other sea road out of the Gulf."
    if t < 3.0:
        bg(c, "gem", GEM, t, (0.55, 0.55))
        fifth(c, 540, 900, 210, (t - 0.4) / 1.0)
        pill(c, "≈ 1/5 OF WORLD OIL USE", W / 2, 400, 80, t - 0.3)
        source_tag(c, "Source: US EIA (2024)", t - 0.3, y=1290)
    else:
        tt = t - 3.0; lanes_map(c, tt + 20, k=0.0, flow=False)
        neon_path(c, [(40, 1000), (540, 1000), (W - 40, 1000)], ease(tt / 1.0), col=ORANGE2, width=16, t=tt)
        text(c, "THE GULF", 170, 900, 44, col=INK, alpha=ease(tt / 0.4)); text(c, "OPEN OCEAN", 900, 900, 40, col=INK, alpha=ease((tt - 0.6) / 0.4))
        pill(c, "THE ONLY SEA EXIT", W / 2, 400, 90, tt - 0.05, col=RED)


def s11(c, t, d):  # F "So just build a pipe around it?"
    pipes(c, t, 0.0)
    pill(c, "A PIPE AROUND IT?", W / 2, 1250, 96, t - 0.05)


def s12(c, t, d):  # M pipelines exist, spare room ~2.5 million barrels a day
    if t < 2.6:
        pipes(c, t + 2, ease(t / 1.6) * 1.3)
        pill(c, "2 PIPELINES", W / 2, 1250, 110, t - 0.05)
    else:
        tt = t - 2.6; bg(c, "t4", T4, tt); bars(c, tt, tt / 1.0)
        pill(c, "ROOM FOR ~2.6M", W / 2, 400, 100, tt - 0.05, col=RED)
        source_tag(c, "Source: US EIA (Saudi + UAE pipelines, 2024 estimate)", tt - 0.4, y=1290, size=22)


def s13(c, t, d):  # F "Out of twenty? So the rest just waits?"
    bg(c, "t4", T4, t + 4); bars(c, t + 4, 2.0)
    pill(c, "THE REST WAITS?", W / 2, 400, 100, t - 1.0, col=RED) if t > 1.0 else pill(c, "OUT OF 20?", W / 2, 400, 110, t, col=RED)


def s14(c, t, d):  # M "It lines up. Tankers stack up outside, like the world's slowest drive-through."
    lanes_map(c, t + 15, k=1.0, flow=False, queue=ease(t / 3.0))
    pill(c, "IT LINES UP", W / 2, 400, 110, t - 0.05)
    if t > 3.0:   # drive-through sign gag
        a = back(min(1, (t - 3.0) / 0.3)); c.save(); c.translate(780, 1230); c.scale(a, a)
        c.set_source_rgb(*RED); rrect(c, -200, -70, 400, 140, 20); c.fill()
        text(c, "DRIVE-THROUGH", 0, -5, 44, col=WHITE); text(c, "WAIT: ALL DAY", 0, 45, 32, col=hexc("FFD9A0")); c.restore()


def s15(c, t, d):  # F "Unpressing the button. So a 21-mile gap keeps a fifth of the world's oil moving."
    if t < 1.4:
        bg(c, "gem", GEM, t + 8, (0.55, 0.55))
        button(c, W / 2, 1050, 0.85, press=1 - ease(t / 0.4), t=t, label="UNDO")
        pill(c, "UNPRESSED", W / 2, 400, 110, t - 0.05, col=OK)
    else:   # loop back to the hook
        hook_frame(c, 0.5 + (t - 1.4) * 0.3, z=lerp(1.06, 1.0, eout((t - 1.4) / 0.6)))


def s_end(c, t, d):
    a = T4.kb(min(1, t / 3), 1.0, 1.06, (0.5, 0.5), (0.52, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
    end_card_logo(c, t, W / 2, 760, 270, LOGO)
    pill(c, "FOLLOW", W / 2, 1180, 110, t - 0.6)
    if t > 1.0: text(c, "how the world really works", W / 2, 1330, 48, col=WHITE, stroke=8, alpha=ease((t - 1.0) / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s_end]
assert len(SCENES) == len(STARTS)
NO_ZB = (7, 9, 13)


def frame(c, gt, surf):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    SCENES[i](c, t, d)
    badge(c, gt)
    if i < len(meta):
        captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))
    if i > 0 and i not in NO_ZB: zoomblur(surf, t)


def events():
    s = STARTS
    ev = [("boom", 0.0), ("pop", 0.3), ("tick", 0.5), ("pop", 1.2)]
    ev += [("whoosh", x - 0.05) for x in s[1:] if x not in [s[i] for i in NO_ZB]]
    ev += [("pop", s[1]), ("pop", s[1] + 0.9), ("pop", s[2] + 0.1), ("thunk", s[2] + 1.6), ("thunk", s[2] + 3.1), ("thunk", s[2] + 4.6)]
    ev += [("pop", s[3]), ("pop", s[4]), ("boom", s[4] + 2.1), ("pop", s[5] + 0.6), ("pop", s[6] + 0.3), ("ding", s[6] + 0.5), ("pop", s[6] + 2.0)]
    ev += [("thunk", s[7] + 0.1), ("boom", s[7] + 0.2), ("clank", s[7] + 0.2)]
    ev += [("pop", s[8])] + [("tick", s[8] + 0.5 + k * 0.12) for k in range(12)] + [("pop", s[9])]
    ev += [("pop", s[10] + 0.3), ("ding", s[10] + 1.4), ("pop", s[10] + 3.0), ("thunk", s[11]), ("pop", s[12]), ("pop", s[12] + 2.6), ("thunk", s[12] + 3.6)]
    ev += [("pop", s[13]), ("pop", s[13] + 1.0)] + [("tick", s[14] + 0.3 + k * 0.2) for k in range(14)] + [("boom", s[14] + 3.0), ("pop", s[14] + 3.0)]
    ev += [("clank", s[15] + 0.1), ("pop", s[15] + 0.1), ("boom", s[15] + 1.4), ("pop", s[16] + 0.6)]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]:
            frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events(), "music_style": "arabic"}, open("events.json", "w"))
        a, b = (int(v) for v in sys.argv[2:4]) if len(sys.argv) > 3 else (0, int(math.ceil(TOTAL * FPS)))
        out = sys.argv[4] if len(sys.argv) > 4 else "video.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a, b):
            frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", a, b, "total", TOTAL)
