"""Video 006 — Empire State Building: "They built the Empire State Building in 410 days" (mega-build).
Structure: narrator (F, Jessica) + interrupting sceptic (M, Eric) who hunts for "the catch" and carries the jokes.
NEW LOOK v4 "Art Deco" (different from 005's cyan ribbons / whip-pans / satellite zooms):
 - deco_title(): cream plates with a double gold rule and stepped (ziggurat) corners that unfold vertically
 - shutter(): elevator-door transition (two deco panels slide apart) instead of whip-pans
 - drawn explainers in a 1930s "assembly sheet" style on textured paper: a stepped ESB tower that grows floor by
   floor with a day counter, flat-pack parts list, rail cart on floor tracks, original generic airship
 - jade caption keywords (engine.CAP_ACCENT), real Lewis Hine 1930-31 photos (CC0/PD) + drone footage
Real media: see credits_006.txt. usage (work dir with meta.json, media/, clipA..C):
  python render_006.py stills <prefix> t1 t2 ...   |   python render_006.py full"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish
from clips import Clip

JADE = hexc("3DDBB4"); CREAM = hexc("F6EBD2"); INK = hexc("14161F"); BRASS = hexc("D9A441"); RED = (0.9, 0.22, 0.2)
engine.CAP_ACCENT = JADE


def finish(a, t, **kw):  # every photo/clip frame gets edge haze (edge-band check)
    return _finish(haze(a, t), t, **kw)


meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]
END = 2.4                      # end card after the last line
STARTS.append(_t); DURS.append(END)
TOTAL = _t + END
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def M(prefix): return sorted(glob.glob(f"media*/{prefix}*"))[0]


HOOK = Photo(M("View_of_Empire_State"), maxz=1.3)            # Dllu, CC BY-SA 4.0
STREET = Photo(M("Empire_State_Building_-_01"), maxz=1.3)     # Carlos Delgado, CC BY-SA 3.0
SUNSET = Photo(M("Empire_State_Building_-_Sunset"), maxz=1.3) # Eric Kilby, CC BY-SA 2.0
SPIRE = Photo(M("Empire_State_Building_Spire"), maxz=1.3)     # Eric Johnson, CC BY-SA 3.0
HINE1 = Photo(M("Empire_State_Building_MET"), archival=True, maxz=1.3)   # Lewis Hine, CC0 (MET)
HINE2 = Photo(M("Photograph_of_a_Workman"), archival=True, maxz=1.3)    # Lewis Hine / NARA, PD
MAST = Photo(M("Raising_the_Mast"), archival=True, maxz=1.3)            # Lewis Hine, PD
COLEMAN = Photo(M("Glenn_O"), archival=True, maxz=1.3)                  # Glenn O. Coleman, PD (artwork)
CA, CB, CC = Clip("clipA"), Clip("clipB"), Clip("clipC")                                   # the Dronalist, CC BY 3.0
P1, P2 = Particles(110, 1), Particles(60, 2)
TX = make_textures(6)
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


# ---------------- look v4: Art Deco ----------------
def deco_title(c, s, x, y, size, t, bg=CREAM, fg=INK, rule=BRASS, maxw=920, sub=None):
    """cream plate with stepped (ziggurat) corners + double brass rule; unfolds vertically like a sign flipping down"""
    if t <= 0: return
    w = text_w(c, s, size)
    if w > maxw - 90: size *= (maxw - 90) / w; w = maxw - 90
    k = back(min(1.0, t / 0.3)); bw, bh = w + 90, size * 1.45; st = 16
    c.save(); c.translate(x, y); c.scale(1, max(0.02, k))
    def plate(dx, dy, ww, hh, s_):
        c.move_to(dx - ww / 2 + s_, dy - hh / 2); c.line_to(dx + ww / 2 - s_, dy - hh / 2); c.line_to(dx + ww / 2 - s_, dy - hh / 2 + s_ / 2)
        c.line_to(dx + ww / 2 - s_ / 2, dy - hh / 2 + s_ / 2); c.line_to(dx + ww / 2 - s_ / 2, dy - hh / 2 + s_); c.line_to(dx + ww / 2, dy - hh / 2 + s_)
        c.line_to(dx + ww / 2, dy + hh / 2 - s_); c.line_to(dx + ww / 2 - s_ / 2, dy + hh / 2 - s_); c.line_to(dx + ww / 2 - s_ / 2, dy + hh / 2 - s_ / 2)
        c.line_to(dx + ww / 2 - s_, dy + hh / 2 - s_ / 2); c.line_to(dx + ww / 2 - s_, dy + hh / 2)
        c.line_to(dx - ww / 2 + s_, dy + hh / 2); c.line_to(dx - ww / 2 + s_, dy + hh / 2 - s_ / 2); c.line_to(dx - ww / 2 + s_ / 2, dy + hh / 2 - s_ / 2)
        c.line_to(dx - ww / 2 + s_ / 2, dy + hh / 2 - s_); c.line_to(dx - ww / 2, dy + hh / 2 - s_); c.line_to(dx - ww / 2, dy - hh / 2 + s_)
        c.line_to(dx - ww / 2 + s_ / 2, dy - hh / 2 + s_); c.line_to(dx - ww / 2 + s_ / 2, dy - hh / 2 + s_ / 2); c.line_to(dx - ww / 2 + s_, dy - hh / 2 + s_ / 2)
        c.close_path()
    plate(10, 14, bw, bh, st * 2); c.set_source_rgba(0, 0, 0, 0.5); c.fill()
    plate(0, 0, bw, bh, st * 2)
    g = cairo.LinearGradient(0, -bh / 2, 0, bh / 2); g.add_color_stop_rgb(0, *[min(1, v * 1.04) for v in bg]); g.add_color_stop_rgb(1, *[v * 0.9 for v in bg])
    c.set_source(g); c.fill_preserve(); c.set_source_rgb(*rule); c.set_line_width(6); c.stroke()
    plate(0, 0, bw - 26, bh - 26, st * 1.4); c.set_source_rgba(*rule, 0.9); c.set_line_width(2.5); c.stroke()
    sw = (t * 0.8) % 2.2                                     # brass glint sweeping across
    if sw < 1:
        g = cairo.LinearGradient(-bw / 2 + sw * bw * 1.3 - 160, 0, -bw / 2 + sw * bw * 1.3, 0)
        g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(0.5, 1, 0.95, 0.8, 0.45); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        plate(0, 0, bw, bh, st * 2); c.set_source(g); c.fill()
    text(c, s, 0, size * 0.36, size, col=fg)
    c.restore()
    if sub and t > 0.25:
        a = ease((t - 0.25) / 0.25); sz = 44; sw2 = text_w(c, sub, sz) + 44
        c.save(); c.translate(x, y + bh / 2 + 48)
        c.set_source_rgba(*INK, 0.88 * a); c.rectangle(-sw2 / 2, -sz * 0.78, sw2, sz * 1.3); c.fill()
        c.set_source_rgba(*JADE, a); c.rectangle(-sw2 / 2, -sz * 0.78, sw2, 5); c.fill()
        text(c, sub, 0, sz * 0.25, sz, col=CREAM, alpha=a); c.restore()


def shutter(c, t, dur=0.3):
    """elevator-door transition: two deco panels part from the centre during the first `dur` s of a scene"""
    if t >= dur: return
    k = eout(t / dur); half = W / 2 * (1 - k)
    for side in (-1, 1):
        x0 = 0 if side < 0 else W - half
        c.save(); c.rectangle(x0, 0, half, H); c.clip()
        g = cairo.LinearGradient(x0, 0, x0 + half, 0); g.add_color_stop_rgb(0, *hexc("1B2B5C")); g.add_color_stop_rgb(1, *hexc("0E1838"))
        c.set_source(g); c.paint()
        ex = half if side < 0 else W - half          # inner edge x
        for j in range(5):                           # brass chevrons / stripes on the doors
            c.set_source_rgba(*BRASS, 0.85); c.set_line_width(5)
            xx = ex - side * (30 + j * 34)
            c.move_to(xx, 0); c.line_to(xx, H); c.stroke()
        tex(c, TX["xray"], dx=side * 200); c.paint_with_alpha(0.35)          # textured doors (edge-band check)
        for j in range(4):                           # brass rails on the outer edge too
            xx = (24 + j * 40) if side < 0 else (W - 24 - j * 40)
            c.set_source_rgba(*BRASS, 0.7); c.set_line_width(4); c.move_to(xx, 0); c.line_to(xx, H); c.stroke()
        for j in range(12):
            yy = 160 * j + 80; c.move_to(ex - side * 200, yy); c.line_to(ex - side * 30, yy - 60); c.line_to(ex - side * 30, yy + 60)
            c.close_path(); c.set_source_rgba(*BRASS, 0.35); c.fill()
        c.restore()


def paper(c, t, tint=CREAM):
    """1930s instruction-sheet background: warm paper with fibre texture + faint blueprint grid (no flat edges)"""
    if "paper" not in _BL:
        n = fbm(H, W, octaves=6, seed=21, base=5); n = (n - n.min()) / (n.max() - n.min())
        a = np.ones((H, W, 3), np.float32) * np.array(tint) * 255 * (0.82 + 0.22 * n[..., None])
        yy = np.linspace(-1, 1, H)[:, None]; xx = np.linspace(-1, 1, W)[None, :]
        a *= (1 - 0.22 * (xx ** 2 + 0.5 * yy ** 2))[..., None]
        _BL["paper"] = np.clip(a, 0, 255).astype(np.uint8)
    to_ctx(c, haze(_BL["paper"], t, amt=8).astype(np.uint8))
    c.set_source_rgba(*hexc("5A7FA8"), 0.18); c.set_line_width(2)
    for x in range(-20, W + 40, 60): c.move_to(x + (t * 6) % 60, 0); c.line_to(x + (t * 6) % 60, H)
    for y in range(0, H + 60, 60): c.move_to(0, y); c.line_to(W, y)
    c.stroke()


# stepped Empire State profile: (top floor of band, half-width in units) — simplified, not to scale
PROFILE = [(5, 1.0), (21, 0.8), (25, 0.72), (30, 0.64), (72, 0.5), (81, 0.42), (86, 0.34)]


def tower(c, x, base, fh, unit, floors, t, col=BRASS, glow=True, derrick=True):
    """stepped skyscraper silhouette revealed up to `floors` (0..102); floors 87-102 = the spire/mast"""
    lo = 0; top_y = base
    c.save()
    for hi, hw in PROFILE:
        if floors <= lo: break
        f1 = min(floors, hi); y0 = base - f1 * fh; h = (f1 - lo) * fh; w = hw * unit * 2
        c.rectangle(x - w / 2, y0, w, h)
        g = cairo.LinearGradient(x - w / 2, 0, x + w / 2, 0)
        g.add_color_stop_rgb(0, *hexc("C9B48A")); g.add_color_stop_rgb(0.45, *hexc("F2E3BE")); g.add_color_stop_rgb(1, *hexc("8E7A57"))
        c.set_source(g); c.fill()
        c.set_source_rgba(*INK, 0.35); c.set_line_width(2)
        for k in range(int(f1 - lo) + 1):                 # floor lines
            yy = base - (lo + k) * fh; c.move_to(x - w / 2, yy); c.line_to(x + w / 2, yy)
        c.stroke()
        c.set_source_rgba(*INK, 0.25); c.set_line_width(max(1.5, unit * 0.05))  # window piers
        for k in range(1, int(hw * 10)):
            xx = x - w / 2 + k * w / int(hw * 10); c.move_to(xx, y0); c.line_to(xx, y0 + h)
        c.stroke()
        c.set_source_rgb(*col); c.set_line_width(4); c.rectangle(x - w / 2, y0, w, h); c.stroke()
        lo = hi; top_y = y0
    if floors > 86:                                      # spire / mast
        k = (floors - 86) / 16.0; y_top = base - 86 * fh - 16 * fh * k
        c.move_to(x - 0.2 * unit, base - 86 * fh); c.line_to(x - 0.03 * unit, y_top); c.line_to(x + 0.03 * unit, y_top); c.line_to(x + 0.2 * unit, base - 86 * fh); c.close_path()
        c.set_source_rgb(*hexc("E8DDC4")); c.fill_preserve(); c.set_source_rgb(*col); c.set_line_width(3); c.stroke(); top_y = y_top
    if derrick and 2 < floors < 101:                     # little derrick riding the top floor
        y = top_y; c.set_source_rgb(*RED); c.set_line_width(5)
        c.move_to(x - 30, y); c.line_to(x - 30, y - 70); c.line_to(x + 60 + 10 * math.sin(t * 2), y - 40); c.stroke()
        c.move_to(x + 60 + 10 * math.sin(t * 2), y - 40); c.line_to(x + 60 + 10 * math.sin(t * 2), y - 10 + 6 * math.sin(t * 3)); c.set_line_width(2); c.stroke()
        if glow: P2.sparks(c, t, x + 20, y - 4, alpha=0.8)
    c.restore()
    return top_y


def airship(c, x, y, s, ang=0.0, t=0.0):
    """original generic 1930s airship (silver envelope, fins, gondola)"""
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.save(); c.scale(1, 0.28); c.arc(0, 0, 300, 0, 2 * math.pi); c.restore()
    g = cairo.LinearGradient(0, -90, 0, 90); g.add_color_stop_rgb(0, 0.95, 0.96, 0.98); g.add_color_stop_rgb(0.5, 0.74, 0.77, 0.82); g.add_color_stop_rgb(1, 0.42, 0.45, 0.52)
    c.set_source(g); c.fill()
    c.set_source_rgba(0.3, 0.32, 0.38, 0.5); c.set_line_width(2)
    for k in range(-4, 5):
        c.save(); c.scale(1, 0.28); c.arc(k * 60, 0, 300 * math.sqrt(max(0.01, 1 - (k * 60 / 300) ** 2)) * 0.2 + 1, -math.pi / 2, math.pi / 2); c.restore(); c.stroke()
    c.set_source_rgb(*RED); c.rectangle(-240, -6, 470, 12); c.fill()                     # band
    for sy in (-1, 1):                                                                    # tail fins
        c.move_to(230, sy * 30); c.line_to(330, sy * 110); c.line_to(345, sy * 110); c.line_to(300, sy * 10); c.close_path()
        c.set_source_rgb(0.55, 0.58, 0.64); c.fill()
    c.set_source_rgb(0.3, 0.3, 0.35); rrect(c, -60, 78, 120, 34, 12); c.fill()            # gondola
    c.set_source_rgba(1, 0.85, 0.5, 0.9)
    for k in range(4): c.rectangle(-48 + k * 26, 86, 16, 12); c.fill()
    pr = (t * 30) % (2 * math.pi)                                                         # propeller blur
    c.set_source_rgba(0.2, 0.2, 0.25, 0.6); c.save(); c.translate(-70, 95); c.scale(0.25, 1); c.arc(0, 0, 26 * abs(math.sin(pr)) + 6, 0, 2 * math.pi); c.restore(); c.fill()
    c.restore()


def cart(c, x, y, s, t):
    """manually pushed rail cart carrying steel beams"""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.set_source_rgb(*hexc("6B4A2E")); c.rectangle(-110, -60, 220, 46); c.fill()
    c.set_source_rgb(*BRASS); c.set_line_width(4); c.rectangle(-110, -60, 220, 46); c.stroke()
    for k in range(3):                                   # I-beams
        c.set_source_rgb(*hexc("8D2F23")); c.rectangle(-150, -88 - k * 20, 300, 16); c.fill()
        c.set_source_rgba(0, 0, 0, 0.35); c.rectangle(-150, -80 - k * 20, 300, 3); c.fill()
    for wx in (-70, 70):
        c.set_source_rgb(0.15, 0.15, 0.17); c.arc(wx, -6, 20, 0, 2 * math.pi); c.fill()
        a = t * 14; c.set_source_rgb(*BRASS); c.set_line_width(3)
        c.move_to(wx, -6); c.line_to(wx + 16 * math.cos(a), -6 + 16 * math.sin(a)); c.stroke()
    c.restore()


def floor_section(c, t, cart_x, speed_lines=0.0):
    """cut-away of two storeys of the steel frame with tracks on the floor slab and a cart running along"""
    bg(c, "hine2", HINE2, t, (0.7, 0.5), dim=0.55)
    c.set_source_rgba(*INK, 0.35); c.paint()
    for fy in (1000, 1330):
        c.set_source_rgb(*hexc("8E8676")); c.rectangle(-20, fy, W + 40, 34); c.fill()                # slab
        c.set_source_rgba(1, 1, 1, 0.15); c.rectangle(-20, fy, W + 40, 6); c.fill()
        c.set_source_rgb(*hexc("2C2C30")); c.rectangle(-20, fy - 8, W + 40, 6); c.fill()               # rails
        for k in range(-1, 20): c.rectangle(k * 60 - (t * 40) % 60, fy - 4, 30, 6)
        c.set_source_rgb(*hexc("4A3A2A")); c.fill()
    for x in (90, 540, 990):                                                                        # columns
        c.set_source_rgb(*hexc("7A2A20")); c.rectangle(x - 22, 640, 44, 1380); c.fill()
        c.set_source_rgba(1, 1, 1, 0.18); c.rectangle(x - 22, 640, 8, 1380); c.fill()
        for ry in range(660, 1900, 70): c.set_source_rgba(0.1, 0.05, 0.03, 0.8); c.arc(x, ry, 5, 0, 2 * math.pi); c.fill()
    c.set_source_rgb(*hexc("7A2A20")); c.rectangle(-20, 640, W + 40, 30); c.fill()
    cart(c, cart_x, 992, 1.8, t)
    if speed_lines > 0:
        for k in range(7):
            y = 880 + k * 18; L = 160 + 60 * (k % 3)
            c.set_source_rgba(1, 1, 1, 0.6 * speed_lines); c.set_line_width(4); c.move_to(cart_x - 220, y); c.line_to(cart_x - 220 - L, y); c.stroke()
    text(c, "(simplified)", W / 2, 1235, 28, col=WHITE, stroke=6, alpha=0.8)


def parts_sheet(c, t, k, missing=0.0):
    """flat-pack style parts list for a skyscraper (the joke: theirs had nothing missing)"""
    paper(c, t)
    text(c, "ASSEMBLY SHEET", W / 2, 650, 60, col=INK)
    c.set_source_rgb(*INK); c.set_line_width(4); c.move_to(160, 680); c.line_to(W - 160, 680); c.stroke()
    items = [("COLUMN", "C-34", 0), ("GIRDER", "G-12", 1), ("BEAM", "B-7", 2), ("RIVET", "×1000s", 3)]
    for name, code, j in items:
        a = ease((k - j * 0.18) / 0.3)
        if a <= 0: continue
        y = 790 + j * 120; x = 200 - (1 - a) * 200
        c.set_source_rgba(*hexc("8D2F23"), a); c.rectangle(x, y - 34, 260 if j < 3 else 40, 40 if j < 3 else 40); c.fill()
        if j < 3:
            c.set_source_rgba(0, 0, 0, 0.3 * a); c.rectangle(x, y - 18, 260, 6); c.fill()
        text(c, name, 520, y, 46, col=INK, align="left", alpha=a)
        c.set_source_rgba(*JADE, a); rrect(c, 820, y - 40, 150, 52, 10); c.fill()
        text(c, code, 895, y - 1, 30 if len(code) < 5 else 24, col=INK, alpha=a)
    if missing > 0:                                       # "screw x1 - MISSING" (his furniture, not theirs)
        a = ease(missing / 0.3); y = 1300
        c.set_source_rgba(*RED, a); c.set_line_width(6); rrect(c, 160, y - 70, W - 320, 110, 18); c.stroke()
        c.save(); c.translate(250, y - 15); c.rotate(0.6)
        c.set_source_rgba(0.35, 0.35, 0.38, a); c.rectangle(-8, -40, 16, 70); c.fill(); c.rectangle(-24, -48, 48, 14); c.fill(); c.restore()
        text(c, "SCREW ×1  —  MISSING", 590, y + 4, 48, col=RED, alpha=a)


def inbox(c, t, k):
    """an invented generic inbox card: unread counter climbing, 'answered this week: 4½' gag"""
    bg(c, "sunset", SUNSET, t, (0.4, 0.5), dim=0.5)
    c.save(); c.translate(W / 2, 960); s = back(min(1, k / 0.35)); c.scale(s, s)
    c.set_source_rgba(0, 0, 0, 0.45); rrect(c, -380 + 14, -330 + 18, 760, 660, 40); c.fill()
    c.set_source_rgb(*CREAM); rrect(c, -380, -330, 760, 660, 40); c.fill()
    c.set_source_rgb(*BRASS); c.set_line_width(6); rrect(c, -380, -330, 760, 660, 40); c.stroke()
    text(c, "INBOX", -330, -250, 54, col=INK, align="left")
    c.set_source_rgb(*RED); rrect(c, 90, -300, 250, 74, 37); c.fill()
    text(c, counter(t - 0.2, 312, 1284, 2.0) + " NEW", 215, -248, 38, col=WHITE)
    for j in range(4):
        y = -150 + j * 100; a = ease((t - 0.15 * j) / 0.3)
        c.set_source_rgba(*INK, 0.1 * a); rrect(c, -330, y - 36, 660, 78, 14); c.fill()
        c.set_source_rgba(*BRASS, a); c.rectangle(-300, y - 18, 64, 42); c.fill()
        c.set_source_rgba(*INK, a); c.set_line_width(3); c.move_to(-300, y - 18); c.line_to(-268, y + 6); c.line_to(-236, y - 18); c.stroke()
        c.set_source_rgba(*INK, 0.3 * a); c.rectangle(-200, y - 12, 380 - j * 40, 14); c.fill(); c.rectangle(-200, y + 12, 250, 10); c.fill()
    text(c, "ANSWERED THIS WEEK: 0", 0, 300, 40, col=RED)
    c.restore()


def phone_vs(c, t, k):
    """bar race: a typical 2-year phone contract vs the 410-day build"""
    bg(c, "hook", HOOK, t, (0.5, 0.35), dim=0.5)
    rows = (("PHONE CONTRACT", 730, 1.0, hexc("9F8CFF"), "~2 YEARS"), ("EMPIRE STATE", 410, 410 / 730, JADE, "410 DAYS"))
    for j, (lab, days, frac, col, tag) in enumerate(rows):
        y = 760 + j * 250; x0, w = 120, 840; a = ease((k - j * 0.15) / 0.3)
        if a <= 0: continue
        c.set_source_rgba(*INK, 0.82 * a); c.rectangle(x0 - 24, y - 80, w + 48, 200); c.fill()
        c.set_source_rgba(*BRASS, a); c.rectangle(x0 - 24, y - 80, w + 48, 5); c.fill()
        text(c, lab, x0, y - 18, 44, col=CREAM, align="left", alpha=a)
        c.set_source_rgba(1, 1, 1, 0.12 * a); c.rectangle(x0, y + 10, w, 66); c.fill()
        c.set_source_rgba(*col, a); c.rectangle(x0, y + 10, max(8, w * frac * eout((k - j * 0.15) / 0.8)), 66); c.fill()
        text(c, tag, x0 + w, y - 18, 40, col=col, align="right", alpha=a)


def lowered(c, a, dy, t):
    """photo/clip frame pushed DOWN by dy px with extra sky painted above it (so a spire tip that sits at the very top
    of the source lands mid-frame, clear of the badge/title zone). The sky continues the frame's own top colour."""
    top = a[:40].reshape(-1, 3).mean(0); hi = top * np.array([0.78, 0.84, 0.95])
    sky = np.empty((H, W, 3), np.float32); k = np.clip(np.arange(H) / max(1, dy), 0, 1)[:, None, None]
    sky[:] = hi * (1 - k) + top * k
    out = sky.copy(); out[dy:] = a[:H - dy]
    m = np.clip((np.arange(H) - dy) / 160.0, 0, 1)[:, None, None]
    out = sky * (1 - m) + out * m
    to_ctx(c, finish(out, t, vign=0.3))


