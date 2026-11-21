"""Video 003b — Old Faithful remake (Bidhan 2026-11-21): emotional two-host delivery, "hidden cave" shock hook with an x-ray cut-away on frame 1, soft sound design.
Based on video 003 — Old Faithful: "never on the hour" (myth vs fact + engineer's take), two hosts (M explains, F asks).
Real NPS photos (public domain) + real eruption footage (Steven Pavlov, CC BY-SA 4.0) + globe zoom + animated
cross-section of the geyser's plumbing (camera survey, constriction, car-sized cavern, pressure-cooker physics).
usage (in work dir with meta.json from tts2.py, media/, clipA..D from clips.extract):
  python render_003.py still <t> <out.png>   |   python render_003.py full"""
import cairo, json, math, os, sys, glob, subprocess, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from photo import Photo, finish, to_ctx, blur
from clips import Clip
import globe as GL

meta = json.load(open("meta.json"))
PAD = 0.14
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"] + PAD
DURS = [m["dur"] + PAD for m in meta]; DURS[-1] += 0.4
TOTAL = STARTS[-1] + DURS[-1]
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix): return sorted(glob.glob(f"media/{prefix}*"))[0]


BLUE = Photo(M("Old_Faithful_eruption_on_a_bluebird"), maxz=1.3)   # NPS, PD
OBS = Photo(M("Old_Faithful_eruption_from_Observation"), maxz=1.3)  # NPS, PD (portrait)
SUN = Photo(M("Sunset_eruption"), maxz=1.3)                         # NPS, PD
AER = Photo(M("Aerial_view_of_Upper_Geyser_Basin__13931213269"), maxz=1.3)  # NPS, PD
CA, CB, CC, CD = Clip("clipA"), Clip("clipB"), Clip("clipC"), Clip("clipD")  # Steven Pavlov, CC BY-SA 4.0
GLOBE = GL.Globe()
LOC = (44.4605, -110.8281)
T = make_textures(5)
P1, P2, P3 = Particles(120, 1), Particles(70, 2), Particles(90, 3)
RED = (0.92, 0.2, 0.22)
_BL = {}


def blurred(key, photo, f=(0.5, 0.5)):
    if key not in _BL: _BL[key] = blur(finish(photo.kb(0, 1.0, 1.0, f, f), 0), 14, 0.62)
    return _BL[key]


def cam(c, z, cx=W / 2, cy=H / 2):
    c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)


def punch(t, at=0.0, amt=0.07):  # quick zoom punch after a beat
    return 1 + amt * (1 - eout((t - at) / 0.35)) if t >= at else 1.0


def project(lat, lon, lat0, lon0, R, cy=H * 0.47):
    p, l, p0, l0 = map(math.radians, (lat, lon, lat0, lon0))
    x = R * math.cos(p) * math.sin(l - l0)
    y = R * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0))
    return W / 2 + x, cy - y


def pin(c, x, y, t, col=RED):
    if t <= 0: return
    k = back(t / 0.35); c.save(); c.translate(x, y); c.scale(k, k)
    for r in (70, 50):
        c.set_source_rgba(1, 0.8, 0.3, 0.25 * (0.5 + 0.5 * math.sin(t * 6))); c.arc(0, 0, r * (1 + 0.15 * math.sin(t * 6)), 0, 2 * math.pi); c.fill()
    c.set_source_rgba(*col, 1); c.arc(0, -46, 26, 0, 2 * math.pi); c.fill()
    c.move_to(-22, -34); c.line_to(0, 0); c.line_to(22, -34); c.fill()
    c.set_source_rgba(1, 1, 1, 1); c.arc(0, -46, 10, 0, 2 * math.pi); c.fill(); c.restore()


def hook_text(c, t, appear=True):
    """frame-1 hook: visible at t=0 (no pop from zero), slight pulse"""
    s = 1 + 0.02 * math.sin(t * 5)
    c.save(); c.translate(W / 2, 430); c.scale(s, s)
    text(c, "NEVER", 0, 0, 190, col=GOLD, stroke=20)
    text(c, "ON THE HOUR?!", 0, 120, 104, col=WHITE, stroke=16)
    c.restore()


# ---------------- cross-section of the geyser plumbing ----------------
VY = 600            # ground surface / vent
PXFT = 15.5         # px per foot of depth
def dy(ft): return VY + ft * PXFT
CAV0, CAV1 = dy(35), dy(45)


def half_w(y):
    """half-width of the conduit at screen y (exaggerated for readability)"""
    n = 3 * math.sin(y / 23.0) + 2 * math.sin(y / 9.0)
    if y < dy(22):
        k = (y - VY) / (dy(22) - VY); return 7 + 30 * (1 - k) ** 1.6 + n * (1 - k)
    if y < CAV0 - 10:
        k = (y - dy(22)) / (CAV0 - 10 - dy(22)); return 7 + 22 * k ** 1.5 + n * 0.6 * k
    if y < CAV1 + 10:
        k = (y - (CAV0 - 10)) / (CAV1 + 20 - CAV0); return 30 + 105 * math.sin(math.pi * k) ** 0.8 + n
    k = min(1, (y - CAV1 - 10) / 300); return 30 - 16 * k + n


