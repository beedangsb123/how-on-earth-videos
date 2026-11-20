"""Video 002 — How Hoover Dam was built without taking 125 years to cool.
usage: python render_002.py still <t> <out.png>   |   python render_002.py full
Run inside the work dir that holds meta.json (from tts2.py)."""
import cairo, json, math, random, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *

meta = json.load(open("meta.json"))
PAD = 0.25
STARTS = []; t0 = 0
for m in meta: STARTS.append(t0); t0 += m["dur"] + PAD
DURS = [m["dur"] + PAD for m in meta]; DURS[-1] += 0.3
TOTAL = STARTS[-1] + DURS[-1]
T = make_textures(2)
P = Particles(70, 3); P2 = Particles(140, 9)
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))

CL, CR, BL, BR, CY, BY = (250, 640), (830, 640), (400, 1330), (680, 1330), 640, 1330


def cam(c, z, cx=W / 2, cy=H / 2, shake=0, t=0):
    c.translate(W / 2 + shake * math.sin(t * 90), H / 2 + shake * math.cos(t * 77)); c.scale(z, z); c.translate(-cx, -cy)


def dam_path(c):
    c.move_to(*CL); c.line_to(*CR); c.curve_to(790, 900, 700, 1150, *BR); c.line_to(*BL); c.curve_to(380, 1150, 290, 900, *CL); c.close_path()


def wall_path(c, side):
    def X(x): return x if side < 0 else W - x
    c.move_to(X(-400), 340); c.line_to(X(-400), 2400); c.line_to(X(430), 2400); c.line_to(X(415), 1480); c.line_to(X(BL[0]), BL[1])
    c.curve_to(X(380), 1150, X(290), 900, X(CL[0]), CL[1]); c.line_to(X(215), 570); c.line_to(X(160), 480); c.line_to(X(70), 440); c.line_to(X(-60), 360); c.close_path()


def canyon(c, t, heat=0.0, xray=0.0, joints=0.0):
    paint_tex(c, T["sky"], dy=-t * 4)
    # distant ridge
    c.move_to(-400, 700); c.line_to(-100, 520); c.line_to(200, 590); c.line_to(420, 500); c.line_to(640, 560); c.line_to(860, 470); c.line_to(1100, 560); c.line_to(1500, 520); c.line_to(1500, 760); c.line_to(-400, 760); c.close_path()
    fill_tex(c, T["rock"], 300, 200); c.move_to(-400, 700); c.line_to(-100, 520); c.line_to(200, 590); c.line_to(420, 500); c.line_to(640, 560); c.line_to(860, 470); c.line_to(1100, 560); c.line_to(1500, 520); c.line_to(1500, 760); c.line_to(-400, 760); c.close_path()
    c.set_source_rgba(0.55, 0.45, 0.75, 0.45); c.fill()
    # river + powerhouse below the dam
    c.rectangle(-400, BY, W + 800, 1200); fill_tex(c, T["water"], 0, -t * 140)
    c.rectangle(330, BY, 420, 120); fill_tex(c, T["concrete"], 50, 50)
    for i in range(7):
        c.set_source_rgba(0.2, 0.25, 0.35, 0.7); c.rectangle(350 + i * 57, BY + 40, 30, 46); c.fill()
    # dam
    dam_path(c); fill_tex(c, T["concrete"])
    g = cairo.LinearGradient(CL[0], 0, CR[0], 0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.35); g.add_color_stop_rgba(0.45, 1, 1, 1, 0.12); g.add_color_stop_rgba(1, 0, 0, 0, 0.4)
    dam_path(c); c.set_source(g); c.fill()
    if joints > 0:
        c.save(); dam_path(c); c.clip(); c.set_source_rgba(0.25, 0.22, 0.2, 0.5 * joints); c.set_line_width(2)
        for i in range(1, 12): x = 250 + i * 580 / 12; c.move_to(x, 600); c.line_to(x, 1340); c.stroke()
        for j in range(1, 24): y = 640 + j * 30; c.move_to(200, y); c.line_to(880, y); c.stroke()
        c.restore()
    if heat > 0:
        rg = cairo.RadialGradient(540, 1000, 40, 540, 980, 520)
        for p, h in ((0, 1.0), (0.5, 0.82), (1, 0.6)): rg.add_color_stop_rgba(p, *thermal_rgb(h * (0.6 + 0.4 * heat)), 0.88 * heat)
        dam_path(c); c.set_source(rg); c.fill()
        glow_stroke(c, lambda: dam_path(c), thermal_rgb(0.85), 6, alpha=0.7 * heat)
    if xray > 0:
        c.save(); dam_path(c); c.clip(); c.set_source_surface(T["xray"], 0, 0); c.paint_with_alpha(0.85 * xray)
        for j in range(22):
            y = 680 + j * 30
            c.move_to(220, y); c.line_to(860, y)
        c.set_source_rgba(0.6, 0.95, 1, 0.55 * xray); c.set_line_width(4); c.stroke()
        c.restore()
    # crest road
    c.set_source_rgba(0.95, 0.92, 0.85, 1); c.rectangle(CL[0] - 5, CY - 12, CR[0] - CL[0] + 10, 14); c.fill()
    for i in range(9):
        c.set_source_rgba(0.3, 0.3, 0.3, 1); c.rectangle(270 + i * 66, CY - 40, 5, 30); c.fill()
    # canyon walls
    for side in (-1, 1):
        wall_path(c, side); fill_tex(c, T["rock"], 0 if side < 0 else 500, 0)
        g = cairo.LinearGradient(0 if side < 0 else W, 0, 420 if side < 0 else W - 420, 0)
        g.add_color_stop_rgba(0, 0, 0, 0, 0.05); g.add_color_stop_rgba(1, 0, 0, 0, 0.4)
        wall_path(c, side); c.set_source(g); c.fill()
    if heat > 0.05:
        P.steam(c, t, 300, 780, 700, rise=520, alpha=0.32 * heat)


