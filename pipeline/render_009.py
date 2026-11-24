"""Video 009 — HOW ON EARTH NEWS #1 (weekly Friday show, PLAYBOOK AUTOPILOT 4): "Breaking news: Florida has a river
that's thirty miles wide" — the Everglades, a slow sheet-flow "river of grass" (natural wonder). Trend tie: GTA 6's
Everglades-style swamp (no game imagery; only a mention). Daniel (anchor) + Alice (field reporter), per_line British
voices at 0.9x, news idents (audio2 news_open / news_close, voice_offset).
Graphics follow the approved sample (pipeline/sample_newsdesk_v3.py): HOW ON EARTH NEWS bug + LIVE, BREAKING lower
thirds, name straps, fact ticker with sources, opening sting — our own invented brand. New for the full episode:
speedometer() for the river's speed, slope_profile() (Lake Okeechobee -> Florida Bay), sheet_flow() cross-section,
shrink_map() (original vs today), a deadpan "SHOES: WET" stat box. usage: python render_009.py stills p t.. | full [a b out]"""
import cairo, json, math, os, sys, glob, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import *
from photo import Photo, to_ctx, blur, haze
from photo import finish as _finish

NEWSRED = (0.78, 0.07, 0.1); NEWSBLUE = (0.04, 0.1, 0.26); AMBER = (1.0, 0.78, 0.2); GRASS = hexc("9BBF4A")
engine.CAP_ACCENT = AMBER
meta = json.load(open("meta.json"))
PRE, POST = 1.4, 2.6
STARTS = []; _t = PRE
for m in meta: STARTS.append(_t); _t += m["dur"]
DURS = [m["dur"] for m in meta]
TOTAL = STARTS[-1] + DURS[-1] + POST


def finish(a, t, **kw): return _finish(haze(a, t), t, **kw)
def M(p): return sorted(glob.glob(f"media*/{p}*"))[0]


BACK = Photo(M("Everglades_Backcountry"), maxz=1.3)        # Everglades NPS, PD
TEAL = Photo(M("Everglades_National_Park_EVER1551"), maxz=1.3)  # NPS Digital Image Archives, PD
PRAIRIE = Photo(M("Everglades_Sawgrass_Prairie_Moni3"), maxz=1.3)  # Moni3, CC BY 3.0
BROWARD = Photo(M("Everglades_in_Eastern_Broward"), maxz=1.3)   # formulanone, CC BY-SA 2.0
HERON = Photo(M("Great_Blue_Heron"), maxz=1.3)             # ImagePerson, CC BY 4.0
GARDNER = Photo(M("Sawgrass_Prairie_NPS"), maxz=1.3)       # Everglades NPS / G. Gardner, PD
SFLA = Photo(M("nasa_PIA03703"), maxz=1.3)                 # NASA, PD
ORBIT = Photo(M("nasa_STS099"), maxz=1.3)                  # NASA STS-99, PD
ISSFL = Photo(M("nasa_iss002e5466"), maxz=1.3)             # NASA ISS, PD
TICK = ("THE EVERGLADES is a slow sheet of water up to 30+ miles wide   •   Winter flow ~100 ft a day, summer up to ~1 mile a day   •   "
        "Land slopes less than 2 inches per mile   •   Less than half the original Everglades remains   •   National park since 1947   •   "
        "Sources: National Park Service, Florida Museum, Live Science   •   ")
_BL = {}


def blurred(key, photo, f=(0.5, 0.5), dim=0.55):
    if key not in _BL: _BL[key] = blur(_finish(photo.kb(0, 1.0, 1.0, f, f), 0), 16, dim)
    return _BL[key]


def bg(c, key, photo, t, f=(0.5, 0.5), dim=0.55):
    to_ctx(c, haze(blurred(key, photo, f, dim), t, amt=30).astype(np.uint8))


def ph(c, photo, t, d, z0=1.0, z1=1.12, f0=(0.5, 0.5), f1=(0.5, 0.5)):
    to_ctx(c, finish(photo.kb(t / max(d, 0.1), z0, z1, f0, f1), t, vign=0.35))


# ---------------- broadcast graphics (from the approved sample) ----------------
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


