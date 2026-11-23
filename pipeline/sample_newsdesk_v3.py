"""SAMPLE v3 (funnier script, news ident sound + sign-off). Was: 20-second SAMPLE v2 (2026-11-23) of the "How On Earth News" satire format — REALISTIC version, no avatars
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
PRE, POST = 1.4, 2.6          # news ident before the first line, closing ident + end card after the last
STARTS = []; _t = PRE
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]
TOTAL = STARTS[-1] + DURS[-1] + POST


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



def wanted(c, t):
    """a 'WANTED' poster for the waterfall (drawn; the 'photo' is a real frame of the falls)"""
    if t <= 0: return
    k = max(0.02, back(t / 0.4)); c.save(); c.translate(W / 2, 760); c.rotate(-0.05); c.scale(k, k)
    c.set_source_rgba(0, 0, 0, 0.45); c.rectangle(-300 + 14, -330 + 18, 600, 640); c.fill()
    c.set_source_rgb(0.93, 0.86, 0.68); c.rectangle(-300, -330, 600, 640); c.fill()
    text(c, "WANTED", 0, -235, 110, col=(0.35, 0.12, 0.05))
    im = Image.fromarray(np.asarray(CB.at(1.0))).resize((440, 782)).crop((0, 230, 440, 530))
    c.set_source_surface(to_surface(np.asarray(im, np.float32) / 255 * np.array([1.0, 0.92, 0.75])), -220, -180); c.paint()
    c.set_source_rgb(0.35, 0.12, 0.05); c.set_line_width(5); c.rectangle(-220, -180, 440, 300); c.stroke()
    for j, ln in enumerate(("NIAGARA FALLS", "WET • EXTREMELY LOUD", "MOVES ~1 FOOT A YEAR")):
        text(c, ln, 0, 175 + j * 52, 44 if j == 0 else 34, col=(0.35, 0.12, 0.05))
    c.restore()


def s0(c, t, d, gt):  # Daniel: "Good evening. Our top story tonight: Niagara Falls is on the run."
    a = AER.kb(t / d, 1.0, 1.15, (0.6, 0.4), (0.6, 0.48)); to_ctx(c, finish(a, t + PRE, vign=0.35))
    bug(c, gt); clock(c, gt); ticker(c, gt)
    lower_third(c, t - 0.2, "NIAGARA FALLS ON THE RUN", "DANIEL", "News desk")
    source_tag(c, "Photo: Zwergelstern / CC BY-SA 3.0", t - 0.4, y=380)


def s1(c, t, d, gt):  # Alice: "It has fled seven miles upstream. Mind you, it took 12,000 years."
    k = ease((t - 1.0) / 2.0); a, mp = aster_view(590, 610, 2.2); to_ctx(c, finish(a, t, vign=0.3))
    pts = [mp(*p) for p in GORGE_PATH[::-1]]
    end = neon_path(c, pts, k, col=(1.0, 0.62, 0.3), width=12, t=t)
    ring_marker(c, *pts[0], 1.0, col=WHITE, r=16); label(c, "LAST SEEN HERE", pts[0][1] + 20, 1.0, x=pts[0][0] + 240, size=32, bg=WHITE, fg=NEWSBLUE)
    if end: ring_marker(c, *end, t + 0.3, col=(0.25, 0.82, 1.0), r=22)
    if t > 1.0: label(c, f"ESCAPED: {int(round(7 * eout(k)))} MILES", 470, t - 1.0, size=44, bg=AMBER, fg=NEWSBLUE)
    if t > 3.4: label(c, "TIME TAKEN: 12,000 YEARS", 560, t - 3.4, size=40, bg=WHITE, fg=NEWSBLUE)
    bug(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "FALLS FLEES 7 MILES UPSTREAM", "ALICE BROOK", "At Niagara Falls")
    source_tag(c, "Image: NASA ASTER (PD)", t - 0.4, y=380)


def s2(c, t, d, gt):  # Daniel: "So, not exactly a getaway car."
    to_ctx(c, finish(CB.at(t).astype(np.float32), t, vign=0.3))
    bug(c, gt); clock(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "NOT EXACTLY A GETAWAY CAR", "DANIEL", "News desk")
    source_tag(c, "Video: Alexis Lewis / CC BY 2.0", t - 0.2, y=380)


def s3(c, t, d, gt):  # Alice: "Witnesses describe the suspect as wet, extremely loud, and moving at about a foot a year."
    to_ctx(c, finish(CC.at(t).astype(np.float32), t, vign=0.35))
    wanted(c, t - 0.3)
    bug(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "SUSPECT: WET, LOUD, ~1 FOOT A YEAR", "ALICE BROOK", "At Niagara Falls")
    source_tag(c, "Speed today: about 1 ft a year (NY State Museum)", t - 0.6, y=380, size=22)


def s4(c, t, d, gt):  # Daniel: "And the motive?"
    to_ctx(c, finish(CA.at(t).astype(np.float32), t, vign=0.3))
    bug(c, gt); clock(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "AND THE MOTIVE?", "DANIEL", "News desk")


def s5(c, t, d, gt):  # Alice: "Soft rock... until the ledge on top simply snaps off."
    a = DRYBW.kb(t / d, 1.05, 1.2, (0.45, 0.5), (0.5, 0.52)); to_ctx(c, finish(a, t, archival=True, vign=0.4))
    label(c, "EVIDENCE: 1969, WHEN THE FALLS RAN DRY", 400, t - 0.1, size=34, bg=WHITE, fg=NEWSBLUE)
    for j, (nm, y, col) in enumerate((("HARD LEDGE", 770, AMBER), ("SOFT SHALE", 880, (1.0, 0.55, 0.3)), ("SNAPPED-OFF BLOCKS", 1000, WHITE))):
        kk = eout((t - 0.6 - j * 0.9) / 0.35)
        if kk > 0:
            c.set_source_rgba(*col, kk); c.set_line_width(5); c.move_to(120, y); c.line_to(120 + 480 * kk, y); c.stroke()
            label(c, nm, y - 34, t - 0.6 - j * 0.9, x=780, size=34, bg=col, fg=NEWSBLUE)
    bug(c, gt); ticker(c, gt)
    lower_third(c, 1.0, "MOTIVE: SOFT ROCK", "ALICE BROOK", "At Niagara Falls")
    source_tag(c, "Photo: NMGiovannucci / CC BY-SA 4.0 · Source: NY State Museum", t - 0.2, y=380, size=22)


def s6(c, t, d, gt):  # Alice sign-off: "This is Alice Brook, for How On Earth News, Niagara Falls." + closing ident / end card
    if t < d:
        to_ctx(c, finish(CA.at(min(t, 3.0)).astype(np.float32), t, vign=0.35))
        bug(c, gt); ticker(c, gt)
        c.save(); k = eout(t / 0.4); c.translate(-(1 - k) * W, 0)
        c.set_source_rgba(*NEWSBLUE, 0.95); c.rectangle(40, 1150, 1000, 120); c.fill()
        c.set_source_rgb(*NEWSRED); c.rectangle(40, 1150, 14, 120); c.fill()
        text(c, "ALICE BROOK", 80, 1205, 50, col=WHITE, align="left")
        text(c, "HOW ON EARTH NEWS  •  NIAGARA FALLS", 80, 1250, 30, col=AMBER, align="left"); c.restore()
    else:  # end card under the closing ident
        tt = t - d; a = AER.kb(1.0, 1.15, 1.15, (0.6, 0.48), (0.6, 0.48)); to_ctx(c, finish(a, t, vign=0.35))
        sting(c, min(tt, 0.9))
        k = eout(tt / 0.4)
        text(c, "Follow for tomorrow's bulletin", W / 2, 1000, 46, col=WHITE, stroke=10, alpha=k)


def opening(c, t, gt):  # pre-roll: news ident title sweep over the aerial
    a = AER.kb(0, 1.0, 1.0, (0.6, 0.4), (0.6, 0.4)); to_ctx(c, finish(a, t, vign=0.35))
    sting(c, min(t * 0.75, 0.95)); bug(c, gt); clock(c, gt)


SCENES = [s0, s1, s2, s3, s4, s5, s6]


def frame(c, gt, surf):
    c.set_source_rgb(*MID); c.paint()
    if gt < PRE:
        opening(c, gt, gt); badge(c, gt); return
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9); t = gt - STARTS[i]; d = DURS[i]
    SCENES[i](c, t, d, gt)
    if 0 < i and t < 0.3: whip(surf, t, direction=1 if i % 2 else -1, maxpx=90)
    badge(c, gt)
    if t < d: captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    return [("news_open", 0.0)] + [("whoosh", x - 0.05) for x in s[1:]] + [("tick", s[1] + 1.0 + k * 0.28) for k in range(8)] + \
           [("thunk", s[3] + 0.3), ("pop", s[5] + 0.6), ("pop", s[5] + 1.5), ("crack", s[5] + 2.4), ("news_close", s[6] + DURS[6] - 0.3)]


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]: frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events(), "voice_offset": PRE}, open("events.json", "w"))
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
        for f in range(int(math.ceil(TOTAL * FPS))): frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("total", TOTAL)
