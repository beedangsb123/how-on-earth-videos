"""20-second SAMPLE (2026-11-23) of the satire format "How On Earth News" — a deadpan British newsreader (ElevenLabs
Daniel) and an over-excited field reporter (ElevenLabs Lily) report a REAL fact as breaking news: Niagara Falls has
"walked" 7 miles upstream in ~12,000 years. Our own invented news brand — no BBC name/logo/look-alike graphics.
Cartoon (clearly non-real) presenters from avatar.py; real Niagara footage + NASA ASTER image with the traced gorge.
usage (work dir with meta.json + l*.wav, media/ + media2/ + clipA..C from video 005): python sample_newsdesk.py stills p t.. | full"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish
from clips import Clip
from avatar import Talk, avatar_card, draw_char, CAST

NEWSRED = (0.82, 0.08, 0.12); NEWSBLUE = (0.05, 0.12, 0.32)
engine.CAP_ACCENT = (1.0, 0.85, 0.3)
meta = json.load(open("meta.json")); talk = Talk(meta)
STARTS = talk.starts; DURS = [m["dur"] for m in meta]; DURS[-1] += 0.6
TOTAL = STARTS[-1] + DURS[-1]


def finish(a, t, **kw): return _finish(haze(a, t), t, **kw)
def M(p): return sorted(glob.glob(f"media*/{p}*"))[0]


CA, CB, CC = Clip("clipA"), Clip("clipB"), Clip("clipC")
AST = Image.open(M("Niagara_Falls__ASTER_")).convert("RGB")
GORGE_PATH = [(579, 745), (582, 730), (595, 715), (591, 700), (595, 685), (597, 670), (602, 655), (604, 640), (598, 625),
              (578, 610), (558, 595), (573, 580), (585, 565), (596, 550), (599, 535), (611, 520), (614, 505), (621, 490),
              (605, 475), (590, 458)]
DAN = dict(CAST["daniel"]); LILY = dict(CAST["lily"]); LILY["shirt"] = (0.85, 0.2, 0.25)
TICK = ("FACT CHECK: Niagara Falls formed about 12,000 years ago near Lewiston, NY  •  It has moved about 7 miles upstream  •  "
        "Hard dolostone sits on soft shale; the shale washes out and the edge breaks off  •  Today it moves about a foot a year  •  "
        "Sources: NY State Museum, Britannica  •  ")


def aster_view(cx, cy, s):
    hw, hh = W / 2 / s, H / 2 / s
    a = np.asarray(AST.resize((W, H), Image.BILINEAR, box=(cx - hw, cy - hh, cx + hw, cy + hh)), np.float32)
    return a, (lambda x, y: ((x - cx) * s + W / 2, (y - cy) * s + H / 2))


def bug(c, t, live=True):
    """our own channel bug + LIVE flag (top-left, under the badge)"""
    c.save(); c.translate(70, 250)
    c.set_source_rgb(*NEWSBLUE); c.rectangle(0, 0, 420, 70); c.fill()
    c.set_source_rgb(*NEWSRED); c.rectangle(0, 0, 14, 70); c.fill()
    text(c, "HOW ON EARTH NEWS", 30, 48, 36, col=WHITE, align="left")
    if live:
        c.set_source_rgb(*NEWSRED); c.rectangle(430, 0, 130, 70); c.fill()
        c.set_source_rgba(1, 1, 1, 0.5 + 0.5 * math.sin(t * 6)); c.arc(458, 35, 10, 0, 2 * math.pi); c.fill()
        text(c, "LIVE", 478, 48, 34, col=WHITE, align="left")
    c.restore()


def lower_third(c, t, head, sub):
    if t <= 0: return
    k = eout(t / 0.4); y = 1180
    c.save(); c.translate(-(1 - k) * W, 0)
    c.set_source_rgb(*NEWSRED); c.rectangle(40, y, 250, 70); c.fill()
    text(c, "BREAKING", 165, y + 50, 40, col=WHITE)
    c.set_source_rgb(1, 1, 1); c.rectangle(290, y, 750, 70); c.fill()
    w = text_w(c, head, 40); sz = 40 * min(1, 720 / w)
    text(c, head, 305, y + 50, sz, col=NEWSBLUE, align="left")
    c.set_source_rgb(*NEWSBLUE); c.rectangle(40, y + 70, 1000, 50); c.fill()
    text(c, sub, 60, y + 106, 30, col=WHITE, align="left")
    c.restore()


def ticker(c, t, y=330):
    c.set_source_rgb(0.98, 0.84, 0.2); c.rectangle(0, y, W, 52); c.fill()
    c.set_source_rgb(*NEWSBLUE); c.rectangle(0, y, 150, 52); c.fill()
    w = text_w(c, TICK, 28); x0 = 160 - (t * 140) % w
    c.save(); c.rectangle(150, y, W - 150, 52); c.clip()
    for k in range(3): text(c, TICK, x0 + k * w, y + 36, 28, col=NEWSBLUE, align="left", stroke=0)
    c.restore(); text(c, "TICKER", 75, y + 36, 26, col=WHITE)


def studio(c, gt, t, mood="serious", wall="clip", wall_t=0.0):
    """news set: blue light-ray backdrop, a video wall with real footage, the anchor at the desk"""
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.04, 0.1, 0.28); g.add_color_stop_rgb(1, 0.02, 0.04, 0.12)
    c.set_source(g); c.paint()
    for k in range(14):  # light rays + floor grid: texture to every edge
        a = -0.9 + k * 0.14 + 0.03 * math.sin(gt * 0.6 + k)
        c.move_to(W / 2, 1500); c.line_to(W / 2 + 2200 * math.sin(a), 1500 - 2200 * math.cos(a)); c.line_to(W / 2 + 2200 * math.sin(a + 0.05), 1500 - 2200 * math.cos(a + 0.05)); c.close_path()
        c.set_source_rgba(0.4, 0.6, 1, 0.06); c.fill()
    for k in range(-12, 13):
        c.move_to(W / 2 + k * 40, 1400); c.line_to(W / 2 + k * 260, H + 20)
    for y in range(1420, H + 40, 60): c.move_to(-20, y); c.line_to(W + 20, y)
    c.set_source_rgba(0.5, 0.7, 1, 0.22); c.set_line_width(2); c.stroke()
    # video wall
    x0, y0, ww, wh = 90, 400, 900, 506
    c.set_source_rgb(0.02, 0.02, 0.05); c.rectangle(x0 - 10, y0 - 10, ww + 20, wh + 20); c.fill()
    fr = CB.at(wall_t) if wall == "clip" else CA.at(wall_t)
    im = Image.fromarray(np.asarray(fr)).resize((ww, int(ww * 1920 / 1080)))
    im = im.crop((0, (im.height - wh) // 2, ww, (im.height - wh) // 2 + wh))
    surf = to_surface(np.asarray(im, np.float32) / 255)
    c.set_source_surface(surf, x0, y0); c.paint()
    c.set_source_rgba(0.5, 0.75, 1, 0.9); c.set_line_width(4); c.rectangle(x0 - 10, y0 - 10, ww + 20, wh + 20); c.stroke()
    # anchor + desk
    c.save(); c.translate(W / 2, 985); c.scale(1.15, 1.15)
    draw_char(c, DAN, gt, mouth=talk.mouth(gt, "M"), mood=mood, look=0.0); c.restore()
    c.move_to(80, 1130); c.line_to(W - 80, 1130); c.line_to(W - 20, 1420); c.line_to(20, 1420); c.close_path()
    g = cairo.LinearGradient(0, 1130, 0, 1420); g.add_color_stop_rgb(0, 0.85, 0.88, 0.95); g.add_color_stop_rgb(1, 0.35, 0.42, 0.6)
    c.set_source(g); c.fill()
    c.set_source_rgb(*NEWSRED); c.rectangle(80, 1130, W - 160, 16); c.fill()


def reporter(c, gt, t, bgimg, mood="excited"):
    to_ctx(c, finish(bgimg, t, vign=0.3))
    # Lily on location, bottom-left, holding a mic
    c.save(); c.translate(240, 945); c.scale(0.85, 0.85)
    draw_char(c, LILY, gt, mouth=talk.mouth(gt, "F"), mood=mood, look=0.4)
    c.set_source_rgb(0.15, 0.15, 0.18); c.save(); c.translate(150, 140); c.rotate(-0.35); rrect(c, -14, 0, 28, 120, 10); c.fill()
    c.arc(0, -8, 30, 0, 2 * math.pi); c.fill(); c.set_source_rgb(*NEWSRED); c.rectangle(-22, 40, 44, 36); c.fill(); c.restore()
    c.restore()


def s0(c, t, d, gt):  # Daniel: "Good evening. Breaking news tonight: Niagara Falls has been caught... walking backwards."
    studio(c, gt, t, mood="serious", wall="clip", wall_t=t)
    bug(c, gt); ticker(c, gt)
    lower_third(c, t - 1.0, "NIAGARA FALLS CAUGHT WALKING BACKWARDS", "Waterfall 'unavailable for comment'")


def s1(c, t, d, gt):  # Lily: "That's right, Daniel! It's crept seven miles in 12,000 years."
    k = ease((t - 0.8) / (d - 1.2)); a, mp = aster_view(590, 610, 2.2)
    reporter(c, gt, t, a)
    pts = [mp(*p) for p in GORGE_PATH[::-1]]
    end = neon_path(c, pts, k, col=(1.0, 0.62, 0.3), width=12, t=t)
    ring_marker(c, *pts[0], 1.0, col=WHITE, r=16)
    if end: ring_marker(c, *end, t + 0.3, col=(0.25, 0.82, 1.0), r=22)
    bug(c, gt); label(c, "LIVE: NIAGARA FALLS", 350, 1.0, x=W / 2 + 120, size=40, bg=WHITE, fg=NEWSBLUE)
    label(c, counter_txt(k), 520, t - 0.8, x=W / 2 + 200, size=60, bg=(1.0, 0.62, 0.3), fg=NEWSBLUE)
    lower_third(c, 1.0, "FALLS HAS MOVED 7 MILES UPSTREAM", "Lily, on the scene  •  Image: NASA ASTER")


def counter_txt(k): return f"{int(round(7 * eout(k)))} MILES"


def s2(c, t, d, gt):  # Daniel: "Seven miles. Has the waterfall offered any explanation?"
    studio(c, gt, t, mood="serious", wall="clipA", wall_t=t)
    bug(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "WATERFALL REFUSES TO EXPLAIN ITSELF", "Experts baffled. Experts not actually baffled.")


def s3(c, t, d, gt):  # Lily: "It has not, Daniel. It's a waterfall. But its soft rock keeps washing away."
    reporter(c, gt, t, CC.at(t).astype(np.float32), mood="playful" if t < 2.2 else "excited")
    bug(c, gt)
    if t > 2.4:
        c.save(); c.translate(560, 820)
        for j, (nm, col) in enumerate((("HARD DOLOSTONE", (0.78, 0.76, 0.72)), ("SOFT SHALE", (0.5, 0.36, 0.3)))):
            k = eout((t - 2.4 - j * 0.3) / 0.35)
            c.set_source_rgba(*col, k); c.rectangle(0, j * 110, 440 * k, 100); c.fill()
            text(c, nm, 20, j * 110 + 64, 40, col=NEWSBLUE if j == 0 else WHITE, align="left", alpha=k)
        if t > 3.4:
            c.set_source_rgba(0.25, 0.82, 1.0, 1); c.set_line_width(8)
            for kk in range(3):
                ph = ((t - 3.4) * 1.2 + kk / 3) % 1
                c.move_to(480 - 200 * ph, 160); c.line_to(440 - 200 * ph, 140); c.move_to(480 - 200 * ph, 160); c.line_to(440 - 200 * ph, 180); c.stroke()
        c.restore()
    lower_third(c, 1.0, "SOFT ROCK WASHING AWAY, EDGE SNAPS OFF", "Source: NY State Museum  •  Video: Alexis Lewis / CC BY 2.0")


def s4(c, t, d, gt):  # Daniel: "Shocking. More after the break."
    studio(c, gt, t, mood="serious", wall="clip", wall_t=3 + t)
    bug(c, gt, live=False); ticker(c, gt)
    if t > 1.0:
        k = eout((t - 1.0) / 0.4)
        c.set_source_rgba(*NEWSBLUE, 0.92 * k); c.rectangle(0, 700, W, 300); c.fill()
        text(c, "MORE AFTER THE BREAK", W / 2, 830, 64, col=WHITE, alpha=k)
        text(c, "Follow How On Earth for the real story", W / 2, 910, 38, col=(1.0, 0.85, 0.3), alpha=k)


SCENES = [s0, s1, s2, s3, s4]


def frame(c, gt, surf):
    i = talk.line(gt); t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    SCENES[i](c, t, d, gt)
    if i > 0: whip(surf, t, direction=1 if i % 2 else -1, maxpx=110)
    badge(c, gt)
    captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    # news sting: boom + rising pops at the top, a stinger at the end
    return [("boom", 0.0), ("pop", 0.1), ("pop", 0.25), ("pop", 0.4), ("pop", 1.0)] + [("whoosh", x - 0.05) for x in s[1:]] + \
           [("tick", s[1] + 0.8 + k * 0.3) for k in range(10)] + [("pop", s[3] + 2.4), ("pop", s[3] + 2.7), ("boom", s[4] + 1.0)]


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]: frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events()}, open("events.json", "w"))
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
        for f in range(int(math.ceil(TOTAL * FPS))): frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("total", TOTAL)
