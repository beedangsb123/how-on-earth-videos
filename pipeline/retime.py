"""retime.py (added 2026-11-26, video 011) — fix caption drift + over-long pauses AFTER tts_el.py.
Found on 011: eleven_v3 dialogue word timestamps were 0.5-0.8 s EARLY on most lines and the pauses inside a line did
not match the audio (check_words.py), so captions would run ahead of the voice. This re-aligns every line's words to
the real voice energy, then optionally shortens long pauses and speeds up the line.
Method per line (l{i}.wav + meta.json "words"):
  1. voiced "islands" from the RMS envelope (10 ms frames; gaps < 0.15 s merged);
  2. dynamic programming assigns consecutive words to islands, matching each island's length to the words' relative
     lengths from the ElevenLabs alignment; islands can be skipped (laughs, breaths) at a cost;
  3. words are spread over their island proportionally -> every caption word sits on real voice;
  4. pauses between islands longer than --max-pause are cut from the middle (word times shifted); lead silence
     trimmed to 0.10 s (0.03 s for line 0); then optional --tempo (atempo, word times scaled).
usage (work dir): python retime.py [--max-pause 0.38] [--tempo 1.0]   (then run check_words.py)"""
import json, sys, subprocess, numpy as np, soundfile as sf

args = sys.argv[1:]
def opt(name, default):
    return float(args[args.index(name) + 1]) if name in args else default
MAXP = opt("--max-pause", 0.38); TEMPO = opt("--tempo", 1.0); TAIL = opt("--tail", 0.15)


def islands(r, fr=100):
    thr = max(0.008, 0.10 * r.max()); v = r > thr; out = []; i = 0; n = len(v)
    while i < n:
        if v[i]:
            j = i
            while j < n and v[j]: j += 1
            out.append([i / fr, j / fr]); i = j
        else: i += 1
    merged = []
    for s, e in out:
        if merged and s - merged[-1][1] < 0.15: merged[-1][1] = e
        else: merged.append([s, e])
    return [x for x in merged if x[1] - x[0] >= 0.06]


def assign(isl, d, scale, skip_pen=0.7, rel=None):
    """rel = each island's loudness vs the loudest one: quiet islands (laughs, breaths) are cheap to skip and
    costly to put words in (011 last line: '[laughs] ...tell them' put 'tell' on the laugh)"""
    I, K = len(isl), len(d); INF = 1e9
    rel = rel if rel is not None else [1.0] * I
    cs = np.concatenate([[0], np.cumsum(d)])
    C = np.full((I + 1, K + 1), INF); B = {}
    C[0, 0] = 0
    for i in range(I):
        L = isl[i][1] - isl[i][0]
        for k in range(K + 1):
            if C[i, k] >= INF: continue
            c = C[i, k] + skip_pen * L * min(1.0, 2 * rel[i])   # island i is a laugh / breath
            if c < C[i + 1, k]: C[i + 1, k] = c; B[(i + 1, k)] = (k, None)
            for k2 in range(k + 1, K + 1):
                c = C[i, k] + abs(L - scale * (cs[k2] - cs[k])) + 0.4 * max(0.0, 0.5 - rel[i])
                if c < C[i + 1, k2]: C[i + 1, k2] = c; B[(i + 1, k2)] = (k, i)
    if C[I, K] >= INF: return None
    res = {}; i, k = I, K
    while i > 0:
        k0, isl_i = B[(i, k)]
        if isl_i is not None: res[isl_i] = (k0, k)
        i, k = i - 1, k0
    return res


def realign(x, sr, words, tagged=False):
    w = int(0.01 * sr); n = len(x) // w
    r = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1)); isl_all = islands(r); isl = list(isl_all)
    # a line that opens with an audio tag ([laughs], [sighs]) often starts with a short burst + pause: not a word
    while tagged and len(isl) > 1 and isl[0][1] - isl[0][0] < 0.3 and isl[1][0] - isl[0][1] > 0.35: isl.pop(0)
    if not words or not isl: return words, isl_all
    d = np.array([max(0.08, e - s) for _, s, e in words])
    tot = sum(e - s for s, e in isl); scale = tot / d.sum(); res = None
    lo = [float(r[int(s * 100):max(int(s * 100) + 1, int(e * 100))].mean()) for s, e in isl]; rel = [v / max(lo) for v in lo]
    for _ in range(3):
        res = assign(isl, d, scale, rel=rel) or res
        if res is None: return words, isl_all
        used = sum(isl[i][1] - isl[i][0] for i in res); scale = used / d.sum()
    out = [None] * len(words)
    for i, (k0, k1) in res.items():
        s, e = isl[i]; seg = d[k0:k1]; t = s
        for j, dj in zip(range(k0, k1), seg):
            dd = (e - s) * dj / seg.sum(); out[j] = [words[j][0], round(float(t), 3), round(float(t + dd), 3)]; t += dd
    return out, isl_all


def compress(x, sr, words, isl, first):
    """cut lead silence + pauses > MAXP between islands (from the middle); returns new audio + shifted words"""
    cuts = []                                   # (time in original, seconds removed)
    lead = 0.03 if first else 0.10
    if isl and isl[0][0] > lead: cuts.append((0.0, isl[0][0] - lead, 0.0))
    for (s0, e0), (s1, e1) in zip(isl, isl[1:]):
        g = s1 - e0
        if g > MAXP: m = (e0 + s1) / 2; rm = g - MAXP; cuts.append((m - rm / 2, rm, m))
    keep = []; pos = 0.0
    for a, rm, _ in cuts:
        keep.append(x[int(pos * sr):int(a * sr)]); pos = a + rm
    end = min(len(x) / sr, (isl[-1][1] + TAIL) if isl else len(x) / sr)
    keep.append(x[int(pos * sr):int(end * sr)])
    fade = int(0.006 * sr); parts = []
    for p in keep:
        p = p.copy()
        if len(p) > 2 * fade: p[:fade] *= np.linspace(0, 1, fade); p[-fade:] *= np.linspace(1, 0, fade)
        parts.append(p)
    y = np.concatenate(parts)
    def shift(t):
        s = 0.0
        for a, rm, _ in cuts:
            if t >= a + rm: s += rm
            elif t > a: s += t - a
        return t - s
    return y, [[wd, round(shift(s), 3), round(shift(e), 3)] for wd, s, e in words]


if __name__ == "__main__":
    meta = json.load(open("meta.json"))
    for i, m in enumerate(meta):
        x, sr = sf.read(f"l{i}.wav")
        if x.ndim > 1: x = x.mean(1)
        ws, isl = realign(x, sr, m["words"], tagged=m.get("text", "").lstrip().startswith("["))
        if any(v is None for v in ws): print(f"line {i}: realign incomplete, kept original", file=sys.stderr); ws = m["words"]
        y, ws = compress(x, sr, ws, isl, i == 0)
        if TEMPO != 1.0:
            sf.write("_r.wav", y, sr)
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", "_r.wav", "-filter:a", f"atempo={TEMPO:.4f}", "-ar", str(sr), "_t.wav"])
            y, _ = sf.read("_t.wav"); ws = [[w, a / TEMPO, b / TEMPO] for w, a, b in ws]
        sf.write(f"l{i}.wav", y, sr); m["words"] = ws; m["dur"] = len(y) / sr
        print(f"line {i:2d} {len(x) / sr:5.2f}s -> {m['dur']:5.2f}s  islands {len(isl)}")
    json.dump(meta, open("meta.json", "w"), indent=1)
    print("total", round(sum(m["dur"] for m in meta), 2))