# ---------------- scenes (one per line) ----------------
def hook_frame(c, t, z=1.0):
    a = HOOK.kb(min(1, t / 5.0), 1.0, 1.1, (0.5, 0.42), (0.5, 0.36))
    c.save(); cam(c, z, W / 2, 900); to_ctx(c, finish(a, t, vign=0.4)); c.restore()
    P1.dust(c, t, col=(1, 0.95, 0.8), alpha=0.22, speed=18, size=3)
    deco_title(c, "BUILT IN", W / 2, 330, 80, t + 1, bg=CREAM)
    deco_title(c, "410 DAYS?!", W / 2, 480, 130, t + 1, bg=JADE)


def s0(c, t, d):  # F hook "They built the Empire State Building in 410 days."
    if t < 1.4: hook_frame(c, t, z=punch(t, 0.9, 0.06))
    else:
        tt = t - 1.4
        to_ctx(c, finish(CA.at(tt).astype(np.float32), tt, vign=0.3))
        deco_title(c, "410 DAYS?!", W / 2, 420, 120, tt + 1, bg=JADE)
        c.set_source_rgba(*INK, 0.85); rrect(c, 300, 1010, 480, 150, 20); c.fill()
        c.set_source_rgb(*BRASS); c.set_line_width(4); rrect(c, 300, 1010, 480, 150, 20); c.stroke()
        text(c, "DAY " + counter(tt - 0.6, 0, 410, 1.6), W / 2, 1110, 78, col=CREAM)
    source_tag(c, "Photo: Dllu / CC BY-SA 4.0" if t < 1.4 else "Video: the Dronalist / CC BY 3.0", t - 0.2 if t < 1.4 else t - 1.5)


