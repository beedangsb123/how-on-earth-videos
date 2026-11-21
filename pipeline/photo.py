"""Real-photo helpers shared by renders (moved out of render_002b.py on 2026-11-21):
Photo(path, archival=False, maxz=1.35).kb(k, z0, z1, f0, f1) -> Ken Burns HxWx3 float;
finish(a, t, archival, heat, xray, vign) -> graded uint8; to_ctx(c, a) paints it; blur(a, r) soft background."""
import numpy as np, cairo
from PIL import Image, ImageFilter
from engine import *


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



def blur(a, r=12, dim=0.7):
    return (np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(r)), np.float32) * dim).astype(np.uint8)
