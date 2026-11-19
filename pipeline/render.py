import cairo, json, math, random, subprocess, sys, os
W, H, FPS = 1080, 1920, 30
meta = json.load(open("meta.json"))
PAD = 0.45
GROUND = 1080

def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def lerpc(c1, c2, t): return tuple(lerp(a, b, t) for a, b in zip(c1, c2))
def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

NAVY, MID, BLUE, ORANGE, GOLD = map(hexc, ["0B1026", "1B2B5C", "3E5C9A", "F28C38", "FFC857"])
SAND, SANDD, RED, REDD, GREY = map(hexc, ["D9A066", "B97A45", "C4502A", "8E3518", "8A8F98"])
GROUNDC, GROUNDD, SEA, MUD = map(hexc, ["A0522D", "5A2A14", "2E7FB8", "6B5B4B"])
rnd = random.Random(7)
STARS = [(rnd.uniform(0, W), rnd.uniform(0, 900), rnd.uniform(1, 2.6), rnd.uniform(.3, .9)) for _ in range(120)]

def sky(c, night=0.0):
    g = cairo.LinearGradient(0, 0, 0, GROUND)
    g.add_color_stop_rgb(0, *NAVY)
    g.add_color_stop_rgb(0.5, *lerpc(MID, NAVY, night))
    g.add_color_stop_rgb(0.8, *lerpc(BLUE, MID, night))
    g.add_color_stop_rgb(0.93, *lerpc(ORANGE, BLUE, night))
    g.add_color_stop_rgb(1, *lerpc(GOLD, ORANGE, night))
    c.set_source(g); c.rectangle(0, 0, W, GROUND); c.fill()
    for x, y, r, a in STARS:
        c.set_source_rgba(1, 1, 1, a * (0.4 + 0.6 * night)); c.arc(x, y, r, 0, 2 * math.pi); c.fill()

def ground(c, top=GROUND, col=GROUNDC):
    g = cairo.LinearGradient(0, top, 0, H)
    g.add_color_stop_rgb(0, *col); g.add_color_stop_rgb(1, *GROUNDD)
    c.set_source(g); c.rectangle(0, top, W, H - top); c.fill()

def uluru_path(c, cx, base, w=760, h=260):
    # generic distant silhouette: steep left end, long gently domed top, slope right
    x0 = cx - w / 2
    c.move_to(x0, base)
    c.curve_to(x0 + w*0.02, base - h*0.55, x0 + w*0.06, base - h*0.95, x0 + w*0.18, base - h)
    c.curve_to(x0 + w*0.45, base - h*1.04, x0 + w*0.72, base - h*0.98, x0 + w*0.86, base - h*0.80)
    c.curve_to(x0 + w*0.94, base - h*0.62, x0 + w*0.98, base - h*0.30, x0 + w, base)
    c.close_path()

def uluru(c, cx=W/2, base=GROUND, col=RED, w=760, h=260, alpha=1):
    uluru_path(c, cx, base, w, h)
    g = cairo.LinearGradient(0, base - h, 0, base)
    g.add_color_stop_rgba(0, *lerpc(col, GOLD, 0.25), alpha); g.add_color_stop_rgba(1, *lerpc(col, (0, 0, 0), 0.35), alpha)
    c.set_source(g); c.fill()

def strata_block(c, cx, cy, bw, bh, angle, alpha=1, cols=(SAND, SANDD)):
    c.save(); c.translate(cx, cy); c.rotate(angle)
    n = 14
    for i in range(n):
        c.set_source_rgba(*(cols[i % 2]), alpha)
        c.rectangle(-bw/2, -bh/2 + i * bh / n, bw, bh / n + 1); c.fill()
    c.restore()

def fam(s): return "Montserrat" if set(s) & set("ṉṟṯ") else "Poppins"
def text(c, s, x, y, size, col=(1, 1, 1), weight=cairo.FONT_WEIGHT_BOLD, align="center", alpha=1, stroke=0):
    c.select_font_face(fam(s), cairo.FONT_SLANT_NORMAL, weight)
    c.set_font_size(size)
    ext = c.text_extents(s)
    xx = x - ext.x_advance / 2 if align == "center" else x
    c.move_to(xx, y); c.text_path(s)
    if stroke:
        c.set_source_rgba(0, 0, 0, 0.85 * alpha); c.set_line_width(stroke); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgba(*col, alpha); c.fill()
    return ext.x_advance