def s1(c, t, d):  # M "410 days? My phone contract lasts longer than that."
    phone_vs(c, t, max(0.0, (t - 0.4) / 0.9))
    deco_title(c, "410 DAYS?", W / 2, 420, 120, t - 0.05, bg=CREAM)


def s2(c, t, d):  # F "102 floors, in just over a year. And the very top was built for something that never worked."
    if t < 3.4:
        bg(c, "street", STREET, t, (0.5, 0.4), dim=0.55)
        fl = 102 * eout(t / 2.6)
        tower(c, W / 2, 1880, 11.0, 210, fl, t)
        deco_title(c, counter(t, 0, 102, 2.6) + " FLOORS", W / 2, 420, 110, t - 0.05, bg=CREAM)
        if t > 2.0: deco_title(c, "IN 13 MONTHS", W / 2, 590, 64, t - 2.0, bg=JADE)
        text(c, "(simplified, not to scale)", W / 2, 1255, 26, col=WHITE, stroke=6, alpha=0.8)
    else:
        tt = t - 3.4; a = STREET.kb(tt / (d - 3.4), 1.05, 1.3, (0.55, 0.45), (0.6, 0.12)); to_ctx(c, finish(a, tt, vign=0.4))
        deco_title(c, "THE VERY TOP…", W / 2, 420, 100, tt - 0.05, bg=CREAM)
        if tt > 2.4: deco_title(c, "NEVER WORKED", W / 2, 580, 80, tt - 2.4, bg=RED, fg=CREAM)
        source_tag(c, "Photo: Carlos Delgado / CC BY-SA 3.0 · Sources: Britannica, ENR", tt - 0.3, size=22)


