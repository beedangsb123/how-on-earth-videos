"""Cartoon avatar hosts (added 2026-11-23 for the 006 test; Bidhan chose stylised hosts in a corner box).
ORIGINAL characters drawn with cairo — clearly cartoon (no real-person likeness, no known characters) so no AI label
is needed. Mouth moves with the real voice (RMS of l{i}.wav), eyes blink, brows react, optional pointing arm.
  from avatar import Char, Talk, avatar_card
  talk = Talk(meta)                 # meta.json from tts_el.py (l{i}.wav in the cwd)
  m = talk.mouth(gt, "M")           # 0..1 mouth opening for that speaker at global time gt
  avatar_card(c, ERIC, x, y, s, gt, mouth=m, active=True, mood="surprised", name="ERIC")
Characters are plain dicts so every video can get a NEW pair (PLAYBOOK: different characters every day)."""
import math, json, numpy as np, soundfile as sf, cairo
from engine import *

FPSA = 100  # envelope samples per second


class Talk:
    def __init__(self, meta):
        self.meta = meta; self.starts = []; t = 0
        for m in meta: self.starts.append(t); t += m["dur"]
        self.env = []
        for i, m in enumerate(meta):
            a, sr = sf.read(f"l{i}.wav")
            if a.ndim > 1: a = a.mean(1)
            hop = sr // FPSA; n = len(a) // hop
            r = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1))
            r = np.convolve(r, np.ones(3) / 3, mode="same")
            self.env.append(np.clip((r - 0.01) / 0.09, 0, 1))

    def line(self, gt):
        return max(j for j in range(len(self.starts)) if self.starts[j] <= gt + 1e-9)

    def mouth(self, gt, spk):
        i = self.line(gt)
        if self.meta[i]["speaker"] != spk: return 0.0
        k = int((gt - self.starts[i]) * FPSA); e = self.env[i]
        return float(e[k]) if 0 <= k < len(e) else 0.0

    def speaking(self, gt):
        return self.meta[self.line(gt)]["speaker"]


def _blink(gt, seed):
    ph = (gt + seed * 1.7) % 3.6
    return 1 - max(0.0, 1 - abs(ph - 3.45) / 0.08) if ph > 3.3 else 1.0