def screen_hook(c, t, l1, l2, y=420, size=118):
    pop_text(c, l1, W / 2, y, size, t + 0.4, col=WHITE, stroke=16)
    pop_text(c, l2, W / 2, y + size + 10, size, t + 0.4, col=GOLD, stroke=16)


# ---------------- scenes ----------------
def s0(c, t, d):
    c.save()
    if t < 1.25: cam(c, 1.0 + 0.06 * t, 540, 980)
    else: cam(c, 1.42 + 0.05 * (t - 1.25), 540, 1010)
    canyon(c, t, heat=0.92 + 0.08 * math.sin(t * 5))
    c.restore()
    screen_hook(c, t, "STILL COOLING", "TODAY?!")
    if t > 1.25: label(c, "IF POURED IN ONE PIECE", 1240, t - 1.25, size=42)


def s1(c, t, d):
    c.save()
    if t < 2.3:
        cam(c, 1.25 + 0.04 * t, 540, 990)
        canyon(c, t + 5, heat=0.15, xray=ease(t / 0.5))
        c.restore()
        pop_text(c, "?", W / 2, 1060, 300, t - 0.3, col=GOLD, stroke=18)
        label(c, "HIDDEN INSIDE", 330, t - 0.1, size=52)
    else:
        k = ease((t - 2.3) / 0.5)
        cam(c, 1.25, 540, lerp(990, 1560, k))
        canyon(c, t + 5, heat=0.0)
        c.restore()
        label(c, "FIRST: THE RIVER", 330, t - 2.4, size=52)


def gorge_x(y): return 540 + 110 * math.sin(y / 280.0)


def gorge_path(c, y0=-400, y1=2400, half=125):
    ys = range(int(y0), int(y1) + 1, 40)
    c.move_to(gorge_x(y0) - half, y0)
    for y in ys: c.line_to(gorge_x(y) - half, y)
    for y in reversed(list(ys)): c.line_to(gorge_x(y) + half, y)
    c.close_path()


TUN = [(-1, 175), (-1, 235), (1, 175), (1, 235)]