def s3(c, t, d):  # M "Sure. So what's the catch?"
    to_ctx(c, finish(CB.at(t).astype(np.float32), t, vign=0.3))
    deco_title(c, "WHAT'S THE CATCH?", W / 2, 430, 96, t - 0.2, bg=CREAM)
    # magnifying glass sweeping over the skyline
    x = 300 + 480 * ease(t / d); y = 900 + 60 * math.sin(t * 3)
    c.set_source_rgba(1, 1, 1, 0.15); c.arc(x, y, 120, 0, 2 * math.pi); c.fill()
    c.set_source_rgb(*BRASS); c.set_line_width(14); c.arc(x, y, 120, 0, 2 * math.pi); c.stroke()
    c.set_line_width(26); c.move_to(x + 85, y + 85); c.line_to(x + 190, y + 190); c.stroke()
    source_tag(c, "Video: the Dronalist / CC BY 3.0", t - 0.2)


def s4(c, t, d):  # F "No catch. Just a clever system. The steel arrived cut and labelled, like flat-pack furniture."
    if t < 2.1:
        a = HINE1.kb(t / 2.1, 1.0, 1.12, (0.8, 0.5), (0.85, 0.45)); to_ctx(c, finish(a, t, archival=True, vign=0.45))
        deco_title(c, "A CLEVER SYSTEM", W / 2, 420, 100, t - 0.7, bg=CREAM)
        label(c, "1930", 1110, t - 0.2, x=200, size=46, bg=BRASS, fg=INK)
        source_tag(c, "Photo: Lewis Hine, 1930 (CC0, The Met)", t - 0.2)
    else:
        tt = t - 2.1; parts_sheet(c, tt, ease(tt / 1.8) * 1.2)
        deco_title(c, "CUT + LABELLED", W / 2, 420, 100, tt - 0.05, bg=JADE)
        if tt > 2.3: deco_title(c, "LIKE FLAT-PACK", W / 2, 1150, 84, tt - 2.3, bg=CREAM)
        source_tag(c, "Source: History.com (steel coded and delivered in order)", tt - 0.4, size=22)