def lower_third(c, t, head, name=None, role=None, tab="BREAKING", y=1150):
    if t <= 0: return
    k = eout(t / 0.45)
    c.save(); c.rectangle(0, y - 10, W * k + 2, 240); c.clip()
    c.set_source_rgb(*NEWSRED); c.rectangle(40, y, 220, 64); c.fill()
    text(c, tab, 150, y + 45, 36 if len(tab) < 9 else 30, col=WHITE)
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
    if t > 1.4: return
    k = eout(t / 0.35) * (1 - ease((t - 1.0) / 0.4))
    c.save(); c.translate(W / 2, 760); c.rotate(-0.06)
    c.set_source_rgba(*NEWSRED, 0.95 * k); c.rectangle(-W * k, -70, 2 * W * k, 140); c.fill()
    c.set_source_rgba(*NEWSBLUE, 0.95 * k); c.rectangle(-W * k, 70, 2 * W * k, 70); c.fill()
    if k > 0.3:
        text(c, "HOW ON EARTH NEWS", 0, 26, 78, col=WHITE, alpha=min(1, (k - 0.3) / 0.3))
        text(c, "THE FRIDAY BULLETIN", 0, 118, 34, col=AMBER, alpha=min(1, (k - 0.3) / 0.3))
    c.restore()


def statbox(c, t, rows, x=640, y=520):
    """deadpan data box (news 'key facts' panel)"""
    if t <= 0: return
    k = eout(t / 0.35); h = 70 + 70 * len(rows)
    c.save(); c.translate((1 - k) * 500, 0)
    c.set_source_rgba(*NEWSBLUE, 0.92); c.rectangle(x, y, 400, h); c.fill()
    c.set_source_rgb(*AMBER); c.rectangle(x, y, 400, 56); c.fill()
    text(c, "KEY FACTS", x + 200, y + 40, 32, col=NEWSBLUE)
    for j, (a_, b_) in enumerate(rows):
        yy = y + 110 + j * 70; text(c, a_, x + 24, yy, 30, col=WHITE, align="left"); text(c, b_, x + 376, yy, 30, col=AMBER, align="right")
    c.restore()


def speedometer(c, x, y, r, frac, label, unit, t):
    c.save(); c.translate(x, y)
    c.set_source_rgba(*NEWSBLUE, 0.92); c.arc(0, 0, r + 30, math.pi, 2 * math.pi); c.close_path(); c.fill()
    for k in range(11):
        a = math.pi + k * math.pi / 10
        c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(6 if k % 5 == 0 else 3)
        c.move_to(math.cos(a) * r * 0.8, math.sin(a) * r * 0.8); c.line_to(math.cos(a) * r, math.sin(a) * r); c.stroke()
    a = math.pi + math.pi * frac + 0.02 * math.sin(t * 20) * frac
    c.set_source_rgb(*NEWSRED); c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(0, 0); c.line_to(math.cos(a) * r * 0.85, math.sin(a) * r * 0.85); c.stroke()
    c.set_source_rgb(*AMBER); c.arc(0, 0, 18, 0, 2 * math.pi); c.fill()
    text(c, label, 0, 90, 64, col=WHITE, stroke=10); text(c, unit, 0, 140, 36, col=AMBER, stroke=8)
    c.restore()


def sheet_flow(c, t, k):
    """cross-section: a thin sheet of water moving THROUGH the sawgrass over limestone (simplified)"""
    bg(c, "heron", HERON, t)
    y0 = 760; c.save(); a = ease(k)
    c.set_source_rgba(*hexc("8A7A5A"), a); c.rectangle(-20, y0 + 200, W + 40, 400); c.fill()      # limestone / peat
    c.set_source_rgba(*hexc("3FA7C9"), 0.85 * a); c.rectangle(-20, y0 + 120, W + 40, 80); c.fill()  # shallow water
    for j in range(40):                                                                                 # sawgrass blades
        x = j * 28 + 10; h = 220 + (j * 37) % 120; sw = 10 * math.sin(t * 2 + j)
        c.set_source_rgba(*GRASS, a); c.set_line_width(5); c.move_to(x, y0 + 200); c.curve_to(x + sw, y0 + 100, x + sw * 2, y0, x + sw * 3, y0 + 200 - h); c.stroke()
    for j in range(6):                                                                                  # flow arrows
        ph_ = (t * 0.35 + j / 6) % 1.0; x = lerp(-60, W + 60, ph_)
        c.set_source_rgba(1, 1, 1, 0.9 * a); c.move_to(x, y0 + 140); c.line_to(x + 50, y0 + 160); c.line_to(x, y0 + 180); c.close_path(); c.fill()
    text(c, "SAWGRASS", 200, y0 - 60, 40, col=WHITE, stroke=8, alpha=a)
    text(c, "SHALLOW WATER, FLOWING", W / 2, y0 + 300, 40, col=WHITE, stroke=8, alpha=a)
    text(c, "(simplified)", W / 2, y0 + 360, 26, col=WHITE, stroke=6, alpha=0.8 * a)
    c.restore()


