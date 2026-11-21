"""Voice generator v2: reads script.json {voice, speed, lines:[[spoken, caption], ...]}.
Two-voice conversational mode (Bidhan 2026-11-21): add "voices": {"M": {"voice": "am_michael", "speed": 1.08},
"F": {"voice": "af_heart", "speed": 1.1}} and give each line a 3rd element "M" or "F" (the speaker); meta.json then
records "speaker" per line so the renderer can colour/position captions per speaker.
Writes l{i}.wav + meta.json with per-line duration and caption text (CAPS words = gold highlight)."""
import json, sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k = Kokoro("/home/claude/models/kokoro.onnx", "/home/claude/models/voices.bin")
S = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "script.json"))
meta = []
V = S.get("voices", {})
for i, line in enumerate(S["lines"]):
    spoken, cap = line[0], line[1]; spk = line[2] if len(line) > 2 else None
    v = V.get(spk, {}) if spk else {}
    a, sr = k.create(spoken, voice=v.get("voice", S.get("voice")), speed=v.get("speed", S.get("speed", 1.0)), lang="en-us")
    # trim leading/trailing silence so the hook starts at 0.0 s
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz): a = a[max(0, nz[0] - 200): nz[-1] + 2000]
    sf.write(f"l{i}.wav", a, sr); meta.append({"text": spoken, "cap": cap, "dur": len(a) / sr, "sr": sr, "speaker": spk})
json.dump(meta, open("meta.json", "w"), indent=1)
print(round(sum(m["dur"] for m in meta), 2), [round(m["dur"], 2) for m in meta])