def s5(c, t, d):  # M "Flat-pack? Mine always comes with one screw missing."
    parts_sheet(c, t + 4, 1.2, missing=max(0, t - 0.9))
    deco_title(c, "FLAT-PACK?", W / 2, 420, 120, t - 0.05, bg=CREAM)


def s6(c, t, d):  # F "Theirs was 57,000 tons of steel. And little railway carts on every floor zipped it to the crews."
    if t < 3.8:
        to_ctx(c, finish(CB.at(2.0 + t * 0.6).astype(np.float32), t, vign=0.3))
        deco_title(c, counter(t - 0.8, 0, 57000, 1.6), W / 2, 420, 140, t - 0.05, bg=CREAM, sub="TONS OF STEEL")
        source_tag(c, "Video: the Dronalist / CC BY 3.0 · Source: ENR", t - 0.3)
    else:
        tt = t - 3.8; x = lerp(-200, 760, eout(tt / 2.2)) if tt < 2.2 else 760 + 20 * math.sin(tt * 4)
        floor_section(c, tt, x)
        deco_title(c, "RAIL CARTS", W / 2, 420, 120, tt - 0.4, bg=JADE)
        if tt > 2.0: deco_title(c, "ON EVERY FLOOR", W / 2, 580, 70, tt - 2.0, bg=CREAM)
        source_tag(c, "Sources: History.com, ENR", tt - 0.4)