def label(c, s, y, alpha):
    c.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(46)
    w = c.text_extents(s).x_advance + 60
    c.set_source_rgba(*GOLD, 0.95 * alpha)
    r = 34; x = W/2 - w/2
    c.new_sub_path(); c.arc(x + r, y + r, r, math.pi/2, 3*math.pi/2); c.arc(x + w - r, y + r, r, -math.pi/2, math.pi/2); c.close_path(); c.fill()
    text(c, s, W/2, y + 50, 46, col=NAVY, alpha=alpha)

def badge(c):
    text(c, "HOW ON EARTH?", W/2, 150, 44, col=(1, 1, 1), alpha=0.9)

# ---------- captions ----------
def chunks(line, dur):
    words = line.split(); out = []; cur = []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[-1] in ".,?!":
            out.append(" ".join(cur)); cur = []
    if cur: out.append(" ".join(cur))
    total = sum(len(x) + 3 for x in out); t = 0; res = []
    for x in out:
        d = dur * (len(x) + 3) / total; res.append((t, t + d, x)); t += d
    return res

def captions(c, line, dur, t):
    for a, b, s in chunks(line, dur):
        if a <= t < b or (t >= dur and s == chunks(line, dur)[-1][2]):
            k = ease((t - a) / 0.12)
            c.save(); c.translate(W/2, 1430); sc = 0.9 + 0.1 * k; c.scale(sc, sc)
            size = 80
            c.select_font_face(fam(s), cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
            wdt = c.text_extents(s).x_advance
            if wdt > 860: size = size * 860 / wdt
            text(c, s, 0, 0, size, col=(1, 1, 1), stroke=14)
            c.restore(); return

# ---------- scenes ----------
def s0(c, t, d):  # hook: x-ray reveal underground
    sky(c); ground(c)
    k = ease((t - 2.2) / 1.6)
    if k > 0:
        c.save(); c.rectangle(0, GROUND, W, H - GROUND); c.clip()
        strata_block(c, W/2 + 20, GROUND + 700, 1400, 640, math.radians(85), alpha=0.85 * k, cols=(RED, REDD))
        c.restore()
        text(c, "IT KEEPS GOING DOWN", W/2, 1690, 54, col=GOLD, alpha=k, stroke=10)
        bob = 10 * math.sin(t * 5)
        c.set_source_rgba(*GOLD, k); c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(W/2 - 40, 1730 + bob); c.line_to(W/2, 1770 + bob); c.line_to(W/2 + 40, 1730 + bob); c.stroke()
    uluru(c)
    badge(c)

def s1(c, t, d):  # mountains rise
    sky(c, 0.2); ground(c)
    k = ease(t / 3.0)
    for i, (x, h, w) in enumerate([(200, 520, 520), (560, 700, 620), (900, 560, 520)]):
        hh = h * k
        c.move_to(x - w/2, GROUND); c.line_to(x, GROUND - hh); c.line_to(x + w/2, GROUND); c.close_path()
        g = cairo.LinearGradient(0, GROUND - hh, 0, GROUND)
        g.add_color_stop_rgb(0, *hexc("C9B8B0")); g.add_color_stop_rgb(1, *hexc("6E5A63"))
        c.set_source(g); c.fill()
        # snow-ish granite highlight
        c.move_to(x, GROUND - hh); c.line_to(x - w*0.1*k, GROUND - hh*0.82); c.line_to(x + w*0.1*k, GROUND - hh*0.82); c.close_path()
        c.set_source_rgba(1, 1, 1, 0.5); c.fill()
    label(c, "550 MILLION YEARS AGO", 260, ease(t / 0.6)); badge(c)

def s2(c, t, d):  # erosion → fans
    sky(c, 0.5); ground(c)
    shrink = 1 - 0.35 * ease(t / d)
    for x, h, w in [(200, 520, 520), (560, 700, 620), (900, 560, 520)]:
        hh = h * shrink
        c.move_to(x - w/2, GROUND); c.line_to(x, GROUND - hh); c.line_to(x + w/2, GROUND); c.close_path()
        c.set_source_rgb(*hexc("8C7880")); c.fill()
    # rain
    c.set_source_rgba(0.75, 0.85, 1, 0.55); c.set_line_width(3)
    for i in range(90):
        x = (i * 97 + 13) % W; y = ((i * 211 + t * 900) % 900) + 200
        c.move_to(x, y); c.line_to(x - 10, y + 40); c.stroke()
    # fan growing at base
    k = ease(t / d)
    fw, fh = 1100 * k + 10, 260 * k + 2
    c.save(); c.rectangle(0, 0, W, H); c.clip()
    n = 8
    for i in range(n):
        c.move_to(W/2 - fw/2, GROUND + fh * (i / n)); c.curve_to(W/2 - fw/4, GROUND - fh * 0.3 + fh * (i/n), W/2 + fw/4, GROUND - fh*0.3 + fh*(i/n), W/2 + fw/2, GROUND + fh*(i/n))
        c.line_to(W/2 + fw/2, GROUND + fh*((i+1)/n)); c.line_to(W/2 - fw/2, GROUND + fh*((i+1)/n)); c.close_path()
        c.set_source_rgb(*(SAND if i % 2 == 0 else SANDD)); c.fill()
    c.restore()
    label(c, "SAND FANS · KILOMETRES THICK", 260, ease(t / 0.6)); badge(c)

def s3(c, t, d):  # sea floods, mud buries, compaction
    sky(c, 0.6); ground(c, GROUND + 260)
    strata_block(c, W/2, GROUND + 130, 1100, 260, 0)
    k = ease(t / 2.5)
    # mud layer descending
    mud_h = 160 * ease((t - 1.5) / 2.5)
    c.set_source_rgb(*MUD); c.rectangle(0, GROUND - mud_h, W, mud_h); c.fill()
    # sea
    sea_top = lerp(GROUND, 520, k)
    c.set_source_rgba(*SEA, 0.75); c.rectangle(0, sea_top, W, GROUND - mud_h - sea_top + 1); c.fill()
    for i in range(6):
        y = sea_top + 4 + math.sin(t * 3 + i) * 4
        c.set_source_rgba(1, 1, 1, 0.35); c.set_line_width(4); c.move_to(i * 200 - 50, y); c.curve_to(i*200+20, y-10, i*200+80, y+10, i*200+150, y); c.stroke()
    # pressure arrows
    pa = ease((t - 3.5) / 1.0)
    for x in (300, 540, 780):
        c.set_source_rgba(1, 1, 1, pa); c.set_line_width(10)
        c.move_to(x, 700); c.line_to(x, 860); c.stroke()
        c.move_to(x - 28, 830); c.line_to(x, 875); c.line_to(x + 28, 830); c.stroke()
    label(c, "~500 MILLION YEARS AGO", 260, ease(t / 0.6)); badge(c)

def s4(c, t, d):  # tilt
    sky(c, 0.4); ground(c)
    ang = lerp(0, math.radians(85), ease((t - 0.6) / 4.5))
    c.save(); c.rectangle(0, GROUND, W, H - GROUND); c.clip()
    strata_block(c, W/2, GROUND + 380, 1000, 300, ang)
    c.restore()
    for side, sx in ((-1, 90), (1, W - 90)):
        a = 0.6 + 0.4 * math.sin(t * 6)
        c.set_source_rgba(*GOLD, a); c.set_line_width(12)
        c.move_to(sx, 1200); c.line_to(sx - side * 120, 1200); c.stroke()
        c.move_to(sx - side * 120 + side * 36, 1166); c.line_to(sx - side * 120, 1200); c.line_to(sx - side * 120 + side * 36, 1234); c.stroke()
    label(c, "400–300 MILLION YEARS AGO", 260, ease(t / 0.6)); badge(c)

def s5(c, t, d):  # erosion reveals top
    sky(c, 0.2)
    k = ease(t / 5.0)
    gtop = lerp(GROUND - 240, GROUND, k)
    # underground block ghost
    c.save(); c.rectangle(0, GROUND, W, H); c.clip()
    ground(c)
    strata_block(c, W/2 + 20, GROUND + 640, 1300, 640, math.radians(85), alpha=0.9, cols=(GREY, hexc("6E737B")))
    c.restore()
    uluru(c, col=lerpc(GREY, RED, 0.6))
    # surrounding soft rock wearing away
    if gtop < GROUND:
        c.set_source_rgb(*hexc("B07A55")); c.rectangle(0, gtop, W, GROUND - gtop); c.fill()
    m = ease((t - 5.4) / 1.0)
    if m > 0:
        x = W/2 - 430
        c.set_source_rgba(1, 1, 1, m); c.set_line_width(5)
        c.move_to(x, GROUND); c.line_to(x, GROUND - 260); c.stroke()
        for y in (GROUND, GROUND - 260): c.move_to(x - 20, y); c.line_to(x + 20, y); c.stroke()
        text(c, "348 m", x + 30, GROUND - 290, 52, col=GOLD, alpha=m, stroke=8)
        text(c, "the rest is underground", W/2, 1720, 50, col=(1, 1, 1), alpha=m, stroke=10)
    badge(c)

def s6(c, t, d):  # rust
    sky(c, 0.0); ground(c)
    k = ease((t - 1.0) / 3.0)
    uluru(c, col=lerpc(GREY, RED, k), w=880, h=300)
    a1 = ease((t - 0.8) / 0.6)
    wdt = text(c, "Fe  +  O", W/2 - 22, 520, 96, col=(1, 1, 1), alpha=a1, stroke=10)
    text(c, "2", W/2 - 22 + wdt / 2 + 4, 545, 56, col=(1, 1, 1), alpha=a1, stroke=8, align="left")
    text(c, "= RUST", W/2, 640, 96, col=lerpc(GREY, ORANGE, k), alpha=ease((t - 2.0) / 0.6), stroke=10)
    badge(c)

def s7(c, t, d):  # respect
    sky(c, ease(t / d) * 0.8); ground(c)
    uluru(c, col=lerpc(RED, hexc("6A2A3A"), ease(t / d)))
    a = ease((t - 0.5) / 1.0)
    text(c, "Aṉangu Country", W/2, 560, 70, col=GOLD, alpha=a, stroke=8)
    text(c, "Uluṟu-Kata Tjuṯa National Park", W/2, 640, 40, col=(1, 1, 1), alpha=a, weight=cairo.FONT_WEIGHT_NORMAL)
    badge(c)

LOGO = cairo.ImageSurface.create_from_png("/home/claude/how-on-earth-videos/pipeline/logo.png")
def s8(c, t, d):  # end card
    c.set_source_rgb(*NAVY); c.paint()
    c.save(); c.translate(0, 300); sky(c, 0.3); c.restore()
    g = cairo.LinearGradient(0, 1380, 0, H); g.add_color_stop_rgba(0, *GOLD, 1); g.add_color_stop_rgba(1, *ORANGE, 1)
    c.set_source(g); c.rectangle(0, 1380, W, H - 1380); c.fill()
    k = ease(t / 0.6)
    c.save(); s = 0.62 * (0.85 + 0.15 * k)
    c.translate(W/2 - 540 * s, 380); c.scale(s, s)
    c.arc(540, 540, 540, 0, 2 * math.pi); c.clip()
    c.set_source_surface(LOGO, 0, 0); c.paint_with_alpha(k); c.restore()
    text(c, "FOLLOW", W/2, 1180, 110, col=(1, 1, 1), alpha=k)
    text(c, "a new wonder every day", W/2, 1260, 54, col=(1, 1, 1), alpha=k, weight=cairo.FONT_WEIGHT_NORMAL)

SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8]

def render(i, still_t=None, out=None):
    d = meta[i]["dur"] + PAD
    line = (meta[i]["text"].replace("Ah-nung-oo", "Aṉangu").replace("Five hundred and fifty million", "550 million")
            .replace("three hundred and forty eight metres", "348 metres"))
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    def frame(t):
        c.set_source_rgb(0, 0, 0); c.paint()
        SCENES[i](c, t, d)
        if i < 8: captions(c, line, meta[i]["dur"], t)
        # fade in/out edges
        fi = min(1, t / 0.25, (d - t) / 0.25)
        if fi < 1: c.set_source_rgba(0, 0, 0, 1 - max(0, fi)); c.paint()
    if still_t is not None:
        frame(still_t); surf.write_to_png(out); return
    n = int(round(d * FPS))
    tmp = f"scene{i}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(n):
        frame(f / FPS); p.stdin.write(surf.get_data())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, f"scene{i}.mp4")

if __name__ == "__main__":
    if sys.argv[1] == "still":
        render(int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    else:
        render(int(sys.argv[1]))