def slope_profile(c, t, k):
    """Lake Okeechobee -> Florida Bay, ~100 miles, dropping < 2 inches per mile (vertical hugely exaggerated)"""
    bg(c, "orbit", ORBIT, t)
    a = ease(k); x0, x1, ya, yb = 90, 990, 760, 960
    c.set_source_rgba(*NEWSBLUE, 0.85 * a); c.rectangle(60, 600, 960, 520); c.fill()
    c.move_to(x0, ya); c.line_to(x0 + (x1 - x0) * a, lerp(ya, yb, a)); c.line_to(x0 + (x1 - x0) * a, 1080); c.line_to(x0, 1080); c.close_path()
    c.set_source_rgba(*GRASS, 0.9); c.fill()
    for j in range(8):
        ph_ = (t * 0.3 + j / 8) % 1.0
        if ph_ > a: continue
        x = lerp(x0, x1, ph_); y = lerp(ya, yb, ph_) - 18
        c.set_source_rgba(*hexc("5FD0F0"), 0.95); c.arc(x, y, 12, 0, 2 * math.pi); c.fill()
    text(c, "LAKE OKEECHOBEE", x0, ya - 40, 32, col=WHITE, align="left", alpha=a)
    if a > 0.95: text(c, "FLORIDA BAY", x1, yb - 50, 32, col=WHITE, align="right")
    text(c, "~100 MILES", W / 2, 1060, 36, col=AMBER, alpha=a)
    text(c, "drop exaggerated", W / 2, 1110, 24, col=WHITE, alpha=0.8 * a)


def kitchen(c, t, k):
    """deadpan: a kitchen floor at a jaunty 1-degree tilt vs the Everglades' 2-inches-per-mile"""
    bg(c, "orbit", ORBIT, t)
    a = ease(k)
    c.set_source_rgba(*NEWSBLUE, 0.9 * a); c.rectangle(60, 600, 960, 520); c.fill()
    for j, (lab, ang, col) in enumerate((("YOUR KITCHEN FLOOR", 0.035, AMBER), ("THE EVERGLADES", 0.0006, GRASS))):
        y = 760 + j * 210
        c.save(); c.translate(140, y); c.rotate(ang * a)
        c.set_source_rgb(*col); c.rectangle(0, 0, 800, 22); c.fill(); c.restore()
        text(c, lab, 140, y - 26, 34, col=WHITE, align="left", alpha=a)
    text(c, "STEEPER", 900, 720, 34, col=AMBER, align="right", alpha=ease((k - 1.0) / 0.3))


def shrink_map(c, t, k):
    """original Everglades area vs what remains (less than half) — bars, not a traced map"""
    to_ctx(c, finish(ISSFL.kb(min(1, t / 5), 1.15, 1.2, (0.4, 0.55), (0.42, 0.55)), t, vign=0.35))
    a = ease(k)
    for j, (lab, frac, col) in enumerate((("ORIGINAL", 1.0, GRASS), ("TODAY", 0.45, AMBER))):
        y = 720 + j * 190; f = lerp(1.0, frac, ease((k - 0.6) / 0.8)) if j else 1.0
        c.set_source_rgba(*NEWSBLUE, 0.9 * a); c.rectangle(60, y - 70, 960, 160); c.fill()
        text(c, lab, 90, y - 15, 38, col=WHITE, align="left", alpha=a)
        c.set_source_rgba(*col, a); c.rectangle(90, y + 15, 900 * f, 50); c.fill()
    text(c, "LESS THAN HALF REMAINS", W / 2, 1060, 40, col=AMBER, stroke=8, alpha=ease((k - 1.2) / 0.3))