def conduit(c, y1=1750):
    ys = list(np.arange(VY - 4, y1, 6))
    c.move_to(W / 2 - half_w(ys[0]), ys[0])
    for y in ys: c.line_to(W / 2 - half_w(y) + 10 * math.sin(y / 130), y)
    for y in reversed(ys): c.line_to(W / 2 + half_w(y) + 10 * math.sin(y / 130), y)
    c.close_path()


def section(c, t, water=0.0, heat=0.0, glow=0.0, steam=0.0, cav=1.0, rain=0.0):
    """full-frame cross-section: sky + tree line + sinter mound above, layered rock below, the conduit cut open"""
    paint_tex(c, T["sky"], dx=t * 8)
    # distant forest band
    c.move_to(-50, VY - 130)
    for x in range(-50, W + 60, 30): c.line_to(x, VY - 150 - 30 * abs(math.sin(x * 0.07)) - 18 * math.sin(x * 0.31))
    c.line_to(W + 60, VY + 10); c.line_to(-50, VY + 10); c.close_path(); c.set_source_rgb(0.12, 0.26, 0.18); c.fill()
    # rock below ground with depth darkening + strata
    c.rectangle(-50, VY, W + 100, H); fill_tex(c, T["rock"], dy=-VY)
    g = cairo.LinearGradient(0, VY, 0, H); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.05, 0.02, 0.06, 0.55)
    c.rectangle(-50, VY, W + 100, H); c.set_source(g); c.fill()
    for j in range(9):
        y = VY + 60 + j * 140
        c.move_to(-50, y)
        for x in range(-50, W + 60, 40): c.line_to(x, y + 14 * math.sin(x / 120 + j))
        c.set_source_rgba(0.1, 0.05, 0.03, 0.35); c.set_line_width(5); c.stroke()
    # magma glow at the bottom
    if glow > 0:
        rg = cairo.RadialGradient(W / 2, H + 260, 50, W / 2, H + 260, 900)
        rg.add_color_stop_rgba(0, 1, 0.75, 0.2, 0.95 * glow); rg.add_color_stop_rgba(0.45, 0.95, 0.3, 0.05, 0.6 * glow); rg.add_color_stop_rgba(1, 0.6, 0.05, 0.0, 0)
        c.set_source(rg); c.paint()
    # sinter mound at the vent
    c.move_to(-50, VY + 10)
    c.curve_to(250, VY + 5, 380, VY - 40, W / 2 - 40, VY - 52); c.line_to(W / 2 + 40, VY - 52)
    c.curve_to(700, VY - 40, 830, VY + 5, W + 50, VY + 10); c.line_to(W + 50, VY + 40); c.line_to(-50, VY + 40); c.close_path()
    fill_tex(c, T["concrete"], dy=40)
    # conduit: dark void, then water fill
    conduit(c); c.set_source_rgb(0.07, 0.06, 0.08); c.fill()
    if cav < 1:  # cavern still unexplored: rock covers it
        c.save(); c.rectangle(0, CAV0 - 40, W, H); c.clip(); conduit(c); fill_tex(c, T["rock"], dy=-VY, alpha=1 - cav); c.restore()
    if water > 0:
        c.save(); conduit(c); c.clip()
        top = lerp(H, VY - 50, ease(water))
        c.rectangle(0, top, W, H); fill_tex(c, T["water"], dy=-t * 60)
        if heat > 0:
            hg = cairo.LinearGradient(0, VY, 0, 1750)
            hg.add_color_stop_rgba(0, *thermal_rgb(0.55 * heat), 0.75 * heat); hg.add_color_stop_rgba(1, *thermal_rgb(min(1, 1.1 * heat)), 0.85 * heat)
            c.rectangle(0, top, W, H); c.set_source(hg); c.fill()
        if steam > 0:  # flash to steam: bubbles race upward
            for a, b, s, ph in P3.p:
                life = (t * (1.5 + s) + ph) % 1.0
                y = lerp(1700, VY - 40, life); x = W / 2 + 10 * math.sin(y / 130) + (a - 0.5) * 2 * half_w(y) * 0.8
                c.set_source_rgba(1, 1, 1, 0.85 * steam); c.arc(x, y, 3 + 9 * s * steam, 0, 2 * math.pi); c.fill()
        c.restore()
    c.save()
    if cav < 1: c.rectangle(0, 0, W, CAV0 - 40); c.clip()
    conduit(c); c.set_source_rgba(0.95, 0.92, 0.85, 0.9); c.set_line_width(4); c.stroke()  # silica lining
    c.restore()
    if rain > 0:  # rain + snowmelt seeping down through cracks
        for a, b, s, ph in P1.p[:80]:
            life = (t * (0.35 + 0.2 * s) + ph) % 1.0
            x = a * W; y = lerp(-20, 1650, life)
            if abs(x - W / 2) < 60: continue
            col = (0.55, 0.85, 1.0) if y > VY else (0.85, 0.95, 1.0)
            c.set_source_rgba(*col, 0.9 * rain * min(1, (1 - life) * 4))
            if y < VY: c.move_to(x, y); c.line_to(x - 4, y + 26); c.set_line_width(4); c.stroke()
            else: c.arc(x + 12 * math.sin(y / 60 + ph * 5), y, 6, 0, 2 * math.pi); c.fill()


