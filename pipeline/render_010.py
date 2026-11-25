"""Video 010 — Mount Rushmore (viewer request): "There's a secret room hidden behind Mount Rushmore's faces."
How the faces were carved (dynamite to within inches, honeycombing, crews on cables, Jefferson moved) + the Hall of
Records (70-ft tunnel, 1998 titanium vault with porcelain panels). Lakota name (Six Grandfathers) stated factually.
Structure NEW: "guided tour" — Hazel (F) = enthusiastic guide, opens + explains; Drew (M) = deadpan tourist with jokes.
NEW LOOK v7 "granite + dynamite" (different from 006 Art Deco / 007 quiz HUD / 008 logistics / 009 news):
 - plate(): engraved granite headline plates (stone texture, chiselled inner shadow, dynamite-red rule) that drop in
   with a dust puff
 - dust_burst(): rock-dust puff + small camera shake as the scene transition (replaces whip / glitch)
 - xray_room(): blueprint-blue cut-away behind the real faces showing the tunnel / hidden room
 - honeycomb(): drawn granite block — drill-hole grid appears, then the slab breaks away
 - meme moments (PLAYBOOK "MEMES INSIDE THE VIDEO"): own "EXPECTATION vs REALITY" split + "group photo" gag,
   no templates, no real faces beyond the landmark itself
Real media: credits_010.txt. usage (work dir with meta.json, media/):
  python render_010.py stills <prefix> t1 t2 ...   |   python render_010.py full [a b out.mp4]"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish

Image.MAX_IMAGE_PIXELS = None
RED = hexc("FF5233"); CREAM = hexc("F4E3C1"); SKY = hexc("6EC6FF"); STONE = hexc("8D8A86"); INK = hexc("1E1C1A")
BLUEPRINT = hexc("0E3A66"); GREEN = hexc("3DDC84")
engine.CAP_ACCENT = hexc("FFB547")


def finish(a, t, **kw):
    return _finish(haze(a, t), t, **kw)


meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]
END = 2.3
STARTS.append(_t); DURS.append(END)
TOTAL = _t + END
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix):
    fs = [f for f in sorted(glob.glob(f"media*/{prefix}*")) if os.path.getsize(f) > 0]
    return fs[0] if fs else None


def P(prefix, **kw):
    f = M(prefix); return Photo(f, **kw) if f else None


FACES = P("Mount_Rushmore_detail_view", maxz=1.25)                 # Thomas Wolf, CC BY-SA 3.0
AERIAL = P("Aerial_view_of_Mount_Rushmore", maxz=1.25)             # Carol M. Highsmith, PD
BUILD = P("Mount_Rushmore_National_Memorial_-_aerial", archival=True, maxz=1.25)   # NPS, PD
WORK = P("Mount_Rushmore2", archival=True, maxz=1.2)               # Rise Studio, PD
UNREST = P("Mount_Rushmore_unrestored", archival=True, maxz=1.2)   # Rise Studio, PD
HALL = P("Mount_Rushmore_Hall_of_Records_opening", maxz=1.2)       # Runner1928, CC BY-SA 4.0
NEEDLES = P("Cathedral_Spires", maxz=1.25)                         # w_lemay, CC BY-SA 2.0
PANEL = P("Borglum_biography_panel", maxz=1.15)                    # NPS employee, PD (optional)
P1 = Particles(110, 5)
TX = make_textures(10)
_BL = {}


def hall_grade(a):  # the tunnel photo is very orange: pull it toward neutral granite
    l = a.mean(2, keepdims=True); return np.clip(0.3 * a + 0.7 * l * np.array([1.0, 0.97, 0.93]) + 8, 0, 255)


def blurred(key, photo, f=(0.5, 0.5), dim=0.6, z=1.0):
    if key not in _BL: _BL[key] = blur(_finish(photo.kb(0, z, z, f, f), 0), 14, dim)
    return _BL[key]


def bg(c, key, photo, t, f=(0.5, 0.5), dim=0.6, z=1.0):
    to_ctx(c, haze(blurred(key, photo, f, dim, z), t, amt=30).astype(np.uint8))


def cam(c, z, cx=W / 2, cy=H / 2):
    c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)


def counter(t, v0, v1, dur, fmt="{:,}"):
    return fmt.format(int(round(lerp(v0, v1, eout(t / dur))))) if t > 0 else fmt.format(v0)


def kb(photo, t, d, z0, z1, f0, f1, **kw):
    a = photo.kb(min(1, max(0, t / d)), z0, z1, f0, f1)
    return finish(a, t, **kw)


# ---------------- look v7: granite + dynamite ----------------
def plate(c, s, x, y, size, t, rule=RED, fg=CREAM, maxw=940, sub=None):
    """engraved granite plate: drops 50 px with a squash, chiselled text (dark inner + light lower edge), red rule"""
    if t <= 0: return
    w = text_w(c, s, size)
    if w > maxw - 80: size *= (maxw - 80) / w; w = maxw - 80
    k = min(1, t / 0.22); drop = (1 - eout(k)) * -50; sq = 1 + 0.06 * math.sin(math.pi * min(1, max(0, (t - 0.18) / 0.16)))
    bw, bh = w + 80, size * 1.5
    c.save(); c.translate(x, y + drop); c.scale(sq, 2 - sq)
    c.set_source_rgba(0, 0, 0, 0.45 * k); rrect(c, -bw / 2 + 10, -bh / 2 + 14, bw, bh, 10); c.fill()
    rrect(c, -bw / 2, -bh / 2, bw, bh, 10); c.save(); c.clip()
    tex(c, TX["concrete"], dx=x * 0.3, dy=y * 0.2); c.paint()
    c.set_source_rgba(0.12, 0.12, 0.14, 0.55); c.paint()                     # darken -> granite grey
    g = cairo.LinearGradient(0, -bh / 2, 0, bh / 2); g.add_color_stop_rgba(0, 1, 1, 1, 0.18); g.add_color_stop_rgba(1, 0, 0, 0, 0.25)
    c.set_source(g); c.paint(); c.restore()
    c.set_source_rgba(1, 1, 1, 0.25); c.set_line_width(3); rrect(c, -bw / 2, -bh / 2, bw, bh, 10); c.stroke()
    c.set_source_rgb(*rule); c.rectangle(-bw / 2 + 24, bh / 2 - 16, (bw - 48) * eout((t - 0.1) / 0.3), 7); c.fill()
    text(c, s, 0, size * 0.36 - 3, size, col=(0.05, 0.05, 0.06), alpha=0.7 * k)    # chisel shadow
    text(c, s, 0, size * 0.36 + 2, size, col=(1, 1, 1), alpha=0.25 * k)
    text(c, s, 0, size * 0.36, size, col=fg, alpha=k)
    c.restore()
    if sub and t > 0.3:
        a = ease((t - 0.3) / 0.25); sz = 40; sw = text_w(c, sub, sz) + 40
        c.save(); c.translate(x, y + bh / 2 + 44)
        c.set_source_rgba(*RED, 0.95 * a); rrect(c, -sw / 2, -sz * 0.8, sw, sz * 1.3, 8); c.fill()
        text(c, sub, 0, sz * 0.25, sz, col=CREAM, alpha=a); c.restore()


def dust_burst(c, t, x=W / 2, y=H / 2, dur=0.5, n=46, spread=520, seed=0):
    """rock-dust puff: tan particles fly out, grow and fade"""
    if t < 0 or t > dur: return
    k = t / dur; r = np.random.default_rng(seed)
    for j in range(n):
        ang = r.random() * 2 * math.pi; sp = (0.3 + r.random()) * spread; sz = 18 + r.random() * 60
        px = x + math.cos(ang) * sp * eout(k); py = y + math.sin(ang) * sp * eout(k) * 0.7 + 60 * k * k
        a = (1 - k) ** 1.5 * 0.55
        g = cairo.RadialGradient(px, py, 0, px, py, sz * (0.6 + k))
        g.add_color_stop_rgba(0, 0.86, 0.80, 0.70, a); g.add_color_stop_rgba(1, 0.86, 0.80, 0.70, 0)
        c.set_source(g); c.arc(px, py, sz * (0.6 + k), 0, 2 * math.pi); c.fill()


def flash(c, t, dur=0.25, col=(1, 0.85, 0.6)):
    if 0 <= t < dur: c.set_source_rgba(*col, 0.75 * (1 - t / dur)); c.paint()


def ruler(c, x, y0, y1, lab, t, col=CREAM):
    k = eout(t / 0.5)
    if k <= 0: return
    ym = lerp(y0, y1, k)
    c.set_source_rgba(*col, 1); c.set_line_width(7); c.move_to(x, y0); c.line_to(x, ym); c.stroke()
    for yy in (y0, ym): c.move_to(x - 26, yy); c.line_to(x + 26, yy); c.stroke()
    if k > 0.95:
        c.set_source_rgba(*INK, 0.85); rrect(c, x - 125, (y0 + y1) / 2 - 45, 250, 90, 12); c.fill()
        text(c, lab, x, (y0 + y1) / 2 + 20, 58, col=engine.CAP_ACCENT)


def ring_meter(c, cx, cy, r, frac, lab, t):
    c.set_source_rgba(*INK, 0.75); c.arc(cx, cy, r + 26, 0, 2 * math.pi); c.fill()
    c.set_line_width(34); c.set_source_rgba(1, 1, 1, 0.15); c.arc(cx, cy, r, 0, 2 * math.pi); c.stroke()
    f = frac * eout(t / 1.2)
    c.set_source_rgb(*RED); c.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * f); c.stroke()
    text(c, f"{int(round(f * 100))}%", cx, cy + 30, 110, col=CREAM)
    text(c, lab, cx, cy + 100, 34, col=CREAM, alpha=0.9)


def stamp(c, s, x, y, t, col=RED, size=150, ang=-0.1):
    if t <= 0: return
    k = min(1, t / 0.16); sc = lerp(1.6, 1.0, eout(k))
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(sc, sc)
    w = text_w(c, s, size) + 80; h = size * 1.3
    c.set_source_rgba(*INK, 0.55 * k); rrect(c, -w / 2, -h / 2, w, h, 20); c.fill()
    c.set_source_rgba(*col, k); c.set_line_width(14); rrect(c, -w / 2, -h / 2, w, h, 20); c.stroke()
    text(c, s, 0, size * 0.36, size, col=col, alpha=k); c.restore()


def xray_room(c, t, k, cx=560, cy=900, label=True):
    """blueprint cut-away glowing through the rock behind the heads: tunnel + room outline (illustrative)"""
    if k <= 0: return
    a = ease(k)
    c.save()
    g = cairo.RadialGradient(cx, cy, 20, cx, cy, 420); g.add_color_stop_rgba(0, *SKY, 0.6 * a); g.add_color_stop_rgba(1, *SKY, 0)
    c.set_source(g); c.arc(cx, cy, 420, 0, 2 * math.pi); c.fill()
    c.set_line_width(9); c.set_source_rgba(0.85, 0.95, 1, a); c.set_dash([22, 12], -t * 60)
    c.move_to(cx + 330, cy + 60); c.line_to(cx + 90, cy + 40); c.stroke()                 # tunnel from the canyon
    rrect(c, cx - 200, cy - 60, 290, 180, 14); c.stroke(); c.set_dash([])                 # the room
    c.set_source_rgba(*BLUEPRINT, 0.55 * a); rrect(c, cx - 200, cy - 60, 290, 180, 14); c.fill()
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    c.set_source_rgba(1, 0.85, 0.4, (0.5 + 0.5 * pulse) * a); rrect(c, cx - 90, cy + 40, 70, 50, 6); c.fill()   # the box
    c.restore()
    if label: text(c, "(illustration)", cx - 55, cy + 175, 26, col=WHITE, stroke=6, alpha=0.8 * a)


def honeycomb(c, t, d):
    """drawn granite block: rows of drill holes appear, then the outer slab cracks off and falls"""
    bg(c, "faces_bg", FACES, t, (0.3, 0.45), dim=0.5, z=1.15)
    x0, y0, bw, bh = 140, 560, 800, 640
    c.save(); rrect(c, x0, y0, bw, bh, 30); c.clip(); tex(c, TX["concrete"], dx=t * 4); c.paint()
    c.set_source_rgba(0.2, 0.2, 0.25, 0.35); c.paint(); c.restore()
    c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(4); rrect(c, x0, y0, bw, bh, 30); c.stroke()
    face_x = x0 + 520                                   # the "final surface" line
    c.set_source_rgba(*engine.CAP_ACCENT, 0.9); c.set_line_width(5); c.set_dash([18, 12])
    c.move_to(face_x, y0 - 30); c.line_to(face_x, y0 + bh + 30); c.stroke(); c.set_dash([])
    text(c, "FINAL FACE", face_x, y0 - 50, 36, col=engine.CAP_ACCENT, stroke=8)
    holes = [(face_x + 40 + j * 44, y0 + 50 + i * 48) for i in range(12) for j in range(5)]
    n = int(len(holes) * ease((t - 0.3) / 1.6))
    fall = ease((t - 2.4) / 0.9)
    c.save(); c.translate(0, 900 * fall * fall); c.rotate(0.08 * fall)
    if fall > 0:   # the slab outside the line breaks away
        c.rectangle(face_x + 8, y0, x0 + bw - face_x - 8, bh); c.set_source_rgba(0.55, 0.53, 0.5, 0.9 * (1 - fall)); c.fill()
    for (hx, hy) in holes[:n]:
        c.set_source_rgba(0.08, 0.07, 0.07, 0.95 * (1 - fall)); c.arc(hx, hy, 12, 0, 2 * math.pi); c.fill()
    c.restore()
    if 2.3 < t < 3.3: dust_burst(c, t - 2.3, face_x + 140, y0 + bh / 2, dur=1.0, spread=300, seed=4)
    # drill bit
    if t < 2.3 and n < len(holes):
        hx, hy = holes[n]; c.set_source_rgba(0.85, 0.85, 0.9, 1); c.set_line_width(10)
        c.move_to(hx + 20, hy); c.line_to(hx + 160, hy); c.stroke()
        c.set_source_rgb(*RED); rrect(c, hx + 150, hy - 26, 120, 52, 10); c.fill()


def chest(c, x, y, s, t):
    """original drawn treasure chest with glow (expectation side of the meme)"""
    g = cairo.RadialGradient(x, y - 40 * s, 10, x, y - 40 * s, 260 * s); g.add_color_stop_rgba(0, 1, 0.85, 0.3, 0.7); g.add_color_stop_rgba(1, 1, 0.85, 0.3, 0)
    c.set_source(g); c.arc(x, y - 40 * s, 260 * s, 0, 2 * math.pi); c.fill()
    c.set_source_rgb(*hexc("7A4A24")); rrect(c, x - 150 * s, y - 60 * s, 300 * s, 160 * s, 14 * s); c.fill()
    c.set_source_rgb(*hexc("8E5A2E")); rrect(c, x - 150 * s, y - 150 * s, 300 * s, 90 * s, 40 * s); c.fill()
    c.set_source_rgb(*engine.CAP_ACCENT)
    for xx in (-110, 90): c.rectangle(x + xx * s, y - 150 * s, 20 * s, 250 * s); c.fill()
    for j in range(7):   # coins
        ph = (t * 1.3 + j / 7) % 1
        c.arc(x + (j - 3) * 34 * s, y - 160 * s - 120 * s * math.sin(math.pi * ph), 16 * s, 0, 2 * math.pi); c.fill()


def panels_drawn(c, x, y, t, n=16):
    """stack of porcelain enamel panels (fallback when no panel photo)"""
    for j in range(n):
        k = ease((t - j * 0.06) / 0.25)
        if k <= 0: continue
        yy = y - j * 14 * k
        c.set_source_rgba(0.95, 0.95, 0.97, k); rrect(c, x - 220 + j * 3, yy - 140, 440, 280, 10); c.fill()
        c.set_source_rgba(0.1, 0.15, 0.3, 0.6 * k); c.set_line_width(3)
        for q in range(6): c.move_to(x - 180 + j * 3, yy - 100 + q * 36); c.line_to(x + 180 + j * 3, yy - 100 + q * 36); c.stroke()


# ---------------- scenes ----------------
HOOKF = (0.5, 0.33)


def hook_frame(c, t, xr=1.0):
    zz = lerp(1.0, 1.07, min(1, t / 3.5))
    to_ctx(c, finish(FACES.kb(0, zz, zz, HOOKF, HOOKF), t, vign=0.3))
    xray_room(c, t, xr, cx=720, cy=1170, label=False)
    plate(c, "SECRET ROOM", W / 2, 360, 150, t + 1, sub="BEHIND THE FACES?!")


def s0(c, t, d):   # F hook
    hook_frame(c, t, xr=ease((t - 0.5) / 0.6))
    if t > 0.5: text(c, "(illustration)", 880, 1385, 24, col=WHITE, stroke=6, alpha=0.8 * ease((t - 0.5) / 0.5))
    source_tag(c, "Photo: Thomas Wolf, foto-tw.de / CC BY-SA 3.0", t - 0.3, y=1370, size=20)


def s1(c, t, d):   # M "Sure. And the noses are full of snacks."
    a = FACES.kb(min(1, t / d), 1.6, 2.0, (0.33, 0.4), (0.33, 0.44)); to_ctx(c, finish(a, t, vign=0.35))
    plate(c, "SNACKS?", W / 2, 400, 120, t - 0.9)
    for j in range(5):   # drawn cookies orbiting the nose (the joke)
        if t < 1.1 + j * 0.1: continue
        ang = t * 1.6 + j * 2 * math.pi / 5; x = 540 + 260 * math.cos(ang); y = 1000 + 120 * math.sin(ang)
        c.set_source_rgb(*hexc("C68A4A")); c.arc(x, y, 34, 0, 2 * math.pi); c.fill()
        c.set_source_rgb(*hexc("3B2414"))
        for q in range(4): c.arc(x + 14 * math.cos(q * 1.7), y + 14 * math.sin(q * 1.7), 6, 0, 2 * math.pi); c.fill()


def s2(c, t, d):   # F "No snacks. But the room is real... and something's in it."
    a = hall_grade(HALL.kb(min(1, t / d), 1.0, 1.15, (0.5, 0.5), (0.52, 0.45))); to_ctx(c, finish(a, t, vign=0.4))
    plate(c, "IT'S REAL", W / 2, 400, 130, t - 0.2, rule=GREEN)
    if t > 2.6: plate(c, "SOMETHING'S INSIDE", W / 2, 580, 70, t - 2.6)
    source_tag(c, "Photo: Runner1928 / CC BY-SA 4.0 · the tunnel entrance", t - 0.2, size=22)


def s3(c, t, d):   # F Lakota: Six Grandfathers (no joke here)
    a = AERIAL.kb(min(1, t / d), 1.5, 1.6, (0.62, 0.3), (0.6, 0.3)); to_ctx(c, finish(a, t, vign=0.3))
    plate(c, "THE SIX GRANDFATHERS", W / 2, 400, 80, t - 0.9, rule=engine.CAP_ACCENT, sub="Lakota name for the mountain")
    source_tag(c, "Photo: Carol M. Highsmith (PD) · Source: Eos / AGU", t - 0.3, size=22)


def s4(c, t, d):   # F "So how do you carve a face sixty feet tall? Dynamite."
    if t < 2.7:
        a = FACES.kb(min(1, t / 2.7), 1.2, 1.35, (0.36, 0.42), (0.36, 0.42)); to_ctx(c, finish(a, t, vign=0.3))
        ruler(c, 150, 640, 1240, "60 FT", t - 0.6)
        plate(c, "HOW?", W / 2, 400, 140, t - 0.1)
        source_tag(c, "Source: Britannica (each head about 60 ft)", t - 0.3, size=22)
    else:
        tt = t - 2.7; sh = 14 * (1 - eout(tt / 0.5)) * math.sin(tt * 70)
        c.save(); c.translate(sh, -sh * 0.6)
        a = BUILD.kb(min(1, tt / (d - 2.7)), 1.1, 1.2, (0.5, 0.5), (0.5, 0.45)); to_ctx(c, finish(a, tt, archival=True, vign=0.4))
        c.restore(); flash(c, tt); dust_burst(c, tt, W / 2, 900, dur=0.9, spread=600, seed=1)
        plate(c, "DYNAMITE", W / 2, 420, 140, tt - 0.05)


def s5(c, t, d):   # F "About ninety percent was blasted off, to within inches of the face."
    a = BUILD.kb(min(1, t / d), 1.2, 1.32, (0.5, 0.45), (0.45, 0.42)); to_ctx(c, finish(a, t + 3, archival=True, vign=0.4))
    if t < 3.2:
        ring_meter(c, W / 2, 900, 200, 0.9, "BLASTED OFF", t - 0.2)
    else:
        tt = t - 3.2
        plate(c, "WITHIN INCHES", W / 2, 400, 110, tt)
        # simple rock profile: blasted line just outside the final face line
        c.save(); c.translate(0, 150)
        c.set_source_rgba(*INK, 0.7); rrect(c, 140, 600, 800, 460, 24); c.fill()
        ys = np.linspace(640, 1020, 40)
        c.set_source_rgba(*engine.CAP_ACCENT, 1); c.set_line_width(6)
        for j, yy in enumerate(ys): (c.move_to if j == 0 else c.line_to)(430 + 90 * math.sin(yy / 70), yy)
        c.stroke()
        c.set_source_rgba(*RED, 1); c.set_dash([14, 10])
        for j, yy in enumerate(ys): (c.move_to if j == 0 else c.line_to)(430 + 90 * math.sin(yy / 70) + 60 * ease(tt / 0.6), yy)
        c.stroke(); c.set_dash([])
        text(c, "FINAL FACE", 300, 1060, 34, col=engine.CAP_ACCENT); text(c, "BLASTED TO HERE", 720, 1060, 34, col=RED)
        text(c, "3-6 INCHES LEFT", W / 2, 1110, 40, col=CREAM, alpha=ease((tt - 0.6) / 0.3))
        c.restore()
    source_tag(c, "Photo: National Park Service (PD) · Source: NPS 'Carving History'", t - 0.3, size=22)


def s6(c, t, d):   # F honeycomb
    honeycomb(c, t, d)
    plate(c, "HONEYCOMBING", W / 2, 400, 110, t - 0.1)
    source_tag(c, "Diagram (simplified) · Source: NPS, Britannica", t - 0.3, size=22)


WORKERS = [(0.57, 0.62), (0.58, 0.72), (0.56, 0.84)]   # tiny figures on the cables (fractions of WORK at z=1)


def s7(c, t, d):   # F "Crews hung off the cliff to do it. In fourteen years, not one worker died."
    if t < 3.0:
        a = WORK.kb(min(1, t / 3.0), 1.0, 1.15, (0.55, 0.6), (0.57, 0.7)); to_ctx(c, finish(a, t, archival=True, vign=0.4))
        plate(c, "HANGING ON CABLES", W / 2, 400, 86, t - 0.2)
    else:
        tt = t - 3.0
        a = UNREST.kb(min(1, tt / (d - 3.0)), 1.0, 1.12, (0.5, 0.45), (0.5, 0.4)); to_ctx(c, finish(a, tt, archival=True, vign=0.4))
        plate(c, counter(tt - 0.1, 0, 14, 0.7) + " YEARS", W / 2, 400, 130, tt - 0.05)
        if tt > 1.6: stamp(c, "0 DEATHS", W / 2, 900, tt - 1.6, col=GREEN, size=130)
        source_tag(c, "Photos: Rise Studio (PD) · Source: NPS (no fatalities)", tt - 0.3, size=22)


def s8(c, t, d):   # F Jefferson moved
    a = FACES.kb(min(1, t / d), 1.05, 1.12, (0.35, 0.45), (0.33, 0.45)); to_ctx(c, finish(a, t, vign=0.3))
    gx, gy = 190, 900
    k = ease((t - 0.3) / 0.5)
    if k > 0 and t < 4.6:
        c.set_source_rgba(*SKY, 0.9 * k); c.set_line_width(8); c.set_dash([20, 12], -t * 40)
        c.save(); c.translate(gx, gy); c.scale(1, 1.3); c.arc(0, 0, 120, 0, 2 * math.pi); c.restore(); c.stroke(); c.set_dash([])
        text(c, "JEFFERSON v1", gx + 90, gy - 190, 44, col=SKY, stroke=10, alpha=k)
    if t > 3.0 and t < 4.6:
        e = ease((t - 3.0) / 0.25); c.set_source_rgba(*RED, e); c.set_line_width(18)
        c.move_to(gx - 110, gy - 140); c.line_to(gx + 110, gy + 140); c.move_to(gx + 110, gy - 140); c.line_to(gx - 110, gy + 140); c.stroke()
    if t > 3.9: flash(c, t - 3.9); dust_burst(c, t - 3.9, gx + 40, gy, dur=0.9, spread=420, seed=2)
    if t > 4.6: plate(c, "BLASTED OFF", W / 2, 1150, 100, t - 4.6)
    plate(c, "ROCK TOO CRACKED", W / 2, 400, 90, t - 1.8)
    source_tag(c, "Illustrative position · Sources: Britannica, Eos", t - 0.3, size=22)


def s9(c, t, d):   # M "Dynamited out of the group photo. Brutal." — meme: polaroid with an empty slot
    bg(c, "faces_g", FACES, t, (0.5, 0.42), dim=0.45, z=1.0)
    c.save(); c.translate(W / 2, 950); c.rotate(-0.06 + 0.02 * math.sin(t * 2))
    c.set_source_rgba(0, 0, 0, 0.4); c.rectangle(-380 + 14, -330 + 18, 760, 700, ); c.fill()
    c.set_source_rgb(0.97, 0.96, 0.92); c.rectangle(-380, -330, 760, 700); c.fill()
    sub = FACES.kb(0, 1.0, 1.0, (0.5, 0.42), (0.5, 0.42))
    im = Image.fromarray(np.clip(sub, 0, 255).astype(np.uint8)).resize((680, 1209)).crop((0, 380, 680, 880))
    s = to_surface(np.asarray(im, np.float32) / 255); c.set_source_surface(s, -340, -290); c.paint()
    # an empty dashed slot where Jefferson v1 would have stood (left of Washington)
    c.set_source_rgba(*RED, 1); c.set_line_width(6); c.set_dash([16, 10]); c.rectangle(-335, -240, 110, 200); c.stroke(); c.set_dash([])
    text(c, "?", -280, -100, 90, col=RED)
    text(c, "GROUP PHOTO, 1930s", 0, 300, 44, col=INK)
    c.restore()
    if t > 1.2: stamp(c, "BRUTAL.", W / 2, 470, t - 1.2, col=RED, size=120)


def s10(c, t, d):  # F Hall of Records planned, 70-ft tunnel, work stopped
    a = FACES.kb(min(1, t / d), 1.05, 1.2, (0.62, 0.42), (0.7, 0.4)); to_ctx(c, finish(a, t, vign=0.3, xray=0.55 * ease(t / 0.8)))
    k = ease((t - 0.4) / 0.6)
    xray_room(c, t, k, cx=600, cy=900)
    plate(c, "HALL OF RECORDS", W / 2, 400, 100, t - 0.1)
    if t > 3.0:
        tt = t - 3.0
        c.set_source_rgba(*INK, 0.8); rrect(c, 300, 1110, 480, 110, 14); c.fill()
        text(c, counter(tt, 0, 70, 1.2) + "-FT TUNNEL", W / 2, 1185, 60, col=engine.CAP_ACCENT)
    if t > 5.2: stamp(c, "WORK STOPPED", W / 2, 640, t - 5.2, col=RED, size=96)
    source_tag(c, "Illustration · Source: NPS 'Hall of Records' (tunnel 1938-39)", t - 0.3, size=22)


def s11(c, t, d):  # F 1998: teak box, titanium vault, 1,200-lb granite lid
    a = hall_grade(HALL.kb(min(1, t / d), 1.15, 1.3, (0.5, 0.55), (0.5, 0.6))); to_ctx(c, finish(a, t, vign=0.4))
    c.set_source_rgba(*INK, 0.35 * ease(t / 0.5)); c.paint()
    plate(c, "1998", W / 2, 400, 140, t - 0.05)
    cx, cy = W / 2, 930
    kb_ = ease((t - 0.8) / 0.5)        # titanium vault rises
    if kb_ > 0:
        g = cairo.LinearGradient(cx - 230, 0, cx + 230, 0)
        for p_, v in ((0, 0.55), (0.45, 0.88), (1, 0.5)): g.add_color_stop_rgba(p_, v, v + 0.02, v + 0.05, kb_)
        c.set_source(g); rrect(c, cx - 230, cy - 150 + (1 - kb_) * 120, 460, 300, 16); c.fill()
        text(c, "TITANIUM VAULT", cx, cy + 40, 46, col=INK, alpha=kb_)
    lid = ease((t - 2.6) / 0.35)
    if t > 2.4:
        ly = lerp(560, cy - 200, lid)
        c.save(); rrect(c, cx - 270, ly - 50, 540, 100, 10); c.clip(); tex(c, TX["concrete"]); c.paint()
        c.set_source_rgba(0.05, 0.05, 0.07, 0.6); c.paint(); c.restore()
        text(c, "GRANITE LID", cx, ly + 16, 42, col=CREAM)
        if lid >= 1: dust_burst(c, t - 2.95, cx, cy - 160, dur=0.7, spread=300, seed=6)
    if t > 3.5:
        c.set_source_rgba(*RED, 1); rrect(c, cx - 170, cy + 175, 340, 90, 12); c.fill()
        text(c, counter(t - 3.5, 0, 1200, 0.8) + " LB", cx, cy + 240, 62, col=CREAM)
    source_tag(c, "Illustration · Sources: NPS, HISTORY (1,200-lb capstone)", t - 0.3, size=22)


def meme_split(c, t, show_reality=0.0, reality_t=0.0, homework=0.0):
    """our own 'EXPECTATION vs REALITY' format (no template): top = expectation, bottom = reality (clear of captions)"""
    to_ctx(c, finish(FACES.kb(0, 1.0, 1.0, (0.5, 0.42), (0.5, 0.42)), t, vign=0.3))
    g = cairo.LinearGradient(0, 0, 0, H)   # darken the middle only: edges keep sky/rock texture (edge-band check)
    for p_, a_ in ((0, 0.0), (0.12, 0.5), (0.75, 0.5), (1, 0.1)): g.add_color_stop_rgba(p_, *INK, a_)
    c.set_source(g); c.paint()
    BX = ((250, "EXPECTATION"), (800, "REALITY"))
    c.save(); c.rectangle(90, 250, 900, 520); c.clip()
    c.set_source_rgb(*hexc("1A2238")); c.paint(); chest(c, W / 2, 600, 1.1, t); c.restore()
    if show_reality > 0:
        c.save(); c.rectangle(90, 800, 900, 520); c.clip()
        c.set_source_rgb(*hexc("3A3D44")); c.paint()
        if PANEL is not None:
            pa = PANEL.kb(0, 1.0, 1.0, (0.5, 0.5), (0.5, 0.5)); im = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8)).resize((300, 533))
            s = to_surface(np.asarray(im, np.float32) / 255); c.set_source_surface(s, W / 2 - 150, 830); c.paint()
        else:
            panels_drawn(c, W / 2, 1090, reality_t)
        c.restore()
        c.set_source_rgba(*INK, 0.85); rrect(c, W / 2 - 250, 1240, 500, 64, 10); c.fill()
        text(c, "16 PORCELAIN PANELS", W / 2, 1285, 40, col=CREAM, alpha=ease(reality_t / 0.4))
    for j, (y, lab) in enumerate(BX):
        if j == 1 and show_reality <= 0: continue
        c.set_source_rgba(0.98, 0.97, 0.93, 1); c.set_line_width(10); c.rectangle(90, y, 900, 520); c.stroke()
        c.set_source_rgba(0.98, 0.97, 0.93, 1); rrect(c, 110, y + 18, text_w(c, lab, 44) + 40, 66, 8); c.fill()
        text(c, lab, 130, y + 68, 44, col=INK, align="left")
    if homework > 0: stamp(c, "HOMEWORK", W / 2, 1080, homework, col=RED, size=130, ang=-0.12)


def s12(c, t, d):  # M "Treasure?"
    meme_split(c, t)


def s13(c, t, d):  # F "Porcelain panels... with the story of the carving and the country."
    meme_split(c, t + 1.1, show_reality=1, reality_t=t)
    source_tag(c, "Source: NPS 'Hall of Records' (16 panels)", t - 0.3, y=1362, size=20)


def s14(c, t, d):  # M "So the treasure... is homework."
    meme_split(c, t + 4.4, show_reality=1, reality_t=4, homework=t - 1.0)


def s15(c, t, d):  # F erosion + loop back to the hook
    if t < 4.6:
        a = NEEDLES.kb(min(1, t / 4.6), 1.0, 1.12, (0.5, 0.45), (0.5, 0.4)); to_ctx(c, finish(a, t, vign=0.3))
        plate(c, "1 INCH", W / 2, 400, 140, t - 1.0)
        if t > 1.9: plate(c, "EVERY " + counter(t - 1.9, 0, 10000, 1.0) + " YEARS", W / 2, 580, 76, t - 1.9)
        source_tag(c, "Photo: w_lemay / CC BY-SA 2.0 (Black Hills granite) · Source: Eos", t - 0.3, size=21)
    else:
        tt = t - 4.6; hook_frame(c, 0.3 + tt * 0.4, xr=1.0)
        plate(c, "NOT GOING ANYWHERE", W / 2, 1180, 76, tt - 0.6, rule=GREEN)


def s_end(c, t, d):
    a = FACES.kb(min(1, t / 3), 1.0, 1.06, (0.5, 0.42), (0.5, 0.42)); to_ctx(c, finish(a, t, vign=0.35))
    end_card_logo(c, t, W / 2, 760, 270, LOGO)
    plate(c, "FOLLOW", W / 2, 1180, 120, t - 0.5)
    if t > 0.9: text(c, "you asked, we dug in", W / 2, 1330, 48, col=WHITE, stroke=8, alpha=ease((t - 0.9) / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s_end]
assert len(SCENES) == len(STARTS), (len(SCENES), len(STARTS))
NO_DUST = (0, 13, 14)       # continuous scenes: no transition puff


def frame(c, gt, surf):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    c.save()
    if i > 0 and t < 0.3:   # small settle + shake as the new scene lands
        z = 1 + 0.04 * (1 - eout(t / 0.3)); sh = 8 * (1 - t / 0.3) * math.sin(t * 90)
        c.translate(W / 2 + sh, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[i](c, t, d)
    c.restore()
    if i > 0 and i not in NO_DUST: dust_burst(c, t, W / 2, H / 2, dur=0.38, n=34, spread=700, seed=i)
    badge(c, gt)
    if i < len(meta):
        captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    ev = [("boom", 0.0), ("pop", 0.6), ("bubble", 0.7)]
    ev += [("whoosh", x - 0.05) for k, x in enumerate(s[1:], 1) if k not in NO_DUST]
    ev += [("pop", s[1] + 1.1), ("pop", s[1] + 1.3), ("pop", s[2] + 0.2), ("pop", s[2] + 2.6), ("pop", s[3] + 0.9)]
    ev += [("tick", s[4] + 0.6 + k * 0.1) for k in range(5)] + [("boom", s[4] + 2.7), ("crack", s[4] + 2.75)]
    ev += [("tick", s[5] + 0.2 + k * 0.12) for k in range(9)] + [("pop", s[5] + 3.2)]
    ev += [("drill", s[6] + 0.3), ("crack", s[6] + 2.4), ("thunk", s[6] + 3.0)]
    ev += [("pop", s[7] + 0.2), ("tick", s[7] + 3.1), ("tick", s[7] + 3.4), ("ding", s[7] + 4.6)]
    ev += [("pop", s[8] + 1.8), ("thunk", s[8] + 3.0), ("boom", s[8] + 3.9), ("pop", s[8] + 4.6)]
    ev += [("scratch", s[9] + 0.05), ("thunk", s[9] + 1.2)]
    ev += [("pop", s[10] + 0.1), ("drill", s[10] + 3.0), ("thunk", s[10] + 5.2)]
    ev += [("pop", s[11]), ("clank", s[11] + 0.9), ("thunk", s[11] + 2.95), ("boom", s[11] + 2.95), ("ding", s[11] + 4.3)]
    ev += [("ding", s[12] + 0.1), ("pop", s[13] + 0.1), ("trombone", s[14] + 0.9), ("thunk", s[14] + 1.0)]
    ev += [("pop", s[15] + 1.0), ("pop", s[15] + 1.9), ("tick", s[15] + 2.0), ("tick", s[15] + 2.4), ("boom", s[15] + 4.6), ("pop", s[16] + 0.5)]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]:
            frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events(), "music_style": "americana"}, open("events.json", "w"))
        a, b = (int(v) for v in sys.argv[2:4]) if len(sys.argv) > 3 else (0, int(math.ceil(TOTAL * FPS)))
        out = sys.argv[4] if len(sys.argv) > 4 else "video.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a, b):
            frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", a, b, "total", TOTAL)