def s7(c, t, d):  # M "Railway carts. Inside a building."
    c.save(); cam(c, 1.25, 540, 960)
    x = lerp(-300, 1400, ease(t / d)); floor_section(c, t + 3, x, speed_lines=1.0)
    c.restore()
    deco_title(c, "INSIDE A BUILDING?!", W / 2, 420, 90, t - 0.05, bg=CREAM)


def s8(c, t, d):  # F "Over 3,000 workers at the peak."
    a = MAST.kb(t / d, 1.0, 1.15, (0.45, 0.5), (0.5, 0.6)); to_ctx(c, finish(a, t, archival=True, vign=0.45))
    deco_title(c, counter(t - 0.2, 0, 3000, 1.2) + "+", W / 2, 420, 150, t - 0.05, bg=CREAM, sub="WORKERS AT THE PEAK")
    source_tag(c, "Photo: Lewis Hine, 1931 (PD) · Source: History.com", t - 0.3, size=22)


def s9(c, t, d):  # F "And the frame climbed four and a half floors a week."
    paper(c, t)
    wk = min(4, int(max(0, t - 1.2) / 0.55) + (1 if t > 1.2 else 0))
    fl = 20 + 4.5 * wk + 4.5 * ease(((t - 1.2) % 0.55) / 0.4) * (1 if 0 < wk < 4 else 0)
    tower(c, 330, 1760, 24.0, 250, min(102, fl), t)
    for j in range(wk):
        a = ease((t - 1.2 - j * 0.55) / 0.3); y = 760 + j * 110
        c.set_source_rgba(*INK, 0.9 * a); rrect(c, 640, y - 46, 360, 80, 14); c.fill()
        text(c, f"WEEK {j + 1}: +4½", 820, y + 10, 40, col=JADE, alpha=a)
    deco_title(c, "4½ FLOORS A WEEK", W / 2, 420, 100, t - 1.2, bg=JADE)
    source_tag(c, "Source: History.com (4½ stories per week)", t - 1.0, y=1250)