def tunnel_pts(side, off):
    pts = []
    for i in range(41):
        u = i / 40; y = lerp(520, 1500, u)
        bulge = math.sin(u * math.pi) * 40
        pts.append((gorge_x(y) + side * (off + bulge), y))
    pts = [(gorge_x(470) + side * 60, 470)] + pts + [(gorge_x(1550) + side * 60, 1550)]
    return pts


def poly(c, pts, frac=1.0):
    n = max(2, int(len(pts) * frac)); c.move_to(*pts[0])
    for p in pts[1:n]: c.line_to(*p)
    return pts[n - 1]


def s2(c, t, d):
    c.save()
    if t < 3.0: z, cx, cy = 1.0 + 0.03 * t, 540, 1000
    elif t < 5.0: z, cx, cy = 1.35, 540, 760
    else: z, cx, cy = 1.05 + 0.02 * (t - 5), 540, 1000
    cam(c, z, cx, cy)
    paint_tex(c, T["rock"], 0, 0)
    c.set_source_rgba(0.95, 0.75, 0.5, 0.12); c.rectangle(-400, -400, W + 800, H + 800); c.fill()
    gorge_path(c, half=150); c.set_source_rgba(0.25, 0.13, 0.08, 0.6); c.fill()
    gorge_path(c); fill_tex(c, T["water"], 0, -t * 160)
    dry = ease((t - 5.2) / 1.4)
    if dry > 0:
        c.save(); c.rectangle(-400, 720, W + 800, 560); c.clip(); gorge_path(c); fill_tex(c, T["sand"], alpha=dry); c.restore()
        for yb in (720, 1280):
            c.set_source_rgba(0.85, 0.8, 0.7, dry); c.rectangle(gorge_x(yb) - 140, yb - 14, 280, 28); c.fill()
    prog = ease((t - 0.5) / 2.6)
    for side, off in TUN:
        pts = tunnel_pts(side, off)
        if prog > 0:
            head = poly(c, pts, prog); c.set_source_rgba(0.12, 0.08, 0.06, 1); c.set_line_width(30); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
            glow_stroke(c, lambda: poly(c, pts, prog), GOLD, 5, alpha=0.9, layers=3)
            if prog < 1: P.sparks(c, t, *head)
        if t > 4.8:
            for k in range(14):
                u = ((t - 4.8) * 0.45 + k / 14) % 1.0
                i = int(u * (len(pts) - 1)); x, y = pts[i]
                c.set_source_rgba(0.75, 0.95, 1, 0.9); c.arc(x, y, 8, 0, 2 * math.pi); c.fill()
    # dam site marker
    c.set_dash([18, 12]); c.set_source_rgba(1, 1, 1, 0.8); c.set_line_width(5)
    c.move_to(gorge_x(1000) - 260, 1000); c.line_to(gorge_x(1000) + 260, 1000); c.stroke(); c.set_dash([])
    c.restore()
    pop_text(c, "4 TUNNELS", W / 2, 420, 120, t - 0.6, col=GOLD, stroke=16)
    if t > 2.9: label(c, "56 FT (17 m) WIDE EACH", 1180, t - 2.9, size=44)
    if t > 5.3: label(c, "RIVER SENT AROUND", 1180, t - 5.3, size=44, bg=hexc("6CC4CF"))
    label(c, "DAM SITE", 520, t - 0.3, size=34, bg=WHITE)


