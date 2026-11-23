"""Video 005 v2 — Niagara Falls: "In 1969, engineers switched off Niagara Falls" (natural wonder, format "timeline"
anchored on a real event). Remade 2026-11-23 after Bidhan's review ("the animations don't look great and look the
same as the last one"; new voices Brian = male, answers / Laura = female, excited + curious).
NEW LOOK v3 (different from 001-004):
 - real satellite imagery instead of drawn maps: one continuous camera move NASA globe -> ASTER regional image ->
   ISS astronaut photo, with glowing neon annotations (neon_path, ring_marker) drawn ON the real ground
 - cliff cross-section built from real photo textures (1969 rock face, gorge water) as a 3-D block diagram with
   lighting, instead of flat cartoon fills
 - cyan "ribbon" headlines that slide in (engine.ribbon) instead of gold pop text; cyan caption keywords
 - whip-pan motion-blur transitions (engine.whip) instead of the gold diagonal wipe
Real media: see credits_005.txt. usage (work dir with meta.json, media/, media2/, clipA..C):
  python render_005.py stills <prefix> t1 t2 ...   |   python render_005.py full"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish
from clips import Clip
import globe as GL

CYAN = (0.25, 0.82, 1.0); RED = (0.95, 0.25, 0.25); GREEN = (0.25, 0.8, 0.45); SAND = (0.93, 0.78, 0.5)
engine.CAP_ACCENT = CYAN


def finish(a, t, **kw):  # every photo/clip frame gets edge haze (edge-band check)
    return _finish(haze(a, t), t, **kw)


meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]; DURS[-1] += 0.4
TOTAL = STARTS[-1] + DURS[-1]
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix): return sorted(glob.glob(f"media*/{prefix}*"))[0]


DRY = Photo(M("Dewatered_American_Falls"), maxz=1.35)             # James St. John, CC BY 2.0 (1969 colour)
DRYBW = Photo(M("1969_Drained"), archival=True, maxz=1.3)          # NMGiovannucci, CC BY-SA 4.0 (1969 b/w)
AMER = Photo(M("American_Falls__Niagara"), maxz=1.3)                # Ken Lund, CC BY-SA 2.0
GORGE = Photo(M("Niagara_Gorge__Niagara_Falls__Ontario__29985358625"), maxz=1.3)   # Ken Lund, CC BY-SA 2.0
GORGE2 = Photo(M("Niagara_Gorge__Niagara_Falls__Ontario__29871779602"), maxz=1.3)  # Ken Lund, CC BY-SA 2.0
AER = Photo(M("Niagara_Falls_Horseshoe_aerial"), maxz=1.3)          # Zwergelstern, CC BY-SA 3.0
POWER = Photo(M("THE_ROBERT_MOSES"), maxz=1.3)                      # George Burns / NARA, PD
CA, CB, CC = Clip("clipA"), Clip("clipB"), Clip("clipC")
GLOBE = GL.Globe()
NIAG = (43.08, -79.07)
P1, P2, P3 = Particles(110, 1), Particles(80, 2), Particles(120, 3)


class Sat:
    """satellite / astronaut image with an exact image->screen mapping so annotations sit on the real ground"""
    def __init__(self, path, up=2):
        im = Image.open(path).convert("RGB")
        self.im = im.resize((im.width * up, im.height * up), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
        self.up = up

    def view(self, cx, cy, s):
        """centre (cx, cy) in ORIGINAL image px, s = screen px per original px -> (HxWx3 float, mapper)"""
        u = self.up; hw, hh = W / 2 / s * u, H / 2 / s * u
        box = (cx * u - hw, cy * u - hh, cx * u + hw, cy * u + hh)
        if min(box[:2]) < 0 or box[2] > self.im.width or box[3] > self.im.height:  # out of range: crop pads, then scale
            a = np.asarray(self.im.crop(tuple(int(v) for v in box)).resize((W, H), Image.BILINEAR), np.float32)
        else: a = np.asarray(self.im.resize((W, H), Image.BILINEAR, box=box), np.float32)
        return a, (lambda x, y: ((x - cx) * s + W / 2, (y - cy) * s + H / 2))


ASTER = Sat(M("Niagara_Falls__ASTER_"))       # NASA/METI/AIST/Japan Space Systems, US/Japan ASTER Science Team, PD
ISS = Sat(M("Niagara_Falls_from_space"))      # NASA astronaut photo, PD
GORGE_PATH = [(579, 745), (582, 730), (595, 715), (591, 700), (595, 685), (597, 670), (602, 655), (604, 640), (598, 625),
              (578, 610), (558, 595), (573, 580), (585, 565), (596, 550), (599, 535), (611, 520), (614, 505), (621, 490),
              (605, 475), (590, 458)]   # traced on the ASTER image: falls (bottom) -> Lewiston / escarpment (top)

# photo textures for the 3-D cliff block (real rock and water instead of flat fills)
def _tex_from(photo, f, z, tint=None, dark=1.0, streak=False):
    a = photo.kb(0, z, z, f, f)
    if tint is not None: a = a.mean(2, keepdims=True) * np.array(tint)
    a = a * dark
    if streak:  # horizontal bedding lines for shale
        yy = np.arange(H)[:, None, None]; a = a * (0.85 + 0.15 * np.sin(yy / 3.1 + np.sin(yy / 41) * 3))
    return to_surface(np.clip(a / 255, 0, 1))


CAP_TEX = _tex_from(DRY, (0.35, 0.35), 1.3, tint=(1.02, 1.0, 0.95), dark=1.05)
SHALE_TEX = _tex_from(DRYBW, (0.5, 0.75), 1.3, tint=(0.78, 0.62, 0.55), dark=0.75, streak=True)
TX = make_textures(5)
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


def counter(t, v0, v1, dur, fmt="{:,}"):
    return fmt.format(int(round(lerp(v0, v1, eout(t / dur))))) if t > 0 else fmt.format(v0)


def tag(c, s, x, y, t, col=CYAN, size=38, side=1):
    """leader-line callout: dot on the spot, line out, text plate (for annotating real imagery)"""
    if t <= 0: return
    k = eout(t / 0.35); lx = x + side * 140 * k; ly = y - 90 * k
    c.save(); c.set_source_rgba(*col, 1); c.set_line_width(5); c.move_to(x, y); c.line_to(lx, ly); c.stroke()
    c.arc(x, y, 10, 0, 2 * math.pi); c.fill()
    w = text_w(c, s, size) + 36; bx = lx if side > 0 else lx - w
    c.set_source_rgba(0.03, 0.05, 0.12, 0.85 * k); c.rectangle(bx, ly - size * 0.9, w, size * 1.35); c.fill()
    c.set_source_rgba(*col, k); c.rectangle(bx, ly - size * 0.9, 8 if side > 0 else w, size * 1.35) if side > 0 else None
    if side > 0: c.fill()
    text(c, s, bx + 18 + (6 if side > 0 else 0), ly + size * 0.15, size, col=WHITE, align="left", alpha=k)
    c.restore()


def scan(c, t, col=CYAN, a=0.10):
    """thin moving scan-lines + corner brackets: the 'satellite feed' look"""
    for j in range(24):
        y = (j * 84 + t * 220) % (H + 84) - 42; c.move_to(0, y); c.line_to(W, y)
    c.set_source_rgba(*col, a); c.set_line_width(2); c.stroke()
    c.set_source_rgba(*col, 0.8); c.set_line_width(6)
    for x, y, dx, dy in ((60, 260, 1, 1), (W - 60, 260, -1, 1), (60, 1260, 1, -1), (W - 60, 1260, -1, -1)):
        c.move_to(x, y + dy * 70); c.line_to(x, y); c.line_to(x + dx * 70, y); c.stroke()


# ---------------- drawn explainers ----------------
def switch_icon(c, x, y, s, off_k):
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


def cliff_block(c, t, under=0.0, snap=0.0, labels=-1.0, flow=1.0):
    """3-D block diagram of the falls edge from real photo textures: hard caprock (1969 rock face) over bedded soft
    shale; the plunge pool eats the shale back (under), the overhang breaks off (snap)"""
    bg(c, "gorge", GORGE2, t, (0.5, 0.45), dim=0.55)
    top, d1, d2 = 820, 1000, 1360; cx = 650; dz = 110            # dz = depth offset of the top face (perspective)
    notch = 230 * under
    # top face: the river running over the caprock (real water texture), seen in perspective
    c.save(); c.move_to(-60, top); c.line_to(cx, top); c.line_to(cx + dz, top - dz); c.line_to(-60 + dz, top - dz); c.close_path()
    fill_tex(c, TX["water"], dx=t * 140, dy=0); c.restore()
    c.save(); c.move_to(-60, top); c.line_to(cx, top); c.line_to(cx + dz, top - dz); c.line_to(-60 + dz, top - dz); c.close_path()
    g = cairo.LinearGradient(0, top - dz, 0, top); g.add_color_stop_rgba(0, 1, 1, 1, 0.25); g.add_color_stop_rgba(1, 0, 0.1, 0.2, 0.15)
    c.set_source(g); c.fill(); c.restore()
    # caprock front face
    c.save(); c.rectangle(-60, top, cx + 60, d1 - top); c.clip(); tex(c, CAP_TEX, dx=-80, dy=-300); c.paint()
    g = cairo.LinearGradient(0, top, 0, d1); g.add_color_stop_rgba(0, 1, 1, 1, 0.18); g.add_color_stop_rgba(1, 0, 0, 0, 0.25)
    c.set_source(g); c.paint(); c.restore()
    # caprock side face (right, in perspective)
    if snap < 0.01:
        c.save(); c.move_to(cx, top); c.line_to(cx + dz, top - dz); c.line_to(cx + dz, d1 - dz); c.line_to(cx, d1); c.close_path()
        c.clip(); tex(c, CAP_TEX, dx=200); c.paint(); c.set_source_rgba(0, 0, 0, 0.35); c.paint(); c.restore()
    # shale with the undercut notch
    c.save(); c.move_to(-60, d1); c.line_to(cx - notch * 0.35, d1)
    c.curve_to(cx - notch, d1 + 80, cx - notch, d2 - 60, cx - notch * 0.2, d2); c.line_to(-60, d2); c.close_path()
    c.clip(); tex(c, SHALE_TEX, dy=-200); c.paint()
    g = cairo.LinearGradient(cx - 300, 0, cx, 0); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.35)
    c.set_source(g); c.paint(); c.restore()
    # lower rock to the frame bottom + plunge pool
    c.save(); c.rectangle(-60, d2, W + 120, H - d2 + 60); c.clip(); tex(c, CAP_TEX, dx=300, dy=-d2); c.paint()
    c.set_source_rgba(0.2, 0.14, 0.1, 0.55); c.paint()   # lit rubble at the gorge floor (textured to the frame edge)
    for k in range(40):
        x = (k * 131) % (W + 100) - 50; y = d2 + 120 + (k * 67) % (H - d2 - 100)
        c.set_source_rgba(1, 0.95, 0.85, 0.12); c.arc(x, y, 18 + k % 13, 0, 2 * math.pi); c.fill()
    c.restore()
    c.save(); c.rectangle(cx - notch - 10, d2 - 50, W - cx + notch + 80, 150); fill_tex(c, TX["water"], dx=-t * 90); c.restore()
    # the breaking overhang (caprock block)
    bw = 150
    if snap > 0:
        ang = 1.25 * eout(snap); dy = 520 * snap ** 2
        c.save(); c.translate(cx, d1 + dy); c.rotate(ang); c.rectangle(-bw, -(d1 - top), bw, d1 - top); c.clip()
        tex(c, CAP_TEX, dx=-cx - 80 + bw, dy=-300 - d1); c.paint(); c.restore()
        c.save(); c.translate(cx, d1 + dy); c.rotate(ang); c.rectangle(-bw, -(d1 - top), bw, d1 - top)
        c.set_source_rgba(0, 0, 0, 0.7); c.set_line_width(4); c.stroke(); c.restore()
        if 0.03 < snap < 0.3:
            c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(7)
            c.move_to(cx - bw, top); c.line_to(cx - bw + 22, top + 60); c.line_to(cx - bw - 10, top + 120); c.line_to(cx - bw + 8, d1); c.stroke()
        if snap > 0.8: P3.sparks(c, (snap - 0.8) * 2, cx - 40, d2 - 30, alpha=0.9)
    # waterfall curtain over the lip
    fx = cx - (bw if snap >= 1 else 0)
    if flow > 0:
        for k in range(30):
            ph = (t * 1.7 + k * 0.137) % 1.0; x = fx + 4 + (k % 7) * 15 + ph * 40
            y0 = top - dz * 0.4; y1 = d2 - 30
            c.move_to(x, y0 + ph * 30); c.curve_to(x + 40, y0 + 60, x + 60, (y0 + y1) / 2, x + 70 + (k % 4) * 10, y1)
            c.set_source_rgba(0.92, 0.98, 1, 0.5 * flow); c.set_line_width(9 + (k % 3) * 4); c.stroke()
        P1.steam(c, t, fx + 20, fx + 380, d2 - 30, rise=220, alpha=0.14 * flow)
    if labels > 0:
        tag(c, "HARD ROCK", 300, top + 90, labels, col=CYAN, side=1)
        if labels > 1.0: tag(c, "SOFT SHALE", 260, d1 + 200, labels - 1.0, col=(1.0, 0.62, 0.3), side=1)


def calendar(c, x, y, t, k):
    months = ["JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]
    i = min(5, int(eout(k) * 5.99))
    c.save(); c.translate(x, y)
    c.set_source_rgba(0, 0, 0, 0.4); rrect(c, -150 + 8, -150 + 10, 300, 300, 30); c.fill()
    c.set_source_rgb(1, 1, 1); rrect(c, -150, -150, 300, 300, 30); c.fill()
    c.set_source_rgb(*CYAN); rrect(c, -150, -150, 300, 90, 30); c.fill(); c.rectangle(-150, -100, 300, 40); c.fill()
    text(c, "1969", 0, -88, 48, col=NAVY)
    text(c, months[i], 0, 70, 110, col=NAVY)
    c.restore()


def flow_bars(c, t, day=0.0, night=0.0):
    """share of the river going over the falls (day: ~half, night: about half again)"""
    for j, (lab, frac, k, col) in enumerate((("DAY", 0.5, day, CYAN), ("NIGHT", 0.25, night, hexc("9F8CFF")))):
        if k <= 0: continue
        y = 700 + j * 230; x0, w = 140, 800; a = min(1, k * 3)
        c.set_source_rgba(0.03, 0.05, 0.12, 0.75 * a); c.rectangle(x0 - 20, y - 70, w + 40, 190); c.fill()
        c.set_source_rgba(*col, a); c.rectangle(x0 - 20, y - 70, 10, 190); c.fill()
        text(c, lab, x0, y - 12, 44, col=WHITE, align="left", alpha=a)
        c.set_source_rgba(1, 1, 1, 0.15 * a); c.rectangle(x0, y + 10, w, 70); c.fill()
        f = lerp(1.0, frac, eout(k))
        c.set_source_rgba(*col, a); c.rectangle(x0, y + 10, max(10, w * f), 70); c.fill()
        text(c, f"{int(round(f * 100))}% OVER THE FALLS", x0 + w, y - 12, 32, col=WHITE, align="right", alpha=a)


# ---------------- scenes (one per line) ----------------
def hook_frame(c, t, z=1.0):
    a = DRY.kb(min(1, t / 5.0), 1.0, 1.12, (0.4, 0.45), (0.45, 0.5))
    c.save(); cam(c, z, W / 2, 1000); to_ctx(c, finish(a, t, vign=0.45)); c.restore()
    P1.dust(c, t, col=(1, 0.95, 0.85), alpha=0.25, speed=20, size=3)
    ribbon(c, "NIAGARA FALLS", W / 2, 330, 96, t + 1, bg=WHITE)
    ribbon(c, "SWITCHED OFF?!", W / 2, 470, 112, t + 1, bg=CYAN, angle=0.03)
    switch_icon(c, 800, 1050, 0.85, ease((t - 0.6) / 0.35))
    label(c, "JUNE 1969", 1110, 1.0, x=280, size=46, bg=WHITE)


def s0(c, t, d):  # M hook — the real dry falls on frame 1, switch flips at 0.6 s
    if t < 2.4: hook_frame(c, t, z=punch(t, 1.2, 0.08))
    else:
        tt = t - 2.4; a = DRYBW.kb(tt / 2.0, 1.0, 1.1, (0.3, 0.6), (0.4, 0.62)); to_ctx(c, finish(a, tt, archival=True, vign=0.45))
        ribbon(c, "THE AMERICAN FALLS — DRY", W / 2, 420, 70, tt, bg=CYAN)
    source_tag(c, "Photo: James St. John / CC BY 2.0", t - 1.4, y=1290)


def s1(c, t, d):  # F excited "Wait, what? You can switch off a waterfall?"
    to_ctx(c, finish(CA.at(t).astype(np.float32), t, vign=0.3))
    ribbon(c, "WAIT, WHAT?!", W / 2, 420, 130, t - 0.1, bg=WHITE)
    if t > 1.2: ribbon(c, "A WATERFALL?", W / 2, 580, 90, t - 1.2, bg=CYAN, angle=0.03)
    source_tag(c, "Video: GolhaMedia / CC BY-SA 4.0", t - 0.2)


def s2(c, t, d):  # M "Well, the American side. And what they found underneath explains why the whole falls is moving."
    # one continuous camera move: globe -> ASTER satellite -> ISS astronaut photo
    if t < 1.5:
        k = ease(t / 1.5); R = 900 * (6.0 ** k); lat0 = lerp(36, NIAG[0], k); lon0 = lerp(-88, NIAG[1], k)
        g = GLOBE.render(lat0, lon0, R).astype(np.float32)
        if t > 1.1:
            a, _ = ASTER.view(579, 745, 1.3 * (1 + 0.5 * (t - 1.1))); g = g * (1 - ease((t - 1.1) / 0.4)) + a * ease((t - 1.1) / 0.4)
        to_ctx(c, finish(g, t, vign=0.3))
        x, y = project(*NIAG, lat0, lon0, R); ring_marker(c, x, y, t - 0.3)
        ribbon(c, "NIAGARA FALLS", W / 2, 420, 110, t - 0.05, bg=CYAN)
    elif t < 2.9:
        tt = t - 1.5; s_ = 1.5 * (2.4 ** ease(tt / 1.4))
        a, mp = ASTER.view(579, 745, s_)
        if tt > 1.0:
            b, _ = ISS.view(845, 600, 1.55 + 0.4 * (tt - 1.0)); a = a * (1 - ease((tt - 1.0) / 0.4)) + b * ease((tt - 1.0) / 0.4)
        to_ctx(c, finish(a, tt, vign=0.3)); scan(c, t)
        if tt < 1.0:
            for nm, (ix, iy) in (("LAKE ONTARIO", (300, 120)), ("LAKE ERIE", (900, 1500))):
                x, y = mp(ix, iy)
                if -100 < x < W + 100 and 150 < y < H - 300: text(c, nm, x, y, 40, col=WHITE, stroke=8)
            x, y = mp(579, 745); ring_marker(c, x, y, tt + 1)
        ribbon(c, "USA  |  CANADA", W / 2, 420, 90, tt, bg=WHITE)
    else:
        tt = t - 2.9; s_ = lerp(1.95, 2.6, ease(tt / (d - 2.9)))
        a, mp = ISS.view(lerp(845, 835, ease(tt / 2)), 600, s_); to_ctx(c, finish(a, tt, vign=0.3)); scan(c, t)
        x, y = mp(820, 585); tag(c, "AMERICAN FALLS", x, y, tt - 0.1, side=1)
        x2, y2 = mp(830, 690); tag(c, "HORSESHOE FALLS", x2, y2, tt - 0.5, col=WHITE, side=1)
        ribbon(c, "THE AMERICAN SIDE", W / 2, 420, 96, tt - 0.05, bg=CYAN)
        if tt > 1.9: ribbon(c, "…IS MOVING?", W / 2, 580, 80, tt - 1.9, bg=WHITE, angle=0.03)
    source_tag(c, "Images: NASA (globe, ASTER, ISS)", t - 0.3)


def s3(c, t, d):  # F curious "Moving? Moving where?"
    a = AMER.kb(t / d, 1.15, 1.28, (0.62, 0.42), (0.66, 0.38)); to_ctx(c, finish(a, t, vign=0.4))
    ribbon(c, "MOVING?!", W / 2, 420, 150, t - 0.05, bg=WHITE)
    for j in range(3):
        k = ((t * 1.3 + j / 3) % 1.0); c.set_source_rgba(*CYAN, 1 - k)
        x = 760 - 260 * k; c.move_to(x, 1000); c.line_to(x + 50, 960); c.line_to(x + 50, 1040); c.close_path(); c.fill()
    source_tag(c, "Photo: Ken Lund / CC BY-SA 2.0", t - 0.2)


DAM = [(927, 549), (921, 575), (915, 601)]
DRYPOLY = [(912, 556), (850, 560), (820, 562), (816, 608), (835, 602), (908, 598)]


def s4(c, t, d):  # M "built a dam of rock across their side of the river. About 28,000 tons of it."
    if t < 3.5:
        a, mp = ISS.view(lerp(880, 870, t / 3.5), 585, lerp(4.2, 4.6, t / 3.5)); to_ctx(c, finish(a, t, vign=0.3)); scan(c, t)
        k_dam = ease((t - 0.9) / 1.2); dry = ease((t - 2.2) / 0.8)
        if dry > 0:  # the channel below the dam dries out: sandy rock bed painted over the real channel
            c.save(); c.move_to(*mp(*DRYPOLY[0])); [c.line_to(*mp(*p)) for p in DRYPOLY[1:]]; c.close_path(); c.clip()
            tex(c, CAP_TEX); c.paint_with_alpha(0.75 * dry); c.set_source_rgba(*SAND, 0.25 * dry); c.paint(); c.restore()
        # river flow arrows (stop once the dam closes)
        if k_dam < 1:
            for j in range(4):
                ph = (t * 0.8 + j / 4) % 1.0; x0, y0 = mp(1000, 563); x1, y1 = mp(935, 568)
                x = lerp(x0, x1, ph); y = lerp(y0, y1, ph)
                c.set_source_rgba(*CYAN, (1 - ph) * (1 - k_dam)); c.move_to(x - 30, y - 22); c.line_to(x - 70, y); c.line_to(x - 30, y + 22); c.close_path(); c.fill()
        neon_path(c, [mp(*p) for p in DAM], k_dam, col=(1.0, 0.62, 0.3), width=16, t=t)
        if k_dam > 0:
            for j in range(int(10 * k_dam)):
                u = j / 9; x, y = mp(lerp(DAM[0][0], DAM[2][0], u), lerp(DAM[0][1], DAM[2][1], u))
                c.set_source_rgba(0.45, 0.4, 0.36, 1); c.arc(x + 6 * math.sin(j * 5), y, 12 + j % 3 * 3, 0, 2 * math.pi); c.fill()
        if t > 1.0: tag(c, "ROCK DAM", *mp(927, 552), t - 1.0, col=(1.0, 0.62, 0.3), side=-1)
        if t > 2.4: tag(c, "DRY", *mp(860, 590), t - 2.4, col=WHITE, side=-1)
        ribbon(c, "A DAM OF ROCK", W / 2, 420, 110, t - 0.6, bg=CYAN)
        source_tag(c, "Image: NASA ISS · Source: USACE Buffalo District", t - 0.3)
    else:
        tt = t - 3.5; a = DRYBW.kb(tt / 3.0, 1.15, 1.25, (0.5, 0.55), (0.6, 0.6)); to_ctx(c, finish(a, tt, archival=True, vign=0.45))
        ribbon(c, counter(tt - 0.4, 0, 28000, 1.4), W / 2, 420, 150, tt - 0.05, bg=WHITE, sub="TONS OF ROCK")
        source_tag(c, "Photo: NMGiovannucci / CC BY-SA 4.0 · Source: NiagaraFallsUSA", tt - 0.3, size=22)


def s5(c, t, d):  # F "And the falls just went dry?"
    a = DRY.kb(t / d, 1.15, 1.3, (0.3, 0.45), (0.32, 0.5)); to_ctx(c, finish(a, t, vign=0.4))
    ribbon(c, "BONE DRY?!", W / 2, 440, 150, t - 1.0, bg=CYAN)


def s6(c, t, d):  # M "For five months. And at the bottom, they found a huge pile of fallen rock."
    if t < 1.4:
        bg(c, "dry", DRY, t); P1.dust(c, t, alpha=0.2)
        calendar(c, W / 2, 900, t, ease((t - 0.1) / 1.2))
        ribbon(c, "5 MONTHS", W / 2, 420, 140, t - 0.05, bg=WHITE)
    else:
        tt = t - 1.4; a = DRYBW.kb(tt / (d - 1.4), 1.0, 1.25, (0.35, 0.62), (0.5, 0.7)); to_ctx(c, finish(a, tt, archival=True, vign=0.45))
        if tt > 1.7:
            c.set_source_rgba(*CYAN, ease((tt - 1.7) / 0.3)); c.set_line_width(9)
            c.arc(W / 2, 1000, 330, -math.pi / 2, -math.pi / 2 + 2 * math.pi * ease((tt - 1.7) / 0.6)); c.stroke()
            ribbon(c, "FALLEN ROCK", W / 2, 420, 130, tt - 1.7, bg=CYAN)
        source_tag(c, "Source: USACE Buffalo District", tt - 0.4)


def s7(c, t, d):  # F "Ooh, where did all that rock come from?"
    a = DRY.kb(t / d, 1.3, 1.4, (0.62, 0.62), (0.66, 0.66)); to_ctx(c, finish(a, t, vign=0.45))
    ribbon(c, "WHERE FROM?", W / 2, 440, 140, t - 0.4, bg=WHITE)


def s8(c, t, d):  # M "The cliff itself. The top layer is hard rock, but underneath, it's soft shale. Basically, packed mud."
    if t < 1.2:
        a = GORGE2.kb(t / 1.2, 1.05, 1.15, (0.3, 0.5), (0.25, 0.5)); to_ctx(c, finish(a, t, vign=0.4))
        ribbon(c, "THE CLIFF ITSELF", W / 2, 420, 110, t - 0.05, bg=CYAN)
        source_tag(c, "Photo: Ken Lund / CC BY-SA 2.0", t - 0.2)
    else:
        tt = t - 1.2
        c.save(); cam(c, lerp(1.1, 1.0, eout(tt / 0.8)), 400, 1000); cliff_block(c, tt, labels=tt - 0.9); c.restore()
        if tt > 4.9: label(c, "= PACKED MUD", 1230, tt - 4.9, x=330, size=40, bg=(1.0, 0.62, 0.3))
        ribbon(c, "HARD ON SOFT", W / 2, 420, 120, tt - 0.2, bg=WHITE)
        source_tag(c, "Source: NY State Museum (Lockport dolostone over Rochester Shale)", tt - 1.0, y=620, size=21)


def s9(c, t, d):  # M "Water eats the soft layer away, the hard edge hangs out, and then it snaps off."
    under = ease(t / 2.4); snap = max(0.0, min(1.0, (t - 3.8) / 0.8))
    sh = 8 * math.sin(t * 60) * (1 if 3.7 < t < 4.2 else 0)
    c.save(); c.translate(sh, 0); cliff_block(c, t + 6, under=under, snap=snap); c.restore()
    if t < 2.0: ribbon(c, "WATER EATS IT", W / 2, 420, 110, t - 0.05, bg=CYAN)
    elif t < 3.8: ribbon(c, "THE EDGE HANGS OUT", W / 2, 420, 96, t - 2.0, bg=WHITE)
    else: ribbon(c, "SNAP!", W / 2, 420, 150, t - 3.8, bg=RED, fg=WHITE)
    if 0.3 < t < 2.4:  # swirling current eating the shale
        for j in range(5):
            ph = (t * 1.4 + j / 5) % 1.0; x = lerp(1000, 640 - 230 * under, ph); y = 1300 - 40 * math.sin(ph * 6 + j)
            c.set_source_rgba(*CYAN, 0.9 * (1 - ph)); c.arc(x, y, 14, 0, 2 * math.pi); c.fill()
    text(c, "(simplified, not to scale)", W / 2, 1190, 28, col=WHITE, stroke=6, alpha=0.8)


def s10(c, t, d):  # F "So the waterfall breaks itself?"
    to_ctx(c, finish(CB.at(t).astype(np.float32), t, vign=0.3))
    ribbon(c, "IT BREAKS ITSELF?!", W / 2, 420, 100, t - 0.9, bg=CYAN)
    source_tag(c, "Video: Alexis Lewis / CC BY 2.0", t - 0.2)


def retreat(c, t, k, s_=2.3, cy=640):
    a, mp = ASTER.view(588, cy, s_); to_ctx(c, finish(a, t, vign=0.3)); scan(c, t)
    pts = [mp(*p) for p in GORGE_PATH[::-1]]            # Lewiston -> falls
    # the gorge the falls left behind, drawn as it walks upstream
    end = neon_path(c, pts, k, col=(1.0, 0.62, 0.3), width=12, t=t)
    x0, y0 = pts[0]; ring_marker(c, x0, y0, 1.0, col=WHITE, r=18)
    label(c, "START: LEWISTON", y0 + 20, 1.0, x=x0 + 250, size=34, bg=WHITE)
    if end: ring_marker(c, end[0], end[1], t + 0.5, col=CYAN, r=24)
    return mp


def s11(c, t, d):  # M "Again and again. 12,000 years ago, it started seven miles downstream."
    if t < 1.5:
        c.save(); cliff_block(c, t + 9, under=1.0, snap=min(1, t / 0.7)); c.restore()
        ribbon(c, "AGAIN & AGAIN", W / 2, 420, 120, t - 0.05, bg=WHITE)
    else:
        tt = t - 1.5
        retreat(c, tt, 0.0 if tt < 1.6 else 0.0)
        ribbon(c, "12,000 YEARS AGO", W / 2, 420, 100, tt - 0.4, bg=CYAN)
        if tt > 2.4: ribbon(c, "7 MILES DOWNSTREAM", W / 2 + 120, 880, 60, tt - 2.4, bg=WHITE, angle=0.02, maxw=700)
        source_tag(c, "Image: NASA ASTER · Sources: NY State Museum, Britannica", tt - 0.3, size=22)


def s12(c, t, d):  # F excited "Seven miles? It's been walking backwards this whole time?"
    k = ease(t / (d - 0.3))
    mp = retreat(c, t + 4, k)
    ribbon(c, "WALKING BACKWARDS?!", W / 2, 420, 92, t - 0.05, bg=WHITE)
    ribbon(c, counter(t, 0, 7, d - 0.4, "{} MILES"), W / 2 + 200, 880, 76, t - 0.05, bg=CYAN, angle=0.02, maxw=500)


def s13(c, t, d):  # M "Yep. But today, it's barely moving."
    a = AER.kb(t / d, 1.0, 1.12, (0.6, 0.4), (0.6, 0.45)); to_ctx(c, finish(a, t, vign=0.35))
    ribbon(c, "TODAY: BARELY MOVING", W / 2, 420, 84, t - 0.5, bg=CYAN)
    if t > 0.9: label(c, "1800s: ~5 FT A YEAR", 620, t - 0.9, size=46, bg=WHITE)
    if t > 1.3: label(c, "NOW: ~1 FT A YEAR", 730, t - 1.3, size=46, bg=CYAN)
    source_tag(c, "Photo: Zwergelstern / CC BY-SA 3.0 · Sources: Britannica, NYSM", t - 0.3, size=22)


def s14(c, t, d):  # F "Wait, why?"
    a = AER.kb(t / d, 1.12, 1.2, (0.6, 0.45), (0.58, 0.5)); to_ctx(c, finish(a, t, vign=0.35))
    ribbon(c, "WHY?!", W / 2, 440, 170, t - 0.3, bg=WHITE)


def s15(c, t, d):  # M "Because we take its water. By day, about half the river goes through tunnels to power stations."
    if t < 1.4:
        to_ctx(c, finish(CC.at(t).astype(np.float32), t, vign=0.3))
        ribbon(c, "WE TAKE ITS WATER", W / 2, 420, 100, t - 0.1, bg=CYAN)
    else:
        tt = t - 1.4
        a = POWER.kb(tt / (d - 1.4), 1.0, 1.15, (0.55, 0.45), (0.6, 0.42)); to_ctx(c, finish(a, tt, vign=0.4))
        flow_bars(c, tt, day=ease((tt - 0.9) / 1.0))
        ribbon(c, "TUNNELS TO POWER", W / 2, 420, 100, tt - 2.3, bg=WHITE) if tt > 2.3 else None
        source_tag(c, "Photo: George Burns / NARA (PD) · Source: Smithsonian", tt - 0.3, size=22)


def s16(c, t, d):  # F "And at night?"
    to_ctx(c, finish(CC.at(2.0 + t).astype(np.float32), t, vign=0.35, night=ease(t / 0.3) * 0.9))
    ribbon(c, "AT NIGHT?", W / 2, 440, 150, t - 0.05, bg=hexc("9F8CFF"), fg=WHITE)


def s17(c, t, d):  # M "Even more. So in a way, they still switch off Niagara Falls. A little, every single night."
    if t < 2.0:
        to_ctx(c, finish(CC.at(2.7 + t).astype(np.float32), t, vign=0.35, night=0.9))
        flow_bars(c, t, day=1.0, night=ease((t - 0.1) / 0.9))
        ribbon(c, "EVEN MORE", W / 2, 420, 130, t - 0.05, bg=hexc("9F8CFF"), fg=WHITE)
        source_tag(c, "Source: 1950 Niagara River Treaty (IJC)", t - 0.4)
    else:  # loop back to the hook image
        hook_frame(c, 0.5 + (t - 2.0) * 0.3, z=lerp(1.08, 1.0, eout((t - 2.0) / 0.6)))


def s18(c, t, d):  # F "That's amazing! Follow for a new wonder every day!"
    to_ctx(c, finish(CA.at(min(3.0, t)).astype(np.float32), t, vign=0.35))
    end_card_logo(c, t, W / 2, 760, 270, LOGO)
    ribbon(c, "FOLLOW", W / 2, 1180, 120, t - 1.2, bg=CYAN)
    if t > 1.5: text(c, "a new wonder every day", W / 2, 1310, 52, col=WHITE, stroke=8, alpha=ease((t - 1.5) / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18]
assert len(SCENES) == len(meta)
NO_WHIP = (10, 12, 14, 16)


def frame(c, gt, surf):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    c.save()
    if i > 0 and t < 0.3:
        z = 1 + 0.06 * (1 - eout(t / 0.3)); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[i](c, t, d)
    c.restore()
    if i > 0 and i not in NO_WHIP: whip(surf, t, direction=1 if i % 2 else -1)
    badge(c, gt)
    if i < len(SCENES) - 1:
        captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    ev = [("boom", 0.0), ("roar", 0.0), ("pop", 0.3), ("thunk", 0.6), ("pop", 1.2), ("pop", 2.4)]
    ev += [("whoosh", x - 0.05) for x in s[1:] if x not in [s[i] for i in NO_WHIP]]
    ev += [("roar", s[1]), ("pop", s[1] + 0.1), ("pop", s[1] + 1.2)]
    ev += [("pop", s[2] + 0.3), ("boom", s[2] + 1.5), ("pop", s[2] + 3.0), ("pop", s[2] + 3.4), ("pop", s[2] + 4.8)]
    ev += [("pop", s[3])] + [("pop", s[4] + 0.6)] + [("thunk", s[4] + 0.9 + k * 0.13) for k in range(0, 10, 2)]
    ev += [("pop", s[4] + 2.4), ("boom", s[4] + 3.5)] + [("tick", s[4] + 3.9 + k * 0.1) for k in range(12)]
    ev += [("pop", s[5] + 1.0)] + [("tick", s[6] + 0.1 + k * 0.22) for k in range(6)] + [("pop", s[6] + 3.1)]
    ev += [("pop", s[7] + 0.4), ("pop", s[8]), ("pop", s[8] + 1.4), ("pop", s[8] + 2.1), ("pop", s[8] + 3.1), ("pop", s[8] + 6.1)]
    ev += [("roar", s[9]), ("pop", s[9]), ("pop", s[9] + 2.0), ("crack", s[9] + 3.8), ("boom", s[9] + 4.5)]
    ev += [("roar", s[10]), ("pop", s[10] + 0.9), ("crack", s[11]), ("thunk", s[11] + 0.6), ("pop", s[11] + 1.9), ("pop", s[11] + 3.9)]
    ev += [("pop", s[12])] + [("tick", s[12] + 0.2 + k * 0.4) for k in range(7)]
    ev += [("pop", s[13] + 0.5), ("pop", s[13] + 0.9), ("pop", s[13] + 1.3), ("pop", s[14] + 0.3)]
    ev += [("roar", s[15]), ("pop", s[15] + 0.1), ("thunk", s[15] + 2.3), ("pop", s[15] + 3.7)]
    ev += [("pop", s[16]), ("pop", s[17]), ("thunk", s[17] + 0.2), ("boom", s[17] + 2.0), ("thunk", s[17] + 2.6), ("pop", s[18] + 1.2)]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]:
            frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events()}, open("events.json", "w"))
        n = int(math.ceil(TOTAL * FPS))
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
        for f in range(n):
            frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", n, "total", TOTAL)