def s10(c, t, d):  # M "Four and a half floors? I can't answer four and a half emails a week."
    inbox(c, t, t)
    deco_title(c, "4½ EMAILS?", W / 2, 420, 120, t - 1.4, bg=CREAM) if t > 1.4 else deco_title(c, "4½ FLOORS?", W / 2, 420, 120, t, bg=CREAM)


def s11(c, t, d):  # M "Fine, it's impressive. So what never worked?"
    to_ctx(c, finish(CA.at(1.5 + t * 0.8).astype(np.float32), t, vign=0.3))
    deco_title(c, "IMPRESSIVE.", W / 2, 420, 110, t - 0.05, bg=CREAM)
    if t > 1.0: deco_title(c, "WHAT NEVER WORKED?", W / 2, 580, 76, t - 1.0, bg=RED, fg=CREAM)


def s12(c, t, d):  # F "The tip. That spire was designed as a parking spot for airships."
    a = SPIRE.kb(t / d, 1.0, 1.06, (0.5, 0.45), (0.5, 0.45))
    a = haze(a * 1.1 + np.array([26, 30, 52]), t, amt=40)                   # dark night photo: lift + strong edge mist
    to_ctx(c, finish(a, t, vign=0.0))
    tx, ty = 335, 690
    if t > 0.2:
        for j in range(2):
            ph = (t * 0.9 + j * 0.5) % 1.0; c.set_source_rgba(*JADE, 0.7 * (1 - ph)); c.set_line_width(5); c.arc(tx, ty, 30 + 70 * ph, 0, 2 * math.pi); c.stroke()
    if t > 2.2:
        k = eout((t - 2.2) / 1.6); airship(c, lerp(1500, tx + 300, k), ty + 20, 0.9, ang=-0.05 * (1 - k), t=t)
    deco_title(c, "THE TIP", W / 2, 420, 120, t - 0.05, bg=CREAM)
    if t > 2.3: deco_title(c, "AN AIRSHIP DOCK", W / 2, 1150, 84, t - 2.3, bg=JADE)
    source_tag(c, "Photo: Eric Johnson / CC BY-SA 3.0 · Source: Smithsonian", t - 0.3, size=22)


def s13(c, t, d):  # M "Parking. For airships."
    a = COLEMAN.kb(t / d, 1.25, 1.35, (0.55, 0.2), (0.55, 0.18)); to_ctx(c, finish(a, t, archival=True, vign=0.4))
    # a big deco "P" sign
    c.save(); c.translate(820, 1000); s = back(min(1, t / 0.25)); c.scale(s, s)
    c.set_source_rgb(*hexc("2257B8")); rrect(c, -90, -90, 180, 180, 20); c.fill()
    c.set_source_rgb(1, 1, 1); c.set_line_width(8); rrect(c, -80, -80, 160, 160, 16); c.stroke()
    text(c, "P", 0, 50, 140, col=WHITE); c.restore()
    deco_title(c, "PARKING?!", W / 2, 420, 140, t - 0.02, bg=CREAM)
    source_tag(c, "Art: Glenn O. Coleman, 'Dirigible Over New York' (PD)", t - 0.1, size=22)


def s14(c, t, d):  # F "Passengers would step off, over 1,000 feet up. But the wind had other ideas."
    lowered(c, HOOK.kb(0, 1.0, 1.0, (0.5, 0.42), (0.5, 0.42)), 480, t)
    tipx, tipy = 536, 740
    wind = ease((t - 3.9) / 0.6)
    ang = -0.35 * wind + 0.05 * math.sin(t * 6) * wind; dx = 380 * wind ** 1.5; dy = -120 * wind
    ax, ay = tipx + 290 + dx, tipy + 40 + dy
    if wind < 0.4:                                      # gangplank to the mast
        c.set_source_rgba(*BRASS, 1 - wind * 2.5); c.set_line_width(6); c.move_to(tipx, tipy + 30); c.line_to(ax - 150, ay + 70); c.stroke()
    airship(c, ax, ay, 0.75, ang=ang, t=t)
    if wind > 0:
        for k in range(9):
            ph = (t * 1.6 + k / 9) % 1.0; y = 300 + k * 110; x = lerp(-200, W + 200, ph)
            c.set_source_rgba(1, 1, 1, 0.55 * wind * math.sin(math.pi * ph)); c.set_line_width(5)
            c.move_to(x, y); c.curve_to(x + 80, y - 30, x + 160, y + 30, x + 260, y); c.stroke()
    if t > 1.5: label(c, "1,000+ FT UP", 1000, t - 1.5, x=300, size=48, bg=BRASS, fg=INK)
    deco_title(c, "STEP OFF HERE?", W / 2, 420, 100, t - 0.05, bg=CREAM) if t < 3.9 else deco_title(c, "THE WIND SAID NO", W / 2, 420, 100, t - 3.9, bg=RED, fg=CREAM)
    source_tag(c, "Photo: Dllu / CC BY-SA 4.0 · Sources: History.com, Smithsonian", t - 0.3, size=21)


def s15(c, t, d):  # M "Did anyone ever actually park there?"
    a = STREET.kb(t / d, 1.25, 1.4, (0.6, 0.12), (0.6, 0.08)); to_ctx(c, finish(a, t, vign=0.4))
    deco_title(c, "EVER PARKED?", W / 2, 420, 120, t - 0.3, bg=CREAM)
    source_tag(c, "Photo: Carlos Delgado / CC BY-SA 3.0", t - 0.2)