def s3(c, t, d):
    if t < 6.3:
        c.save(); cam(c, 1.05 + 0.02 * t, 540, 1000)
        canyon(c, t + 10, heat=ease(t / 2.5) * 0.85)
        if t > 3.7:
            k = ease((t - 3.7) / 1.8); x = 150
            c.set_source_rgba(*GOLD, 1); c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.move_to(x, BY); c.line_to(x, lerp(BY, CY, k)); c.stroke()
            c.move_to(x - 40, BY); c.line_to(x + 40, BY); c.stroke()
            ty = lerp(BY, CY, k); c.move_to(x - 30, ty + 34); c.line_to(x, ty); c.line_to(x + 30, ty + 34); c.stroke()
        c.restore()
        if t < 3.7: pop_text(c, "CONCRETE GETS HOT", W / 2, 420, 100, t - 1.3, col=GOLD, stroke=16)
        else:
            k = ease((t - 3.7) / 1.8)
            pop_text(c, f"{int(round(726 * k))} FT TALL", W / 2, 420, 120, t - 3.7, col=GOLD, stroke=16)
            text(c, "221 m", W / 2, 520, 56, col=WHITE, stroke=10, alpha=ease((t - 5.4) / 0.3))
    else:
        tt = t - 6.3
        c.save(); cam(c, 1.0 + 0.03 * tt, 540, 1000)
        paint_tex(c, T["rock"], 200, 100)
        c.set_source_rgba(0.1, 0.05, 0.02, 0.25); c.rectangle(-400, -400, W + 800, H + 800); c.fill()
        # lake (upstream, left) and river (downstream, right)
        c.rectangle(-400, 560, 520, 900); fill_tex(c, T["water"], 0, -tt * 30)
        c.rectangle(860, 1320, 800, 140); fill_tex(c, T["water"], 0, tt * 30)
        # cross-section profile: crest 45 ft, base 660 ft
        sc = 1.05; bx0 = 540 - 330 * sc; bx1 = 540 + 330 * sc; topx0 = bx0 + 40; topx1 = topx0 + 45 * sc
        def prof():
            c.move_to(topx0, 500); c.line_to(topx1, 500); c.curve_to(topx1 + 60, 900, bx1 - 200, 1300, bx1, 1460); c.line_to(bx0, 1460); c.close_path()
        prof(); fill_tex(c, T["concrete"])
        rg = cairo.LinearGradient(bx0, 0, bx1, 0); rg.add_color_stop_rgba(0, *thermal_rgb(0.95), 0.75); rg.add_color_stop_rgba(1, *thermal_rgb(0.7), 0.6)
        prof(); c.set_source(rg); c.fill()
        glow_stroke(c, prof, thermal_rgb(0.9), 5, alpha=0.8)
        P.steam(c, tt + 3, bx0 + 100, bx1 - 50, 1100, rise=500, alpha=0.25)
        k = ease((tt - 0.3) / 1.6)
        c.set_source_rgba(*GOLD, 1); c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND)
        y = 1540; c.move_to(540 - 330 * sc * k, y); c.line_to(540 + 330 * sc * k, y); c.stroke()
        for s in (-1, 1):
            xe = 540 + s * 330 * sc * k; c.move_to(xe - s * 30, y - 30); c.line_to(xe, y); c.line_to(xe - s * 30, y + 30); c.stroke()
        c.restore()
        pop_text(c, f"{int(round(660 * k))} FT THICK", W / 2, 420, 116, tt, col=GOLD, stroke=16)
        text(c, "201 m  ·  at the base", W / 2, 520, 52, col=WHITE, stroke=10, alpha=ease((tt - 1.8) / 0.3))


CRACKS = []
_r = random.Random(5)
for i in range(9):
    x, y = _r.uniform(330, 750), _r.uniform(700, 1150); pts = [(x, y)]
    for j in range(12):
        x += _r.uniform(-28, 28); y += _r.uniform(10, 40); pts.append((x, y))
    CRACKS.append(pts)


def s4(c, t, d):
    shake = 9 if 4.1 < t < 4.6 else 0
    c.save(); cam(c, 1.1 + 0.06 * t, 540, 1000, shake, t)
    canyon(c, t + 20, heat=1.0 - 0.25 * ease((t - 1) / 3))
    ck = ease((t - 4.1) / 0.8)
    if ck > 0:
        c.save(); dam_path(c); c.clip()
        for pts in CRACKS:
            glow_stroke(c, lambda: poly(c, pts, ck), (1, 0.95, 0.7), 4, alpha=1, layers=3)
            poly(c, pts, ck); c.set_source_rgba(0.1, 0.03, 0.02, 1); c.set_line_width(5); c.stroke()
        c.restore()
    c.restore()
    k = ease((t - 0.9) / 2.3)
    pop_text(c, f"{int(round(125 * k))} YEARS", W / 2, 430, 140, t - 0.8, col=GOLD, stroke=18)
    text(c, "to cool down", W / 2, 530, 60, col=WHITE, stroke=10, alpha=ease((t - 1.0) / 0.3))
    if t > 4.1: label(c, "AND IT CRACKS", 1200, t - 4.1, size=50, bg=hexc("E5484D"), fg=WHITE)