def draw_char(c, ch, gt, mouth=0.0, mood="neutral", look=0.0, point=0.0):
    """character centred at (0, 0) = middle of the face, face radius ~100 units"""
    skin, hair, shirt = ch["skin"], ch["hair"], ch["shirt"]
    bob = 3 * math.sin(gt * 2.2 + ch.get("seed", 0)) + 6 * mouth
    c.save(); c.translate(0, bob * 0.3)
    # shoulders / shirt
    c.move_to(-170, 260); c.curve_to(-160, 150, -90, 120, 0, 120); c.curve_to(90, 120, 160, 150, 170, 260); c.close_path()
    g = cairo.LinearGradient(0, 120, 0, 260); g.add_color_stop_rgb(0, *shirt); g.add_color_stop_rgb(1, *[v * 0.7 for v in shirt])
    c.set_source(g); c.fill()
    if ch.get("tie"):
        c.move_to(-14, 128); c.line_to(14, 128); c.line_to(22, 230); c.line_to(0, 250); c.line_to(-22, 230); c.close_path(); c.set_source_rgb(*ch["tie"]); c.fill()
    if ch.get("collar", True):
        c.set_source_rgb(0.96, 0.96, 0.98)
        c.move_to(-40, 120); c.line_to(0, 150); c.line_to(-10, 175); c.line_to(-55, 135); c.close_path(); c.fill()
        c.move_to(40, 120); c.line_to(0, 150); c.line_to(10, 175); c.line_to(55, 135); c.close_path(); c.fill()
    # neck
    c.rectangle(-28, 70, 56, 60); c.set_source_rgb(*[v * 0.88 for v in skin]); c.fill()
    # pointing arm
    if point > 0:
        c.save(); c.translate(120, 190); c.rotate(-0.9 * ease(point))
        c.set_source_rgb(*shirt); rrect(c, -22, -22, 150, 44, 22); c.fill()
        c.set_source_rgb(*skin); c.arc(140, 0, 26, 0, 2 * math.pi); c.fill(); rrect(c, 150, -8, 50, 16, 8); c.fill()
        c.restore()
    # back hair (long styles)
    if ch.get("long"):
        c.move_to(-110, -20); c.curve_to(-130, 80, -120, 150, -70, 170); c.line_to(70, 170); c.curve_to(120, 150, 130, 80, 110, -20); c.close_path()
        c.set_source_rgb(*hair); c.fill()
    # ears + head
    for sx in (-1, 1):
        c.set_source_rgb(*[v * 0.92 for v in skin]); c.arc(sx * 98, 10, 22, 0, 2 * math.pi); c.fill()
    g = cairo.RadialGradient(-30, -40, 10, 0, 0, 120)
    g.add_color_stop_rgb(0, *[min(1, v * 1.08) for v in skin]); g.add_color_stop_rgb(1, *[v * 0.9 for v in skin])
    c.save(); c.scale(1, 1.08); c.arc(0, 0, 100, 0, 2 * math.pi); c.restore(); c.set_source(g); c.fill()
    # hair (top)
    style = ch.get("style", "short")
    c.set_source_rgb(*hair)
    if style == "short":
        c.move_to(-102, -10); c.curve_to(-110, -110, -30, -128, 10, -118); c.curve_to(70, -120, 112, -80, 102, -10)
        c.curve_to(90, -60, 40, -78, 0, -70); c.curve_to(-40, -80, -90, -60, -102, -10); c.fill()
    elif style == "quiff":
        c.move_to(-102, -10); c.curve_to(-112, -100, -40, -150, 30, -140); c.curve_to(90, -132, 116, -80, 102, -10)
        c.curve_to(80, -70, 30, -95, -10, -80); c.curve_to(-50, -70, -90, -50, -102, -10); c.fill()
    elif style == "bob":
        c.move_to(-114, 80); c.line_to(-114, -20); c.curve_to(-118, -152, 118, -152, 114, -20); c.line_to(114, 80)
        c.line_to(98, 80); c.line_to(98, -20); c.curve_to(80, -66, 40, -60, 0, -64); c.curve_to(-40, -60, -80, -66, -98, -20)
        c.line_to(-98, 80); c.close_path(); c.fill()
    elif style == "bun":
        c.arc(0, -120, 38, 0, 2 * math.pi); c.fill()
        c.move_to(-104, -5); c.curve_to(-108, -115, 108, -115, 104, -5); c.curve_to(80, -70, -80, -70, -104, -5); c.fill()
    elif style == "bald":
        c.move_to(-104, 10); c.curve_to(-108, -30, -95, -45, -86, -40); c.line_to(-90, 20); c.close_path(); c.fill()
        c.move_to(104, 10); c.curve_to(108, -30, 95, -45, 86, -40); c.line_to(90, 20); c.close_path(); c.fill()
    # eyes
    bl = _blink(gt, ch.get("seed", 0))
    surpr = 1.0 if mood in ("surprised", "excited") else 0.0
    er = 17 + 4 * surpr
    for sx in (-1, 1):
        ex, ey = sx * 38, -6
        c.save(); c.translate(ex, ey); c.scale(1, max(0.08, bl))
        c.set_source_rgb(1, 1, 1); c.arc(0, 0, er, 0, 2 * math.pi); c.fill()
        c.set_source_rgb(0.12, 0.1, 0.12); c.arc(4 * look, 2, er * 0.55, 0, 2 * math.pi); c.fill()
        c.set_source_rgb(1, 1, 1); c.arc(4 * look + 4, -3, 3.5, 0, 2 * math.pi); c.fill()
        c.restore()
        # brows
        lift = -12 * surpr - (6 if mood == "curious" and sx > 0 else 0)
        tilt = (0.25 * sx if mood == "serious" else -0.12 * sx * surpr)
        c.save(); c.translate(ex, ey - 32 + lift); c.rotate(tilt)
        c.set_source_rgb(*[v * 0.8 for v in hair]); rrect(c, -20, -5, 40, 10, 5); c.fill(); c.restore()
    if ch.get("glasses"):
        c.set_source_rgba(0.1, 0.1, 0.15, 1); c.set_line_width(5)
        for sx in (-1, 1): c.arc(sx * 38, -6, 28, 0, 2 * math.pi); c.stroke()
        c.move_to(-10, -8); c.line_to(10, -8); c.stroke()
    # nose + cheeks
    c.set_source_rgba(*[v * 0.8 for v in skin], 1); c.move_to(0, 4); c.curve_to(-8, 26, -2, 34, 8, 32); c.set_line_width(4); c.stroke()
    for sx in (-1, 1):
        c.set_source_rgba(1, 0.45, 0.45, 0.22); c.arc(sx * 60, 30, 16, 0, 2 * math.pi); c.fill()
    # mouth
    mo = max(0.0, min(1.0, mouth))
    smile = 0.6 if mood in ("warm", "playful", "excited", "neutral", "intrigued") else 0.2
    if mo < 0.06:
        c.move_to(-26, 52); c.curve_to(-10, 52 + 12 * smile, 10, 52 + 12 * smile, 26, 52)
        c.set_source_rgb(0.45, 0.15, 0.15); c.set_line_width(5); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    else:
        h = 6 + 26 * mo; w = 22 + 6 * mo; cy = 50 + h * 0.5
        c.save(); c.translate(0, cy); c.scale(w / 30, h / 30); c.arc(0, 0, 30, 0, 2 * math.pi); c.restore()
        c.save(); c.clip_preserve(); c.set_source_rgb(0.35, 0.08, 0.1); c.fill()
        c.rectangle(-w, cy - h, 2 * w, h * 0.42); c.set_source_rgb(1, 1, 1); c.fill()          # top teeth
        c.save(); c.translate(0, cy + h * 0.75); c.scale(w / 34, h / 60); c.arc(0, 0, 30, 0, 2 * math.pi); c.restore()
        c.set_source_rgb(0.92, 0.42, 0.48); c.fill(); c.restore(); c.new_path()                  # tongue
    if ch.get("headset"):
        c.set_source_rgb(0.15, 0.15, 0.18); c.set_line_width(9); c.arc(0, -10, 112, math.pi * 1.05, math.pi * 1.95); c.stroke()
        c.move_to(-104, 20); c.curve_to(-100, 60, -70, 75, -36, 68); c.set_line_width(5); c.stroke()
        c.arc(-34, 68, 8, 0, 2 * math.pi); c.fill()
    c.restore()