# ---------------- scenes ----------------
def s0(c, t, d, gt):   # D: breaking, a river 30 miles wide
    ph(c, BACK, t, d, 1.0, 1.12, (0.5, 0.45), (0.5, 0.5)); bug(c, gt); ticker(c, gt)
    if t > 2.6:
        k = ease((t - 2.6) / 0.6); c.set_source_rgba(1, 1, 1, k); c.set_line_width(6)
        c.move_to(90, 820); c.line_to(90 + 900 * k, 820); c.stroke()
        for x in (90, 90 + 900 * k): c.move_to(x, 795); c.line_to(x, 845); c.stroke()
        text(c, "UP TO 30+ MILES", W / 2, 790, 54, col=WHITE, stroke=10, alpha=k)
    lower_third(c, t - 0.4, "FLORIDA RIVER 'UP TO 30 MILES WIDE'", "DANIEL", "NEWS DESK")
    source_tag(c, "Photo: Everglades NPS (PD) · Source: National Park Service", t - 0.5, y=1040, size=22)


def s1(c, t, d, gt):   # D: hiding in plain sight; reporter standing in it
    ph(c, GARDNER, t, d, 1.05, 1.15, (0.5, 0.55), (0.55, 0.55)); bug(c, gt); ticker(c, gt)
    lower_third(c, t - 0.2, "HIDING IN PLAIN SIGHT")
    if t > 3.0: lower_third(c, t - 3.0, "LIVE: THE EVERGLADES, FLORIDA", tab="LIVE", y=1290)


def s2(c, t, d, gt):   # A: in the Everglades, shoes in the river
    ph(c, PRAIRIE, t, d, 1.0, 1.1, (0.5, 0.6), (0.5, 0.62)); bug(c, gt); ticker(c, gt)
    lower_third(c, t - 0.1, "REPORTER CONFIRMS SHOES ARE WET", "ALICE", "FIELD REPORTER • THE EVERGLADES", tab="LIVE")
    statbox(c, t - 2.4, (("LOCATION", "IN RIVER"), ("SHOES", "WET")))
    source_tag(c, "Photo: Moni3 / CC BY 3.0", t - 0.3, y=1040)


def s3(c, t, d, gt):   # D: looks like a field
    ph(c, PRAIRIE, t + 4, d + 4, 1.1, 1.2, (0.5, 0.6), (0.55, 0.6)); bug(c, gt); ticker(c, gt)
    lower_third(c, t - 0.2, "ANCHOR: 'IT LOOKS LIKE A FIELD'")


def s4(c, t, d, gt):   # A: shallow water full of sawgrass — the river of grass
    if t < 2.4:
        ph(c, HERON, t, 2.4, 1.0, 1.1, (0.5, 0.5), (0.55, 0.5)); bug(c, gt); ticker(c, gt)
        source_tag(c, "Photo: ImagePerson / CC BY 4.0", t - 0.2, y=1040)
    else:
        tt = t - 2.4; sheet_flow(c, tt, tt / 0.5); bug(c, gt); ticker(c, gt, y=1560)
        if tt > 3.6: lower_third(c, tt - 3.6, "THE 'RIVER OF GRASS'", y=1290)


def s5(c, t, d, gt):   # D: how fast?
    ph(c, TEAL, t, d, 1.0, 1.08); bug(c, gt); ticker(c, gt)
    speedometer(c, W / 2, 880, 260, 0.0, "?", "SPEED", t)
    lower_third(c, t - 0.3, "HOW FAST IS IT?")
    source_tag(c, "Photo: NPS Digital Image Archives (PD)", t - 0.3, y=1040)


def s6(c, t, d, gt):   # A: winter ~100 feet a day
    ph(c, TEAL, t + 2, d + 2, 1.08, 1.14); bug(c, gt); ticker(c, gt)
    speedometer(c, W / 2, 880, 260, 0.02 * ease(t / 0.8), "100 FT", "A DAY (WINTER)", t)
    lower_third(c, t - 0.5, "WINTER FLOW: ABOUT 100 FEET A DAY")


