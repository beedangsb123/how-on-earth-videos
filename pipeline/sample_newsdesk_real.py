"""20-second SAMPLE v2 (2026-11-23) of the "How On Earth News" satire format — REALISTIC version, no avatars
(Bidhan: "doesn't sound British", "make it more realistic, except the avatars").
Voices: ElevenLabs Daniel (British newsreader) + Alice (British field reporter) rendered with tts_el.py
"model": "per_line" (eleven_multilingual_v2 keeps the British accent). Visuals: real footage/photos full-frame with
broadcast graphics (our own invented brand — no BBC name/logo/look-alike), NASA ASTER satellite with the traced gorge.
usage (work dir with meta.json + l*.wav, media/ media2/ clipA..C from video 005): python sample_newsdesk_real.py stills p t.. | full"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish
from clips import Clip

NEWSRED = (0.78, 0.07, 0.1); NEWSBLUE = (0.04, 0.1, 0.26); AMBER = (1.0, 0.78, 0.2)
engine.CAP_ACCENT = AMBER
meta = json.load(open("meta.json"))
STARTS = []; _t = 0
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]; DURS[-1] += 0.8
TOTAL = STARTS[-1] + DURS[-1]


def finish(a, t, **kw): return _finish(haze(a, t), t, **kw)
def M(p): return sorted(glob.glob(f"media*/{p}*"))[0]


CA, CB, CC = Clip("clipA"), Clip("clipB"), Clip("clipC")
AER = Photo(M("Niagara_Falls_Horseshoe_aerial"), maxz=1.3)
DRYBW = Photo(M("1969_Drained"), archival=True, maxz=1.3)
AST = Image.open(M("Niagara_Falls__ASTER_")).convert("RGB")
GORGE_PATH = [(579, 745), (582, 730), (595, 715), (591, 700), (595, 685), (597, 670), (602, 655), (604, 640), (598, 625),
              (578, 610), (558, 595), (573, 580), (585, 565), (596, 550), (599, 535), (611, 520), (614, 505), (621, 490),
              (605, 475), (590, 458)]
TICK = ("NIAGARA FALLS formed about 12,000 years ago near Lewiston, NY   •   Has moved about 7 miles upstream   •   "
        "Hard dolostone on top of soft shale   •   Now moving about a foot a year   •   Sources: NY State Museum, Britannica   •   ")


def aster_view(cx, cy, s):
    hw, hh = W / 2 / s, H / 2 / s
    a = np.asarray(AST.resize((W, H), Image.BILINEAR, box=(cx - hw, cy - hh, cx + hw, cy + hh)), np.float32)
    return a, (lambda x, y: ((x - cx) * s + W / 2, (y - cy) * s + H / 2))


def bug(c, gt, live=True):
    c.save(); c.translate(60, 262)
    c.set_source_rgba(*NEWSBLUE, 0.92); c.rectangle(0, 0, 380, 60); c.fill()
    c.set_source_rgb(*NEWSRED); c.rectangle(0, 0, 10, 60); c.fill()
    text(c, "HOW ON EARTH NEWS", 24, 42, 32, col=WHITE, align="left")
    if live:
        c.set_source_rgb(*NEWSRED); c.rectangle(388, 0, 112, 60); c.fill()
        c.set_source_rgba(1, 1, 1, 0.5 + 0.5 * math.sin(gt * 6)); c.arc(412, 30, 9, 0, 2 * math.pi); c.fill()
        text(c, "LIVE", 430, 42, 30, col=WHITE, align="left")
    c.restore()


def clock(c, gt):
    text(c, "19:00 ET", W - 190, 302, 30, col=WHITE, align="left", stroke=6)


def lower_third(c, t, head, name=None, role=None):
    """broadcast-style lower third: red BREAKING tab, white headline bar, navy name strap"""
    if t <= 0: return
    k = eout(t / 0.45); y = 1150
    c.save(); c.rectangle(0, y - 10, W * k + 2, 240); c.clip()
    c.set_source_rgb(*NEWSRED); c.rectangle(40, y, 220, 64); c.fill()
    text(c, "BREAKING", 150, y + 45, 36, col=WHITE)
    c.set_source_rgba(1, 1, 1, 0.97); c.rectangle(260, y, 780, 64); c.fill()
    w = text_w(c, head, 38); sz = 38 * min(1, 750 / w)
    text(c, head, 278, y + 45, sz, col=NEWSBLUE, align="left")
    if name:
        c.set_source_rgba(*NEWSBLUE, 0.95); c.rectangle(40, y + 64, 1000, 52); c.fill()
        text(c, name, 60, y + 101, 30, col=AMBER, align="left")
        text(c, role, 60 + text_w(c, name, 30) + 24, y + 101, 28, col=WHITE, align="left")
    c.restore()


def ticker(c, gt, y=1088):
    c.set_source_rgba(*NEWSBLUE, 0.9); c.rectangle(0, y, W, 46); c.fill()
    c.set_source_rgb(*AMBER); c.rectangle(0, y, 140, 46); c.fill()
    w = text_w(c, TICK, 26); x0 = 150 - (gt * 120) % w
    c.save(); c.rectangle(140, y, W - 140, 46); c.clip()
    for k in range(3): text(c, TICK, x0 + k * w, y + 32, 26, col=WHITE, align="left", stroke=0)
    c.restore(); text(c, "FACTS", 70, y + 32, 24, col=NEWSBLUE)


def sting(c, t):
    """opening title sweep: two diagonal bars with the show name (first 1.4 s)"""
    if t > 1.4: return
    k = eout(t / 0.35) * (1 - ease((t - 1.0) / 0.4))
    c.save(); c.translate(W / 2, 760); c.rotate(-0.06)
    c.set_source_rgba(*NEWSRED, 0.95 * k); c.rectangle(-W * k, -70, 2 * W * k, 140); c.fill()
    c.set_source_rgba(*NEWSBLUE, 0.95 * k); c.rectangle(-W * k, 70, 2 * W * k, 70); c.fill()
    if k > 0.3:
        text(c, "HOW ON EARTH NEWS", 0, 26, 78, col=WHITE, alpha=min(1, (k - 0.3) / 0.3))
        text(c, "THE EVENING BULLETIN", 0, 118, 34, col=AMBER, alpha=min(1, (k - 0.3) / 0.3))
    c.restore()


def s0(c, t, d, gt):  # Daniel: "Good evening. Geologists have confirmed that Niagara Falls is, in fact, on the move."
    a = AER.kb(t / d, 1.0, 1.15, (0.6, 0.4), (0.6, 0.48)); to_ctx(c, finish(a, t, vign=0.35))
    sting(c, t)
    bug(c, gt); clock(c, gt); ticker(c, gt)
    lower_third(c, t - 1.4, "NIAGARA FALLS IS ON THE MOVE", "DANIEL", "News desk")
    source_tag(c, "Photo: Zwergelstern / CC BY-SA 3.0", t - 1.6, y=380)


def s1(c, t, d, gt):  # Alice: "...about 12,000 years ago, it has crept seven miles upstream."
    k = ease((t - 1.6) / (d - 2.0)); a, mp = aster_view(590, 610, 2.2); to_ctx(c, finish(a, t, vign=0.3))
    pts = [mp(*p) for p in GORGE_PATH[::-1]]
    end = neon_path(c, pts, k, col=(1.0, 0.62, 0.3), width=12, t=t)
    ring_marker(c, *pts[0], 1.0, col=WHITE, r=16); label(c, "WHERE IT STARTED", pts[0][1] + 20, 1.0, x=pts[0][0] + 250, size=32, bg=WHITE, fg=NEWSBLUE)
    if end: ring_marker(c, *end, t + 0.3, col=(0.25, 0.82, 1.0), r=22)
    if t > 1.6: label(c, f"{int(round(7 * eout(k)))} MILES IN 12,000 YEARS", 470, t - 1.6, size=44, bg=AMBER, fg=NEWSBLUE)
    bug(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "FALLS HAS CREPT 7 MILES UPSTREAM", "ALICE", "At Niagara Falls")
    source_tag(c, "Image: NASA ASTER (PD)", t - 0.4, y=380)


def s2(c, t, d, gt):  # Daniel: "Seven miles. And the cause?"
    to_ctx(c, finish(CB.at(t).astype(np.float32), t, vign=0.3))
    bug(c, gt); clock(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "SEVEN MILES. AND THE CAUSE?", "DANIEL", "News desk")
    source_tag(c, "Video: Alexis Lewis / CC BY 2.0", t - 0.2, y=380)


def s3(c, t, d, gt):  # Alice: "Soft rock... the water scoops it out from underneath, and the hard edge on top simply snaps off."
    if t < 3.0:
        to_ctx(c, finish(CC.at(t).astype(np.float32), t, vign=0.3))
        source_tag(c, "Video: Alexis Lewis / CC BY 2.0", t - 0.2, y=380)
    else:
        tt = t - 3.0; a = DRYBW.kb(tt / (d - 3.0), 1.05, 1.2, (0.45, 0.5), (0.5, 0.52)); to_ctx(c, finish(a, tt, archival=True, vign=0.4))
        label(c, "1969: THE FALLS RUN DRY", 400, tt - 0.1, size=40, bg=WHITE, fg=NEWSBLUE)
        # annotate the real cliff: hard cap on top, softer rock below, the fallen blocks at the foot
        for j, (nm, y, col) in enumerate((("HARD CAPROCK", 770, AMBER), ("SOFT SHALE", 880, (1.0, 0.55, 0.3)), ("FALLEN BLOCKS", 1000, WHITE))):
            kk = eout((tt - 0.3 - j * 0.35) / 0.35)
            if kk > 0:
                c.set_source_rgba(*col, kk); c.set_line_width(5); c.move_to(120, y); c.line_to(120 + 480 * kk, y); c.stroke()
                label(c, nm, y - 34, tt - 0.3 - j * 0.35, x=780, size=34, bg=col, fg=NEWSBLUE)
        source_tag(c, "Photo: NMGiovannucci / CC BY-SA 4.0 · Source: NY State Museum", tt - 0.2, y=380, size=22)
    bug(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "SOFT ROCK WASHES OUT, HARD EDGE SNAPS OFF", "ALICE", "At Niagara Falls")


def s4(c, t, d, gt):  # Daniel: "Extraordinary. Alice, at Niagara Falls. Thank you."
    to_ctx(c, finish(CA.at(min(t, 3.0)).astype(np.float32), t, vign=0.35))
    bug(c, gt, live=False); clock(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "NIAGARA FALLS: STILL ON THE MOVE", "DANIEL", "News desk")
    if t > 1.8:
        k = eout((t - 1.8) / 0.4)
        c.set_source_rgba(*NEWSBLUE, 0.9 * k); c.rectangle(0, 640, W, 230); c.fill()
        text(c, "THE FULL STORY", W / 2, 740, 64, col=WHITE, alpha=k)
        text(c, "Follow How On Earth", W / 2, 820, 40, col=AMBER, alpha=k)


SCENES = [s0, s1, s2, s3, s4]


def frame(c, gt, surf):
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9); t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    SCENES[i](c, t, d, gt)
    if i > 0: whip(surf, t, direction=1 if i % 2 else -1, maxpx=90)
    badge(c, gt)
    captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    return [("boom", 0.0), ("pop", 0.15), ("pop", 0.3), ("tick", 0.45), ("tick", 0.6), ("thunk", 1.4)] + \
           [("whoosh", x - 0.05) for x in s[1:]] + [("tick", s[1] + 1.6 + k * 0.3) for k in range(10)] + \
           [("pop", s[3] + 3.3), ("pop", s[3] + 3.65), ("pop", s[3] + 4.0), ("boom", s[4] + 1.8)]


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