def avatar_card(c, ch, x, y, s, gt, mouth=0.0, active=False, mood="neutral", name=None, col=GOLD, look=0.0, point=0.0, box=True):
    """character in a rounded picture-in-picture card at (x, y) = card centre, scale s (card 300 x 330 at s=1)"""
    c.save(); c.translate(x, y); k = s * (1.08 if active else 1.0); c.scale(k, k)
    w, h = 300, 330
    if box:
        c.set_source_rgba(0, 0, 0, 0.45); rrect(c, -w / 2 + 8, -h / 2 + 12, w, h, 36); c.fill()
        g = cairo.LinearGradient(0, -h / 2, 0, h / 2); g.add_color_stop_rgb(0, *[min(1, v * 0.9 + 0.1) for v in ch["bg"]]); g.add_color_stop_rgb(1, *[v * 0.6 for v in ch["bg"]])
        rrect(c, -w / 2, -h / 2, w, h, 36); c.set_source(g); c.fill()
        c.save(); rrect(c, -w / 2, -h / 2, w, h, 36); c.clip()
        c.translate(0, 10); c.scale(1.05, 1.05); draw_char(c, ch, gt, mouth, mood, look, point); c.restore()
        c.set_source_rgba(*(col if active else (1, 1, 1)), 1 if active else 0.6); c.set_line_width(8 if active else 4); rrect(c, -w / 2, -h / 2, w, h, 36); c.stroke()
        if name:
            nw = text_w(c, name, 34) + 34
            c.set_source_rgb(*(col if active else (0.1, 0.12, 0.25))); rrect(c, -nw / 2, h / 2 - 28, nw, 50, 25); c.fill()
            text(c, name, 0, h / 2 + 8, 34, col=NAVY if active else WHITE)
    else:
        draw_char(c, ch, gt, mouth, mood, look, point)
    c.restore()


# a starter cast (all original): pick a different pair each video
CAST = {
    "eric":   {"skin": (0.93, 0.76, 0.62), "hair": (0.25, 0.17, 0.1), "shirt": (0.2, 0.42, 0.75), "style": "short", "bg": (0.18, 0.3, 0.55), "seed": 1, "glasses": True},
    "jess":   {"skin": (0.80, 0.58, 0.42), "hair": (0.12, 0.08, 0.06), "shirt": (0.95, 0.45, 0.3), "style": "bun", "bg": (0.55, 0.25, 0.35), "seed": 2},
    "daniel": {"skin": (0.95, 0.8, 0.7), "hair": (0.55, 0.55, 0.58), "shirt": (0.12, 0.14, 0.22), "style": "short", "bg": (0.1, 0.15, 0.3), "seed": 3, "tie": (0.75, 0.1, 0.15)},
    "lily":   {"skin": (0.96, 0.82, 0.72), "hair": (0.75, 0.35, 0.15), "shirt": (0.85, 0.75, 0.3), "style": "bob", "bg": (0.25, 0.45, 0.4), "seed": 4},
    "brian":  {"skin": (0.55, 0.38, 0.26), "hair": (0.08, 0.06, 0.05), "shirt": (0.3, 0.55, 0.35), "style": "bald", "bg": (0.2, 0.35, 0.25), "seed": 5},
    "laura":  {"skin": (0.97, 0.84, 0.74), "hair": (0.95, 0.8, 0.4), "shirt": (0.55, 0.35, 0.8), "style": "bob", "bg": (0.35, 0.25, 0.55), "seed": 6, "long": True},
}
