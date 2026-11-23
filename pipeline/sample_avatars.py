"""20-second SAMPLE (2026-11-23) of the cartoon-avatar-host format for video 006 — Empire State Building in 410 days.
Voices Eric (male, answers) + Jessica (female, excited/curious). Look: construction "caution tape" headlines, orange
accent, real Lewis Hine 1930-31 photos (MET CC0 / NARA PD) + Rudolphous (CC BY-SA 4.0), drawn steel frame growing.
usage (work dir with meta.json + l*.wav from tts_el.py, media/): python sample_avatars.py stills p t.. | full"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish
from avatar import Talk, avatar_card, CAST

ORANGE2 = (1.0, 0.55, 0.1); YEL = (1.0, 0.82, 0.1)
engine.CAP_ACCENT = YEL
meta = json.load(open("meta.json")); talk = Talk(meta)
STARTS = talk.starts; DURS = [m["dur"] for m in meta]; DURS[-1] += 0.6
TOTAL = STARTS[-1] + DURS[-1]


def finish(a, t, **kw): return _finish(haze(a, t), t, **kw)
def M(p): return sorted(glob.glob(f"media/{p}*"))[0]


ESB = Photo(M("New_York_-_Empire_State"), maxz=1.5)        # Rudolphous CC BY-SA 4.0 (crop keeps the truck out)
HINE = Photo(M("Empire_State_Building_MET"), archival=True, maxz=1.3)   # Lewis Hine, MET CC0
MAST = Photo(M("Raising_the_Mast"), archival=True, maxz=1.3)            # Lewis Hine, PD
P1 = Particles(90, 1)
ERIC = dict(CAST["eric"]); JESS = dict(CAST["jess"])


def tape(c, s, x, y, size, t, angle=-0.04):
    """headline on yellow-black construction caution tape that unrolls from the left"""
    if t <= 0: return
    w = text_w(c, s, size); k = eout(t / 0.35); bw = (w + 120) * k; bh = size * 1.4
    c.save(); c.translate(x, y); c.rotate(angle)
    c.set_source_rgba(0, 0, 0, 0.4); c.rectangle(-(w + 120) / 2 + 10, -bh / 2 + 12, bw, bh); c.fill()
    c.rectangle(-(w + 120) / 2, -bh / 2, bw, bh); c.save(); c.clip()
    c.set_source_rgb(*YEL); c.paint()
    sb = 18   # hazard stripes only in thin bands top + bottom, solid yellow behind the text
    c.save(); c.rectangle(-(w + 120) / 2, -bh / 2, w + 120, sb); c.rectangle(-(w + 120) / 2, bh / 2 - sb, w + 120, sb); c.clip()
    for j in range(-10, 60):
        x0 = -(w + 120) / 2 + j * 44
        c.move_to(x0, -bh / 2); c.line_to(x0 + 20, -bh / 2); c.line_to(x0 + 20 - bh * 0.4, bh / 2); c.line_to(x0 - bh * 0.4, bh / 2); c.close_path()
    c.set_source_rgb(0.08, 0.08, 0.08); c.fill(); c.restore()
    c.restore()
    if k > 0.6: text(c, s, 0, size * 0.36, size, col=(0.06, 0.06, 0.08), alpha=ease((k - 0.6) / 0.4))
    c.restore()


def frame_build(c, t, floors, x0=300, base=1500, fw=480, fh=22, col=ORANGE2):
    """drawn steel skeleton: `floors` storeys of columns + beams, the top floor flashing as it is added"""
    n = int(floors); frac = floors - n
    c.save(); c.set_line_cap(cairo.LINE_CAP_SQUARE)
    for f in range(n + 1):
        y = base - f * fh
        if f == n and frac <= 0: break
        a = 1.0 if f < n else frac
        c.set_source_rgba(*col, a); c.set_line_width(6); c.move_to(x0, y); c.line_to(x0 + fw, y); c.stroke()
        for k in range(7):
            xx = x0 + k * fw / 6; c.move_to(xx, y); c.line_to(xx, y - fh * (1 if f < n else frac)); c.stroke()
    if n > 0:
        c.set_source_rgba(1, 1, 1, 0.5 + 0.5 * math.sin(t * 12)); c.set_line_width(8)
        c.move_to(x0, base - n * fh); c.line_to(x0 + fw, base - n * fh); c.stroke()
    c.restore()


def cards(c, gt, moods):
    spk = talk.speaking(gt)
    avatar_card(c, ERIC, 215, 1090, 0.82, gt, mouth=talk.mouth(gt, "M"), active=spk == "M", mood=moods[0], name="ERIC", col=YEL, look=0.6)
    avatar_card(c, JESS, 790, 1090, 0.82, gt, mouth=talk.mouth(gt, "F"), active=spk == "F", mood=moods[1], name="JESS", col=YEL, look=-0.6)


def s0(c, t, d, gt):  # M "The Empire State Building went up in just 410 days."
    a = ESB.kb(min(1, t / d), 1.25, 1.4, (0.5, 0.22), (0.5, 0.18)); to_ctx(c, finish(a, t, vign=0.35))
    tape(c, "BUILT IN 410 DAYS?!", W / 2, 420, 92, t + 1)
    cards(c, gt, ("intrigued", "curious"))
    source_tag(c, "Photo: Rudolphous / CC BY-SA 4.0", t - 0.5, y=600)


def s1(c, t, d, gt):  # F "Wait, 410 days? For a 102-story tower?"
    a = HINE.kb(t / d, 1.0, 1.15, (0.6, 0.4), (0.7, 0.35)); to_ctx(c, finish(a, t, archival=True, vign=0.4))
    tape(c, "WAIT, 410 DAYS?!", W / 2, 420, 100, t - 0.05)
    if t > 2.2:
        n = counter_val = int(round(lerp(0, 102, eout((t - 2.2) / 1.6))))
        tape(c, f"{n} STORIES", W / 2, 580, 80, t - 2.2, angle=0.03)
    cards(c, gt, ("warm", "surprised"))
    source_tag(c, "Photo: Lewis Hine, 1930-31 / MET (CC0)", t - 0.4, y=700)


def s2(c, t, d, gt):  # M "At top speed, the frame rose four and a half floors a week."
    to_ctx(c, haze(blur(_finish(MAST.kb(0, 1.0, 1.0), 0, archival=True), 10, 0.55), t, amt=30).astype(np.uint8))
    wk = 1 + int(max(0, t - 0.8) / 0.6)
    frame_build(c, t, min(4.5 * wk, 4.5 * 6) if t > 0.8 else 0, x0=220, base=930, fw=640, fh=12)
    tape(c, "4½ FLOORS A WEEK", W / 2, 420, 90, t - 1.6)
    if t > 0.8: label(c, f"WEEK {min(wk, 6)}", 520, t - 0.8, size=48, bg=WHITE)
    cards(c, gt, ("warm", "intrigued"))
    source_tag(c, "Sources: History.com, Britannica", t - 0.4, y=700)


def s3(c, t, d, gt):  # F "Okay, how is that even possible?"
    a = HINE.kb(t / d, 1.15, 1.3, (0.78, 0.35), (0.82, 0.3)); to_ctx(c, finish(a, t, archival=True, vign=0.4))
    tape(c, "HOW?!", W / 2, 440, 150, t - 0.05)
    cards(c, gt, ("neutral", "surprised"))


def rail(c, t):
    """floor plan strip with a little railway and a cart carrying materials along it"""
    y = 800
    c.set_source_rgba(0.1, 0.1, 0.12, 0.75); c.rectangle(-20, y - 120, W + 40, 240); c.fill()
    c.set_source_rgb(0.75, 0.75, 0.78); c.set_line_width(6)
    for dy in (-22, 22): c.move_to(-20, y + dy); c.line_to(W + 20, y + dy); c.stroke()
    for k in range(0, W + 60, 40):
        c.set_source_rgb(0.45, 0.3, 0.18); c.rectangle(k - 6, y - 34, 12, 68); c.fill()
    x = lerp(-200, W + 200, (t * 0.35) % 1.0)
    c.set_source_rgb(*ORANGE2); rrect(c, x - 110, y - 90, 220, 70, 10); c.fill()
    for k in range(4):
        c.set_source_rgb(0.75, 0.72, 0.66); c.rectangle(x - 95 + k * 48, y - 130, 40, 40); c.fill()
    c.set_source_rgb(0.15, 0.15, 0.15)
    for dx in (-70, 70): c.arc(x + dx, y - 10, 18, 0, 2 * math.pi); c.fill()


def s4(c, t, d, gt):  # M "They ran it like a factory, with little railways on every floor."
    a = MAST.kb(t / d, 1.0, 1.12, (0.5, 0.5), (0.5, 0.45)); to_ctx(c, finish(a, t, archival=True, vign=0.4))
    tape(c, "A FACTORY IN THE SKY", W / 2, 420, 84, t - 0.3)
    if t > 1.4: rail(c, t - 1.4); label(c, "A RAILWAY ON EVERY FLOOR", 640, t - 1.4, size=40, bg=YEL)
    if t > d - 1.4: label(c, "FULL STORY SOON", 940, t - (d - 1.4), size=46, bg=WHITE)
    cards(c, gt, ("playful", "excited"))
    source_tag(c, "Photo: Lewis Hine / PD · Source: History.com", t - 0.4, y=1290)


SCENES = [s0, s1, s2, s3, s4]


def frame(c, gt, surf):
    i = talk.line(gt); t = gt - STARTS[i]; d = DURS[i]
    c.set_source_rgb(*MID); c.paint()
    SCENES[i](c, t, d, gt)
    if i > 0: whip(surf, t, direction=1 if i % 2 else -1)
    badge(c, gt)
    captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"))


def events():
    s = STARTS
    return [("boom", 0.0), ("pop", 0.3)] + [("whoosh", x - 0.05) for x in s[1:]] + \
           [("pop", s[1] + 2.2)] + [("tick", s[1] + 2.2 + k * 0.1) for k in range(14)] + \
           [("thunk", s[2] + 0.8 + k * 0.6) for k in range(6)] + [("pop", s[2] + 1.6), ("pop", s[3]), ("pop", s[4] + 0.3), ("pop", s[4] + 1.4)]


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
