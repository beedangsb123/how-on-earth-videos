"""Audio v2: voice lines placed on the timeline + original synth music (driving pulse, ducked
under the voice) + synthesised SFX (whoosh, boom, tick, thunk, crack, pop, drill).
usage (in work dir with meta.json, l*.wav, events.json): python audio2.py [pad] [transpose] [bpm]  -> mix.wav
Rotate transpose (semitones from A minor) and bpm every video (anti-slop rule). 003: +5 (D minor), 92 bpm.
SFX kinds: whoosh boom tick thunk crack pop drill hiss (steam roar) bubble (rising blips) splash."""
import json, sys, numpy as np, soundfile as sf
SR = 44100
PAD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25
TR = int(sys.argv[2]) if len(sys.argv) > 2 else 0
BPM = float(sys.argv[3]) if len(sys.argv) > 3 else 100
meta = json.load(open("meta.json")); ev = json.load(open("events.json"))
T = ev["total"]; N = int(T * SR) + SR
t = np.arange(N) / SR
rng = np.random.default_rng(4)

# ---- voice ----
voice = np.zeros(N); pos = 0.0
for i, m in enumerate(meta):
    a, sr = sf.read(f"l{i}.wav")
    if a.ndim > 1: a = a.mean(1)
    if sr != SR: a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    s = int(pos * SR); voice[s:s + len(a)] += a[:N - s]; pos += m["dur"] + PAD
voice = voice / (np.max(np.abs(voice)) + 1e-9) * 0.92

# ---- music: A minor driving pulse, 100 bpm ----
def hz(n): return 440 * 2 ** ((n + TR - 69) / 12)
beat = 60.0 / BPM; music = np.zeros(N)
prog = [[45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [48, 55, 60, 64, 67], [43, 50, 55, 59, 62]]
bar = beat * 4
for b in range(int(T / bar) + 1):
    ch = prog[b % 4]; s = int(b * bar * SR); e = min(N, int((b + 1) * bar * SR + 0.5 * SR))
    tt = t[s:e] - b * bar; env = np.clip(tt / 0.4, 0, 1) * np.clip((bar + 0.5 - tt) / 0.6, 0, 1)
    for n in ch[1:]:
        f = hz(n); music[s:e] += 0.10 * env * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 1.004 * tt))
    for k in range(8):  # eighth-note bass pulse
        s2 = int((b * bar + k * beat / 2) * SR); e2 = min(N, s2 + int(0.28 * SR)); t2 = t[s2:e2] - (b * bar + k * beat / 2)
        music[s2:e2] += 0.32 * np.exp(-t2 * 9) * np.sin(2 * np.pi * hz(ch[0] - 12) * t2)
    for k in range(16):  # sixteenth arpeggio
        s2 = int((b * bar + k * beat / 4) * SR); e2 = min(N, s2 + int(0.14 * SR)); t2 = t[s2:e2] - (b * bar + k * beat / 4)
        n = ch[[1, 2, 3, 4, 3, 2][k % 6]] + 12
        music[s2:e2] += 0.07 * np.exp(-t2 * 22) * np.sign(np.sin(2 * np.pi * hz(n) * t2)) * 0.5
    for k in range(4):  # kick on beats
        s2 = int((b * bar + k * beat) * SR); e2 = min(N, s2 + int(0.2 * SR)); t2 = t[s2:e2] - (b * bar + k * beat)
        music[s2:e2] += 0.45 * np.exp(-t2 * 25) * np.sin(2 * np.pi * (50 + 90 * np.exp(-t2 * 40)) * t2)
music /= np.max(np.abs(music)) + 1e-9
# duck under voice
env = np.convolve(np.abs(voice), np.ones(2205) / 2205, mode="same")
duck = 1 - 0.6 * np.clip(env / 0.05, 0, 1)
duck = np.convolve(duck, np.ones(4410) / 4410, mode="same")
music *= 0.32 * duck
music *= np.clip((T - t) / 1.0, 0, 1)

# ---- sfx ----
sfx = np.zeros(N)
def add(at, a):
    s = int(at * SR)
    if s < 0: a = a[-s:]; s = 0
    e = min(N, s + len(a)); sfx[s:e] += a[:e - s]
def lp(x, k):  # crude low-pass
    return np.convolve(x, np.ones(k) / k, mode="same")
L = lambda d: np.arange(int(d * SR)) / SR
for kind, at in ev["events"]:
    if kind == "whoosh":
        tt = L(0.45); n = rng.standard_normal(len(tt))
        x = lp(n, 6) - lp(n, 40); add(at - 0.1, 0.35 * x * np.sin(np.pi * tt / 0.45) ** 2)
    elif kind == "boom":
        tt = L(1.4); add(at, 0.9 * np.exp(-tt * 3.5) * np.sin(2 * np.pi * (38 + 60 * np.exp(-tt * 12)) * tt) + 0.1 * lp(rng.standard_normal(len(tt)), 60) * np.exp(-tt * 6))
    elif kind == "tick":
        tt = L(0.03); add(at, 0.18 * np.exp(-tt * 300) * np.sin(2 * np.pi * 2400 * tt))
    elif kind == "thunk":
        tt = L(0.18); add(at, 0.35 * np.exp(-tt * 30) * np.sin(2 * np.pi * (120 + 80 * np.exp(-tt * 50)) * tt) + 0.08 * lp(rng.standard_normal(len(tt)), 8) * np.exp(-tt * 60))
    elif kind == "crack":
        tt = L(0.6); n = rng.standard_normal(len(tt)) * (rng.random(len(tt)) > 0.97)
        add(at, 0.7 * lp(n, 3) * np.exp(-tt * 6))
    elif kind == "pop":
        tt = L(0.12); add(at, 0.25 * np.exp(-tt * 40) * np.sin(2 * np.pi * (600 + 900 * tt) * tt))
    elif kind == "drill":
        tt = L(2.6); add(at, 0.07 * np.sign(np.sin(2 * np.pi * 55 * tt)) * lp(rng.standard_normal(len(tt)), 4) * np.clip(tt / 0.2, 0, 1) * np.clip((2.6 - tt) / 0.3, 0, 1))
    elif kind == "hiss":  # steam roar: band-passed noise swelling over 2.5 s
        tt = L(2.5); n = rng.standard_normal(len(tt)); x = lp(n, 3) - lp(n, 30)
        add(at, 0.22 * x * np.clip(tt / 0.3, 0, 1) * np.clip((2.5 - tt) / 1.2, 0, 1))
    elif kind == "bubble":
        for j in range(7):
            tt = L(0.07); f = 500 + 120 * j + rng.random() * 80
            add(at + j * 0.09, 0.12 * np.exp(-tt * 50) * np.sin(2 * np.pi * (f + 2500 * tt) * tt))
    elif kind == "splash":
        tt = L(0.7); n = rng.standard_normal(len(tt)); add(at, 0.3 * (lp(n, 2) - lp(n, 12)) * np.exp(-tt * 6))
mix = voice + music + 0.8 * sfx
mix = mix[:int(T * SR)]
mix = mix / np.max(np.abs(mix)) * 0.95
sf.write("mix.wav", np.stack([mix, mix], 1), SR)
print("audio", len(mix) / SR)
