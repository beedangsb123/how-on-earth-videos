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

VOICES = {"M": "LERny3t2s1OQcjLCatHn",   # "Bidhan" — Bidhan's own voice (replaced 2026-11-22; looked up by name at run time)
          "F": "cgSgspJ2msm6clMCkdW9"}   # Jessica — Playful, Bright, Warm (female, American)
TAGS = {"urgent": "[excited]", "excited": "[excited]", "surprised": "[surprised]", "curious": "[curious]",
        "awe": "[amazed]", "playful": "[playful]", "serious": "[serious]", "neutral": "",
        # calmer, content-fitting options (Bidhan 2026-11-22: drama must fit what is said)
        "intrigued": "[intrigued]", "matter_of_fact": "[matter-of-fact]", "warm": "[warmly]", "thoughtful": "[thoughtfully]"}
API = "https://api.elevenlabs.io/v1"
LEAD = 0.10   # max silence kept before each line's first word (reactions feel snappier)


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


def tighten(x, sr, max_gap=0.25, tail=0.08, thr=0.006, with_map=False, lead=0.1):
    """shorten silences inside a line to max_gap and the trailing pause to tail (v3 tends to leave long gaps).
    with_map=True also returns (orig_times, new_times) breakpoints so word timestamps can be moved with the audio."""
    win = int(0.02 * sr); n = len(x) // win
    if n < 3: return (x, ([0, len(x) / sr], [0, len(x) / sr])) if with_map else x
    e = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1)); loud = e > thr
    out = []; i = 0; po, pn = [0.0], [0.0]; newlen = 0
    while i < n:
        j = i
        while j < n and loud[j] == loud[i]: j += 1
        chunk = x[i * win:j * win]
        if not loud[i]:
            keep = int((tail if j == n else max_gap) * sr)
            if i == 0: keep = min(keep, int(lead * sr))
            if len(chunk) > keep: chunk = np.concatenate([chunk[:keep // 2], chunk[-(keep - keep // 2):]]) if keep > 0 else chunk[:0]
        out.append(chunk); newlen += len(chunk); po.append(j * win / sr); pn.append(newlen / sr); i = j
    out.append(x[n * win:]); y = np.concatenate(out)
    po.append(len(x) / sr); pn.append(len(y) / sr)
    return (y, (po, pn)) if with_map else y


def words_from_alignment(al):
    """[(word, start, end)] from ElevenLabs character alignment, skipping [audio tags]"""
    ch, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    out, cur, t0, t1, tag = [], "", None, None, False
    for c, a_, b_ in zip(ch, st, en):
        if c == "[": tag = True
        if tag:
            if c == "]": tag = False
            continue
        if c.isspace():
            if cur: out.append((cur, t0, t1)); cur = ""
            continue
        if not cur: t0 = a_
        cur += c; t1 = b_
    if cur: out.append((cur, t0, t1))
    return out


def resolve_bidhan(default):
    """Bidhan may retrain/replace his voice: use the newest personal voice whose name starts with 'Bidhan'.
    Falls back to the stored id, then to Chris (iP95p4xoKVk53GoZ742B) if neither exists."""
    try:
        vs = call("/../v2/voices?voice_type=personal&page_size=50").get("voices", [])
        mine = sorted([v for v in vs if v["name"].lower().startswith("bidhan")], key=lambda v: v.get("created_at_unix") or 0)
        if mine: return mine[-1]["voice_id"]
        return default if any(v["voice_id"] == default for v in vs) else "iP95p4xoKVk53GoZ742B"
    except SystemExit:
        return default


def per_line(S, V, gap=0.22):
    """Added 2026-11-23: eleven_v3 dialogue can drift a voice's accent (British voices came out American-sounding).
    Script option "model": "per_line" renders each line separately with eleven_multilingual_v2 (keeps the voice's own
    accent; audio tags are NOT supported, so emotions become voice settings), then joins them into the same
    dialogue.json structure (audio, voice_segments, alignment) the rest of this script expects."""
    STY = {"excited": 0.65, "surprised": 0.6, "playful": 0.55, "curious": 0.45, "warm": 0.35, "intrigued": 0.4,
           "serious": 0.15, "matter_of_fact": 0.1, "neutral": 0.2, "awe": 0.4, "thoughtful": 0.25}
    parts, segs, chars, st, en = [], [], [], [], []; t0 = 0.0; sr = 44100
    for i, line in enumerate(S["lines"]):
        txt = line[0]; emo = line[3] if len(line) > 3 and isinstance(line[3], str) else "neutral"
        r = call(f"/text-to-speech/{V[line[2]]}/with-timestamps?output_format=mp3_44100_128",
                 {"text": txt, "model_id": S.get("line_model", "eleven_multilingual_v2"),
                  "voice_settings": {"stability": 0.45, "similarity_boost": 0.85, "style": STY.get(emo, 0.3), "use_speaker_boost": True,
                                    "speed": S.get("speed", 1.0)}})   # Bidhan 2026-11-23: news bulletins at ~0.9
        open("_l.mp3", "wb").write(base64.b64decode(r["audio_base64"]))
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", "_l.mp3", "-ac", "1", "-ar", str(sr), "_l.wav"])
        x, _ = sf.read("_l.wav"); dur = len(x) / sr
        al = r["alignment"]
        if i: chars.append(" "); st.append(t0 - gap); en.append(t0 - gap)
        chars += al["characters"]; st += [t0 + v for v in al["character_start_times_seconds"]]; en += [t0 + v for v in al["character_end_times_seconds"]]
        segs.append({"dialogue_input_index": i, "start_time_seconds": t0, "end_time_seconds": t0 + dur})
        parts.append(np.concatenate([x, np.zeros(int(gap * sr))])); t0 += dur + gap
    sf.write("_all.wav", np.concatenate(parts), sr)
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", "_all.wav", "-b:a", "192k", "_all.mp3"])
    return {"audio_base64": base64.b64encode(open("_all.mp3", "rb").read()).decode(), "voice_segments": segs,
            "alignment": {"characters": chars, "character_start_times_seconds": st, "character_end_times_seconds": en}}


def credits_left():
    s = call("/user/subscription"); return s["character_limit"] - s["character_count"]


if __name__ == "__main__":
    S = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "script.json"))
    if "--reuse" not in sys.argv: VOICES["M"] = resolve_bidhan(VOICES["M"]); print("male voice", VOICES["M"])
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
        if S.get("model") == "per_line":
            d = per_line(S, V)   # accent-faithful mode (one eleven_multilingual_v2 call per line, no audio tags)
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
    al = d.get("alignment") or d.get("normalized_alignment")
    WORDS = words_from_alignment(al) if al else []
    meta = []
    for i, line in enumerate(S["lines"]):
        x = a[int(starts[i] * sr):int(ends[i] * sr)]
        x, (po, pn) = tighten(x, sr, with_map=True)
        sf.write(f"l{i}.wav", x, sr)
        ws = [[w, float(np.interp(t0 - starts[i], po, pn)), float(np.interp(t1 - starts[i], po, pn))]
              for w, t0, t1 in WORDS if starts[i] - 0.05 <= t0 < ends[i] - 0.02]
        # 2026-11-22 (video 004): v3 leaves ~0.3 s of breath/silence before every line -> slow turn-taking and +3 s
        # total. Trim the lead to LEAD (line 0: voice at ~0.0 s for the hook) and shift the word times with it.
        if ws:
            cut = max(0.0, ws[0][1] - (0.03 if i == 0 else LEAD))
            x = x[int(cut * sr):]; ws = [[w, max(0.0, a_ - cut), max(0.0, b_ - cut)] for w, a_, b_ in ws]
            fade = int(0.012 * sr); x[:fade] *= np.linspace(0, 1, fade)
            sf.write(f"l{i}.wav", x, sr)
        meta.append({"text": line[0], "cap": line[1], "dur": len(x) / sr, "sr": sr, "speaker": line[2],
                     "emotion": line[3] if len(line) > 3 else "neutral", "speech_end": seg[i][1] - starts[i], "words": ws})
    json.dump(meta, open("meta.json", "w"), indent=1)
    print("total", round(sum(m["dur"] for m in meta), 2), [round(m["dur"], 2) for m in meta])
