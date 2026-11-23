"""Video 005 — Niagara Falls: "In 1969, engineers switched off Niagara Falls" -> what they found (a pile of fallen rock)
-> hard caprock over soft shale -> the falls breaks itself and has walked 7 miles upstream in ~12,000 years -> today
it barely moves because half the river goes to power stations by day, even more at night (natural wonder, format
"timeline" + a real event). Man (Bidhan's voice) opens and explains today, woman (Jessica) asks/reacts.
Real media: dewatered American Falls 1969 (James St. John CC BY 2.0; NMGiovannucci CC BY-SA 4.0), American Falls +
Niagara Gorge (Ken Lund CC BY-SA 2.0), Horseshoe aerial (Zwergelstern CC BY-SA 3.0), Robert Moses power plant (George
Burns / NARA, PD), video GolhaMedia (CC BY-SA 4.0) + Alexis Lewis (CC BY 2.0), NASA globe.
Drawn explainers: on/off switch, top-down map with the 1969 rock dam, cliff cross-section (hard dolomite over soft
shale) with undercut + collapse, 12,000-year retreat map, day/night flow bars.
usage (work dir with meta.json from tts_el.py, media/, clipA..C):
  python render_005.py stills <prefix> t1 t2 ...   |   python render_005.py full"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish
from clips import Clip
import globe as GL


def finish(a, t, **kw):  # every photo/clip frame gets edge haze (edge-band check)
    return _finish(haze(a, t), t, **kw)


meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]; DURS[-1] += 0.4
TOTAL = STARTS[-1] + DURS[-1]
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix): return sorted(glob.glob(f"media/{prefix}*"))[0]


DRY = Photo(M("Dewatered_American_Falls"), maxz=1.35)             # James St. John, CC BY 2.0 (1969 colour)
DRYBW = Photo(M("1969_Drained"), archival=True, maxz=1.3)          # NMGiovannucci, CC BY-SA 4.0 (1969 b/w)
AMER = Photo(M("American_Falls__Niagara"), maxz=1.3)                # Ken Lund, CC BY-SA 2.0
GORGE = Photo(M("Niagara_Gorge"), maxz=1.3)                         # Ken Lund, CC BY-SA 2.0
AER = Photo(M("Niagara_Falls_Horseshoe_aerial"), maxz=1.3)          # Zwergelstern, CC BY-SA 3.0
POWER = Photo(M("THE_ROBERT_MOSES"), maxz=1.3)                      # George Burns / NARA, PD
CA, CB, CC = Clip("clipA"), Clip("clipB"), Clip("clipC")
GLOBE = GL.Globe()
NIAG = (43.08, -79.07)
P1, P2, P3 = Particles(110, 1), Particles(80, 2), Particles(120, 3)
TX = make_textures(5)
RED = (0.92, 0.2, 0.22); GREEN = (0.25, 0.8, 0.45); RIVER = (0.18, 0.55, 0.7)
DOLO = (0.72, 0.68, 0.6); SHALE = (0.36, 0.3, 0.28)
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


def project(lat, lon, lat0, lon0, R, cy=H / 2):
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


def counter(t, v0, v1, dur, fmt="{:,}"):
    return fmt.format(int(round(lerp(v0, v1, eout(t / dur))))) if t > 0 else fmt.format(v0)


def arrow(c, x0, y0, x1, y1, col=GOLD, w=12, head=34, alpha=1.0):
    ang = math.atan2(y1 - y0, x1 - x0)
    c.save(); c.set_source_rgba(0, 0, 0, 0.45 * alpha); c.set_line_width(w + 8); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x0, y0); c.line_to(x1 - head * 0.6 * math.cos(ang), y1 - head * 0.6 * math.sin(ang)); c.stroke()
    c.set_source_rgba(*col, alpha); c.set_line_width(w)
    c.move_to(x0, y0); c.line_to(x1 - head * 0.6 * math.cos(ang), y1 - head * 0.6 * math.sin(ang)); c.stroke()
    c.move_to(x1, y1)
    c.line_to(x1 - head * math.cos(ang - 0.45), y1 - head * math.sin(ang - 0.45))
    c.line_to(x1 - head * math.cos(ang + 0.45), y1 - head * math.sin(ang + 0.45)); c.close_path(); c.fill(); c.restore()


# ---------------- drawn explainers ----------------
def switch_icon(c, x, y, s, off_k, t=0.0):
    """big ON/OFF toggle; off_k 0 = ON (green, knob right), 1 = OFF (red, knob left)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    w, h = 300, 140
    c.set_source_rgba(0, 0, 0, 0.45); rrect(c, -w / 2 + 8, -h / 2 + 12, w, h, h / 2); c.fill()
    c.set_source_rgb(*lerpc(GREEN, RED, off_k)); rrect(c, -w / 2, -h / 2, w, h, h / 2); c.fill()
    c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(8); rrect(c, -w / 2, -h / 2, w, h, h / 2); c.stroke()
    kx = lerp(w / 2 - h / 2, -w / 2 + h / 2, eout(off_k))
    text(c, "OFF" if off_k > 0.5 else "ON", -kx * 0.75, 22, 58, col=WHITE, stroke=0)
    g = cairo.RadialGradient(kx - 15, -15, 5, kx, 0, h / 2)
    g.add_color_stop_rgb(0, 1, 1, 1); g.add_color_stop_rgb(1, 0.78, 0.8, 0.85)
    c.arc(kx, 0, h / 2 - 12, 0, 2 * math.pi); c.set_source(g); c.fill()
    c.restore()


