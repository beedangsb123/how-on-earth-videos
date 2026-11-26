"""Words-vs-voice check (PLAYBOOK "FUN FIRST + CLEAN AUDIO"): every caption word must have voice under it.
For each line l{i}.wav + meta.json words: RMS inside each word's [start, end] vs the line's speech level.
Also estimates a per-line timing offset (best shift of the word mask onto the energy envelope).
usage (work dir): python check_words.py   -> prints suspicious words + per-line best offset; exit 1 if any line is off > 0.25 s"""
import json, sys, numpy as np, soundfile as sf
meta = json.load(open("meta.json")); bad = 0
for i, m in enumerate(meta):
    a, sr = sf.read(f"l{i}.wav")
    if a.ndim > 1: a = a.mean(1)
    w = int(0.01 * sr); n = len(a) // w
    r = np.sqrt((a[:n * w].reshape(n, w) ** 2).mean(1)); thr = 0.08 * r.max()
    voiced = (r > thr).astype(float)
    mask = np.zeros(n)
    for _, s, e in m["words"]: mask[int(s * 100):max(int(s * 100) + 1, int(e * 100))] = 1
    best, bo = -1, 0
    for o in range(-80, 81, 2):   # shift words by o*10 ms
        sh = np.roll(mask, o); sh[:max(0, o)] = 0
        if o < 0: sh[o:] = 0
        sc = (sh * voiced).sum() / (sh.sum() + 1e-9)
        if sc > best + 1e-6: best, bo = sc, o
    silent = [wd for wd, s, e in m["words"] if r[int(s * 100):max(int(s * 100) + 1, int(e * 100))].mean() < 0.5 * thr]
    sc0 = (mask * voiced).sum() / (mask.sum() + 1e-9)
    if best - sc0 < 0.05: bo, best = 0, sc0       # a shift must clearly help, else the words already sit on the voice
    flag = abs(bo) > 25 or best < 0.6
    bad += flag
    print(f"line {i:2d} dur {m['dur']:.2f} best-offset {bo * 10:+4d} ms coverage {best:.2f}" + (f" silent: {silent}" if silent else "") + ("  <-- OFF" if flag else ""))
print("RESULT:", "FAIL" if bad else "PASS")
sys.exit(1 if bad else 0)