COL_OFF = [random.Random(11 + j).uniform(0, 1.6) for j in range(12)]


def s5(c, t, d):
    if t < 5.4:
        c.save(); cam(c, 1.12 + 0.03 * t, 540, 1000)
        canyon(c, t + 30, heat=0)
        # cover dam with rising columns
        c.save(); dam_path(c); c.clip()
        c.set_source_surface(T["rock"], 0, 0); c.paint(); c.set_source_rgba(0.1, 0.05, 0.03, 0.45); c.paint()
        cw = 580 / 12
        for j in range(12):
            p = eout((t - 0.2 - COL_OFF[j]) / 3.4); hgt = 690 * p
            x = 250 + j * cw
            c.rectangle(x + 2, BY - hgt, cw - 4, hgt); fill_tex(c, T["concrete"], j * 37, 0)
            shade = 0.12 if j % 2 else 0.0
            c.set_source_rgba(0, 0, 0, shade); c.rectangle(x + 2, BY - hgt, cw - 4, hgt); c.fill()
            c.set_source_rgba(0.3, 0.27, 0.24, 0.6); c.set_line_width(2)
            yy = BY
            while yy > BY - hgt: c.move_to(x + 2, yy); c.line_to(x + cw - 2, yy); c.stroke(); yy -= 15
            if 0 < p < 1:
                c.set_source_rgba(*GOLD, 0.9); c.rectangle(x + 2, BY - hgt - 6, cw - 4, 8); c.fill()
        c.restore(); c.restore()
        n = int(round(215 * ease((t - 0.4) / 3.0)))
        pop_text(c, f"{n} COLUMNS", W / 2, 430, 130, t - 0.4, col=GOLD, stroke=16)
        if t > 3.3: label(c, "UP TO 60 FT SQUARE", 1200, t - 3.3, size=46)
    else:
        tt = t - 5.4
        c.save(); cam(c, 1.0 + 0.05 * tt, 540, 1000)
        paint_tex(c, T["xray"], 0, 0)
        c.set_source_rgba(1, 1, 1, 0.12); c.set_line_width(2)
        for i in range(-10, 40): c.move_to(i * 60, -400); c.line_to(i * 60, 2400); c.move_to(-400, i * 60); c.line_to(1500, i * 60)
        c.stroke()
        # one column, lifts stacking (each lift 5 ft)
        n = int(2 + tt * 5)
        for i in range(n):
            y = 1500 - i * 110; drop = 0
            if i == n - 1: drop = -200 * (1 - eout((tt * 5) % 1))
            c.rectangle(340, y - 100 + drop, 400, 100); fill_tex(c, T["concrete"], i * 50, 0)
            c.set_source_rgba(0.2, 0.2, 0.2, 0.7); c.set_line_width(3); c.rectangle(340, y - 100 + drop, 400, 100); c.stroke()
        yb = 1500 - (n - 2) * 110
        c.set_source_rgba(*GOLD, 1); c.set_line_width(8)
        c.move_to(780, yb); c.line_to(820, yb); c.line_to(820, yb - 100); c.line_to(780, yb - 100); c.stroke()
        text(c, "5 FT", 840, yb - 30, 64, col=GOLD, align="left", stroke=10)
        c.restore()
        pop_text(c, "5 FT AT A TIME", W / 2, 430, 120, tt, col=GOLD, stroke=16)


BX0, BY0, BS, GAP = 60, 520, 300, 20
BLOCKS = [(BX0 + i * (BS + GAP), BY0 + j * (BS + GAP)) for j in range(4) for i in range(3)]