def river_map(c, t, dam=0.0, dry=0.0):
    """schematic top-down map: the river flows UP the screen, Goat Island splits it, Horseshoe Falls (left, Canada)
    and American Falls (right, USA) near the top; the 1969 rock dam fills across the American channel."""
    paint_tex(c, TX["terrain"], dx=40 * math.sin(t * 0.2), dy=0)
    # gorge at the top
    c.save(); c.rectangle(-50, -50, W + 100, 560); fill_tex(c, TX["rock"], dy=-200); c.restore()
    # river body (bottom) + two channels
    def chan(pts, wid):
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]
        c.set_line_width(wid); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.save(); tex(c, TX["water"], dy=-t * 120)
    chan([(560, H + 100), (560, 1500), (520, 1150)], 620); c.stroke()
    chan([(470, 1150), (330, 800), (300, 560)], 330); c.stroke()
    c.restore()
    # American channel: water or dry riverbed
    c.save(); tex(c, TX["water"], dy=-t * 120)
    chan([(640, 1180), (790, 820), (820, 560)], 190); c.stroke(); c.restore()
    if dry > 0:
        c.save(); c.push_group(); tex(c, TX["sand"]); chan([(768, 860), (790, 820), (820, 560)], 192); c.stroke(); c.pop_group_to_source(); c.paint_with_alpha(dry); c.restore()
    # Goat Island
    c.save(); c.move_to(520, 1020); c.curve_to(690, 980, 700, 760, 650, 560); c.line_to(470, 560); c.curve_to(430, 760, 420, 980, 520, 1020); c.close_path()
    c.set_source_rgb(0.3, 0.55, 0.28); c.fill_preserve(); c.set_source_rgba(0.1, 0.25, 0.1, 0.8); c.set_line_width(5); c.stroke(); c.restore()
    for k in range(40):  # trees on the island
        x = 520 + 110 * math.sin(k * 2.3); y = 600 + (k * 37 % 400)
        c.set_source_rgba(0.15, 0.4 + 0.1 * math.sin(k), 0.15, 0.8); c.arc(x, y, 14 + (k % 3) * 5, 0, 2 * math.pi); c.fill()
    # falls lines (white crests)
    for pts in ([(140, 600), (230, 500), (360, 480), (470, 560)], [(700, 560), (930, 540)]):
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]
        c.set_source_rgba(1, 1, 1, 0.95 if pts[0][0] < 600 else 1 - 0.9 * dry); c.set_line_width(22); c.stroke()
    P3.dust(c, t, col=(1, 1, 1), alpha=0.35, speed=60, size=4)
    # the rock dam: boulders dropping in, left -> right
    if dam > 0:
        n = 18
        for j in range(int(n * min(1, dam)) + 1):
            if j >= n: break
            u = j / (n - 1); x = lerp(665, 870, u); y = lerp(905, 870, u) + 8 * math.sin(j * 3)
            k = min(1, (dam * n - j) * 1.5)
            yy = y - 120 * (1 - eout(k))
            c.set_source_rgba(0.35, 0.3, 0.27, 1); c.arc(x, yy, 26 + (j * 7 % 10), 0, 2 * math.pi); c.fill()
            c.set_source_rgba(0.6, 0.55, 0.5, 1); c.arc(x - 6, yy - 6, 12, 0, 2 * math.pi); c.fill()
    text(c, "CANADA", 150, 1000, 52, col=WHITE, stroke=10)
    text(c, "USA", 960, 1000, 52, col=WHITE, stroke=10)