def s16(c, t, d):  # F "One small airship, in 1931. For about three minutes."
    lowered(c, CB.at(1.0 + t * 0.4).astype(np.float32), 520, t)
    k = eout(t / 1.2); airship(c, lerp(1500, 770, k), lerp(560, 660, k), 0.45, t=t)
    label(c, "SEPT 1931", 1100, t - 1.3, x=300, size=50, bg=BRASS, fg=INK)
    if t > 2.5:
        tt = t - 2.5; stopwatch(c, 760, 1020, 120, min(tt, 1.4) * 1.6, run=tt < 1.4, col=BRASS)
        secs = int(min(180, tt / 1.4 * 180)); deco_title(c, f"{secs // 60}:{secs % 60:02d}", W / 2, 420, 140, tt + 1, bg=JADE)
    else: deco_title(c, "ONE AIRSHIP", W / 2, 420, 110, t - 0.05, bg=CREAM)
    source_tag(c, "Source: Smithsonian (Sept 1931, about three minutes)", t - 0.3, size=22)


def s17(c, t, d):  # M "[laughs] So, 410 days to build it, and three minutes of parking."
    if t < 2.6:
        bg(c, "hook", HOOK, t, (0.5, 0.35), dim=0.55)
        deco_title(c, "410 DAYS", W / 2, 720, 150, t - 0.85, bg=CREAM, sub="TO BUILD IT")
        if t > 2.0: deco_title(c, "3 MINUTES", W / 2, 1080, 130, t - 2.0, bg=JADE, sub="OF PARKING")
    else:  # loop back to the hook image
        hook_frame(c, 0.5 + (t - 2.6) * 0.3, z=lerp(1.08, 1.0, eout((t - 2.6) / 0.6)))


def s_end(c, t, d):
    to_ctx(c, finish(CA.at(min(3.0, t)).astype(np.float32), t, vign=0.35))
    end_card_logo(c, t, W / 2, 760, 270, LOGO)
    deco_title(c, "FOLLOW", W / 2, 1180, 120, t - 0.6, bg=JADE)
    if t > 1.0: text(c, "a new wonder every day", W / 2, 1320, 52, col=WHITE, stroke=8, alpha=ease((t - 1.0) / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s_end]
assert len(SCENES) == len(STARTS)
NO_SHUT = (5, 7, 10, 13, 18)


def frame(c, gt, surf):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    c.save()
    if i > 0 and t < 0.3:
        z = 1 + 0.05 * (1 - eout(t / 0.3)); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[i](c, t, d)
    c.restore()
    if i > 0 and i not in NO_SHUT: shutter(c, t)
    badge(c, gt)
    if i < len(meta):
        captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    ev = [("boom", 0.0), ("pop", 0.25), ("pop", 0.4), ("clank", 0.9)]
    ev += [("whoosh", x - 0.05) for x in s[1:] if x not in [s[i] for i in NO_SHUT]]
    ev += [("tick", s[0] + 2.0 + k * 0.13) for k in range(12)] + [("ding", s[0] + 3.6)]
    ev += [("pop", s[1]), ("thunk", s[1] + 1.3), ("thunk", s[1] + 1.45)]
    ev += [("pop", s[2])] + [("clank", s[2] + 0.2 + k * 0.4) for k in range(6)] + [("ding", s[2] + 2.6), ("pop", s[2] + 2.0), ("pop", s[2] + 3.4), ("boom", s[2] + 5.8)]
    ev += [("pop", s[3] + 0.2), ("pop", s[4] + 0.7), ("clank", s[4] + 2.2), ("clank", s[4] + 2.4), ("clank", s[4] + 2.6), ("pop", s[4] + 4.4)]
    ev += [("pop", s[5]), ("thunk", s[5] + 0.9)]
    ev += [("pop", s[6])] + [("tick", s[6] + 0.8 + k * 0.12) for k in range(13)] + [("clank", s[6] + 3.8), ("thunk", s[6] + 4.2), ("clank", s[6] + 6.0)]
    ev += [("pop", s[7]), ("clank", s[7] + 0.8)]
    ev += [("pop", s[8])] + [("tick", s[8] + 0.2 + k * 0.1) for k in range(10)]
    ev += [("pop", s[9] + 1.2)] + [("clank", s[9] + 1.2 + k * 0.55) for k in range(4)]
    ev += [("pop", s[10] + 0.1), ("pop", s[10] + 1.4), ("thunk", s[10] + 2.6)]
    ev += [("pop", s[11]), ("pop", s[11] + 1.0)]
    ev += [("pop", s[12]), ("boom", s[12] + 2.2), ("pop", s[12] + 2.3)]
    ev += [("pop", s[13]), ("thunk", s[13] + 0.1)]
    ev += [("pop", s[14]), ("pop", s[14] + 1.5), ("whoosh", s[14] + 3.9), ("pop", s[14] + 3.9)]
    ev += [("pop", s[15] + 0.3), ("pop", s[16]), ("pop", s[16] + 1.3)] + [("tick", s[16] + 2.5 + k * 0.14) for k in range(10)] + [("ding", s[16] + 3.9)]
    ev += [("boom", s[17] + 0.85), ("ding", s[17] + 2.0), ("thunk", s[17] + 2.6), ("pop", s[18] + 0.6)]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]:
            frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events(), "music_style": "swing"}, open("events.json", "w"))
        a, b = (int(v) for v in sys.argv[2:4]) if len(sys.argv) > 3 else (0, int(math.ceil(TOTAL * FPS)))
        out = sys.argv[4] if len(sys.argv) > 4 else "video.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a, b):
            frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", a, b, "total", TOTAL)