def s7(c, t, d, gt):   # D: faster queues
    ph(c, TEAL, t + 5, d + 5, 1.14, 1.2); bug(c, gt); ticker(c, gt)
    speedometer(c, W / 2, 880, 260, 0.02, "100 FT", "A DAY", t)
    statbox(c, t - 1.6, (("THE RIVER", "<0.001 MPH"), ("A QUEUE", "FASTER")), x=600, y=440)
    lower_third(c, t - 0.3, "ANCHOR UNIMPRESSED")


def s8(c, t, d, gt):   # A: summer up to a mile a day
    ph(c, BROWARD, t, d, 1.0, 1.1, (0.5, 0.4), (0.5, 0.5)); bug(c, gt); ticker(c, gt)
    speedometer(c, W / 2, 880, 260, 0.02 + 0.5 * ease((t - 0.6) / 1.0), "1 MILE", "A DAY (SUMMER)", t)
    if t > 3.0: lower_third(c, t - 3.0, "'PRACTICALLY A SPRINT'")
    source_tag(c, "Photo: formulanone / CC BY-SA 2.0 · Source: NPS", t - 0.3, y=1040)


def s9(c, t, d, gt):   # D: what makes it flow?
    ph(c, SFLA, t, d, 1.0, 1.05, (0.25, 0.5), (0.25, 0.5)); bug(c, gt); ticker(c, gt)
    lower_third(c, t - 0.2, "WHAT MAKES IT FLOW?")
    source_tag(c, "Image: NASA (PD)", t - 0.2, y=1040)


def s10(c, t, d, gt):  # A: slope < 2 in/mile, Lake Okeechobee -> Florida Bay
    slope_profile(c, t, t / 2.6); bug(c, gt); ticker(c, gt, y=1560)
    lower_third(c, t - 0.4, "LAND DROPS < 2 INCHES PER MILE", y=1290)
    source_tag(c, "Source: Florida Museum · Image: NASA (PD)", t - 0.5, y=560)


def s11(c, t, d, gt):  # D: kitchen floor steeper
    kitchen(c, t, t / 0.8); bug(c, gt); ticker(c, gt, y=1560)
    lower_third(c, t - 1.8, "ANCHOR'S KITCHEN FLOOR 'STEEPER'", y=1290)


def s12(c, t, d, gt):  # A: used to be twice the size, more than half drained
    shrink_map(c, t, t / 1.0); bug(c, gt); ticker(c, gt, y=1560)
    lower_third(c, t - 2.6, "MORE THAN HALF DRAINED", y=1290)
    source_tag(c, "Image: NASA ISS (PD) · Source: Florida Museum", t - 0.3, y=560)


def s13(c, t, d, gt):  # D: gamers may recognise its look-alike in GTA 6
    ph(c, BACK, t, d, 1.15, 1.25, (0.4, 0.5), (0.45, 0.5)); bug(c, gt); ticker(c, gt)
    lower_third(c, t - 0.3, "SPOTTED: A VIDEO-GAME LOOK-ALIKE (GTA 6)", tab="TRENDING")
    statbox(c, t - 1.6, (("LOOK-ALIKE", "IN GTA 6"), ("REAL ONE", "100 FT/DAY")), x=600, y=440)


def s14(c, t, d, gt):  # A: the real one is slower; sign-off
    ph(c, GARDNER, t, d, 1.0, 1.1, (0.5, 0.5), (0.45, 0.5)); bug(c, gt); ticker(c, gt)
    if t < 2.0: lower_third(c, t - 0.2, "THE REAL ONE: 'MUCH SLOWER'")
    else:
        tt = t - 2.0; c.save(); k = eout(tt / 0.4); c.translate(-(1 - k) * W, 0)
        c.set_source_rgba(*NEWSBLUE, 0.95); c.rectangle(40, 1150, 1000, 120); c.fill()
        c.set_source_rgb(*NEWSRED); c.rectangle(40, 1150, 14, 120); c.fill()
        text(c, "ALICE", 80, 1205, 50, col=WHITE, align="left")
        text(c, "HOW ON EARTH NEWS  •  THE EVERGLADES", 80, 1250, 30, col=AMBER, align="left"); c.restore()