def cliff_section(c, t, under=0.0, snap=0.0, flow=1.0, labels=0.0):
    """side view: hard dolomite caprock over soft shale; the plunge pool undercuts the shale; the overhang breaks"""
    paint_tex(c, TX["sky"], dy=-300)
    top, d1, d2 = 760, 940, 1330           # top surface, dolomite/shale boundary, pool level
    cx = 640                                 # cliff face x
    notch = 230 * under                      # how deep the shale is eaten back
    # hard caprock (dolostone): grey rock texture, irregular blocky joints
    c.save(); c.rectangle(-60, top, cx + 60, d1 - top); c.clip(); paint_tex(c, TX["rock"], dx=10, dy=40)
    c.set_source_rgba(0.62, 0.62, 0.62, 0.72); c.paint()
    for k in range(60):
        x = (k * 97) % (cx + 40) - 20; y = top + (k * 53) % (d1 - top)
        c.set_source_rgba(1, 1, 1, 0.10); c.arc(x, y, 6 + k % 9, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(0.25, 0.24, 0.23, 0.75); c.set_line_width(4)
    for j, y in enumerate((top + 62, top + 118)):
        c.move_to(-60, y); [c.line_to(x, y + 6 * math.sin(x / 37 + j)) for x in range(0, cx + 20, 30)]; c.stroke()
    for k in range(9):
        x = 40 + k * 70 + (k * 29) % 25; y0 = top + (0 if k % 2 else 62)
        c.move_to(x, y0); c.line_to(x + 8, y0 + 40); c.line_to(x - 4, y0 + 62); c.stroke()
    c.restore()
    # shale, with the undercut notch
    c.save(); c.move_to(-60, d1); c.line_to(cx - notch * 0.35, d1)
    c.curve_to(cx - notch, d1 + 80, cx - notch, d2 - 60, cx - notch * 0.2, d2); c.line_to(-60, d2); c.close_path()
    c.set_source_rgb(*SHALE); c.fill_preserve(); c.save(); c.clip()
    for y in range(d1 + 14, d2, 18):
        c.set_source_rgba(0.2, 0.16, 0.15, 0.7); c.set_line_width(3); c.move_to(-60, y + 4 * math.sin(y)); c.line_to(cx, y); c.stroke()
    c.restore(); c.restore()
    # lower rock + ground fills the bottom of the frame (texture to the edge)
    c.save(); c.rectangle(-60, d2, W + 120, H - d2 + 60); fill_tex(c, TX["rock"], dy=d2); c.restore()
    # plunge pool
    c.save(); c.rectangle(cx - notch, d2 - 40, W - cx + notch + 60, 140); fill_tex(c, TX["water"], dx=t * 80); c.restore()
    # river on top
    c.save(); c.rectangle(-60, top - 60, cx + 60 - (0 if snap < 0.01 else 0), 60); fill_tex(c, TX["water"], dx=t * 160); c.restore()
    # breaking overhang block
    bw = 150
    if snap > 0:
        ang = 1.2 * eout(snap); dy = 520 * snap ** 2
        c.save(); c.translate(cx, d1 + dy); c.rotate(ang); c.rectangle(-bw, -(d1 - top), bw, d1 - top)
        fill_tex(c, TX["concrete"]); c.set_source_rgba(0, 0, 0, 0.6); c.set_line_width(5); c.rectangle(-bw, -(d1 - top), bw, d1 - top); c.stroke(); c.restore()
        if snap > 0.05 and snap < 0.25:  # crack flash
            c.set_source_rgba(1, 1, 1, 0.8); c.set_line_width(8); c.move_to(cx - bw, top); c.line_to(cx - bw + 20, top + 60); c.line_to(cx - bw - 10, top + 110); c.line_to(cx - bw + 10, d1); c.stroke()
        if snap > 0.8: P3.sparks(c, (snap - 0.8) * 2, cx - 40, d2 - 30, alpha=0.9)
    else:
        c.set_source_rgba(1, 0.3, 0.3, 0.0);
    # waterfall curtain
    fx = cx - (bw if snap >= 1 else 0)
    if flow > 0:
        for k in range(26):
            ph = (t * 1.6 + k * 0.137) % 1.0; x = fx + 10 + (k % 6) * 14 + ph * 50
            y0 = top - 40; y1 = d2 - 20
            c.move_to(x, y0 + ph * 40); c.curve_to(x + 40, y0 + 60, x + 60, (y0 + y1) / 2, x + 70 + (k % 4) * 10, y1)
            c.set_source_rgba(0.9, 0.97, 1, 0.55 * flow); c.set_line_width(10 + (k % 3) * 4); c.stroke()
        P1.steam(c, t, fx + 20, fx + 360, d2 - 20, rise=200, alpha=0.16 * flow)
    if labels > 0:
        a = min(1, labels)
        label(c, "HARD ROCK", top + 40, labels, x=300, size=44, bg=WHITE)
        if labels > 0.8: label(c, "SOFT SHALE", d1 + 120, labels - 0.8, x=280, size=44, bg=ORANGE, fg=NAVY)


def retreat_map(c, t, k):
    """the river from Lake Erie (bottom) to Lake Ontario (top); the falls start at the escarpment (Lewiston) and
    walk upstream, leaving the gorge behind them"""
    paint_tex(c, TX["terrain"], dy=-20 * t)
    # lakes
    c.save(); c.rectangle(-60, -60, W + 120, 330); fill_tex(c, TX["water"], dx=t * 30); c.restore()
    c.save(); c.rectangle(-60, H - 330, W + 120, 400); fill_tex(c, TX["water"], dx=-t * 30); c.restore()
    text(c, "LAKE ONTARIO", W / 2, 230, 48, col=WHITE, stroke=10)
    text(c, "LAKE ERIE", W / 2, H - 120, 48, col=WHITE, stroke=10)
    # river path
    pts = [(540, 270), (560, 420), (520, 560), (560, 700), (600, 860), (560, 1000), (520, 1150), (560, 1350), (540, 1600)]
    c.save(); c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.line_to(540, H - 300)
    tex(c, TX["water"], dy=t * 120); c.set_line_width(70); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke(); c.restore()
    # escarpment
    c.save(); c.move_to(-60, 640); [c.line_to(x, 640 + 18 * math.sin(x / 70)) for x in range(0, W + 80, 40)]
    c.set_source_rgba(0.35, 0.22, 0.12, 0.95); c.set_line_width(26); c.stroke()
    c.set_dash([4, 14]); c.set_source_rgba(1, 1, 1, 0.6); c.set_line_width(4)
    c.move_to(-60, 610); [c.line_to(x, 610 + 18 * math.sin(x / 70)) for x in range(0, W + 80, 40)]; c.stroke(); c.restore()
    text(c, "ESCARPMENT", 200, 590, 34, col=WHITE, stroke=8)
    # falls position: y from 650 (start, Lewiston) to 1150 (today)
    fy = lerp(650, 1150, eout(k))
    c.save(); c.move_to(540, 640); c.line_to(560, fy)
    c.set_source_rgba(0.22, 0.12, 0.06, 0.9); c.set_line_width(110); c.set_line_cap(cairo.LINE_CAP_BUTT); c.stroke(); c.restore()
    c.save(); c.move_to(540, 640); c.line_to(560, fy); tex(c, TX["water"], dy=t * 160); c.set_line_width(56); c.stroke(); c.restore()
    c.set_source_rgba(1, 1, 1, 1); c.set_line_width(18); c.move_to(480, fy); c.line_to(640, fy); c.stroke()
    P3.dust(c, t, col=(1, 1, 1), alpha=0.5, speed=30, size=3)
    label(c, "LEWISTON", 660, 1.0, x=830, size=40, bg=WHITE)
    # distance bracket
    if k > 0.05:
        c.set_source_rgba(*GOLD, 1); c.set_line_width(8)
        c.move_to(760, 650); c.line_to(800, 650); c.line_to(800, fy); c.line_to(760, fy); c.stroke()
        text(c, counter(k, 0, 7, 1.0, "{} MI"), 900, (650 + fy) / 2 + 20, 64, col=GOLD, stroke=12)


def flow_bars(c, t, day=0.0, night=0.0):
    """two stacked bars: share of the river going over the falls (day: ~half, night: about half again)"""
    for j, (lab, frac, k, col) in enumerate((("DAY", 0.5, day, GOLD), ("NIGHT", 0.25, night, hexc("6FB7FF")))):
        if k <= 0: continue
        y = 700 + j * 230; x0, w = 140, 800; a = min(1, k * 3)
        c.set_source_rgba(0.04, 0.06, 0.15, 0.7 * a); rrect(c, x0 - 20, y - 70, w + 40, 190, 30); c.fill()
        text(c, lab, x0, y - 12, 44, col=WHITE, align="left", stroke=8, alpha=a)
        c.set_source_rgba(1, 1, 1, 0.2 * a); rrect(c, x0, y + 10, w, 70, 35); c.fill()
        f = lerp(1.0, frac, eout(k))
        c.set_source_rgba(*col, a); rrect(c, x0, y + 10, max(70, w * f), 70, 35); c.fill()
        text(c, "OVER THE FALLS", x0 + w, y - 12, 34, col=WHITE, align="right", stroke=8, alpha=a)


# ---------------- scenes (one per line) ----------------
def hook_frame(c, t, z=1.0):
    a = DRY.kb(min(1, t / 5.0), 1.0, 1.12, (0.4, 0.45), (0.45, 0.5))
    c.save(); cam(c, z, W / 2, 1000); to_ctx(c, finish(a, t, vign=0.45)); c.restore()
    P1.dust(c, t, col=(1, 0.95, 0.85), alpha=0.25, speed=20, size=3)
    s_ = 1 + 0.02 * math.sin(t * 5)
    c.save(); c.translate(W / 2, 390); c.scale(s_, s_)
    text(c, "NIAGARA FALLS…", 0, 0, 92, col=WHITE, stroke=16)
    text(c, "SWITCHED OFF?!", 0, 110, 112, col=GOLD, stroke=18)
    c.restore()
    switch_icon(c, 820, 1060, 0.85, ease((t - 0.6) / 0.35), t)
    label(c, "1969", 1150, 1.0, x=250, size=56, bg=GOLD)


def s0(c, t, d):  # M hook "In 1969, engineers switched off Niagara Falls." — dry falls photo + switch flips at 0.6 s
    if t < 3.1:
        hook_frame(c, t, z=punch(t, 1.2, 0.08))
    else:
        tt = t - 3.1; a = DRYBW.kb(tt / 2.0, 1.0, 1.1, (0.3, 0.6), (0.4, 0.62)); to_ctx(c, finish(a, tt, archival=True, vign=0.45))
        pop_text(c, "THE AMERICAN FALLS, DRY", W / 2, 420, 84, tt - 0.05, col=GOLD, stroke=14)
    source_tag(c, "Photo: James St. John / CC BY 2.0", t - 1.6, y=1290)


def s1(c, t, d):  # F "Wait, you can switch off a waterfall?" — roaring real footage
    to_ctx(c, finish(CA.at(t).astype(np.float32), t, vign=0.3))
    pop_text(c, "A WATERFALL?!", W / 2, 420, 140, t - 0.5, col=GOLD, stroke=18)
    switch_icon(c, W / 2, 1080, 0.8, 0.5 + 0.5 * math.sin(t * 7) if t > 1.0 else 0.0, t)
    source_tag(c, "Video: GolhaMedia / CC BY-SA 4.0", t - 0.2)


def s2(c, t, d):  # M "Well, the American side. And what they found underneath explains why the whole falls is moving."
    if t < 3.0:  # globe zoom to Niagara, between the lakes
        k = ease(t / 2.8); R = 900 * (5.5 ** k); lat0 = lerp(30, NIAG[0], k); lon0 = lerp(-95, NIAG[1], k)
        to_ctx(c, finish(GLOBE.render(lat0, lon0, R).astype(np.float32), t, vign=0.3))
        x, y = project(*NIAG, lat0, lon0, R); pin(c, x, y, t - 0.4)
        pop_text(c, "NIAGARA FALLS", W / 2, 420, 120, t - 0.2, col=GOLD, stroke=16)
        if t > 1.6: label(c, "USA  |  CANADA", 560, t - 1.6, size=44, bg=WHITE)
    else:
        tt = t - 3.0
        a = AMER.kb(tt / (d - 3.0), 1.05, 1.25, (0.6, 0.4), (0.66, 0.38)); to_ctx(c, finish(a, tt, vign=0.4))
        label(c, "THE AMERICAN SIDE", 520, tt, size=50)
        if tt > 2.0:
            arrow(c, 820, 1150, 520, 1050, col=GOLD, alpha=ease((tt - 2.0) / 0.3))
            pop_text(c, "MOVING?!", W / 2, 420, 150, tt - 2.0, col=GOLD, stroke=18)
        source_tag(c, "Photo: Ken Lund / CC BY-SA 2.0", tt - 0.3)


def s3(c, t, d):  # M "built a dam of rock across their side of the river. About 28,000 tons of it."
    if t < 4.4:
        river_map(c, t, dam=ease((t - 1.2) / 2.2), dry=ease((t - 3.2) / 1.0))
        pop_text(c, "A DAM OF ROCK", W / 2, 420, 120, t - 0.6, col=GOLD, stroke=16)
        if t > 1.0: label(c, "AMERICAN FALLS", 600, t - 1.0, x=840, size=34, bg=WHITE)
        if t > 0.3: label(c, "HORSESHOE FALLS", 600, t - 0.3, x=250, size=34, bg=WHITE)
    else:
        tt = t - 4.4; a = DRYBW.kb(tt / 3.0, 1.15, 1.25, (0.5, 0.55), (0.6, 0.6)); to_ctx(c, finish(a, tt, archival=True, vign=0.45))
        pop_text(c, counter(tt - 0.4, 0, 28000, 1.4), W / 2, 430, 170, tt - 0.4, col=GOLD, stroke=18)
        if tt > 0.9: text(c, "TONS OF ROCK", W / 2, 520, 70, col=WHITE, stroke=12, alpha=ease((tt - 0.9) / 0.3))
        source_tag(c, "Photo: NMGiovannucci / CC BY-SA 4.0 · Source: NiagaraFallsUSA", tt - 0.3, size=22)


def s4(c, t, d):  # F "And the falls just went dry?"
    a = DRY.kb(t / d, 1.15, 1.3, (0.3, 0.45), (0.32, 0.5)); to_ctx(c, finish(a, t, vign=0.4))
    pop_text(c, "DRY?!", W / 2, 440, 200, t - 0.9, col=GOLD, stroke=20)


def calendar(c, x, y, t, k):
    months = ["JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]
    i = min(5, int(eout(k) * 5.99))
    c.save(); c.translate(x, y)
    c.set_source_rgba(0, 0, 0, 0.4); rrect(c, -150 + 8, -150 + 10, 300, 300, 30); c.fill()
    c.set_source_rgb(1, 1, 1); rrect(c, -150, -150, 300, 300, 30); c.fill()
    c.set_source_rgb(*RED); rrect(c, -150, -150, 300, 90, 30); c.fill(); c.rectangle(-150, -100, 300, 40); c.fill()
    text(c, "1969", 0, -88, 48, col=WHITE)
    text(c, months[i], 0, 70, 110, col=NAVY)
    c.restore()


def s5(c, t, d):  # M "For five months. And at the bottom, they found a huge pile of fallen rock."
    if t < 2.4:
        bg(c, "dry", DRY, t); P1.dust(c, t, alpha=0.2)
        calendar(c, W / 2, 900, t, ease((t - 0.2) / 1.8))
        pop_text(c, "5 MONTHS", W / 2, 420, 150, t - 0.1, col=GOLD, stroke=18)
    else:
        tt = t - 2.4; a = DRYBW.kb(tt / (d - 2.4), 1.0, 1.25, (0.35, 0.62), (0.5, 0.7)); to_ctx(c, finish(a, tt, archival=True, vign=0.45))
        pop_text(c, "FALLEN ROCK", W / 2, 420, 140, tt - 1.2, col=GOLD, stroke=18)
        if tt > 1.4:
            c.set_source_rgba(*GOLD, ease((tt - 1.4) / 0.3)); c.set_line_width(8)
            c.arc(W / 2, 1000, 330, 0, 2 * math.pi * ease((tt - 1.4) / 0.6)); c.stroke()
        source_tag(c, "Source: USACE Buffalo District", tt - 0.4)


def s6(c, t, d):  # F "Where did all that rock come from?"
    a = DRY.kb(t / d, 1.3, 1.4, (0.62, 0.62), (0.66, 0.66)); to_ctx(c, finish(a, t, vign=0.45))
    pop_text(c, "WHERE FROM?", W / 2, 440, 150, t - 0.05, col=GOLD, stroke=18)


def s7(c, t, d):  # M "The cliff itself. The top layer is hard rock, but underneath, it's soft shale. Basically, packed mud."
    if t < 1.3:
        a = GORGE.kb(t / 1.3, 1.1, 1.2, (0.2, 0.55), (0.25, 0.55)); to_ctx(c, finish(a, t, vign=0.4))
        pop_text(c, "THE CLIFF", W / 2, 420, 170, t - 0.05, col=GOLD, stroke=18)
    else:
        tt = t - 1.3
        c.save(); cam(c, lerp(1.08, 1.0, eout(tt / 0.6)), 400, 1000); cliff_section(c, tt, labels=tt - 0.8); c.restore()
        if tt > 4.4: label(c, "= PACKED MUD", 1150, tt - 4.4, x=300, size=40, bg=GOLD)
        pop_text(c, "HARD ON SOFT", W / 2, 420, 130, tt - 0.4, col=GOLD, stroke=16)
        source_tag(c, "Source: NY State Museum (Lockport dolostone over Rochester Shale)", tt - 1.0, y=640, size=21)


def s8(c, t, d):  # M "Water eats the soft layer away, the hard edge hangs out, and then it snaps off."
    under = ease(t / 2.4); snap = max(0.0, min(1.0, (t - 3.6) / 1.0))
    sh = 8 * math.sin(t * 60) * (1 if 3.5 < t < 4.0 else 0)
    c.save(); c.translate(sh, 0); cliff_section(c, t + 3, under=under, snap=snap); c.restore()
    head = "EATS" if t < 1.9 else ("HANGS OUT" if t < 3.5 else "SNAPS!")
    pop_text(c, head, W / 2, 420, 170 if len(head) < 6 else 140, t - (0 if t < 1.9 else 1.9 if t < 3.5 else 3.5), col=RED if t >= 3.5 else GOLD, stroke=18)
    if 0.5 < t < 3.5: arrow(c, 980, 1200, 700 - 200 * under, 1150, col=hexc("6FB7FF"), alpha=0.9)
    text(c, "(simplified, not to scale)", W / 2, 1120, 28, col=WHITE, stroke=6, alpha=0.8)


def s9(c, t, d):  # F "So the waterfall breaks itself?"
    to_ctx(c, finish(CB.at(t).astype(np.float32), t, vign=0.3))
    pop_text(c, "BREAKS ITSELF?!", W / 2, 420, 120, t - 0.6, col=GOLD, stroke=18)
    source_tag(c, "Video: Alexis Lewis / CC BY 2.0", t - 0.2)


def s10(c, t, d):  # M "Again and again. 12,000 years ago, it started seven miles downstream."
    if t < 1.4:
        c.save(); cliff_section(c, t + 8, under=1.0, snap=min(1, t / 0.8)); c.restore()
        pop_text(c, "AGAIN & AGAIN", W / 2, 420, 130, t - 0.05, col=GOLD, stroke=16)
    else:
        tt = t - 1.4; k = ease((tt - 1.2) / (d - 1.6))
        retreat_map(c, tt, k)
        yrs = "12,000 YEARS AGO" if k < 0.95 else "TODAY"
        label(c, yrs, 440, 1.0, x=W / 2, size=44, bg=WHITE)
        source_tag(c, "Sources: NY State Museum · Britannica", tt - 0.4)


def s11(c, t, d):  # F "Seven miles? It's been walking backwards this whole time?"
    a = GORGE.kb(t / d, 1.0, 1.2, (0.45, 0.5), (0.35, 0.45)); to_ctx(c, finish(a, t, vign=0.4))
    pop_text(c, "7 MILES?!", W / 2, 420, 170, t - 0.05, col=GOLD, stroke=18)
    if t > 1.1:
        label(c, "WALKING BACKWARDS", 560, t - 1.1, size=50, bg=WHITE)
        arrow(c, 300, 1150, 300 + 420 * ease((t - 1.1) / 0.8) + 1, 1080, col=GOLD)
    source_tag(c, "Photo: Ken Lund / CC BY-SA 2.0", t - 0.3)


def s12(c, t, d):  # M "Yep. But today, it's barely moving."
    a = AER.kb(t / d, 1.0, 1.12, (0.6, 0.4), (0.6, 0.45)); to_ctx(c, finish(a, t, vign=0.35))
    pop_text(c, "BARELY MOVING", W / 2, 420, 130, t - 0.6, col=GOLD, stroke=16)
    if t > 1.0:
        text(c, "1800s: ~5 FT / YEAR", W / 2, 560, 52, col=WHITE, stroke=10, alpha=ease((t - 1.0) / 0.3))
    if t > 1.6:
        text(c, "NOW: ~1 FT / YEAR", W / 2, 640, 52, col=GOLD, stroke=10, alpha=ease((t - 1.6) / 0.3))
    source_tag(c, "Photo: Zwergelstern / CC BY-SA 3.0 · Sources: Britannica, NYSM", t - 0.3, size=22)


def s13(c, t, d):  # M "Because we take its water. By day, about half the river goes through tunnels to power stations."
    if t < 2.0:
        to_ctx(c, finish(CC.at(t).astype(np.float32), t, vign=0.3))
        pop_text(c, "WE TAKE ITS WATER", W / 2, 420, 110, t - 0.3, col=GOLD, stroke=16)
    else:
        tt = t - 2.0
        a = POWER.kb(tt / (d - 2.0), 1.0, 1.15, (0.55, 0.45), (0.6, 0.42)); to_ctx(c, finish(a, tt, vign=0.4))
        flow_bars(c, tt, day=ease((tt - 0.3) / 1.0))
        if tt > 1.6: label(c, "TUNNELS TO POWER", 1130, tt - 1.6, size=46, bg=WHITE)
        source_tag(c, "Photo: George Burns / NARA (PD) · Source: Smithsonian", tt - 0.3, size=22)


def s14(c, t, d):  # F "And at night?"
    to_ctx(c, finish(CC.at(2.0 + t).astype(np.float32), t, vign=0.35, night=ease(t / 0.4) * 0.9))
    pop_text(c, "AT NIGHT?", W / 2, 440, 160, t - 0.05, col=hexc("BFE0FF"), stroke=18)


def s15(c, t, d):  # M "Even more. So in a way, they still switch off Niagara Falls. A little, every single night."
    if t < 2.4:
        to_ctx(c, finish(CC.at(2.75 + t).astype(np.float32), t, vign=0.35, night=0.9))
        flow_bars(c, t, day=1.0, night=ease((t - 0.2) / 1.0))
        pop_text(c, "EVEN MORE", W / 2, 420, 150, t - 0.05, col=GOLD, stroke=18)
        source_tag(c, "Source: 1950 Niagara River Treaty (IJC)", t - 0.4)
    else:  # loop back to the hook image
        tt = t - 2.4
        hook_frame(c, 0.6 + tt * 0.3, z=lerp(1.08, 1.0, eout(tt / 0.6)))


def s16(c, t, d):
    bg(c, "aer", AER, t)
    end_card_logo(c, t, W / 2, 680, 290, LOGO)
    pop_text(c, "FOLLOW", W / 2, 1150, 130, t, col=GOLD, stroke=14)
    text(c, "a new wonder every day", W / 2, 1240, 54, col=WHITE, stroke=8, alpha=ease(t / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16]
assert len(SCENES) == len(meta)
NO_WIPE = (9, 14)


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
    if i > 0 and i not in NO_WIPE: wipe(c, t, col=GOLD if i % 2 else ORANGE)


def events():
    s = STARTS
    ev = [("boom", 0.0), ("pop", 0.3), ("thunk", 0.6), ("pop", 1.2), ("roar", 0.0), ("pop", 3.1)]
    ev += [("whoosh", x - 0.05) for x in s[1:] if x not in [s[i] for i in NO_WIPE]]
    ev += [("roar", s[1]), ("pop", s[1] + 0.5)] + [("thunk", s[1] + 1.0 + k * 0.45) for k in range(3)]
    ev += [("pop", s[2] + 0.2), ("pop", s[2] + 0.4), ("pop", s[2] + 1.6), ("pop", s[2] + 3.0), ("pop", s[2] + 5.0)]
    ev += [("pop", s[3] + 0.6)] + [("thunk", s[3] + 1.2 + k * 2.2 / 18) for k in range(0, 18, 2)] + [("boom", s[3] + 4.4)]
    ev += [("tick", s[3] + 4.8 + k * 0.1) for k in range(12)]
    ev += [("pop", s[4] + 0.9), ("pop", s[5] + 0.1)] + [("tick", s[5] + 0.2 + k * 0.36) for k in range(6)]
    ev += [("pop", s[5] + 3.6), ("pop", s[6]), ("pop", s[7]), ("pop", s[7] + 1.7), ("pop", s[7] + 2.1), ("pop", s[7] + 2.9), ("pop", s[7] + 5.7)]
    ev += [("roar", s[8]), ("pop", s[8]), ("pop", s[8] + 1.9), ("crack", s[8] + 3.6), ("boom", s[8] + 4.5)]
    ev += [("roar", s[9]), ("pop", s[9] + 0.6), ("crack", s[10]), ("thunk", s[10] + 0.7), ("pop", s[10] + 1.4)]
    ev += [("tick", s[10] + 2.6 + k * 0.25) for k in range(8)]
    ev += [("pop", s[11]), ("pop", s[11] + 1.1), ("pop", s[12] + 0.6), ("pop", s[12] + 1.0), ("pop", s[12] + 1.6)]
    ev += [("roar", s[13]), ("pop", s[13] + 0.3), ("thunk", s[13] + 2.3), ("pop", s[13] + 3.6)]
    ev += [("pop", s[14]), ("thunk", s[15] + 0.2), ("pop", s[15]), ("boom", s[15] + 2.4), ("thunk", s[15] + 3.0), ("pop", s[16])]
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