def serp(x, y):
    pts = []; m = 34
    for k in range(5):
        yy = y + m + k * (BS - 2 * m) / 4
        a, b = (x + m, x + BS - m) if k % 2 == 0 else (x + BS - m, x + m)
        pts += [(a, yy), (b, yy)]
    return pts


def blocks(c, t, heat, pipe_prog, flow=None, grout=0.0, merge=0.0, pipe_col=(0.75, 0.78, 0.82)):
    paint_tex(c, T["xray"], 0, 0)
    c.set_source_rgba(1, 1, 1, 0.1); c.set_line_width(2)
    for i in range(-10, 40): c.move_to(i * 60, -400); c.line_to(i * 60, 2400); c.move_to(-400, i * 60); c.line_to(1500, i * 60)
    c.stroke()
    if grout > 0:  # grout rising in the gaps
        top = lerp(BY0 + 4 * (BS + GAP), BY0 - GAP, grout)
        c.rectangle(BX0 - GAP, top, 3 * (BS + GAP) + GAP, BY0 + 4 * (BS + GAP) - top); c.set_source_rgba(*GOLD, 1); c.fill()
    for (x, y) in BLOCKS:
        c.rectangle(x, y, BS, BS); fill_tex(c, T["concrete"], x, y)
        c.rectangle(x, y, BS, BS); c.set_source_rgba(*thermal_rgb(heat), 0.72 * (1 - merge)); c.fill()
        pts = serp(x, y)
        if pipe_prog > 0:
            poly(c, pts, pipe_prog); c.set_source_rgba(*pipe_col, 1); c.set_line_width(11); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
            poly(c, pts, pipe_prog); c.set_source_rgba(1, 1, 1, 0.5); c.set_line_width(3); c.stroke()
        if flow:
            col, spd = flow
            L = len(pts) - 1
            for k in range(10):
                u = (t * spd + k / 10) % 1.0; f = u * L; i = int(f); r = f - i
                px = lerp(pts[i][0], pts[i + 1][0], r); py = lerp(pts[i][1], pts[i + 1][1], r)
                c.set_source_rgba(*col, 0.95); c.arc(px, py, 8, 0, 2 * math.pi); c.fill()
        if heat > 0.3:  # heat arrows escaping
            for k in range(2):
                u = (t * 0.8 + k * 0.5 + x * 0.001) % 1.0
                ax = x + BS * (0.3 + 0.4 * k); ay = y + BS * 0.8 - u * BS * 0.7
                c.set_source_rgba(*thermal_rgb(0.9), (heat - 0.3) * math.sin(u * math.pi)); c.set_line_width(6)
                c.move_to(ax - 16, ay + 16); c.line_to(ax, ay); c.line_to(ax + 16, ay + 16); c.stroke()
    if merge > 0:
        c.rectangle(BX0 - GAP / 2, BY0 - GAP / 2, 3 * (BS + GAP), 4 * (BS + GAP)); fill_tex(c, T["concrete"], alpha=merge)


def s6(c, t, d):
    heat = lerp(0.95, 0.12, ease((t - 3.6) / 5.0))
    flow = None
    if t > 3.2: flow = ((0.45, 0.85, 0.85), 0.25)
    if t > 5.3: flow = ((0.85, 0.97, 1.0), 0.45)
    c.save()
    if t < 5.3: cam(c, 1.0 + 0.025 * t, 540, 1000)
    else: cam(c, 1.55 + 0.03 * (t - 5.3), 380, 840)
    blocks(c, t, heat, ease((t - 0.7) / 1.6), flow)
    c.restore()
    if t < 3.2: pop_text(c, "COOLING PIPES", W / 2, 420, 120, t - 0.9, col=GOLD, stroke=16)
    elif t < 5.3: pop_text(c, "RIVER WATER", W / 2, 420, 120, t - 3.2, col=hexc("6CC4CF"), stroke=16)
    else: pop_text(c, "CHILLED WATER", W / 2, 420, 120, t - 5.3, col=hexc("BFE8FF"), stroke=16)
    if t > 7.3: label(c, "HEAT PULLED OUT", 1200, t - 7.3, size=48, bg=hexc("BFE8FF"))
    if t < 3.0: label(c, "INSIDE EVERY BLOCK", 520, t - 0.2, size=40, bg=WHITE)