def depth_ruler(c, t, upto_ft, x=150):
    a = min(1, t / 0.3)
    c.set_source_rgba(1, 1, 1, 0.9 * a); c.set_line_width(4); c.move_to(x, VY); c.line_to(x, dy(48)); c.stroke()
    for ft in range(0, 50, 5):
        y = dy(ft); c.move_to(x - (18 if ft % 10 == 0 else 10), y); c.line_to(x, y); c.stroke()
        if ft % 10 == 0: text(c, f"{ft}", x - 30, y + 10, 28, col=WHITE, align="right", alpha=a, stroke=6)
    text(c, "FEET", x, VY - 20, 26, col=GOLD, alpha=a, stroke=6)
    y = dy(upto_ft); c.set_source_rgba(*GOLD, a); c.move_to(x + 4, y); c.line_to(x + 30, y - 14); c.line_to(x + 30, y + 14); c.close_path(); c.fill()


def camera_probe(c, y, t, light=1.0):
    x = W / 2 + 10 * math.sin(y / 130)
    c.set_source_rgba(0.9, 0.9, 0.9, 0.9); c.set_line_width(3); c.move_to(W / 2, VY - 300); c.line_to(x, y - 30); c.stroke()
    if light > 0:  # light cone
        lg = cairo.LinearGradient(0, y, 0, y + 220); lg.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.65 * light); lg.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
        c.move_to(x - 10, y + 10); c.line_to(x - 70, y + 220); c.line_to(x + 70, y + 220); c.line_to(x + 10, y + 10); c.close_path(); c.set_source(lg); c.fill()
    c.set_source_rgb(*GOLD); rrect(c, x - 11, y - 34, 22, 44, 6); c.fill()
    c.set_source_rgb(1, 1, 0.85); c.arc(x, y + 8, 6, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(1, 0.3, 0.3, 0.5 + 0.5 * math.sin(t * 10)); c.arc(x, y - 24, 4, 0, 2 * math.pi); c.fill()


def squeeze_arrows(c, y, t, gap=None):
    gap = gap or half_w(y) + 22; k = 8 * math.sin(t * 8)
    for sgn in (-1, 1):
        x = W / 2 + 10 * math.sin(y / 130) + sgn * (gap + 40 + k)
        c.move_to(x + sgn * 70, y); c.line_to(x, y); c.set_source_rgb(*GOLD); c.set_line_width(10); c.stroke()
        c.move_to(x, y); c.line_to(x + sgn * 28, y - 22); c.line_to(x + sgn * 28, y + 22); c.close_path(); c.fill()


def car(c, cx, cy, w, a):
    """dashed outline of a small car, to show the cavern scale"""
    h = w * 0.36; c.save(); c.translate(cx - w / 2, cy - h / 2)
    c.move_to(0, h * 0.75); c.line_to(0, h * 0.45); c.line_to(w * 0.18, h * 0.38); c.line_to(w * 0.32, 0); c.line_to(w * 0.7, 0)
    c.line_to(w * 0.84, h * 0.38); c.line_to(w, h * 0.48); c.line_to(w, h * 0.75); c.close_path()
    c.set_dash([14, 9], 0); c.set_source_rgba(*GOLD, a); c.set_line_width(6); c.stroke(); c.set_dash([])
    for wx in (0.2, 0.8):
        c.arc(w * wx, h * 0.78, h * 0.2, 0, 2 * math.pi); c.set_source_rgba(*GOLD, a); c.set_line_width(6); c.stroke()
    c.restore()


def thermo(c, t, level, x=120, y0=1180, y1=760):
    c.save()
    c.set_source_rgba(0, 0, 0, 0.5); rrect(c, x - 34, y1 - 40, 68, y0 - y1 + 120, 34); c.fill()
    c.set_source_rgb(1, 1, 1); rrect(c, x - 18, y1 - 24, 36, y0 - y1 + 40, 18); c.fill()
    col = thermal_rgb(min(1, level))
    c.set_source_rgb(*col); c.arc(x, y0 + 30, 34, 0, 2 * math.pi); c.fill()
    top = lerp(y0, y1, level); c.rectangle(x - 10, top, 20, y0 - top + 20); c.fill()
    bp = lerp(y0, y1, 0.62)  # surface boiling-point mark
    c.set_source_rgb(*GOLD); c.set_line_width(4); c.move_to(x + 22, bp); c.line_to(x + 60, bp); c.stroke()
    text(c, "BOILING", x + 64, bp + 9, 26, col=GOLD, align="left", stroke=6)
    c.restore()


def gauge(c, cx, cy, r, val, t):
    c.save()
    c.set_source_rgba(0, 0, 0, 0.45); c.arc(cx + 5, cy + 8, r, 0, 2 * math.pi); c.fill()
    c.set_source_rgb(0.95, 0.95, 0.97); c.arc(cx, cy, r, 0, 2 * math.pi); c.fill()
    c.set_source_rgb(*NAVY); c.set_line_width(8); c.arc(cx, cy, r, 0, 2 * math.pi); c.stroke()
    c.set_line_width(14); c.set_source_rgb(0.3, 0.75, 0.4); c.arc(cx, cy, r * 0.75, math.pi * 0.8, math.pi * 1.4); c.stroke()
    c.set_source_rgb(*RED); c.arc(cx, cy, r * 0.75, math.pi * 1.8, math.pi * 2.2); c.stroke()
    a = math.pi * (0.8 + 1.4 * val) + 0.03 * math.sin(t * 30)
    c.set_source_rgb(*NAVY); c.set_line_width(7); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(cx, cy); c.line_to(cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82); c.stroke()
    c.arc(cx, cy, 10, 0, 2 * math.pi); c.fill()
    text(c, "PRESSURE", cx, cy + r + 44, 30, col=WHITE, stroke=6); c.restore()


def plume(c, x, base, h, t, a=1.0):
    """little geyser icon: white column + puffs"""
    for j in range(7):
        k = j / 6; y = base - h * k; r = 14 + 26 * k + 4 * math.sin(t * 6 + j)
        c.set_source_rgba(1, 1, 1, a * (0.95 - 0.35 * k)); c.arc(x + 6 * math.sin(t * 3 + j), y, r, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(0.85, 0.85, 0.8, a); c.save(); c.translate(x, base + 8); c.scale(80, 16); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); c.fill()


def counter(c, t, v0, v1, dur, fmt="{:,}"):
    return fmt.format(int(round(lerp(v0, v1, eout(t / dur))))) if t > 0 else fmt.format(v0)


# ---------------- scenes ----------------
SHIFT = 470          # photo moved up so the geyser base sits on the cut-away ground line
GROUND = 950
CAVE_Y = 1190


def cutaway(c, t, glow=1.0):
    """frame-1 x-ray cut-away under the real photo: torn ground edge, conduit, glowing car-sized cave"""
    c.save()
    c.move_to(-20, GROUND)
    for x in range(-20, W + 40, 36): c.line_to(x, GROUND + 14 * math.sin(x * 0.11) + 8 * math.sin(x * 0.37))
    c.line_to(W + 40, H + 20); c.line_to(-20, H + 20); c.close_path()
    c.save(); c.clip_preserve(); fill_tex(c, T["xray"]); c.restore()
    c.set_source_rgba(*GOLD, 0.9); c.set_line_width(6); c.stroke()
    for j in range(16):  # scan lines
        y = (GROUND + j * 70 + t * 160) % (H - GROUND) + GROUND
        c.move_to(0, y); c.line_to(W, y)
    c.set_source_rgba(0.7, 0.9, 1, 0.10); c.set_line_width(3); c.stroke()
    cx = W / 2
    # conduit from the vent down to the cave, narrowing then opening
    def pipe():
        c.move_to(cx - 30, GROUND - 4); c.curve_to(cx - 8, GROUND + 90, cx - 6, CAVE_Y - 120, cx - 10, CAVE_Y - 75)
        c.line_to(cx + 10, CAVE_Y - 75); c.curve_to(cx + 6, CAVE_Y - 120, cx + 8, GROUND + 90, cx + 30, GROUND - 4); c.close_path()
    pipe(); c.set_source_rgba(0.75, 0.93, 1, 0.95); c.fill()
    # cave
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    for r in (4, 3, 2, 1):
        c.save(); c.translate(cx, CAVE_Y); c.scale(330 + r * 26, 125 + r * 18); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.set_source_rgba(1, 0.75, 0.3, 0.07 * glow * (1 + pulse)); c.fill()
    c.save(); c.translate(cx, CAVE_Y); c.scale(330, 125); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
    g = cairo.RadialGradient(cx, CAVE_Y, 10, cx, CAVE_Y, 330)
    g.add_color_stop_rgb(0, 0.65, 0.92, 1); g.add_color_stop_rgb(1, 0.12, 0.45, 0.75)
    c.set_source(g); c.fill_preserve(); c.set_source_rgba(1, 1, 1, 0.95); c.set_line_width(5); c.stroke()
    car(c, cx, CAVE_Y + 10, 400, 1.0)
    text(c, "35–45 FT DOWN", cx, CAVE_Y - 140, 40, col=GOLD, stroke=10)
    for a_, b_, s_, ph in P3.p[:30]:  # boiling bubbles in the cave
        life = (t * (0.8 + s_) + ph) % 1.0
        x = cx + (a_ - 0.5) * 520; y = CAVE_Y + 80 - life * 170
        c.set_source_rgba(1, 1, 1, 0.7 * (1 - life)); c.arc(x, y, 4 + 6 * s_, 0, 2 * math.pi); c.fill()
    c.restore()


def hook_frame(c, t, z=1.0):
    a = BLUE.kb(t / 4.0, 1.0, 1.08, (0.43, 0.42), (0.43, 0.4))
    c.save(); cam(c, z, W / 2, CAVE_Y); c.save(); c.translate(0, -SHIFT); to_ctx(c, finish(a, t)); c.restore()
    cutaway(c, t); c.restore()
    s_ = 1 + 0.02 * math.sin(t * 5)
    c.save(); c.translate(W / 2, 400); c.scale(s_, s_)
    text(c, "A HIDDEN CAVE", 0, 0, 112, col=GOLD, stroke=18)
    text(c, "UNDER OLD FAITHFUL?!", 0, 92, 70, col=WHITE, stroke=14)
    c.restore()


def s0(c, t, d):  # HOOK: real photo + x-ray cut-away showing the cave on frame 1; punch-in at 1.2 s
    hook_frame(c, t, z=punch(t, 1.2, 0.08) * lerp(1.0, 1.06, ease((t - 1.2) / (d - 1.2))))


def s1(c, t, d):  # F: "Wait, never?" real footage
    to_ctx(c, finish(CA.at(t).astype(np.float32), t, vign=0.25))
    pop_text(c, "NEVER?!", W / 2, 470, 170, t - 0.05, col=GOLD, stroke=18)
    source_tag(c, "Video: Steven Pavlov / CC BY-SA 4.0", t)


def s2(c, t, d):  # M: "it's why rangers can predict every eruption... the trick is genius"
    a = OBS.kb(t / d, 1.05, 1.2, (0.5, 0.35), (0.5, 0.3))
    to_ctx(c, finish(a, t))
    pop_text(c, "PREDICTED", W / 2, 400, 140, t - 0.4, col=GOLD, stroke=16)
    label(c, "EVERY ERUPTION", 470, t - 0.8, size=52, bg=WHITE)
    k = back((t - 1.0) / 0.35)
    if k > 0: c.save(); c.translate(W / 2, 830); c.scale(k, k); stopwatch(c, 0, 0, 120, t); c.restore()
    if t > 2.9: label(c, "THE TRICK IS GENIUS", 1080, t - 2.9, size=50)


def globe_k(gt):  # globe progress across s3+s4
    return min(1.0, (gt - STARTS[3]) / (DURS[3] + 3.0))


def s3(c, t, d):
    a, R = GLOBE.frame(globe_k(STARTS[3] + t), *LOC, R0=430, R1=5200)
    to_ctx(c, a)
    pop_text(c, "WHERE?", W / 2, 420, 150, t - 0.05, col=GOLD, stroke=16)


def s4(c, t, d):  # globe zoom -> aerial basin -> real eruption with counters
    gt = STARTS[4] + t; k = globe_k(gt)
    T1 = 3.0 - DURS[3] + DURS[3]  # globe ends at t = 3.0 into this scene
    if t < 3.0:
        a, R = GLOBE.frame(k, *LOC, R0=430, R1=5200)
        to_ctx(c, a)
        x, y = W / 2, H * 0.47
        pin(c, x, y, t - 1.4)
        label(c, "YELLOWSTONE · WYOMING", y + 40, t - 1.6, size=44, bg=WHITE)
    elif t < 5.0:
        tt = t - 3.0
        a, R = GLOBE.frame(1.0, *LOC, R0=430, R1=5200)
        ph = finish(AER.kb(tt / 2.0, 1.0, 1.1, (0.45, 0.5), (0.45, 0.5)), tt)
        to_ctx(c, GL.handoff(a, ph, tt / 0.6) if tt < 0.6 else ph)
        P2.steam(c, tt, 100, 900, 1100, rise=500, alpha=0.12)
        pop_text(c, "~HALF", W / 2, 420, 170, tt - 0.4, col=GOLD, stroke=18)
        text(c, "OF THE WORLD'S GEYSERS", W / 2, 520, 60, col=WHITE, stroke=12, alpha=ease((tt - 0.7) / 0.3))
        source_tag(c, "Source: USGS Yellowstone Volcano Observatory", tt - 0.3)
    else:
        tt = t - 5.0
        to_ctx(c, finish(CB.at(tt).astype(np.float32), tt, vign=0.25))
        # gallons counter
        g0 = 0.6
        if tt > g0 - 0.2:
            txt = counter(c, tt - g0, 0, 8400, 1.4)
            pop_text(c, txt, W / 2, 400, 150, tt - g0 + 0.2, col=GOLD, stroke=18)
            text(c, "GALLONS OF BOILING WATER", W / 2, 480, 50, col=WHITE, stroke=10, alpha=ease((tt - g0) / 0.3))
        # height ruler grows 0 -> 184 ft beside the plume
        h0 = 2.6
        if tt > h0:
            k = eout((tt - h0) / 1.4); base = 1180; top = lerp(base, 640, k); x = 820
            c.set_source_rgba(*GOLD, 1); c.set_line_width(8); c.move_to(x, base); c.line_to(x, top); c.stroke()
            for y in np.arange(base, top, -60): c.move_to(x - 16, y); c.line_to(x, y); c.stroke()
            c.move_to(x - 30, top); c.line_to(x + 30, top); c.set_line_width(10); c.stroke()
            text(c, counter(c, tt - h0, 0, 184, 1.4) + " FT", x - 20, top - 30, 76, col=GOLD, stroke=12)
        source_tag(c, "Source: NPS · Video: S. Pavlov / CC BY-SA 4.0", tt - 0.2)


def s5(c, t, d):  # F: "what's down there?" x-ray dive
    xr = 0.8 * ease(t / 0.7)
    a = SUN.kb(t / d, 1.05, 1.35, (0.5, 0.6), (0.5, 0.75))
    to_ctx(c, finish(a, t, xray=xr))
    for j in range(24):
        y = (j * 90 + t * 400) % (H + 100) - 50
        c.move_to(-20, y); c.line_to(W + 20, y)
    c.set_source_rgba(0.6, 0.85, 1, 0.12 * xr); c.set_line_width(3); c.stroke()
    pop_text(c, "DOWN THERE?", W / 2, 440, 130, t - 0.05, col=GOLD, stroke=16)


def s6(c, t, d):  # camera survey down the vent
    z = lerp(1.0, 1.12, ease(t / d)); c.save(); cam(c, z, W / 2, 820)
    section(c, t, cav=0.0)
    yprobe = lerp(VY - 120, dy(22) - 20, ease((t - 1.2) / 4.2))
    camera_probe(c, yprobe, t)
    if t > 5.6: squeeze_arrows(c, dy(22), t)
    c.restore()
    depth_ruler(c, t, max(0, (yprobe - VY) / PXFT))
    label(c, "1990s: A CAMERA DOWN THE VENT", 300, t - 0.3, size=44, bg=WHITE)
    if t > 1.2:
        ft = int(max(0, min(22, (yprobe - VY + 20) / PXFT)))
        pop_text(c, f"{ft} FT", 830, 760, 90, t - 1.2, col=GOLD, stroke=14, maxw=220)
    if t > 5.8: label(c, "JUST A FEW INCHES", dy(22) + 70, t - 5.8, x=W / 2, size=48)
    source_tag(c, "Source: NPS · Hutchinson et al., Geology 1997", t - 0.5, y=410)


def s7(c, t, d):  # F: "a few inches?!" — zoom into the squeeze
    z = lerp(1.6, 2.4, eout(t / 0.8)); c.save(); cam(c, z, W / 2, dy(22))
    section(c, STARTS[7] + t, cav=0.0); squeeze_arrows(c, dy(22), t)
    camera_probe(c, dy(22) - 20, t); c.restore()
    pop_text(c, "A FEW INCHES?!", W / 2, 430, 120, t - 0.05, col=GOLD, stroke=16)


def s8(c, t, d):  # cavern the size of a car
    c.save(); cam(c, lerp(1.25, 1.15, ease(t / d)), W / 2, 1000)
    reveal = ease((t - 0.4) / 0.6)
    section(c, STARTS[8] + t, cav=reveal)
    camera_probe(c, lerp(dy(22) - 20, CAV0 + 30, ease(t / 0.9)), t)
    if t > 1.0: car(c, W / 2, (CAV0 + CAV1) / 2 + 10, 220, ease((t - 1.0) / 0.4))
    c.restore()
    pop_text(c, "CAVERN", W / 2, 400, 150, t - 0.3, col=GOLD, stroke=18)
    label(c, "SIZE OF A SMALL CAR · 35–45 FT DOWN", 500, t - 1.0, size=38, bg=WHITE)
    if t > 2.0: pop_text(c, "THE CAVE!", W / 2, 800, 84, t - 2.0, col=WHITE, stroke=14)


def s9(c, t, d):  # pressure cooker
    rain = ease((t - 0.8) / 0.5) * (1 - ease((t - 4.0) / 0.6))
    glow = ease((t - 2.4) / 0.8); water = ease((t - 1.0) / 2.0); heat = ease((t - 3.0) / 2.5)
    c.save(); cam(c, lerp(0.98, 1.06, t / d), W / 2, 1000)
    section(c, t, water=water, heat=heat, glow=glow, rain=rain)
    if t > 2.8:  # heat arrows rising from magma
        for j in range(5):
            x = 200 + j * 170; k = ((t * 0.8 + j * 0.23) % 1.0); y = lerp(1850, 1500, k)
            c.set_source_rgba(1, 0.6, 0.2, 0.8 * (1 - k) * glow); c.move_to(x, y); c.line_to(x - 22, y + 36); c.line_to(x + 22, y + 36); c.close_path(); c.fill()
    if t > 6.0:  # weight of the water column pressing down
        for j in range(3):
            y = VY - 40 + j * 110 + 20 * math.sin(t * 6); k = back((t - 6.0 - j * 0.1) / 0.3)
            if k <= 0: continue
            c.save(); c.translate(W / 2 + 160, y); c.scale(k, k); c.set_source_rgb(*GOLD)
            c.move_to(-16, -40); c.line_to(16, -40); c.line_to(16, 0); c.line_to(34, 0); c.line_to(0, 40); c.line_to(-34, 0); c.line_to(-16, 0); c.close_path(); c.fill(); c.restore()
    c.restore()
    pop_text(c, "PRESSURE COOKER", W / 2, 400, 110, t - 0.05, col=GOLD, stroke=16)
    if 0.9 < t < 4.2: label(c, "RAIN + SNOWMELT", 480, t - 0.9, size=42, bg=WHITE)
    if t > 2.6: label(c, "MAGMA HEAT", 1230, t - 2.6, size=42, bg=ORANGE, fg=WHITE) if t < 6.0 else None
    if t > 3.2: thermo(c, t, min(0.9, 0.2 + 0.7 * ease((t - 3.2) / 2.0)), x=110, y0=1150, y1=820)
    if t > 4.6: label(c, "HOTTER THAN BOILING", 500, t - 4.6, size=46) if t < 6.0 else label(c, "TOO MUCH WEIGHT TO BOIL", 500, t - 6.0, size=42, bg=RED, fg=WHITE)


def s10(c, t, d):  # spill -> pressure drop -> flash to steam -> real eruption
    if t < 3.0:
        sh = 6 * math.sin(t * 60) * ease((t - 1.6) / 0.3)
        c.save(); c.translate(sh, 0); cam(c, 1.04)
        section(c, STARTS[10] + t, water=1.0, heat=1.0, glow=1.0, steam=ease((t - 1.5) / 0.5))
        if t > 0.3:  # spill at the vent
            for a, b, s, ph in P2.p[:40]:
                life = ((t - 0.3) * 1.4 + ph) % 1.0; ang = math.pi * (0.15 + 0.7 * a)
                x = W / 2 - math.cos(ang) * life * 260; y = VY - 60 - math.sin(ang) * life * 180 + life * life * 260
                c.set_source_rgba(0.75, 0.92, 1, 0.9 * (1 - life)); c.arc(x, y, 6 + 6 * s, 0, 2 * math.pi); c.fill()
        c.restore()
        gauge(c, 800, 900, 105, 1 - ease((t - 0.7) / 1.0), t)
        if t < 1.5: pop_text(c, "SPILL", W / 2, 400, 150, t - 0.2, col=GOLD, stroke=18)
        else: pop_text(c, "FLASHES TO STEAM", W / 2, 400, 120, t - 1.5, col=GOLD, stroke=16)
    else:
        tt = t - 3.0
        to_ctx(c, finish(CC.at(tt).astype(np.float32), tt, vign=0.25))
        P2.steam(c, tt, 300, 760, 1100, rise=700, alpha=0.2)
        pop_text(c, "WHOOSH", W / 2, 420, 170, tt - 0.05, col=GOLD, stroke=18)


def s11(c, t, d):  # F: "how do rangers call the next one?"
    a = SUN.kb(t / d, 1.0, 1.12, (0.45, 0.5), (0.45, 0.45))
    to_ctx(c, finish(a, t))
    pop_text(c, "THE NEXT ONE?", W / 2, 420, 130, t - 0.05, col=GOLD, stroke=16)
    k = back((t - 0.3) / 0.35)
    if k > 0: c.save(); c.translate(W / 2, 820); c.scale(k, k); stopwatch(c, 0, 0, 110, t); c.restore()


def s12(c, t, d):  # time the eruption: short -> 68 min, long -> 94 min
    to_ctx(c, blurred("blue", BLUE))
    P1.dust(c, t, alpha=0.25)
    if t < 2.0:
        k = back(t / 0.35); c.save(); c.translate(W / 2, 800); c.scale(k * 1.2, k * 1.2); stopwatch(c, 0, 0, 150, t * 2); c.restore()
        pop_text(c, "TIME IT", W / 2, 420, 150, t - 0.05, col=GOLD, stroke=18)
    else:
        tt = t - 2.0
        def row(y, tag, h, val, t0):
            if tt < t0: return
            u = tt - t0; a = min(1, u / 0.3)
            c.set_source_rgba(0.04, 0.07, 0.18, 0.72 * a); rrect(c, 70, y - 150, W - 230, 300, 40); c.fill()
            c.set_source_rgba(*GOLD, a); c.set_line_width(5); rrect(c, 70, y - 150, W - 230, 300, 40); c.stroke()
            plume(c, 220, y + 100, h * eout(u / 0.6), u, a)
            text(c, tag, 520, y - 70, 46, col=WHITE, alpha=a, stroke=8)
            ar = eout((u - 0.3) / 0.4); c.set_source_rgba(*GOLD, a); c.set_line_width(8)
            c.move_to(360, y + 10); c.line_to(360 + 120 * ar, y + 10); c.stroke()
            if u > 0.5:
                text(c, counter(c, u - 0.5, 0, val, 0.8) + " MIN", 700, y + 50, 100, col=GOLD, stroke=14)
        row(640, "SHORT ERUPTION", 110, 68, 0.0)
        row(1020, "LONG ERUPTION", 220, 94, 2.9)
        text(c, "NEXT ERUPTION IN ABOUT…", W / 2, 400, 54, col=WHITE, stroke=10, alpha=ease(tt / 0.3))
        source_tag(c, "Source: NPS Yellowstone geyser predictions (±10 min)", tt - 0.3)


def s13(c, t, d):  # F: "and that works?"
    to_ctx(c, finish(CD.at(t).astype(np.float32), t, vign=0.25))
    pop_text(c, "WORKS?", W / 2, 460, 170, t - 0.03, col=GOLD, stroke=18)


def s14(c, t, d):  # 9 in 10 within 10 min -> loop back to hook
    if t < 2.9:
        to_ctx(c, blurred("blue_r", BLUE, (0.3, 0.55)))
        for i in range(10):
            col_ = i % 5; rw = i // 5; x = 190 + col_ * 175; y = 760 + rw * 260; u = t - 0.15 - i * 0.12
            if u <= 0: continue
            k = back(u / 0.3); c.save(); c.translate(x, y); c.scale(k, k)
            good = i < 9
            c.set_source_rgba(*(GOLD if good else (0.55, 0.55, 0.6)), 1); c.arc(0, 0, 70, 0, 2 * math.pi); c.fill()
            if good:
                c.set_source_rgb(*NAVY); c.set_line_width(14); c.set_line_cap(cairo.LINE_CAP_ROUND)
                c.move_to(-28, 2); c.line_to(-8, 24); c.line_to(30, -22); c.stroke()
            else:
                c.set_source_rgb(1, 1, 1); c.set_line_width(12); c.move_to(-22, -22); c.line_to(22, 22); c.move_to(22, -22); c.line_to(-22, 22); c.stroke()
            c.restore()
        pop_text(c, "9 IN 10", W / 2, 430, 170, t - 0.05, col=GOLD, stroke=18)
        label(c, "WITHIN ±10 MINUTES", 520, t - 0.9, size=50, bg=WHITE)
    else:
        tt = t - 2.9
        hook_frame(c, tt + 4.0, z=lerp(1.08, 1.0, eout(tt / 0.6)))


def s15(c, t, d):
    to_ctx(c, blurred("blue", BLUE))
    end_card_logo(c, t, W / 2, 680, 290, LOGO)
    pop_text(c, "FOLLOW", W / 2, 1150, 130, t, col=GOLD, stroke=14)
    text(c, "a new wonder every day", W / 2, 1240, 54, col=WHITE, stroke=8, alpha=ease(t / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15]


def frame(c, gt):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    c.save()
    if i > 0 and t < 0.3 and i not in (4,):
        z = 1 + 0.08 * (1 - eout(t / 0.3)); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[i](c, t, d)
    c.restore()
    if i < len(SCENES) - 1:
        badge(c, gt); captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"))
    if i > 0 and i != 4: wipe(c, t, col=GOLD if i % 2 else ORANGE)


def events():
    s = STARTS
    ev = [("boom", 0.0), ("hiss", 0.0), ("whoosh", 1.15), ("pop", 1.2), ("crack", 1.6)] + [("whoosh", x - 0.05) for x in s[1:]]
    ev += [("boom", s[2] + 0.6), ("pop", s[2] + 2.4)] + [("tick", s[2] + 3.0 + k * 0.25) for k in range(8)]
    ev += [("whoosh", s[3] + 0.2), ("whoosh", s[4] + 1.0), ("pop", s[4] + 1.4), ("whoosh", s[4] + 3.0), ("pop", s[4] + 3.4)]
    ev += [("boom", s[4] + 5.0), ("hiss", s[4] + 5.0)] + [("tick", s[4] + 5.6 + k * 0.07) for k in range(18)] + [("tick", s[4] + 7.6 + k * 0.07) for k in range(18)] + [("pop", s[4] + 9.0)]
    ev += [("whoosh", s[5] + 0.1), ("drill", s[6] + 1.2), ("pop", s[6] + 0.3)] + [("tick", s[6] + 1.3 + k * 0.2) for k in range(20)] + [("thunk", s[6] + 5.7), ("pop", s[6] + 5.9)]
    ev += [("whoosh", s[7] + 0.05), ("boom", s[8] + 0.5), ("pop", s[8] + 1.0)]
    ev += [("pop", s[9] + 0.1), ("splash", s[9] + 1.0), ("bubble", s[9] + 3.4), ("pop", s[9] + 4.7), ("thunk", s[9] + 6.0), ("thunk", s[9] + 6.1), ("thunk", s[9] + 6.2)]
    ev += [("splash", s[10] + 0.3), ("bubble", s[10] + 1.5), ("bubble", s[10] + 2.0), ("whoosh", s[10] + 2.8), ("boom", s[10] + 3.0), ("hiss", s[10] + 3.0)]
    ev += [("tick", s[11] + 0.4 + k * 0.25) for k in range(6)] + [("tick", s[12] + k * 0.25) for k in range(8)]
    ev += [("whoosh", s[12] + 2.0), ("pop", s[12] + 2.5)] + [("tick", s[12] + 2.5 + k * 0.06) for k in range(14)]
    ev += [("whoosh", s[12] + 4.9), ("pop", s[12] + 5.4)] + [("tick", s[12] + 5.4 + k * 0.06) for k in range(14)]
    ev += [("boom", s[13]), ("pop", s[14] + 0.1)] + [("pop", s[14] + 0.15 + i * 0.12) for i in range(10)]
    ev += [("whoosh", s[14] + 2.85), ("hiss", s[14] + 2.9), ("crack", s[14] + 4.3), ("pop", s[15])]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "still":
        frame(c, float(sys.argv[2])); surf.write_to_png(sys.argv[3])
    elif sys.argv[1] == "stills":  # python render_003.py stills out_prefix t1 t2 ...
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
