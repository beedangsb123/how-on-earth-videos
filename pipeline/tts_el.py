"""Voice generator v4 — ElevenLabs Text-to-Dialogue (eleven_v3), chosen by Bidhan 2026-11-21 (pair A: Chris + Jessica).
Same script format as tts2.py: {"lines": [[spoken, caption, speaker "M"/"F", emotion?], ...]}.
 - emotion presets become v3 audio tags at the start of the line (unless the line already starts with "[").
 - one API call for the whole conversation -> natural turn-taking, real question intonation.
 - /with-timestamps gives each line's start/end, so the audio is cut into l{i}.wav (each segment keeps the
   natural pause that follows it) and meta.json is written exactly like tts2.py -> render with PAD = 0 and run
   audio2.py with pad 0.
API key: env ELEVENLABS_API_KEY or /home/claude/.elevenlabs_key (NEVER commit the key: this repo is public).
Falls back with exit code 2 if the API fails or credits are too low -> then use tts2.py (kokoro).
usage: python tts_el.py script.json [--reuse]   (--reuse re-cuts the saved dialogue.json without spending credits)"""
import json, sys, os, base64, subprocess, numpy as np, soundfile as sf

VOICES = {"M": "iP95p4xoKVk53GoZ742B",   # Chris — Charming, Down-to-Earth (male, American)
          "F": "cgSgspJ2msm6clMCkdW9"}   # Jessica — Playful, Bright, Warm (female, American)
TAGS = {"urgent": "[excited]", "excited": "[excited]", "surprised": "[surprised]", "curious": "[curious]",
        "awe": "[amazed]", "playful": "[playful]", "serious": "[serious]", "neutral": ""}
API = "https://api.elevenlabs.io/v1"


def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k and os.path.exists("/home/claude/.elevenlabs_key"): k = open("/home/claude/.elevenlabs_key").read().strip()
    if not k: sys.exit("no ElevenLabs key")
    return k


def call(path, body=None, out=None):
    cmd = ["curl", "-s", "-m", "300", "-w", "\n%{http_code}", "-H", f"xi-api-key: {key()}"]
    if body is not None: cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(body)]
    r = subprocess.run(cmd + [API + path], capture_output=True)
    data, _, code = r.stdout.rpartition(b"\n")
    if code != b"200": print("ElevenLabs HTTP", code.decode(), data[:300], file=sys.stderr); sys.exit(2)
    return json.loads(data)


def tighten(x, sr, max_gap=0.32, tail=0.22, thr=0.006):
    """shorten silences inside a line to max_gap and the trailing pause to tail (v3 tends to leave long gaps)"""
    win = int(0.02 * sr); n = len(x) // win
    if n < 3: return x
    e = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1)); loud = e > thr
    out = []; i = 0
    while i < n:
        j = i
        while j < n and loud[j] == loud[i]: j += 1
        chunk = x[i * win:j * win]
        if not loud[i]:
            keep = int((tail if j == n else max_gap) * sr)
            if i == 0: keep = min(keep, int(0.05 * sr))
            if len(chunk) > keep: chunk = np.concatenate([chunk[:keep // 2], chunk[-(keep - keep // 2):]]) if keep > 0 else chunk[:0]
        out.append(chunk); i = j
    out.append(x[n * win:]); return np.concatenate(out)


def credits_left():
    s = call("/user/subscription"); return s["character_limit"] - s["character_count"]


if __name__ == "__main__":
    S = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "script.json"))
    V = {**VOICES, **{k: v["el"] for k, v in S.get("voices", {}).items() if isinstance(v, dict) and "el" in v}}
    inputs = []
    for line in S["lines"]:
        spoken, spk = line[0], line[2]; emo = line[3] if len(line) > 3 else "neutral"
        tag = TAGS.get(emo, "") if isinstance(emo, str) else ""
        inputs.append({"text": spoken if spoken.lstrip().startswith("[") or not tag else f"{tag} {spoken}", "voice_id": V[spk]})
    need = sum(len(i["text"]) for i in inputs)
    if "--reuse" not in sys.argv:
        left = credits_left(); print("characters", need, "credits left", left)
        if left < need + 500: print("not enough ElevenLabs credits", file=sys.stderr); sys.exit(2)
    if os.path.exists("dialogue.json") and "--reuse" in sys.argv: d = json.load(open("dialogue.json"))
    else:
        d = call("/text-to-dialogue/with-timestamps?output_format=mp3_44100_128", {"model_id": "eleven_v3", "inputs": inputs})
        json.dump(d, open("dialogue.json", "w"))
    open("dialogue.mp3", "wb").write(base64.b64decode(d["audio_base64"]))
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", "dialogue.mp3", "-ac", "1", "-ar", "44100", "dialogue.wav"])
    a, sr = sf.read("dialogue.wav")
    # line boundaries from voice_segments (dialogue_input_index); merge segments of the same input
    seg = {}
    for s in d.get("voice_segments", []):
        i = s["dialogue_input_index"]; st, en = s["start_time_seconds"], s["end_time_seconds"]
        seg[i] = (min(st, seg.get(i, (st, en))[0]), max(en, seg.get(i, (st, en))[1]))
    n = len(inputs); assert len(seg) == n, f"timestamps for {len(seg)}/{n} lines"
    starts = [0.0] + [seg[i][0] for i in range(1, n)]
    ends = starts[1:] + [min(len(a) / sr, seg[n - 1][1] + 0.25)]
    meta = []
    for i, line in enumerate(S["lines"]):
        x = a[int(starts[i] * sr):int(ends[i] * sr)]
        x = tighten(x, sr)
        sf.write(f"l{i}.wav", x, sr)
        meta.append({"text": line[0], "cap": line[1], "dur": len(x) / sr, "sr": sr, "speaker": line[2],
                     "emotion": line[3] if len(line) > 3 else "neutral", "speech_end": seg[i][1] - starts[i]})
    json.dump(meta, open("meta.json", "w"), indent=1)
    print("total", round(sum(m["dur"] for m in meta), 2), [round(m["dur"], 2) for m in meta])
