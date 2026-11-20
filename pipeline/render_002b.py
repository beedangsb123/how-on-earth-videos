"""Video 002b — Hoover Dam remake: real photos (Wikimedia Commons / NARA / USBR) + globe zoom + animated overlays.
usage (in work dir with meta.json from tts2.py and media/ from fetch_media.py):
  python render_002b.py still <t> <out.png>   |   python render_002b.py full"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import globe as GL
import render_002 as R2   # reuse the animated diagrams (gorge+tunnels, cracks, x-ray blocks, grout)

meta = json.load(open("meta.json"))
PAD = 0.22
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"] + PAD
DURS = [m["dur"] + PAD for m in meta]; DURS[-1] += 0.3
TOTAL = STARTS[-1] + DURS[-1]


def M(prefix):
    return sorted(glob.glob(f"media/{prefix}*"))[0]


# ---------------- photos ----------------
LUT_THERM = (np.array([thermal_rgb(i / 255) for i in range(256)]) * 255).astype(np.float32)
_rng = np.random.default_rng(7)
GRAIN = [(_rng.standard_normal((H // 2, W // 2)) * 6).astype(np.float32) for _ in range(3)]


class Photo:
    def __init__(self, path, archival=False, maxz=1.35):
        im = Image.open(path).convert("RGB")
        r = max(W * maxz / im.width, H * maxz / im.height)
        self.im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
        self.maxz = maxz; self.archival = archival

    def kb(self, k, z0=1.0, z1=1.15, f0=(0.5, 0.5), f1=(0.5, 0.5)):
        """Ken Burns: k 0..1 -> numpy HxWx3 float"""
        e = ease(k); z = lerp(z0, z1, e); fx = lerp(f0[0], f1[0], e); fy = lerp(f0[1], f1[1], e)
        cw = W * self.maxz / z; ch = H * self.maxz / z
        cx = min(max(fx * self.im.width, cw / 2), self.im.width - cw / 2)
        cy = min(max(fy * self.im.height, ch / 2), self.im.height - ch / 2)
        a = np.asarray(self.im.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)), np.float32)
        if self.archival:  # warm sepia + film grain + vignette ("1930s photo" look)
            l = a.mean(2, keepdims=True)
            a = l * np.array([1.08, 0.96, 0.78]) + 8
        return a


def finish(a, t, archival=False, heat=0.0, xray=0.0, vign=0.35):
    if heat > 0:
        l = a.mean(2).clip(0, 255).astype(np.uint8)
        th = LUT_THERM[np.clip(l.astype(np.int32) + 40, 0, 255)]
        a = a * (1 - heat * 0.8) + th * heat * 0.8
    if xray > 0:
        l = a.mean(2, keepdims=True)
        a = a * (1 - xray) + xray * (np.array([0.25, 0.55, 0.95]) * l + np.array([10, 30, 70]))
    if archival:
        g = GRAIN[int(t * 12) % 3]; a = a + np.kron(g, np.ones((2, 2)))[..., None]
    if vign:
        yy = np.linspace(-1, 1, H)[:, None]; xx = np.linspace(-1, 1, W)[None, :]
        a = a * (1 - vign * 0.5 * (xx ** 2 + 0.6 * yy ** 2))[..., None]
    return np.clip(a, 0, 255).astype(np.uint8)


def to_ctx(c, a):
    s = to_surface(a.astype(np.float32) / 255); c.set_source_surface(s, 0, 0); c.paint()


AER = Photo(M("Aerial_view_Hoover"))                 # Mariordo, CC BY-SA 4.0
WIDE = Photo(M("Hoover_Dam_Aerial_View2"))           # Laslovarga, CC BY-SA 3.0
TOWER = Photo(M("Hoover_Dam__Nevada"))               # Dietmar Rabich, CC BY-SA 4.0
FORMS = Photo(M("Damforms"), True)                   # USBR, public domain
TUNNELS = Photo(M("Looking_upstream_into_Black"), True)   # NARA 293813, PD
WATER1 = Photo(M("First_water"), True)               # NARA 293776, PD
POUR = Photo(M("First_8-cubic"), True)               # NARA 293883, PD
COLS = Photo(M("Looking_upstream_through"), True)    # NARA 293922, PD
GLOBE = GL.Globe()
LOC = (36.016, -114.737)


def project(lat, lon, lat0, lon0, R, cy=H * 0.47):
    p, l, p0, l0 = map(math.radians, (lat, lon, lat0, lon0))
    x = R * math.cos(p) * math.sin(l - l0)
    y = R * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0))
    return W / 2 + x, cy - y


def pin(c, x, y, t, col=(0.9, 0.2, 0.25)):
    if t <= 0: return
    k = back(t / 0.35); c.save(); c.translate(x, y); c.scale(k, k)
    for r in (70, 50):
        c.set_source_rgba(1, 0.8, 0.3, 0.25 * (0.5 + 0.5 * math.sin(t * 6))); c.arc(0, 0, r * (1 + 0.15 * math.sin(t * 6)), 0, 2 * math.pi); c.fill()
    c.set_source_rgba(*col, 1); c.arc(0, -46, 26, 0, 2 * math.pi); c.fill()
    c.move_to(-22, -34); c.line_to(0, 0); c.line_to(22, -34); c.fill()
    c.set_source_rgba(1, 1, 1, 1); c.arc(0, -46, 10, 0, 2 * math.pi); c.fill(); c.restore()


def tag(c, s, t):  # small "1930s PHOTO" / credit tag, bottom-left above the caption zone
    if t <= 0: return
    a = min(1, t / 0.3); c.save()
    w = text_w(c, s, 28) + 30
    c.set_source_rgba(0, 0, 0, 0.45 * a); rrect(c, 70, 1240, w * (28 / 28) * 0.8 + 30, 46, 23); c.fill()
    c.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(24)
    c.move_to(88, 1271); c.set_source_rgba(1, 1, 1, 0.9 * a); c.show_text(s); c.restore()


def steam(c, t, a=0.3): R2.P.steam(c, t, 150, 930, 1250, rise=900, alpha=a)


# ---------------- scenes ----------------
def s0(c, t, d):  # hook: real aerial, thermal pulse, punch-in at 1.2 s
    heat = 0.5 + 0.15 * math.sin(t * 6)
    if t < 1.2: a = AER.kb(t / 1.2, 1.0, 1.08, (0.52, 0.42), (0.52, 0.42))
    else: a = AER.kb((t - 1.2) / 1.5, 1.28, 1.34, (0.5, 0.45), (0.5, 0.46))
    to_ctx(c, finish(a, t, heat=heat)); steam(c, t, 0.28)
    pop_text(c, "STILL COOLING", W / 2, 420, 120, t + 0.4, col=WHITE, stroke=16)
    pop_text(c, "TODAY?!", W / 2, 548, 130, t + 0.4, col=GOLD, stroke=16)


def s1(c, t, d):  # globe zoom to Black Canyon -> handoff into real aerial
    kz = min(1.0, t / 3.3)
    g, R = GLOBE.frame(kz, *LOC, lon_start=LOC[1] + 95)
    if t < 3.3:
        to_ctx(c, g)
        if kz > 0.5: pin(c, W / 2, H * 0.47, (kz - 0.5) * 6)
    else:
        k = (t - 3.3) / 0.8
        ph = finish(WIDE.kb(min(1, (t - 3.3) / 2.9), 1.3, 1.12, (0.42, 0.45), (0.45, 0.42)), t, vign=0.25)
        to_ctx(c, GL.handoff(g, ph, min(1, k)) if k < 1 else ph)
        label(c, "BLACK CANYON", 760, t - 3.6, size=48)
        label(c, "NEVADA / ARIZONA, USA", 850, t - 3.8, size=34, bg=WHITE)
    if t > 1.1:
        pop_text(c, "726 FT", W / 2, 430, 140, t - 1.1, col=GOLD, stroke=16)
        text(c, "221 m of concrete", W / 2, 520, 54, col=WHITE, stroke=10, alpha=ease((t - 1.5) / 0.3))


def s2(c, t, d):  # archival: two impossible problems
    if t < 2.5:
        to_ctx(c, finish(FORMS.kb(t / 2.5, 1.05, 1.2, (0.5, 0.45), (0.5, 0.5)), t, archival=True)); tag(c, "1930s PHOTO · USBR", t - 0.2)
        pop_text(c, "2 IMPOSSIBLE", W / 2, 420, 120, t - 0.3, col=WHITE, stroke=16)
        pop_text(c, "PROBLEMS", W / 2, 540, 120, t - 0.5, col=GOLD, stroke=16)
    else:
        tt = t - 2.5
        to_ctx(c, finish(POUR.kb(tt / 2.8, 1.0, 1.15, (0.5, 0.4), (0.45, 0.5)), t, archival=True)); tag(c, "1930s PHOTO · NARA", tt - 0.2)
        pop_text(c, "#2 IS WILD", W / 2, 440, 130, tt - 0.3, col=GOLD, stroke=16)


def s3(c, t, d):  # problem 1: the river
    if t < 3.2:
        to_ctx(c, finish(TUNNELS.kb(t / 3.2, 1.0, 1.25, (0.5, 0.45), (0.62, 0.55)), t, archival=True)); tag(c, "BLACK CANYON, 1930s · NARA", t - 0.2)
        pop_text(c, "PROBLEM 1", W / 2, 400, 110, t - 0.1, col=WHITE, stroke=16)
        pop_text(c, "THE RIVER", W / 2, 510, 120, t - 0.3, col=hexc("6CC4CF"), stroke=16)
    elif t < 6.6:
        R2.s2(c, (t - 3.2) * 1.35 + 0.4, 8.0)       # animated plan view: 4 tunnels bored, river diverted
    else:
        tt = t - 6.6
        to_ctx(c, finish(WATER1.kb(tt / 2.8, 1.05, 1.2, (0.55, 0.5), (0.5, 0.55)), t, archival=True)); tag(c, "FIRST WATER THROUGH A TUNNEL · NARA", tt - 0.2)
        pop_text(c, "RIVER SENT AROUND", W / 2, 430, 100, tt - 0.2, col=hexc("6CC4CF"), stroke=16)


def s4(c, t, d):  # problem 2: heat
    if t < 3.0:
        to_ctx(c, finish(POUR.kb(t / 3.0, 1.15, 1.3, (0.4, 0.45), (0.5, 0.5)), t, archival=True, heat=0.65 * ease(t / 1.5))); steam(c, t, 0.25)
        pop_text(c, "PROBLEM 2", W / 2, 400, 110, t - 0.1, col=WHITE, stroke=16)
        pop_text(c, "HEAT", W / 2, 520, 140, t - 0.3, col=ORANGE, stroke=16)
    elif t < 6.8:
        tt = t - 3.0
        to_ctx(c, finish(AER.kb(tt / 3.8, 1.1, 1.25, (0.52, 0.42), (0.5, 0.45)), t, heat=0.9)); steam(c, t, 0.3)
        k = ease((tt - 0.8) / 2.2)
        pop_text(c, f"{int(round(125 * k))} YEARS", W / 2, 430, 140, tt - 0.6, col=GOLD, stroke=18)
        text(c, "to cool if poured in one go", W / 2, 520, 50, col=WHITE, stroke=10, alpha=ease((tt - 0.8) / 0.3))
    else:
        R2.s4(c, (t - 6.8) + 3.6, 6.0)            # cracks spreading on the hot dam (animated)


def s5(c, t, d):  # the blocks
    if t < 3.6:
        to_ctx(c, finish(FORMS.kb(t / 3.6, 1.0, 1.3, (0.5, 0.42), (0.52, 0.5)), t, archival=True)); tag(c, "THE BLOCKS, 1930s · USBR", t - 0.2)
        n = int(round(215 * ease((t - 0.3) / 2.4)))
        pop_text(c, f"{n} BLOCKS", W / 2, 430, 130, t - 0.2, col=GOLD, stroke=16)
    else:
        tt = t - 3.6
        to_ctx(c, finish(COLS.kb(tt / 4.0, 1.05, 1.2, (0.5, 0.7), (0.5, 0.35)), t, archival=True)); tag(c, "COLUMN FORMS · NARA", tt - 0.2)
        pop_text(c, "UP TO 60 FT WIDE", W / 2, 420, 100, tt - 0.1, col=GOLD, stroke=16)
        pop_text(c, "5 FT AT A TIME", W / 2, 530, 100, tt - 1.6, col=WHITE, stroke=16)


def s6(c, t, d):  # pipes (x-ray animation)
    R2.s6(c, t, d)


def s7(c, t, d):  # grout -> one solid wall (real photo)
    if t < 3.0:
        R2.s7(c, t * 1.5, 6.0)
    else:
        tt = t - 3.0
        if tt < 0.25: c.set_source_rgba(1, 1, 0.9, 1); c.paint()
        to_ctx(c, finish(AER.kb(tt / 2.2, 1.3, 1.22, (0.5, 0.45), (0.52, 0.44)), t))
        if tt < 0.4: c.set_source_rgba(1, 1, 0.9, 0.7 * (1 - tt / 0.4)); c.paint()
        pop_text(c, "ONE SOLID WALL", W / 2, 430, 120, tt, col=GOLD, stroke=16)


def s8(c, t, d):  # pipes still inside -> globe road SF -> NY
    if t < 3.0:
        to_ctx(c, finish(TOWER.kb(t / 3.0, 1.0, 1.15, (0.5, 0.5), (0.45, 0.55)), t, xray=0.75 * ease(t / 0.8)))
        c.save()
        for j in range(27):
            y = 60 + j * 70 + 6 * math.sin(t * 3 + j)
            c.move_to(-20, y); c.line_to(W + 20, y)
        c.set_source_rgba(*GOLD, 0.25 + 0.2 * math.sin(t * 6)); c.set_line_width(5); c.stroke(); c.restore()
        pop_text(c, "HUNDREDS", W / 2, 400, 140, t - 0.2, col=GOLD, stroke=16)
        pop_text(c, "OF MILES OF PIPE", W / 2, 510, 84, t - 0.4, col=WHITE, stroke=14)
    else:
        tt = t - 3.0; lon0 = -99 + 4 * tt / 4.6; lat0 = 36; R = 1250
        to_ctx(c, GLOBE.render(lat0, lon0, R))
        sf, ny = (37.77, -122.42), (40.71, -74.01)
        k = ease((tt - 0.3) / 2.6); n = 60
        pts = [project(lerp(sf[0], ny[0], i / n) + 4.0 * math.sin(math.pi * i / n), lerp(sf[1], ny[1], i / n), lat0, lon0, R) for i in range(n + 1)]
        m = max(2, int(n * k) + 1)
        def road():
            c.move_to(*pts[0])
            for p in pts[1:m]: c.line_to(*p)
        c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        road(); c.set_source_rgba(0.15, 0.15, 0.15, 0.7); c.set_line_width(26); c.stroke()
        road(); c.set_source_rgba(0.88, 0.86, 0.8, 1); c.set_line_width(18); c.stroke()
        glow_stroke(c, road, GOLD, 4, alpha=0.9, layers=3)
        pin(c, *pts[0], tt - 0.1); pin(c, *pts[-1], tt - 2.8)
        label(c, "SAN FRANCISCO", pts[0][1] + 30, tt - 0.3, x=max(250, pts[0][0] + 60), size=34, bg=WHITE)
        if tt > 2.8: label(c, "NEW YORK", pts[-1][1] - 150, tt - 2.8, x=min(780, pts[-1][0] - 80), size=34, bg=WHITE)
        pop_text(c, "ONE CONCRETE ROAD", W / 2, 420, 100, tt - 0.1, col=GOLD, stroke=16)
        text(c, "16 ft wide · 8 in thick", W / 2, 500, 50, col=WHITE, stroke=10, alpha=ease((tt - 0.8) / 0.3))


def s9(c, t, d):  # loop back to the hook framing
    heat = 0.85 * ease((t - (d - 1.2)) / 1.0)
    a = AER.kb(t / d, 1.12, 1.0, (0.52, 0.42), (0.52, 0.42))
    to_ctx(c, finish(a, t, heat=heat))
    if heat > 0.1: steam(c, t, 0.25 * heat)
    pop_text(c, "NOT ONE PIECE", W / 2, 430, 120, t - 0.1, col=GOLD, stroke=16)


BLUR = None
def s10(c, t, d):
    global BLUR
    if BLUR is None:
        BLUR = np.asarray(Image.fromarray(finish(AER.kb(0, 1.0, 1.0, (0.52, 0.42)), 0)).filter(ImageFilter.GaussianBlur(10)), np.float32)
    to_ctx(c, (BLUR * 0.75).astype(np.uint8))
    k = back(t / 0.4)
    c.save(); s = 0.56 * k; c.translate(W / 2 - 540 * s, 360); c.scale(s, s)
    c.arc(540, 540, 540, 0, 2 * math.pi); c.clip(); c.set_source_surface(R2.LOGO, 0, 0); c.paint(); c.restore()
    c.set_source_rgba(*GOLD, 1); c.set_line_width(10); c.arc(W / 2, 360 + 540 * 0.56 * k, 540 * 0.56 * k, 0, 2 * math.pi); c.stroke()
    pop_text(c, "FOLLOW", W / 2, 1150, 130, t, col=GOLD, stroke=14)
    text(c, "a new wonder every day", W / 2, 1240, 54, col=WHITE, stroke=8, alpha=ease(t / 0.4))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]


def frame(c, gt):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9)
    t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*NAVY); c.paint()
    c.save()
    if i > 0 and t < 0.3:
        z = 1 + 0.08 * (1 - eout(t / 0.3)); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[i](c, t, d)
    c.restore()
    if i < len(SCENES) - 1:
        badge(c); captions(c, meta[i]["cap"], meta[i]["dur"], t)
    if i > 0: wipe(c, t, col=GOLD if i % 2 else ORANGE)


def events():
    s = STARTS
    ev = [("boom", 0.0), ("whoosh", 1.15)] + [("whoosh", x - 0.05) for x in s[1:]]
    ev += [("whoosh", s[1] + 3.3), ("boom", s[1] + 3.4), ("pop", s[1] + 1.1)]
    ev += [("whoosh", s[2] + 2.5), ("whoosh", s[3] + 3.2), ("drill", s[3] + 3.6), ("whoosh", s[3] + 6.6)]
    ev += [("whoosh", s[4] + 3.0)] + [("tick", s[4] + 3.8 + k * 0.1) for k in range(22)] + [("crack", s[4] + 6.9), ("boom", s[4] + 6.9)]
    ev += [("tick", s[5] + 0.3 + k * 0.11) for k in range(22)] + [("whoosh", s[5] + 3.6)] + [("thunk", s[5] + 4.0 + k * 0.3) for k in range(8)]
    ev += [("boom", s[7] + 2.8), ("whoosh", s[7] + 3.0), ("whoosh", s[8] + 3.0), ("pop", s[8] + 3.1), ("pop", s[8] + 5.8), ("pop", s[9] + 0.1), ("pop", s[10])]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "still":
        frame(c, float(sys.argv[2])); surf.write_to_png(sys.argv[3])
    else:
        json.dump({"total": TOTAL, "events": events()}, open("events.json", "w"))
        n = int(math.ceil(TOTAL * FPS))
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
        for f in range(n):
            frame(c, f / FPS); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", n, "total", TOTAL)