def s15(c, t, d, gt):  # D: "And that is the news. Slowly." + closing ident / end card
    if t < d:
        ph(c, BACK, t, d, 1.0, 1.04, (0.5, 0.45), (0.5, 0.45)); bug(c, gt); ticker(c, gt)
        lower_third(c, t - 0.1, "AND THAT IS THE NEWS. SLOWLY.", tab="END")
    else:
        tt = t - d; to_ctx(c, finish(BACK.kb(0, 1.0, 1.0, (0.5, 0.45), (0.5, 0.45)), t, vign=0.35))
        sting(c, min(tt, 0.9))
        k = eout(tt / 0.4)
        end_card_logo(c, tt, W / 2, 1150, 200, LOGO) if tt > 0.9 else None
        text(c, "Follow for next Friday's bulletin", W / 2, 1420, 46, col=WHITE, stroke=10, alpha=k)


LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))


def opening(c, t, gt):
    to_ctx(c, finish(BACK.kb(0, 1.0, 1.0, (0.5, 0.45), (0.5, 0.45)), t, vign=0.35))
    sting(c, min(t * 0.75, 0.95)); bug(c, gt)
    text(c, "FRIDAY 27 NOV", W - 70, 302, 30, col=WHITE, align="right", stroke=6)


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15]
assert len(SCENES) == len(meta)


def frame(c, gt, surf):
    c.set_source_rgb(*MID); c.paint()
    if gt < PRE:
        opening(c, gt, gt); badge(c, gt); return
    i = max(j for j in range(len(STARTS)) if STARTS[j] <= gt + 1e-9); t = gt - STARTS[i]; d = DURS[i]
    SCENES[i](c, t, d, gt)
    if 0 < i and t < 0.3: whip(surf, t, direction=1 if i % 2 else -1, maxpx=90)
    badge(c, gt)
    if t < d: captions(c, meta[i]["cap"], meta[i]["dur"], t, speaker=meta[i].get("speaker"), words=meta[i].get("words"), y=1470)


def events():
    s = STARTS
    ev = [("news_open", 0.0)] + [("whoosh", x - 0.05) for x in s[1:]]
    ev += [("pop", s[0] + 0.4), ("tick", s[0] + 2.6), ("pop", s[1] + 0.2), ("pop", s[1] + 3.0), ("pop", s[2] + 0.1), ("ding", s[2] + 2.4)]
    ev += [("pop", s[3] + 0.2), ("pop", s[4] + 2.4), ("pop", s[4] + 6.0), ("pop", s[5] + 0.3)] + [("tick", s[6] + 0.1 + k * 0.3) for k in range(3)]
    ev += [("pop", s[7] + 0.3), ("thunk", s[7] + 1.6)] + [("tick", s[8] + 0.6 + k * 0.1) for k in range(10)] + [("pop", s[8] + 3.0)]
    ev += [("pop", s[9] + 0.2), ("pop", s[10] + 0.4), ("pop", s[11] + 1.8), ("thunk", s[11] + 1.0), ("pop", s[12] + 2.6), ("pop", s[13] + 0.3), ("ding", s[13] + 1.6)]
    ev += [("pop", s[14] + 0.2), ("pop", s[14] + 2.0), ("pop", s[15] + 0.1), ("news_close", s[15] + DURS[15] - 0.3)]
    return ev


if __name__ == "__main__":
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    if sys.argv[1] == "stills":
        for x in sys.argv[3:]: frame(c, float(x), surf); surf.write_to_png(f"{sys.argv[2]}_{x}.png")
    else:
        json.dump({"total": TOTAL, "events": events(), "voice_offset": PRE, "music_style": "news"}, open("events.json", "w"))
        a, b = (int(v) for v in sys.argv[2:4]) if len(sys.argv) > 3 else (0, int(math.ceil(TOTAL * FPS)))
        out = sys.argv[4] if len(sys.argv) > 4 else "video.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a, b): frame(c, f / FPS, surf); p.stdin.write(surf.get_data())
        p.stdin.close(); p.wait(); print("frames", a, b, "total", TOTAL)
