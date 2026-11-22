"""Video 004 — Statue of Liberty: a skin as thin as two pennies + Gustave Eiffel's hidden iron skeleton (mega-build,
format "engineer's take"). Woman (Jessica) opens and explains today, man (Bidhan's voice) asks/reacts.
Real media: Daniel Schwen frontal photo (PD), AskALotl front view (CC0), Burkouri boat video (CC0), NPS boat video (PD),
1880s Paris workshop + assembly + head photos (PD), HAER interior armature photo (Jet Lowe, PD), Carol M. Highsmith
aerial (PD), NASA globe. Drawn explainers: magnifier cross-section of the skin vs two pennies, iron bars + copper
saddles sliding, copper vs iron expansion and tearing, sway in the wind, the inner Eiffel pylon.
usage (work dir with meta.json from tts_el.py, media/, clipA..C):
  python render_004.py stills <prefix> t1 t2 ...   |   python render_004.py full"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish


def finish(a, t, **kw):  # every photo/clip frame gets edge haze (edge-band check)
    return _finish(haze(a, t), t, **kw)
from clips import Clip
import globe as GL

meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]; DURS[-1] += 0.4
TOTAL = STARTS[-1] + DURS[-1]
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix): return sorted(glob.glob(f"media/{prefix}*"))[0]


FRONT = Photo(M("Statue_of_Liberty_frontal_2_crop"), maxz=1.3)       # Daniel Schwen, PD
FV = Photo(M("Front_view_of_Statue"), maxz=1.3)                      # AskALotl, CC0
SHOP = Photo(M("Construction-of-Statue-of-Liberty-04"), archival=True, maxz=1.3)   # 1880s Paris workshop, PD

HEAD = Photo(M("Head_of_the_Statue"), archival=True, maxz=1.3)                     # head on display in Paris 1878, PD
ARM = Photo(M("ARMATURE_AND_FRAMEWORK"), maxz=1.3)                   # HAER, Jet Lowe, PD
AER = Photo(M("Aerial_view_of_the_Statue"), maxz=1.3)                # Carol M. Highsmith, PD
CA, CB, CC = Clip("clipA"), Clip("clipB"), Clip("clipC")
GLOBE = GL.Globe()
NYC, PARIS = (40.69, -74.04), (48.86, 2.35)
P1, P2, P3 = Particles(110, 1), Particles(70, 2), Particles(90, 3)
RED = (0.92, 0.2, 0.22)
COPPER = (0.80, 0.47, 0.25); PATINA = (0.42, 0.75, 0.64); IRON = (0.42, 0.44, 0.48)
_BL = {}


def blurred(key, photo, f=(0.5, 0.5), dim=0.62):
    if key not in _BL: _BL[key] = blur(_finish(photo.kb(0, 1.0, 1.0, f, f), 0), 14, dim)
    return _BL[key]


def bg(c, key, photo, t, f=(0.5, 0.5), dim=0.62):
    to_ctx(c, haze(blurred(key, photo, f, dim), t, amt=30).astype(np.uint8))


def cam(c, z, cx=W / 2, cy=H / 2):
    c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)


def punch(t, at=0.0, amt=0.07):
    return 1 + amt * (1 - eout((t - at) / 0.35)) if t >= at else 1.0


def project(lat, lon, lat0, lon0, R, cy=H * 0.47):
    p, l, p0, l0 = map(math.radians, (lat, lon, lat0, lon0))
    x = R * math.cos(p) * math.sin(l - l0)
    y = R * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0))
    return W / 2 + x, cy - y


def pin(c, x, y, t, col=RED):
    if t <= 0: return
    k = back(t / 0.35); c.save(); c.translate(x, y); c.scale(k, k)
    c.set_source_rgba(1, 0.8, 0.3, 0.25 * (0.5 + 0.5 * math.sin(t * 6))); c.arc(0, 0, 50, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(*col, 1); c.arc(0, -46, 26, 0, 2 * math.pi); c.fill()
    c.move_to(-22, -34); c.line_to(0, 0); c.line_to(22, -34); c.fill()
    c.set_source_rgba(1, 1, 1, 1); c.arc(0, -46, 10, 0, 2 * math.pi); c.fill(); c.restore()


def wind(c, t, alpha=0.5, n=26, speed=900, y0=300, y1=1300):
    """curved white wind streaks sweeping left -> right"""
    for a, b, s, ph in P2.p[:n]:
        life = (t * (0.6 + 0.5 * s) + ph) % 1.0
        x = lerp(-300, W + 300, life); y = lerp(y0, y1, b) + 30 * math.sin(life * 6 + ph * 9)
        ln = 140 + 220 * s
        c.move_to(x - ln, y + 10); c.curve_to(x - ln * 0.6, y - 8, x - ln * 0.3, y + 6, x, y)
        c.set_source_rgba(1, 1, 1, alpha * math.sin(math.pi * life)); c.set_line_width(3 + 4 * s)
        c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()


# ---------------- drawn explainers ----------------
def penny(c, x, y, w, h):
    """a coin seen edge-on: copper-coloured rim with ridges"""
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, 0.95, 0.62, 0.38); g.add_color_stop_rgb(0.5, 0.75, 0.42, 0.22); g.add_color_stop_rgb(1, 0.55, 0.28, 0.14)
    rrect(c, x, y, w, h, h / 2.5); c.set_source(g); c.fill()
    c.set_source_rgba(0.35, 0.16, 0.06, 0.6); c.set_line_width(2)
    for k in range(int(w / 14)):
        c.move_to(x + 8 + k * 14, y + 3); c.line_to(x + 8 + k * 14, y + h - 3); c.stroke()


def magnifier(c, t, cx, cy, r, tx, ty, k=1.0):
    """zoom bubble pointing at (tx, ty): cross-section of the copper skin next to two stacked pennies"""
    if k <= 0: return
    c.save()
    c.set_source_rgba(*GOLD, 0.9 * k); c.set_line_width(5); c.move_to(tx, ty); c.line_to(cx - r * 0.6, cy + r * 0.75); c.stroke()
    c.set_source_rgba(*GOLD, k); c.arc(tx, ty, 14, 0, 2 * math.pi); c.fill()
    c.translate(cx, cy); s = back(k) if k < 1 else 1.0; c.scale(s, s)
    c.set_source_rgba(0, 0, 0, 0.4); c.arc(8, 12, r, 0, 2 * math.pi); c.fill()
    c.arc(0, 0, r, 0, 2 * math.pi); c.save(); c.clip()
    bg = cairo.LinearGradient(0, -r, 0, r); bg.add_color_stop_rgb(0, 0.10, 0.16, 0.32); bg.add_color_stop_rgb(1, 0.05, 0.08, 0.18)
    c.set_source(bg); c.paint()
    # the skin in cross-section: a horizontal band (outer patina on top, copper below), two pennies beside it
    th = 64; py = -th / 2 - 10; sx0, sx1 = -r, -r * 0.08
    c.rectangle(sx0, py, sx1 - sx0, th * 0.3); c.set_source_rgb(*PATINA); c.fill()
    c.rectangle(sx0, py + th * 0.3, sx1 - sx0, th * 0.7); c.set_source_rgb(*COPPER); c.fill()
    for xx in range(int(sx0), int(sx1), 18):  # hammer dimples
        c.set_source_rgba(1, 0.85, 0.6, 0.25); c.arc(xx + 9, py + th * 0.65, 5, 0, 2 * math.pi); c.fill()
    text(c, "OUTSIDE", (sx0 + sx1) / 2 + 30, py - 22, 28, col=WHITE, alpha=0.9)
    text(c, "INSIDE", (sx0 + sx1) / 2 + 30, py + th + 44, 28, col=WHITE, alpha=0.9)
    text(c, "SKIN", (sx0 + sx1) / 2 + 30, py - 70, 38, col=GOLD, stroke=6)
    px = r * 0.02
    for j in range(2):  # visible on frame 1 (thumbnail); small settle bounce
        b_ = 8 * math.sin(t * 5 + j * 2) * (1 - ease(t / 2.0)) if t < 2.0 else 0
        penny(c, px, py + j * (th / 2) + b_, 190, th / 2 - 2)
    text(c, "2 PENNIES", px + 95, py - 22, 32, col=WHITE, stroke=6)
    c.set_source_rgba(*GOLD, 1); c.set_line_width(4); c.set_dash([8, 6])
    c.move_to(sx0, py); c.line_to(px + 200, py); c.move_to(sx0, py + th); c.line_to(px + 200, py + th); c.stroke(); c.set_dash([])
    c.restore()
    c.arc(0, 0, r, 0, 2 * math.pi); c.set_source_rgba(1, 1, 1, 1); c.set_line_width(8); c.stroke()
    c.arc(0, 0, r + 6, 0, 2 * math.pi); c.set_source_rgba(*GOLD, 1); c.set_line_width(4); c.stroke()
    text(c, "≈ 2.4 MM", 0, r * 0.78, 40, col=GOLD, stroke=8)
    c.restore()


def hook_frame(c, t, z=1.0):
    a = FRONT.kb(t / 5.0, 1.0, 1.1, (0.45, 0.5), (0.42, 0.52))
    c.save(); cam(c, z, W / 2, 1000); to_ctx(c, finish(a, t, vign=0.45))
    P1.dust(c, t, col=(0.85, 0.95, 1), alpha=0.25, speed=18, size=3)   # sky specks: no flat edge bands
    c.restore()
    magnifier(c, t, 700, 960, 250, 400, 1180, k=1.0)
    s_ = 1 + 0.02 * math.sin(t * 5)
    c.save(); c.translate(W / 2, 400); c.scale(s_, s_)
    text(c, "SKIN THIS THIN?!", 0, 0, 104, col=GOLD, stroke=18)
    text(c, "= 2 PENNIES", 0, 96, 76, col=WHITE, stroke=14)
    c.restore()


def bars_diagram(c, t, slide=0.0, alpha=1.0):
    """iron bar from the inner pylon, ending in a copper 'saddle' clip riveted to the skin; skin slides by `slide` px"""
    c.save()
    sx = 760  # skin line x
    for j, y in enumerate((760, 1100)):
        # iron bar (fixed)
        g = cairo.LinearGradient(0, y - 16, 0, y + 16); g.add_color_stop_rgb(0, 0.6, 0.62, 0.66); g.add_color_stop_rgb(1, 0.28, 0.3, 0.34)
        c.rectangle(-20, y - 16, sx - 50, 32); c.set_source(g); c.fill()
        c.set_source_rgba(0, 0, 0, 0.5); c.set_line_width(2); c.rectangle(-20, y - 16, sx - 50, 32); c.stroke()
        for k in range(5):  # rivets on the bar
            c.set_source_rgb(0.75, 0.77, 0.8); c.arc(60 + k * 120, y, 6, 0, 2 * math.pi); c.fill()
    # copper skin (moves) — textured wavy band
    c.save(); c.translate(0, slide)
    c.move_to(sx, -200)
    for y in range(-200, H + 220, 40): c.line_to(sx + 22 * math.sin(y / 170), y)
    c.line_to(W + 50, H + 220); c.line_to(W + 50, -200); c.close_path()
    g = cairo.LinearGradient(sx, 0, W, 0); g.add_color_stop_rgb(0, *COPPER); g.add_color_stop_rgb(0.15, 0.62, 0.36, 0.2); g.add_color_stop_rgb(0.2, *PATINA); g.add_color_stop_rgb(1, 0.3, 0.6, 0.52)
    c.set_source(g); c.fill_preserve(); c.save(); c.clip()
    for yy in range(-200, H + 220, 150):  # riveted sheet seams + hammered dimples on the skin (texture to the edge)
        c.set_source_rgba(0.15, 0.35, 0.3, 0.6); c.set_line_width(5); c.move_to(sx - 40, yy + 30 * math.sin(yy)); c.line_to(W + 60, yy + 60); c.stroke()
        for k in range(9):
            c.set_source_rgba(0.85, 1, 0.92, 0.5); c.arc(sx + 60 + k * 32, yy + 12 + k * 3.3, 5, 0, 2 * math.pi); c.fill()
        for k in range(14):
            r_ = 10 + (k * 37 % 23); c.set_source_rgba(0, 0.1, 0.08, 0.18); c.arc(sx + 50 + (k * 71 % 300), yy + 40 + (k * 53 % 100), r_, 0, 2 * math.pi); c.fill()
    c.restore()
    for y in (760, 1100):  # U-shaped saddles riveted to the skin, open towards the bar
        yy = y - slide
        c.set_source_rgb(0.86, 0.52, 0.28); c.set_line_width(14); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(sx - 70, yy - 40 + 0); c.line_to(sx + 4, yy - 40); c.line_to(sx + 4, yy + 40); c.line_to(sx - 70, yy + 40); c.stroke()
        for dy_ in (-40, 40):
            c.set_source_rgb(0.98, 0.75, 0.45); c.arc(sx + 10, yy + dy_, 8, 0, 2 * math.pi); c.fill()
    c.restore()
    c.restore()


def strips(c, t, h_c, h_i, locked=0.0, tear=0.0):
    """copper vs iron strips anchored at the left; lengths grow by h (exaggerated)"""
    x0, L0 = 120, 560
    for y, col, h, name in ((760, COPPER, h_c, "COPPER"), (930, IRON, h_i, "IRON")):
        L = L0 * (1 + h)
        bow = 60 * tear if name == "COPPER" else 0
        c.save()
        c.move_to(x0, y - 34); c.curve_to(x0 + L * 0.33, y - 34 - bow, x0 + L * 0.66, y - 34 - bow, x0 + L, y - 34)
        c.line_to(x0 + L, y + 34); c.curve_to(x0 + L * 0.66, y + 34 - bow, x0 + L * 0.33, y + 34 - bow, x0, y + 34); c.close_path()
        g = cairo.LinearGradient(0, y - 34, 0, y + 34)
        g.add_color_stop_rgb(0, *[min(1, v * 1.25) for v in col]); g.add_color_stop_rgb(1, *[v * 0.7 for v in col])
        c.set_source(g); c.fill_preserve(); c.set_source_rgba(0, 0, 0, 0.5); c.set_line_width(3); c.stroke()
        text(c, name, x0 + 75, y + 14, 40, col=WHITE, align="left", stroke=6)
        c.restore()
    # wall anchor
    c.rectangle(60, 680, 60, 340); c.set_source_rgb(0.18, 0.2, 0.3); c.fill()
    if locked > 0:
        for y in (760, 930):
            for x in (x0 + 40, x0 + L0 - 30):
                c.set_source_rgba(*GOLD, locked); c.arc(x, y - (0 if y == 930 else 60 * tear * (0.2 if x < 300 else 0.0)), 14, 0, 2 * math.pi); c.fill()
        c.set_source_rgba(*GOLD, locked); c.set_line_width(10)
        c.move_to(x0 + 40, 760); c.line_to(x0 + 40, 930); c.move_to(x0 + L0 - 30, 760); c.line_to(x0 + L0 - 30, 930); c.stroke()
    if tear > 0.3:  # zig-zag rip in the copper
        k = min(1, (tear - 0.3) / 0.4); cx = x0 + L0 * 0.5
        c.move_to(cx, 760 - 34 - 45 * tear)
        for j in range(6): c.line_to(cx + (14 if j % 2 else -14), 760 - 34 - 45 * tear + (j + 1) * 12 * k)
        c.set_source_rgb(*RED); c.set_line_width(8); c.stroke()


def sun(c, x, y, r, t, a=1.0):
    c.save(); c.translate(x, y); c.rotate(t * 0.8)
    for k in range(12):
        c.rotate(math.pi / 6); c.move_to(r * 1.2, 0); c.line_to(r * 1.6, 0)
        c.set_source_rgba(1, 0.75, 0.2, a); c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.arc(0, 0, r, 0, 2 * math.pi); c.set_source_rgba(1, 0.82, 0.3, a); c.fill(); c.restore()


def snow(c, x, y, r, t, a=1.0):
    c.save(); c.translate(x, y); c.rotate(-t * 0.4); c.set_source_rgba(0.8, 0.93, 1, a); c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(6):
        c.rotate(math.pi / 3); c.move_to(0, 0); c.line_to(r, 0)
        c.move_to(r * 0.6, 0); c.line_to(r * 0.85, r * 0.22); c.move_to(r * 0.6, 0); c.line_to(r * 0.85, -r * 0.22)
    c.stroke(); c.restore()


def lattice(c, cx, ytop, ybot, wtop, wbot, t, k=1.0, col=GOLD, lw=6):
    """Eiffel-style lattice pylon drawn up to fraction k of its height (builds upward)"""
    if k <= 0: return
    n = 12; yk = lerp(ybot, ytop, k)
    def xs(y):
        u = (ybot - y) / (ybot - ytop); w = lerp(wbot, wtop, u ** 0.7); return cx - w / 2, cx + w / 2
    c.save(); c.set_line_cap(cairo.LINE_CAP_ROUND)
    pts = []
    for j in range(n + 1):
        y = lerp(ybot, ytop, j / n)
        if y < yk - 1: break
        pts.append((y, *xs(y)))
    def path():
        for i, (y, l, r) in enumerate(pts):
            c.move_to(l, y); c.line_to(r, y)
            if i:
                py, pl, pr = pts[i - 1]; c.move_to(pl, py); c.line_to(l, y); c.move_to(pr, py); c.line_to(r, y)
                c.move_to(pl, py); c.line_to(r, y); c.move_to(pr, py); c.line_to(l, y)
    glow_stroke(c, path, col, lw, alpha=1.0, layers=3)
    c.restore()


def eiffel_icon(c, x, y, h, k=1.0, col=GOLD):
    """simple Eiffel Tower silhouette (public-domain structure, our own drawing)"""
    if k <= 0: return
    c.save(); c.translate(x, y); s = back(k) if k < 1 else 1; c.scale(s, s)
    w = h * 0.42
    c.move_to(-w / 2, 0); c.curve_to(-w * 0.25, -h * 0.25, -w * 0.08, -h * 0.6, -w * 0.03, -h * 0.92); c.line_to(0, -h)
    c.line_to(w * 0.03, -h * 0.92); c.curve_to(w * 0.08, -h * 0.6, w * 0.25, -h * 0.25, w / 2, 0)
    c.line_to(w * 0.3, 0); c.curve_to(w * 0.2, -h * 0.12, -w * 0.2, -h * 0.12, -w * 0.3, 0); c.close_path()
    c.set_source_rgba(0, 0, 0, 0.5); c.set_line_width(10); c.stroke_preserve(); c.set_source_rgb(*col); c.fill()
    for f in (0.28, 0.58):
        ww = w * (0.36 if f < 0.5 else 0.16); c.rectangle(-ww, -h * f, 2 * ww, h * 0.035); c.set_source_rgb(*col); c.fill()
    c.restore()


def counter(t, v0, v1, dur, fmt="{:,}"):
    return fmt.format(int(round(lerp(v0, v1, eout(t / dur))))) if t > 0 else fmt.format(v0)


# ---------------- scenes (one per line) ----------------
def s0(c, t, d):  # F hook: "copper skin only as thick as two pennies" — photo + magnifier on frame 1, punch at 1.2 s
    hook_frame(c, t, z=punch(t, 1.2, 0.08) * lerp(1.0, 1.05, ease((t - 1.2) / (d - 1.2))))
    source_tag(c, "Source: NPS Statue Statistics", t - 2.0, y=1290)


def s1(c, t, d):  # M "Two pennies? On something that big?" — real boat footage + height ruler
    to_ctx(c, finish(CA.at(t).astype(np.float32), t, vign=0.3))
    pop_text(c, "THAT BIG?!", W / 2, 420, 160, t - 0.9, col=GOLD, stroke=18)
    u = ease((t - 0.3) / 1.6); x = 860; yb, yt = 1120, 600
    if u > 0:
        c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(6); c.move_to(x, yb); c.line_to(x, lerp(yb, yt, u)); c.stroke()
        for k in range(0, int(16 * u) + 1):
            y = lerp(yb, yt, k / 16); c.move_to(x - 16, y); c.line_to(x, y); c.stroke()
        pop_text(c, counter(t - 0.3, 0, 151, 1.6, "{} FT"), x - 110, lerp(yb, yt, u) + 20, 64, t - 0.3, col=GOLD, stroke=12, maxw=240)
    source_tag(c, "Video: Burkouri / CC0", t - 0.2)


def s2(c, t, d):  # F "how does she survive the wind? the secret's hidden inside, a famous name"
    xr = 0.85 * ease((t - 2.6) / 0.6)
    to_ctx(c, finish(CB.at(t).astype(np.float32) * 1.06, t, vign=0.3, xray=xr))
    wind(c, t, alpha=0.55 * (1 - 0.6 * xr), y0=250, y1=1250)
    if t < 2.6: pop_text(c, "THE WIND?", W / 2, 420, 140, t - 0.4, col=GOLD, stroke=16)
    else:
        for j in range(22):
            y = (j * 90 + t * 400) % (H + 100) - 50; c.move_to(-20, y); c.line_to(W + 20, y)
        c.set_source_rgba(0.6, 0.85, 1, 0.10 * xr); c.set_line_width(3); c.stroke()
        pop_text(c, "HIDDEN INSIDE", W / 2, 420, 120, t - 2.6, col=GOLD, stroke=16)
        if t > 4.0: label(c, "BUILT BY A FAMOUS NAME…", 540, t - 4.0, size=44, bg=WHITE)
    source_tag(c, "Video: U.S. National Park Service", t - 0.2)


def s3(c, t, d):  # M "Okay, tell me."
    a = FV.kb(t / d, 1.12, 1.22, (0.5, 0.3), (0.5, 0.25)); to_ctx(c, finish(a, t, vign=0.4))
    pop_text(c, "WHO?!", W / 2, 440, 190, t - 0.05, col=GOLD, stroke=20)


def s4(c, t, d):  # F Paris workshop, 300 sheets hammered by hand
    if t < 2.9:
        a = SHOP.kb(t / 2.9, 1.0, 1.12, (0.42, 0.3), (0.35, 0.28)); to_ctx(c, finish(a, t, archival=True, vign=0.45))
        label(c, "PARIS, 1880s", 520, t - 0.3, size=48, bg=WHITE)
    else:
        tt = t - 2.9
        a = HEAD.kb(tt / 3.0, 1.05, 1.18, (0.5, 0.3), (0.5, 0.25)); to_ctx(c, finish(a, tt, archival=True, vign=0.45))
    pop_text(c, counter(t - 1.2, 0, 300, 1.4), W / 2, 420, 170, t - 1.2, col=GOLD, stroke=18)
    if t > 1.4: text(c, "COPPER SHEETS", W / 2, 500, 64, col=WHITE, stroke=12, alpha=ease((t - 1.4) / 0.3))
    if t > 3.6: label(c, "SHAPED BY HAND", 1060, t - 3.6, size=48)
    source_tag(c, "Photos: 1880s, public domain · Source: Copper Development Assoc.", t - 0.5, size=22)


def hammer(c, x, y, ang, s=1.0):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.set_source_rgb(0.55, 0.36, 0.2); rrect(c, -10, -10, 20, 200, 8); c.fill()
    g = cairo.LinearGradient(0, -40, 0, 30); g.add_color_stop_rgb(0, 0.85, 0.87, 0.9); g.add_color_stop_rgb(1, 0.4, 0.42, 0.46)
    rrect(c, -70, -45, 140, 60, 12); c.set_source(g); c.fill(); c.restore()


def s5(c, t, d):  # M "With actual hammers?"
    a = HEAD.kb(t / d, 1.2, 1.3, (0.5, 0.25), (0.5, 0.22)); to_ctx(c, finish(a, t, archival=True, vign=0.45))
    ph = (t * 3.2) % 1.0; ang = -0.9 + 0.9 * (ph * 2 if ph < 0.5 else 2 - ph * 2)
    hammer(c, 760, 900, ang, 1.4)
    if ph > 0.45 and ph < 0.7: P3.sparks(c, ph, 640, 960, alpha=0.9)
    pop_text(c, "HAMMERS?!", W / 2, 440, 160, t - 0.05, col=GOLD, stroke=18)


def soda_can(c, x, y, t, crush):
    """drawn soda can (no brand) that crumples as crush goes 0 -> 1"""
    c.save(); c.translate(x, y); c.scale(1, 1 - 0.45 * crush)
    w, h = 220, 400
    c.move_to(-w / 2, -h / 2)
    for j in range(9):
        yy = -h / 2 + (j + 1) * h / 9; c.line_to(-w / 2 + (24 * crush if j % 2 else -10 * crush), yy)
    for j in range(9, -1, -1):
        yy = -h / 2 + j * h / 9; c.line_to(w / 2 - (24 * crush if j % 2 else -10 * crush), yy)
    c.close_path()
    g = cairo.LinearGradient(-w / 2, 0, w / 2, 0)
    g.add_color_stop_rgb(0, 0.55, 0.6, 0.68); g.add_color_stop_rgb(0.35, 0.95, 0.96, 1); g.add_color_stop_rgb(1, 0.45, 0.5, 0.58)
    c.set_source(g); c.fill_preserve(); c.set_source_rgba(0, 0, 0, 0.5); c.set_line_width(4); c.stroke()
    c.rectangle(-w / 2 + 6, -40, w - 12, 80); c.set_source_rgba(*ORANGE, 0.9); c.fill()
    c.restore()


def statue_skeleton(c, t, k=1.0, bars=1.0):
    """drawn inner frame over the frontal photo: central lattice pylon + iron bars fanning out to the skin"""
    lattice(c, 470, 640, 1900, 70, 220, t, k=k, col=GOLD, lw=5)
    if bars > 0:
        c.save(); c.set_line_cap(cairo.LINE_CAP_ROUND)
        for j in range(26):
            y = lerp(700, 1820, j / 25); side = -1 if j % 2 else 1
            reach = (170 + 90 * math.sin(j * 1.7)) * min(1, max(0, bars * 26 - j) )
            if reach <= 0: continue
            x0 = 470 + side * lerp(35, 110, j / 25)
            c.move_to(x0, y); c.line_to(x0 + side * reach, y - 40 * side * 0.3)
            c.set_source_rgba(0.85, 0.9, 1, 0.85); c.set_line_width(5); c.stroke()
            c.set_source_rgba(*COPPER, 0.95); c.arc(x0 + side * reach, y - 40 * side * 0.3, 8, 0, 2 * math.pi); c.fill()
        c.restore()


def s6(c, t, d):  # F "a shell that thin would fold like a soda can. So inside, there's an iron skeleton."
    if t < 2.7:
        bg(c, "front", FRONT, t); P1.dust(c, t, alpha=0.25)
        soda_can(c, W / 2, 880, t, ease((t - 0.9) / 0.6))
        pop_text(c, "SODA CAN", W / 2, 420, 150, t - 0.6, col=GOLD, stroke=18)
        if t > 1.5: label(c, "THIN SHELL = FOLDS", 1160, t - 1.5, size=46, bg=RED, fg=WHITE)
    else:
        tt = t - 2.7; xr = 0.9 * ease(tt / 0.5)
        a = FRONT.kb(0.2, 1.0, 1.0, (0.45, 0.5), (0.45, 0.5)); to_ctx(c, finish(a, tt, vign=0.45, xray=xr))
        for j in range(22):
            y = (j * 90 + tt * 400) % (H + 100) - 50; c.move_to(-20, y); c.line_to(W + 20, y)
        c.set_source_rgba(0.6, 0.85, 1, 0.12 * xr); c.set_line_width(3); c.stroke()
        statue_skeleton(c, tt, k=ease((tt - 0.3) / 1.6), bars=0.0)
        pop_text(c, "IRON SKELETON", W / 2, 420, 120, tt - 0.2, col=GOLD, stroke=16)


def s7(c, t, d):  # F "a tower in the middle, over 1,300 iron bars reaching out to the skin"
    if t < 2.2:
        a = FRONT.kb(0.2, 1.0, 1.0, (0.45, 0.5), (0.45, 0.5)); to_ctx(c, finish(a, t, vign=0.45, xray=0.9))
        statue_skeleton(c, t, k=1.0, bars=ease(t / 1.8))
        pop_text(c, "A TOWER INSIDE", W / 2, 420, 120, t - 0.05, col=GOLD, stroke=16)
    else:
        tt = t - 2.2
        a = ARM.kb(tt / 3.0, 1.12, 1.3, (0.45, 0.6), (0.4, 0.55)); to_ctx(c, finish(a, tt, vign=0.45))
        pop_text(c, counter(tt - 0.1, 0, 1300, 1.3) + "+", W / 2, 430, 170, tt - 0.1, col=GOLD, stroke=18)
        text(c, "IRON BARS", W / 2, 520, 70, col=WHITE, stroke=12, alpha=ease((tt - 0.3) / 0.3))
        source_tag(c, "Photo: Jet Lowe, HAER / Library of Congress (PD)", tt - 0.3)


def s8(c, t, d):  # M "So the skin's bolted onto the bars?"
    a = ARM.kb(t / d, 1.3, 1.45, (0.4, 0.55), (0.42, 0.6)); to_ctx(c, finish(a, t, vign=0.45))
    pop_text(c, "BOLTED ON?", W / 2, 440, 150, t - 0.05, col=GOLD, stroke=18)
    k = back((t - 0.6) / 0.35)
    if k > 0:  # bolt icon
        c.save(); c.translate(W / 2, 880); c.scale(k, k)
        c.set_source_rgb(0.8, 0.82, 0.86)
        for i in range(6):
            a_ = i * math.pi / 3; c.line_to(70 * math.cos(a_), 70 * math.sin(a_))
        c.close_path(); c.fill_preserve(); c.set_source_rgba(0, 0, 0, 0.6); c.set_line_width(5); c.stroke()
        c.arc(0, 0, 28, 0, 2 * math.pi); c.set_source_rgb(0.5, 0.52, 0.56); c.fill(); c.restore()


def diagram_bg(c, t):
    bg(c, "front_d", FRONT, t, (0.5, 0.6), dim=0.55)
    P1.dust(c, t, col=(0.8, 0.9, 1), alpha=0.18, speed=12)


def s9(c, t, d):  # F "Nope — genius part. The bars sit in copper clips, so the skin can slide."
    diagram_bg(c, t)
    slide = 36 * math.sin(max(0, t - 2.6) * 3.2) * ease((t - 2.6) / 0.4)
    bars_diagram(c, t, slide)
    pop_text(c, "NOPE!", W / 2, 420, 170, t - 0.05, col=GOLD, stroke=18) if t < 1.6 else pop_text(c, "COPPER CLIPS", W / 2, 420, 130, t - 1.6, col=GOLD, stroke=16)
    if t > 0.6: label(c, "IRON BAR", 640, t - 0.6, x=300, size=40, bg=WHITE)
    if t > 1.8: label(c, "COPPER CLIP", 850, t - 1.8, x=560, size=40)
    if t > 0.9: label(c, "COPPER SKIN", 560, t - 0.9, x=880, size=36, bg=PATINA, fg=NAVY)
    if t > 2.8:  # up/down arrows on the skin
        c.save(); c.set_source_rgb(*GOLD); x = 930; yc = 930 + slide * 0.5
        for sg in (-1, 1):
            c.move_to(x - 30, yc + sg * 70); c.line_to(x, yc + sg * 120); c.line_to(x + 30, yc + sg * 70); c.close_path(); c.fill()
        c.rectangle(x - 9, yc - 75, 18, 150); c.fill(); c.restore()
        label(c, "IT SLIDES", 1100, t - 2.8, x=880, size=40, bg=GOLD)
    source_tag(c, "Source: Copper Development Assoc. (1,500 copper saddles)", t - 1.0, size=22)


def s10(c, t, d):  # M "Why would you want it loose?"
    diagram_bg(c, t)
    c.save(); cam(c, lerp(1.25, 1.35, t / d), 760, 900); bars_diagram(c, t, 30 * math.sin(t * 3.2)); c.restore()
    pop_text(c, "LOOSE?!", W / 2, 430, 180, t - 0.05, col=GOLD, stroke=20)


def s11(c, t, d):  # F "Heat and cold. Copper and iron grow by different amounts. Lock them together, and the skin tears."
    diagram_bg(c, t)
    if t < 1.4:  hc, hi = 0.14 * ease(t / 0.8), 0.08 * ease(t / 0.8); sun(c, 880, 560, 60, t, a=min(1, t / 0.2)); head = "HEAT"
    elif t < 2.9: u = ease((t - 1.4) / 0.7); hc, hi = lerp(0.14, -0.12, u), lerp(0.08, -0.07, u); snow(c, 880, 560, 70, t); head = "COLD"
    elif t < 4.0: u = ease((t - 2.9) / 0.4); hc, hi = lerp(-0.12, 0, u), lerp(-0.07, 0, u); head = "DIFFERENT AMOUNTS"
    else: hc, hi = 0.0, 0.0; head = "LOCKED = TEARS"
    lock = ease((t - 4.0) / 0.4); tear = ease((t - 4.9) / 0.8)
    sh = 7 * math.sin(t * 55) * tear * (1 - ease((t - 5.9) / 0.4))
    c.save(); c.translate(sh, 0)
    if t > 4.6: sun(c, 880, 560, 60, t, a=ease((t - 4.6) / 0.3))
    strips(c, t, hc if t < 4.0 else 0.06 * tear, hi if t < 4.0 else 0.0, locked=lock, tear=tear)
    c.restore()
    pop_text(c, head, W / 2, 420, 130 if len(head) < 10 else 100, t - (0 if t < 1.4 else 1.4 if t < 2.9 else 2.9 if t < 4.0 else 4.0),
             col=RED if t >= 4.0 else GOLD, stroke=16)
    text(c, "(movement exaggerated)", W / 2, 1110, 30, col=WHITE, stroke=6, alpha=0.8)


def s12(c, t, d):  # F "in strong wind she sways about 3 inches. She bends so she doesn't break."
    ang = 0.022 * math.sin(t * 2.4) * ease(t / 0.6)
    a = finish(FRONT.kb(0.3, 1.08, 1.08, (0.45, 0.5), (0.45, 0.5)), t, vign=0.45)
    s = to_surface(a.astype(np.float32) / 255)
    c.save(); c.translate(W / 2, H + 300); c.rotate(ang); c.translate(-W / 2, -(H + 300))
    c.set_source_surface(s, 0, 0); c.paint(); c.restore()
    wind(c, t, alpha=0.6, y0=300, y1=1250)
    # torch arc ruler
    tx = W / 2 + (270 - W / 2) * math.cos(ang) - (160 - H - 300) * math.sin(ang); ty = 220
    c.save(); c.set_source_rgba(*GOLD, 0.95); c.set_line_width(6)
    c.arc(W / 2, H + 300, H + 300 - 200, -math.pi / 2 - 0.30, -math.pi / 2 - 0.22); c.stroke(); c.restore()
    if t > 0.5: label(c, "STRONG WIND", 560, t - 0.5, size=46, bg=WHITE)
    pop_text(c, "SWAYS 3 IN", W / 2, 430, 140, t - 1.2, col=GOLD, stroke=18) if t < 3.4 else pop_text(c, "BENDS, NOT BREAKS", W / 2, 430, 100, t - 3.4, col=GOLD, stroke=16)
    text(c, "(sway exaggerated)", W / 2, 1180, 30, col=WHITE, stroke=6, alpha=0.8)
    source_tag(c, "Source: NPS (50 mph wind: 3 in sway)", t - 0.8)


def s13(c, t, d):  # M "That's brilliant. So who designed it?"
    a = AER.kb(t / d, 1.0, 1.12, (0.5, 0.55), (0.5, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
    pop_text(c, "BRILLIANT", W / 2, 420, 150, t - 0.05, col=GOLD, stroke=18) if t < 1.2 else pop_text(c, "WHO DESIGNED IT?", W / 2, 420, 110, t - 1.2, col=GOLD, stroke=16)
    source_tag(c, "Photo: Carol M. Highsmith / Library of Congress (PD)", t - 0.3)


def s14(c, t, d):  # F "Gustave Eiffel. A few years later, he built the Eiffel Tower." — globe New York -> Paris
    k = ease(t / (d * 0.8)); lat0 = lerp(46, 50, k); lon0 = lerp(-60, -10, k); R = 900 * (1 + 0.5 * ease((t - 1.5) / 2))
    to_ctx(c, finish(GLOBE.render(lat0, lon0, R).astype(np.float32), t, vign=0.3))
    x1, y1 = project(*NYC, lat0, lon0, R); x2, y2 = project(*PARIS, lat0, lon0, R)
    u = ease((t - 0.3) / 1.4)
    if u > 0:  # great-circle-ish arc
        mx, my = (x1 + x2) / 2, min(y1, y2) - 260
        c.move_to(x1, y1); n = 30
        for j in range(1, int(n * u) + 1):
            s_ = j / n; x = (1 - s_) ** 2 * x1 + 2 * (1 - s_) * s_ * mx + s_ * s_ * x2; y = (1 - s_) ** 2 * y1 + 2 * (1 - s_) * s_ * my + s_ * s_ * y2
            c.line_to(x, y)
        c.set_source_rgba(*GOLD, 1); c.set_line_width(7); c.set_dash([18, 12]); c.stroke(); c.set_dash([])
    pin(c, x1, y1, t - 0.1, col=(0.3, 0.75, 0.6)); pin(c, x2, y2, t - 1.5)
    eiffel_icon(c, x2, y2 - 90, 330, k=ease((t - 1.9) / 0.4))
    pop_text(c, "GUSTAVE EIFFEL", W / 2, 420, 120, t - 0.05, col=GOLD, stroke=16)
    if t > 2.0: label(c, "THEN: THE EIFFEL TOWER", 520, t - 2.0, size=44, bg=WHITE)


def s15(c, t, d):  # M "No way! A little Eiffel Tower inside Lady Liberty?"
    a = FRONT.kb(0.2, 1.0, 1.0, (0.45, 0.5), (0.45, 0.5)); to_ctx(c, finish(a, t, vign=0.45, xray=0.85 * ease(t / 0.4)))
    statue_skeleton(c, t, k=ease(t / 0.9), bars=ease((t - 0.6) / 1.2))
    eiffel_icon(c, 860, 1180, 300, k=ease((t - 1.6) / 0.4))
    if t > 1.6: text(c, "=", 700, 1060, 120, col=WHITE, stroke=10, alpha=ease((t - 1.6) / 0.3))
    pop_text(c, "NO WAY!", W / 2, 420, 170, t - 0.05, col=GOLD, stroke=18) if t < 1.3 else pop_text(c, "A MINI EIFFEL INSIDE", W / 2, 420, 96, t - 1.3, col=GOLD, stroke=16)


def s16(c, t, d):  # F loop: "Holding up a skin as thin as two pennies." -> back to the hook frame
    hook_frame(c, t + 1.0, z=lerp(1.08, 1.0, eout(t / 0.6)))


def s17(c, t, d):
    bg(c, "front", FRONT, t)
    end_card_logo(c, t, W / 2, 680, 290, LOGO)
    pop_text(c, "FOLLOW", W / 2, 1150, 130, t, col=GOLD, stroke=14)
    text(c, "a new wonder every day", W / 2, 1240, 54, col=WHITE, stroke=8, alpha=ease(t / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17]
assert len(SCENES) == len(meta)


def frame(c, gt):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    c.save()
    if i > 0 and t < 0.3:
        z = 1 + 0.08 * (1 - eout(t / 0.3)); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[i](c, t, d)
    c.restore()
    if i < len(SCENES) - 1:
        badge(c, gt); captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))
    if i > 0 and i not in (10, 16): wipe(c, t, col=GOLD if i % 2 else ORANGE)


def events():
    s = STARTS
    ev = [("boom", 0.0), ("pop", 0.3), ("pop", 0.55), ("pop", 1.2)] + [("whoosh", x - 0.05) for x in s[1:] if x not in (s[10], s[16])]
    ev += [("tick", s[1] + 0.3 + k * 0.1) for k in range(16)] + [("pop", s[1] + 0.9)]
    ev += [("hiss", s[2] + 0.2), ("boom", s[2] + 2.6), ("pop", s[2] + 4.0), ("pop", s[3])]
    ev += [("pop", s[4] + 0.3), ("tick", s[4] + 1.2)] + [("tick", s[4] + 1.2 + k * 0.12) for k in range(1, 11)] + [("pop", s[4] + 3.6)]
    ev += [("thunk", s[5] + k / 3.2 + 0.15) for k in range(5)]
    ev += [("crack", s[6] + 0.9), ("pop", s[6] + 1.5), ("boom", s[6] + 2.7)]
    ev += [("tick", s[7] + 0.05 + k * 0.07) for k in range(20)] + [("pop", s[7] + 2.3)] + [("tick", s[7] + 2.3 + k * 0.1) for k in range(12)]
    ev += [("thunk", s[8] + 0.6), ("pop", s[9]), ("pop", s[9] + 0.6), ("pop", s[9] + 0.9), ("pop", s[9] + 1.8), ("pop", s[9] + 2.8)]
    ev += [("pop", s[10]), ("pop", s[11]), ("pop", s[11] + 1.4), ("pop", s[11] + 2.9), ("thunk", s[11] + 4.0), ("crack", s[11] + 5.1)]
    ev += [("pop", s[12] + 0.5), ("pop", s[12] + 1.2), ("pop", s[12] + 3.4), ("pop", s[13]), ("pop", s[13] + 1.2)]
    ev += [("pop", s[14]), ("pop", s[14] + 1.5), ("boom", s[14] + 1.9), ("pop", s[14] + 2.0)]
    ev += [("pop", s[15]), ("pop", s[15] + 1.3), ("boom", s[15] + 1.6), ("whoosh", s[16] - 0.05), ("pop", s[17])]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]:
            frame(c, float(x)); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events()}, open("events.json", "w"))
        n = int(math.ceil(TOTAL * FPS))
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
        for f in range(n):
            frame(c, f / FPS); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", n, "total", TOTAL)
