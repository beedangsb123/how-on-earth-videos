"""outro.py (added 2026-11-28, Bidhan: "the video ends abruptly near the end — Follow for... add to the end").
Replaces a finished video's old end card with a proper outro: a SPOKEN follow line in one of the video's own
ElevenLabs voices, a closing card (blurred last scene + logo + FOLLOW FOR MORE), and a warm chord that rings out to
silence, so nothing is cut off mid-sound.  New renders build this in directly (render_012b: END 2.8 + "outro" SFX +
music_fade); this tool fixes videos that were already rendered.
usage: python outro.py in.mp4 old_end_seconds voice_id "Follow for more!" out.mp4 [outro_seconds=2.6]"""
import sys, os, json, math, subprocess, tempfile, numpy as np, soundfile as sf, cairo
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import W, H, FPS, text, text_w, rrect, hexc, ease, eout, back, end_card_logo, badge
import tts_el

SR = 44100
src, old_end, voice, line, out = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
OUT_S = float(sys.argv[6]) if len(sys.argv) > 6 else 2.6
tmp = tempfile.mkdtemp()
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]))
cut = dur - old_end

# ---- spoken follow line (single short ElevenLabs call, eleven_v3) ----
import base64
r = subprocess.run(["curl", "-s", "-m", "120", "-w", "\n%{http_code}", "-H", f"xi-api-key: {tts_el.key()}", "-H", "Content-Type: application/json",
                    "-X", "POST", "-d", json.dumps({"text": line, "model_id": "eleven_v3", "voice_settings": {"stability": 0.0}}),
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"], capture_output=True)
body, _, code = r.stdout.rpartition(b"\n")
if code != b"200": sys.exit("ElevenLabs HTTP " + code.decode())
open(f"{tmp}/v.mp3", "wb").write(body)
subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/v.mp3", "-ac", "1", "-ar", str(SR), f"{tmp}/v.wav"])
v, _ = sf.read(f"{tmp}/v.wav")
rms = np.sqrt(np.convolve(v ** 2, np.ones(441) / 441, "same")); on = np.nonzero(rms > 0.01)[0]
v = v[max(0, on[0] - 400):min(len(v), on[-1] + 2000)]                          # trim silence around the line
v = v / (np.abs(v).max() + 1e-9) * 0.9
OUT_S = max(OUT_S, 0.15 + len(v) / SR + 1.0)   # the card always outlasts the spoken line by ~1 s (chord rings out after it)

# ---- audio: original up to the cut (0.5 s fade) + chord that rings out + the voice ----
subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", str(SR), f"{tmp}/a.wav"])
a, _ = sf.read(f"{tmp}/a.wav"); a = a.mean(1)
n_cut = int(cut * SR); body_a = a[:n_cut + int(0.5 * SR)].copy()
fade = np.linspace(1, 0, int(0.5 * SR)); body_a[n_cut:] *= fade
N = n_cut + int(OUT_S * SR); mix = np.zeros(N); mix[:len(body_a)] += body_a[:N]
tt = np.arange(int(OUT_S * SR)) / SR
env = np.clip(tt / 0.2, 0, 1) * np.exp(-tt * 1.4) * np.clip((OUT_S - tt) / 0.4, 0, 1)
chord = sum(np.sin(2 * np.pi * f * tt) * (1 + 0.12 * np.sin(2 * np.pi * 4.5 * tt)) for f in (146.8, 220.0, 293.7, 370.0, 440.0))
mix[n_cut:] += 0.09 * env * chord
vs = n_cut + int(0.15 * SR); mix[vs:vs + len(v)] += v[:N - vs] * 0.95
mix = mix / np.abs(mix).max() * 0.95
mix[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
sf.write(f"{tmp}/mix.wav", np.stack([mix, mix], 1), SR)

# ---- closing card frames over the blurred last scene ----
subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", f"{cut - 0.1:.2f}", "-i", src, "-frames:v", "1", f"{tmp}/last.png"])
bgim = Image.open(f"{tmp}/last.png").convert("RGB").filter(ImageFilter.GaussianBlur(14))
bga = (np.asarray(bgim, np.float32) * 0.6).astype(np.uint8)
LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"))
LIME = hexc("A6F03C"); surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
bgs = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
np.frombuffer(bgs.get_data(), np.uint8).reshape(H, W, 4)[:, :, :3] = bga[:, :, ::-1]; bgs.mark_dirty()
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", f"{tmp}/card.mp4"], stdin=subprocess.PIPE)
for f in range(int(round(OUT_S * FPS))):
    t = f / FPS; c.set_source_surface(bgs, 0, 0); c.paint()
    end_card_logo(c, t, W / 2, 760, 270, LOGO)
    k = back(min(1, t / 0.35)); s = "FOLLOW FOR MORE"; sz = 86; w = text_w(c, s, sz) + 90
    c.save(); c.translate(W / 2, 1150); c.scale(k, k)
    c.set_source_rgba(0.06, 0.1, 0.24, 0.95); rrect(c, -w / 2, -sz * 0.8, w, sz * 1.6, 24); c.fill()
    c.set_source_rgba(*LIME, 1); rrect(c, -w / 2, -sz * 0.8, 16, sz * 1.6, 8); c.fill()
    text(c, s, 0, sz * 0.36, sz, col=(1, 1, 1)); c.restore()
    if t > 0.5: text(c, "a new wonder, explained daily", W / 2, 1360, 44, col=(1, 1, 1), stroke=8, alpha=ease((t - 0.5) / 0.4))
    badge(c, cut + t)
    p.stdin.write(surf.get_data())
p.stdin.close(); p.wait()

# ---- join: original video up to the cut + closing card, new audio ----
subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", f"{tmp}/card.mp4", "-i", f"{tmp}/mix.wav", "-filter_complex",
                       f"[0:v]trim=0:{cut:.3f},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[a];[1:v]fps={FPS},format=yuv420p[b];[a][b]concat=n=2:v=1:a=0[v]",
                       "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "192k", "-shortest", out])
print("outro done", out, round(cut + OUT_S, 2), "s")