def s7(c, t, d):
    merge = ease((t - 4.2) / 0.8)
    c.save(); cam(c, lerp(1.25, 1.0, ease(t / 4)), 540, 1000)
    blocks(c, t, 0.1, 1.0, None, grout=ease((t - 0.6) / 3.2), merge=merge, pipe_col=lerpc((0.75, 0.78, 0.82), GOLD, ease((t - 0.3) / 0.8)))
    c.restore()
    if merge > 0 and t < 5.0:
        c.set_source_rgba(1, 1, 0.9, 0.6 * (1 - ease((t - 4.2) / 0.8))); c.paint()
    if t < 4.2: pop_text(c, "GROUT IN", W / 2, 420, 130, t - 0.4, col=GOLD, stroke=16)
    else: pop_text(c, "ONE SOLID WALL", W / 2, 420, 120, t - 4.2, col=GOLD, stroke=16)


ROAD = [(lerp(150, 920, i / 60), 900 + 120 * math.sin(i / 60 * 5.5) - 140 * (i / 60)) for i in range(61)]


def s8(c, t, d):
    if t < 3.2:
        c.save(); cam(c, 1.2 + 0.05 * t, 540, 990)
        canyon(c, t + 40, xray=1.0)
        c.save(); dam_path(c); c.clip()
        def net():
            for j in range(22):
                y = 680 + j * 30; c.move_to(220, y); c.line_to(860, y)
        glow_stroke(c, net, GOLD, 4, alpha=0.6 + 0.4 * math.sin(t * 6))
        c.restore(); c.restore()
        pop_text(c, "HUNDREDS", W / 2, 400, 140, t - 0.2, col=GOLD, stroke=16)
        pop_text(c, "OF MILES OF PIPE", W / 2, 510, 84, t - 0.5, col=WHITE, stroke=14)
    else:
        tt = t - 3.2; k = ease((tt - 0.3) / 3.0)
        hx, hy = poly_head(k)
        z = lerp(1.5, 1.0, ease((tt - 2.6) / 1.4))
        cx = lerp(hx, 540, ease((tt - 2.6) / 1.4)); cy = lerp(hy, 900, ease((tt - 2.6) / 1.4))
        c.save(); cam(c, z, cx, cy)
        paint_tex(c, T["terrain"], 0, 0)
        for mx, my, ms in ((330, 760, 160), (420, 820, 120), (560, 700, 130), (250, 1060, 110), (700, 1080, 100)):
            c.move_to(mx - ms, my + ms * 0.6); c.line_to(mx, my - ms * 0.6); c.line_to(mx + ms, my + ms * 0.6); c.close_path(); fill_tex(c, T["rock"], mx, my)
            c.move_to(mx - ms * 0.25, my - ms * 0.3); c.line_to(mx, my - ms * 0.6); c.line_to(mx + ms * 0.25, my - ms * 0.3); c.close_path(); c.set_source_rgba(1, 1, 1, 0.85); c.fill()
        poly(c, ROAD, k); c.set_source_rgba(0.2, 0.2, 0.2, 0.6); c.set_line_width(40); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
        poly(c, ROAD, k); tex(c, T["concrete"]); c.set_line_width(30); c.stroke()
        c.set_dash([20, 16]); poly(c, ROAD, k); c.set_source_rgba(*GOLD, 0.9); c.set_line_width(4); c.stroke(); c.set_dash([])
        for (px, py) in (ROAD[0], ROAD[-1]):
            c.set_source_rgba(0.9, 0.2, 0.25, 1); c.arc(px, py - 40, 22, 0, 2 * math.pi); c.fill()
            c.move_to(px - 18, py - 30); c.line_to(px, py); c.line_to(px + 18, py - 30); c.fill()
            c.set_source_rgba(1, 1, 1, 1); c.arc(px, py - 40, 9, 0, 2 * math.pi); c.fill()
        c.restore()
        # pin labels in screen space follow the world -> simpler: fixed placement once zoomed out
        a = ease((tt - 2.9) / 0.4)
        if a > 0:
            label(c, "SAN FRANCISCO", 1120, tt - 2.9, x=330, size=38, bg=WHITE)
            label(c, "NEW YORK", 560, tt - 3.1, x=760, size=38, bg=WHITE)
        pop_text(c, "ONE CONCRETE ROAD", W / 2, 420, 100, tt - 0.1, col=GOLD, stroke=16)
        text(c, "16 ft wide · 8 in thick", W / 2, 500, 50, col=WHITE, stroke=10, alpha=ease((tt - 0.8) / 0.3))


def poly_head(k):
    n = max(2, int(len(ROAD) * k)); return ROAD[n - 1]


def s9(c, t, d):
    heat = 0.9 * ease((t - (d - 1.4)) / 1.2)
    c.save(); cam(c, 1.0 + 0.05 * t, 540, 980)
    canyon(c, t + 50, heat=heat, joints=1.0 - heat)
    c.restore()
    pop_text(c, "NOT ONE PIECE", W / 2, 420, 120, t - 0.2, col=GOLD, stroke=16)
    if t > 1.8: label(c, "215 COLUMNS + PIPES", 1220, t - 1.8, size=44)


def s10(c, t, d):
    c.save(); cam(c, 1.05 + 0.03 * t, 540, 900)
    canyon(c, t + 60, heat=0.0, joints=0.6)
    c.restore()
    c.set_source_rgba(*NAVY, 0.45); c.paint()
    k = back(t / 0.4)
    c.save(); s = 0.56 * k; c.translate(W / 2 - 540 * s, 360); c.scale(s, s)
    c.arc(540, 540, 540, 0, 2 * math.pi); c.clip(); c.set_source_surface(LOGO, 0, 0); c.paint(); c.restore()
    c.set_source_rgba(*GOLD, 1); c.set_line_width(10); c.arc(W / 2, 360 + 540 * 0.56 * k, 540 * 0.56 * k, 0, 2 * math.pi); c.stroke()
    pop_text(c, "FOLLOW", W / 2, 1150, 130, t, col=GOLD, stroke=14)
    text(c, "a new wonder every day", W / 2, 1240, 54, col=WHITE, stroke=8, alpha=ease(t / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]


def frame(c, gt):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*NAVY); c.paint()
    c.save()
    if i > 0 and t < 0.3:  # punch-in on each cut
        z = 1 + 0.08 * (1 - eout(t / 0.3)); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[i](c, t, d)
    c.restore()
    if i < len(SCENES) - 1:
        badge(c)
        captions(c, meta[i]["cap"], meta[i]["dur"], t)
    if i > 0: wipe(c, t, col=GOLD if i % 2 else ORANGE)


def events():
    ev = [("boom", 0.0)]
    for i, s in enumerate(STARTS[1:], 1): ev.append(("whoosh", s - 0.05))
    s = STARTS
    ev += [("tick", s[3] + 3.7 + k * 0.12) for k in range(15)]
    ev += [("tick", s[3] + 6.6 + k * 0.12) for k in range(13)]
    ev += [("tick", s[4] + 0.9 + k * 0.1) for k in range(23)]
    ev += [("crack", s[4] + 4.1), ("boom", s[4] + 4.1)]
    ev += [("thunk", s[5] + 0.4 + k * 0.28) for k in range(12)]
    ev += [("thunk", s[5] + 5.4 + k * 0.2) for k in range(10)]
    ev += [("drill", s[2] + 0.5), ("boom", s[7] + 4.2), ("boom", s[1] + 0.3), ("pop", s[9] + 0.2), ("pop", s[10])]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "still":
        frame(c, float(sys.argv[2])); surf.write_to_png(sys.argv[3])
    else:
        json.dump({"total": TOTAL, "events": events()}, open("events.json", "w"))
        n = int(math.ceil(TOTAL * FPS))
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
        for f in range(n):
            frame(c, f / FPS); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", n, "total", TOTAL)
