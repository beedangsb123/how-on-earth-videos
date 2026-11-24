# How On Earth — Channel Playbook

Faceless short-video channel: **natural wonders and mega-builds, and how they came to be.**
Owner: Bidhan. Goal: **US$500/month combined** across TikTok, Instagram, Facebook, YouTube.

## AUTOPILOT MODE — Bidhan 2026-11-23, valid until 2027 (READ FIRST; overrides older rules where they clash)
Bidhan will not review or add anything until 2027: no drafts, no approval, the channel runs itself. ElevenLabs credits
(Starter, 40,000 chars/month, resets ~21st) are reserved for the videos — keep each script ≤ ~1,200 characters incl.
tags; never generate samples or extra tests. Only push-notify him when something is broken or needs his account.
Theme stays: natural wonders and man-made wonders — the HOW.
**Note for the daily task:** Bidhan edited its opening line on 2026-11-23 to "follow PLAYBOOK AUTOPILOT MODE: no
files, notify only on problems". So where the task's later steps still say "10:00 am" (step 7) or "send Bidhan the
finished video with SendUserFile" (step 9), use the country-based posting time in rule 7 below (10:00 am stays the
default for US and small-population topics) and do NOT send the file; just end with the short summary message.

1. **Funny + relatable is now part of every video** ("everyone would love a good smile or a laugh"). At least two
   genuine laughs or relatable comparisons per video (dry understatement, absurd-but-true framing, everyday
   comparisons), always built on a REAL, sourced fact. Family-friendly; joke about the place/structure/physics, never
   about people, cultures, religions or accents; no stereotypes; no real public figures.
2. **Research the day first** (every run, before picking the topic): what is trending yesterday/today (news, Google
   Trends-style searches, YouTube/TikTok trending in the niche), and which occasions/festivals are coming in the next
   1-10 days. Tie the topic to them when it fits naturally, e.g. Christmas → Christmas Island's red crab migration /
   Rockefeller tree; New Year → Sydney Harbour Bridge fireworks engineering; Thanksgiving → Plymouth Rock?; Diwali →
   Golden Temple/Jaipur; Chinese New Year (6 Feb 2027) → Great Wall; Australia Day / India Republic Day (26 Jan);
   Ramadan/Eid → Sheikh Zayed Mosque/Petra; Valentine's → Taj Mahal; Holi; Easter → Easter Island. Avoid tragedies
   and political news even if trending. Note in LOG.md which trend/occasion (if any) the topic used.
2a. **TREND RADAR — be proactive (Bidhan 2026-11-24: "No GTA reference videos yet???? be more proactive with finding out
   what's trendy")**. EVERY run, before anything else, scan pop culture, not just news/holidays: big game launches
   (GTA 6 launched 19 Nov 2026 with a record $3.79B day one), movies/trailers, streaming shows, sports finals, viral
   searches, space launches, and what Shorts/TikTok creators in the niche are posting this week (search e.g. "trending
   this week", "biggest launch this week", "<month> releases"). Ask: is there a REAL wonder/structure/place behind it?
   (game/movie locations -> the real place; e.g. GTA 6 Leonida = Florida: Bahia Honda/Seven Mile Bridge, Everglades,
   Miami's man-made islands, Florida Keys reef.) **48-hour rule:** when a big trend fits, make it NOW: it bumps the
   planned topic (even an already-scheduled post; move that one to the next free day and log it). Never use game/movie
   footage, logos, fonts, characters or look-alike art; only real imagery of the real place + our own graphics; the
   title may name the game/show (nominative, e.g. "the real bridge from GTA 6"). Keep the video about the HOW. Note the
   trend in LOG.md and how the post did in LEARNINGS.md so we learn whether trend videos beat evergreen ones.
3. **Watch what works on big channels**: once a week skim what popular Shorts channels in the niche post (format,
   hook, length, humour, posting cadence) and what stalls; write 3 bullets in LEARNINGS.md. Research 2026-11-23
   (vidIQ, Metricool 2026 study of 799,718 videos): the Shorts feed gives >61% of views; the "viewed vs swiped away"
   ratio on the seed audience decides promotion; average Shorts view duration fell to ~16 s, so the payoff must be
   promised in frame 1 (3-7 word on-screen hook + 5-10 word spoken hook, one promise); 13 s and ~60 s Shorts
   performed best; curiosity / "did you know" / comparison / revelation hooks; 1-5 relevant hashtags.
4. **Formats rotate (see "No formula scripts")**, plus two WEEKLY shows:
   - **Fridays: "How On Earth News"** — deadpan British newsreader (ElevenLabs Daniel onwK4e9ZLuTAKqWW03F9) + British
     field reporter (Alice Xb7hH8MSUJpSbSDYk0k2, or George / Lily), slightly QUIRKIER and SLOWER: tts_el.py
     "model": "per_line" (keeps the accent) + "speed": 0.9. News ident at start and end (audio2 events news_open /
     news_close, voice_offset 1.4 s), music_style "news", broadcast graphics (bug, LIVE, fact ticker with sources,
     BREAKING lower thirds, name straps), sign-off "This is <reporter>, for How On Earth News, <place>". Reference:
     pipeline/sample_newsdesk_v3.py (Bidhan approved this sample). Our own invented brand — no BBC name/logo/look.
   - **Tuesdays: "How On Earth Weather"** — American weather presenter (e.g. Eric / Roger / Brian) giving an absurd-but-
     true "forecast" for a wonder (e.g. "Antarctica: 100% chance of ice, for the next 30 million years").
   - Other days: the rotating structures, voices per the daily rotation.
4a. **Creative freedom (Bidhan 2026-11-23: "countless opportunities and room for creativity… you're the manager
   now")**: keep inventing formats and test them against the analytics. Ideas in the pool: **stand-up comedy set**
   (a comedian character on a small stage with a mic and spotlight, doing a tight bit about a wonder — real facts as
   the punchlines, light "audience" reactions synthesised in audio2, no canned laugh-track recordings), nature-doc
   parody narrator, tour guide who keeps getting the scale wrong, "the wonder reviews itself" (first person), game
   show / quiz, courtroom ("the case of the shrinking glacier"), cooking-show recipe for a canyon, sports commentary of
   a slow geological race. Also **"Press the button"** (from a reference video Bidhan liked, 2026-11-23): a big red button
   "Press to run the world without <the Panama Canal / the Suez Canal / Hoover Dam / bees / the Gulf Stream>" and a
   quick-fire chain of real consequences, shown with real footage + our graphics (never realistic AI people). Same rules apply: real sourced facts, brand-safe, jokes about places and physics only, and
   log the format in LOG.md so its numbers can be compared.
4b. **Avatars (Bidhan 2026-11-23: "keep the avatars if they are free … you're the manager now")**: our own cartoon
   hosts from pipeline/avatar.py are free and may be used whenever they help — the manager (each run) decides. Never
   paid or realistic AI avatars. Give them a setting that fits the format: a news desk for the News anchor, a
   reporter with a microphone on location, a weather map for the Weather presenter, hard hats on a construction site
   for mega-builds, field gear at a natural wonder. Keep them small (corner or lower third) so the real footage stays
   the star; vary their look and the cast every video (new CAST entries are fine), matching the day's voices.
5. **Accent follows the country of the topic** (real native-accent voices, never a put-on accent): Australia/NZ →
   Australian (premade Charlie IKne3meq5aSn9XLyUdCD; shared library e.g. Emma 56bWURjYFHyYyVf490Dp / Arabella
   aEO01A4wXwd1O8GPgGlF), India → Indian (shared e.g. Ruhaan siw1N9V8LmYeEWKyWBxv, Monika Sogam 2zRM7PkgwBPiau2jvVXc,
   Ranbir 2iAXJEMO2o0PqUHzvZwQ), UK → British (Daniel, George, Alice, Lily), USA → American. Shared voices must be
   added first (POST /v1/voices/add/{public_owner_id}/{voice_id}, free; 10 slots, 1 used on 2026-11-23); find them
   with GET /v1/shared-voices?accent=<x>&language=en. Use "model": "per_line" for accented voices.
6. **Music follows the place** (audio2.py events.json "music_style", all original synthesis): India / Taj Mahal /
   Central Asia → "sufi" (drone + raga-style phrases + tabla-like drums); Egypt / Middle East / North Africa →
   "arabic" (maqam Hijaz phrases + darbuka); news → "news"; Christmas/holidays → "festive"; Latin America → "latin";
   China/Japan/Korea → "eastasia"; otherwise "default" with a new key/tempo.
7. **Posting time follows the country's evening** (main post; Stories 1-2 min later; still ONE main post per day,
   never in the past, never two in the same day — check getScheduledPosts):
   USA/Canada, and any place with a small population or no big home audience → 10:00 Sydney (6 pm ET / 3 pm PT);
   Australia/NZ → 19:00 Sydney; India/South Asia → 00:30 Sydney (7 pm IST); UK/Europe → 06:00 Sydney (7 pm GMT);
   Middle East/Egypt → 04:00 Sydney (7 pm Cairo); East Asia → 21:00 Sydney (7 pm Tokyo); Latin America → 09:00 Sydney.
   (Summer-time shifts: re-check offsets in March/April and October.)

## Standing rules from Bidhan, 2026-11-24 (live)
- **Never wait for Bidhan's go-ahead** on any video: make it, schedule it, log it. **Never send him the video or a draft
  in the chat** (the GTA 6 draft was a one-off because the topic was new). Notify only on problems.
- **Hashtags per platform** (whatever works on each, but never unrelated to the video). So the 10:00 "main post" is now
  FOUR single-network posts at the same time (Metricool has one shared text per post), each with its own caption and tags:
  - TikTok: short punchy caption + 5–6 tags: 3–4 topic tags + #fyp + #howonearth (add a trend tag like #gta6 when relevant).
  - Instagram: full caption + credits + 5–6 tags: topic tags + #reels + #howonearth; first comment = engagement question.
  - Facebook: full caption + credits + 5–6 tags: topic tags + #facebookreels + #howonearth; first comment as IG.
  - YouTube: #shorts first + 3–4 topic tags + #howonearth in the text; "#shorts" in the title; searchable tags list.
  The "is a main post already scheduled at 10:00?" check now means: any non-draft Reel/short/TikTok post at that time.
  Log all four post ids in LOG.md. Stories (IG+FB) stay one post each at 10:01/10:02.

## Channel mission (Bidhan's own words, 2026-11-20)
Bidhan is a civil engineer who has always been fascinated by how things work — big designs, big buildings — and equally by geography and geology: how natural landscapes came about. He believes people are more interested in the **HOW** than the what/why. The channel should become a platform for like-minded, curious people. "Nothing fancy" — daily, educational, accurate. Every video must answer a clear "how did this come about / how does this work" question, about either a natural landscape or a great human-made structure. Entertainment hooks serve the education, never replace it.
**Topic filter (Bidhan, 2026-11-20): a topic is used ONLY if it passes all three:**
1. **Viral-friendly** — a famous or visually stunning subject most people recognise, with a surprising "wait, what?" fact that works as a 1.5 s hook and makes people share or comment.
2. **Good for monetisation** — appeals to high-value audiences (US/UK/AU/CA adults), fits the 61–75 s format, and links naturally to sponsors/affiliates (travel and tours, learning apps, STEM kits, tools, documentaries).
3. **Ad-friendly** — brand-safe: no disasters with deaths as the focus, no war, politics, religion disputes, tragedy, gore or controversy; family-friendly wording.
If a topic fails any one of these, pick another. Note in LOG.md for each video one line on why it passed.

## Accounts
- Metricool brand: blogId `8221611`, timezone Australia/Sydney. Connected: facebook (How On Earth Page), instagram (@thehowonearth), tiktok (@the.how.on.earth — handle changed from @how.on.earth7, confirmed by Bidhan's screenshot 2026-11-23; display name How On Earth 🌍, personal account — keep personal for Creator Rewards), youtube.
- Public profile links: TikTok https://www.tiktok.com/@the.how.on.earth · Instagram https://www.instagram.com/thehowonearth/ · Facebook https://www.facebook.com/1474038465792135 · YouTube https://www.youtube.com/@thehowonearth (handle @thehowonearth)
- Video hosting: this repo. Public raw URL pattern:
  `https://raw.githubusercontent.com/beedangsb123/how-on-earth-videos/main/videos/<file>.mp4`
- Log of every video: `LOG.md`. Lessons from analytics: `LEARNINGS.md`.

## Video spec
- 1080×1920, 30 fps, H.264 CRF 18, AAC. **61–75 s** (must exceed 60 s for TikTok Creator Rewards / Facebook).
- Voiceover: kokoro-onnx (models from github.com/thewh1teagle/kokoro-onnx releases `model-files-v1.0`), voice `am_michael`. Spell tricky names phonetically for TTS, correct spelling in captions.
- Background music: original synth (pipeline/music.py), ducked under voice. Never use copyrighted music.
- Burnt-in captions in the safe zone: y≈1300–1500, max width 860 px. Keep anything important out of: top 180 px, bottom 400 px, right 160 px (platform UI).
- Brand: night-to-dawn palette — navy #0B1026, #1B2B5C, blue #3E5C9A, orange #F28C38, gold #FFC857. Poppins Bold (Montserrat for ṉ ṟ ṯ). Small "HOW ON EARTH?" badge top. End card with logo + "FOLLOW".

## Bidhan's feedback on video 002 (2026-11-20, clarified the same day)
Video 002 (pure animation) "doesn't sound interesting and doesn't have any stock images or real-world videos". Do better.
1. **Real photos/footage are the PREFERENCE (not mandatory).** Where good free-licence material exists, make it the main visual (Ken Burns motion) with our animated labels, arrows, counters, cross-sections and x-rays on top; use animation for what no photo can show (inside a structure, deep time, processes). Find media with `pipeline/fetch_media.py` (Wikimedia Commons PD/CC0/CC BY/CC BY-SA + NASA). US-government archives (NARA, USBR, NPS, NASA) are public domain and full of construction photos. Avoid close-up faces, logos and Indigenous sacred-site close-ups. Credit CC BY/BY-SA authors in the caption.
2. **Globe zoom = a suggestion, not a rule.** Use `pipeline/globe.py` (spin + zoom from space, `handoff()` iris into a real aerial photo, `project()`-style lat/lon overlays for routes/comparisons) when it looks cool and helps show WHERE or HOW BIG — skip it when it doesn't.
3. **Voices: a MAN and a WOMAN in every video, as a conversation** (Bidhan 2026-11-21; replaces "one voice, alternating"). Two hosts trading lines: one asks/reacts ("Wait — a hundred and twenty-five years?"), the other explains; quick back-and-forth in the hook and at the reveals, longer explaining lines in between. Natural, lively, friendly — like two curious friends, not a lecture. Alternate who opens the video each day. Use `tts2.py` two-voice mode ("voices": {"M": …, "F": …} + speaker per line + an emotion preset per line). Defaults: man am_michael (or am_fenrir/am_puck if livelier), woman af_heart (or af_bella). Captions: tint or tag per speaker (e.g. woman's lines with a small gold dot, man's with a blue dot) so viewers can follow. Keep gaps between speakers short (0.1–0.2 s) so it feels like a real conversation.
4. **Sound interesting**: script as a story — shock-number hook → the PROBLEM (stakes) → why it seemed impossible → the clever HOW → payoff twist → loop line. Short punchy sentences, "you" framing, vivid comparisons, a "wait, what?" every ~15 s. Cut flat linking lines.
5. Hook shot = the most striking image of the subject (real photo if available) + ≤6-word claim.
6. ~~Send Bidhan the finished video file every run~~ — SUPERSEDED 2026-11-23 by AUTOPILOT MODE: no drafts or files needed until 2027; notify only on problems.
7. **Channel badge v2** (Bidhan: "make the How On Earth icon more attractive"): use `badge(c, t)` from engine.py (glossy navy pill, gold rim, spinning mini-globe with orbit, HOW ON white + EARTH? gold, light sweep every 4 s; pass the global time so it animates) and `end_card_logo()` for the end card (pulsing halo + rotating gold arcs). Keep improving it if it still looks plain.
Reference builds: `pipeline/render_003.py` (Old Faithful: real footage via `clips.py`, photos via `photo.py`, animated cross-section, two-host speaker captions, `source_tag`, audio2 args `pad transpose bpm`); `pipeline/render_002b.py` (Hoover Dam remake: real aerials + NARA/USBR archival photos with sepia/grain, globe zoom, thermal-camera tint on photos, globe route SF→NY).

## Bidhan's feedback on video 003 (2026-11-21) — EMOTION + a stronger HOOK (mandatory from video 004)
Video 003 (Old Faithful) was "fine", but the voices sounded neutral and the hook didn't land.
1. **Voices must show emotion — never a flat read.** Give EVERY script line an emotion preset as its 4th element in
   script_NNN.json (tts2.py v3): `urgent` (the hook), `surprised` ("Wait — WHAT?!"), `excited`, `curious` (questions),
   `awe` (slow, low: the big reveal), `playful`, `serious`; or a dict {"speed", "pitch", "gain"}. Never more than 2
   `neutral` lines in a row. Write for emotion too: real reactions and interjections ("No way.", "Hold on —",
   "That's insane!", "Okay, that's actually terrifying"), exclamation marks, a laugh-line or banter once per video, the
   asker genuinely stunned at each reveal, the explainer clearly loving the topic. Try livelier voices (am_puck,
   am_fenrir, af_bella, af_nicole) and pick by listening-proxy: the one whose test lines differ most in pace and pitch.
2. **Hook = the most shocking concrete thing, instantly visual, no context needed.** A myth/negation ("X has never
   done Y") needs the viewer to already care, so it is weak. Instead lead with a surprising physical fact, number or
   danger the first frame can SHOW, with stakes or a "you" angle, e.g. "There's a car-sized cave under this geyser."
   / "This bridge grows 18 cm every summer." / "You could stand inside this pipe — it carries a whole river."
   Process every run: write 5 candidate hooks, score each 1–5 on (surprise, visual on frame 1, curiosity gap, ≤9
   words), use the best, and note the runner-up in LOG.md. Line 2 = the other host's emotional reaction
   ("Wait — a CAVE?!"), line 3 opens the loop. The hook frame shows the shocking thing itself (photo + drawn overlay,
   e.g. an x-ray cut-away revealing the cave), with ≤6 words of on-screen text.

## VOICES = ElevenLabs (Bidhan 2026-11-21, Starter plan, 40,000 characters/month ≈ 1 video/day)
- Default engine: `pipeline/tts_el.py` (ElevenLabs Text-to-Dialogue, model eleven_v3) — the whole conversation in ONE call,
  so turn-taking and question intonation sound natural. **M = Bidhan's own voice "Bidhan"** (LERny3t2s1OQcjLCatHn since 2026-11-22; tts_el.py picks the newest
  personal voice named "Bidhan…" automatically, so retrained versions are used without code changes; Chris
  iP95p4xoKVk53GoZ742B is the backup) and **F = Jessica** (cgSgspJ2msm6clMCkdW9, playful, bright, warm). Same script JSON as tts2;
  the emotion preset becomes a v3 audio tag ([excited], [curious], [surprised], [amazed], [playful]); you may also
  put tags inside the text ("[laughs]", "[whispers]") — sparingly, max ~4 per video.
- tts_el.py cuts the dialogue into l{i}.wav WITH a short natural pause after each line (long v3 pauses are tightened),
  so render with PAD = 0 and run `audio2.py 0 <transpose> <bpm>`. It also saves dialogue.json (re-cut free with --reuse)
  and per-word timestamps in meta.json → ALWAYS pass `words=meta[i]["words"]` to captions() so subtitles appear exactly
  when each word is spoken (Bidhan 2026-11-21: delayed subtitles look unprofessional). Write captions with the same
  number of words as the spoken line ("fifteen-storey" ↔ "15-STOREY").
- Bidhan's clone speaks a bit slower: aim for ≤ ~1,000 characters of script so the video stays ≤ 75 s without
  speeding up the audio.
- Keep each script ≤ ~1,100 characters (credits). tts_el.py checks credits first; if the API fails or credits are
  low (exit code 2), fall back to tts2.py (kokoro) and tell Bidhan.
- The API key is in the daily task's private instructions → write it to /home/claude/.elevenlabs_key (chmod 600).
  NEVER commit it, print it, or put it in any file in this repo (the repo is public).
- api.elevenlabs.io is on the network allowlist (added by Bidhan 2026-11-21).

## NEW VOICES EVERY DAY + a fresh look (Bidhan 2026-11-23 — overrides "M = Bidhan's own voice" above)
Bidhan reviewed 005 v1: "the animations don't look great and look the same as the last one", and asked for different
ElevenLabs characters — the FEMALE is excited and curious (she asks), the MALE answers the questions — and
"different characters every day".
- Voices: use a DIFFERENT male + female pair every video (set "voices": {"M": {"el": id}, "F": {"el": id}} in
  script_NNN.json — tts_el.py uses them). Never repeat the previous video's pair. Rotation (premade, American unless
  noted), go down the list and log the pair in LOG.md:
  005 Brian nPczCjzI2devNBz1zQrb + Laura FGY2WhTYpPnrIDTdsKH5 · 006 Eric cjVigY5qzO86Huf0OWal + Jessica cgSgspJ2msm6clMCkdW9 ·
  007 Liam TX3LPaxmHKxFdv7VOQHJ + Sarah EXAVITQu4vr4xnSDxMaL · 008 Roger CwhRBWXzGAHq8TQ4Fs17 + Matilda XrExE9yKIg1WjnnlVkGX ·
  009 Will bIHbv24MWmeRgasZH58o + Bella hpp4J3VqNfWAUOO0d1Us · 010 Chris iP95p4xoKVk53GoZ742B + Laura · 011 Bill
  pqHfZKP75CvOlQylNhV4 + Jessica · 012 Charlie (Australian) IKne3meq5aSn9XLyUdCD + Sarah — then start again. (Bidhan's own
  cloned voice is no longer the default; use it only if he asks.)
- Emotion: female lines mostly `excited` / `curious` (genuine, not shouty); male lines `warm`, `matter_of_fact`,
  `intrigued`, one `playful`. The man usually delivers the hook; she reacts.
- Look: never reuse the previous video's visual language. Rotate per video: headline style (engine.ribbon vs pop_text
  vs others), accent colour (engine.CAP_ACCENT), transition (engine.whip vs wipe vs others), and the explainer style.
  Prefer REAL imagery with annotations on top (satellite/astronaut photos via a Sat-style view + neon_path,
  ring_marker, leader-line tags) and photo-textured 3-D block diagrams over flat cartoon fills. Reference:
  pipeline/render_005.py (look v3: NASA globe -> ASTER -> ISS continuous zoom, cyan ribbons, whip-pans).

## No formula scripts (Bidhan 2026-11-23: "why does she have to say wait every time", "same script in every file")
- BANNED as a reaction opener: "Wait", "Hang on", "Hold on", "No way", "Okay, tell me", "Wait, what?". Never reuse a
  reaction phrase used in the last 3 videos (check script_NNN.json files before writing).
- Change the STRUCTURE every video, not just the topic. Rotate: two-host Q&A · one narrator + one interrupting
  sceptic · news-desk parody (British anchor + field reporter) · "walk-through" told as a tour on location ·
  countdown/list · myth-vs-fact quiz where the viewer guesses · first-person story of the place/structure. Never two
  videos in a row with the same structure, the same hook pattern, or the woman always asking / man always answering.
- Try a different option every video (voices, structure, look, music) and log which one was used in LOG.md so the
  analytics can compare them.

## Emotion must FIT the line (Bidhan 2026-11-22)
Bidhan likes the dramatic ElevenLabs v3 tone (his reference: the "new Bidhan voice test" clip) but NOT drama
pasted onto ordinary facts — e.g. "a cave the size of a car" was delivered like a shocking/trolling reveal, which it
isn't. Rules:
- Choose each line's emotion from what it actually says. Plain information → `neutral`, `matter_of_fact`, `warm` or
  `intrigued` (a hint of wonder). Questions → `curious`. Save `excited` / `surprised` / `awe` for 2–3 genuinely
  surprising beats per video (the biggest reveal, the twist, the payoff) — never on every line, never on the hook by
  default.
- The hook should sound intriguing and confident ("here's something you didn't know"), not shouted.
- Reactions from the other host carry most of the surprise; the explainer stays relaxed and sure of himself.
- Avoid exclamation marks on lines that aren't truly exciting (v3 exaggerates them).
- Keep the v3 conversation mode and default settings (Bidhan liked them); no speed-up of his voice.

## Bidhan's review of the 003 remake (2026-11-21) — mandatory
1. **Questions must SOUND like questions.** kokoro reads "A cave?" flat, like a statement. Until a better voice engine
   is in place: keep questions very short, start them with a question word or "wait/so/really", and in tts2.py raise
   the pitch over the last ~0.4 s of every line ending in "?" (+2 to +3 semitones, smooth ramp). Check by ear-proxy:
   compare pitch of the last 0.4 s vs the rest (should be clearly higher).
2. **No speaker dots in captions** (they looked like bullet points mid-sentence). captions() now defaults to no dot;
   speaker is shown only by a subtle text tint.
3. **No meta lines that echo our jargon** ("I'm hooked", "the hook", "stick with me, the trick is genius").
   Hosts talk about the subject, not about the video.
4. **Smoother map zoom:** no iris/ring handoff. One continuous camera move: globe → regional satellite view →
   the real aerial photo, crossfading at matched centre and scale with slight motion blur, constant zoom speed.
5. **For non-science people (clarified by Bidhan 2026-11-21):** real terms like "magma", "pressure" and some
   numbers with units (feet, minutes) are FINE. What to avoid is an outburst of numbers and fast, science-y delivery.
   - Never more than one number per sentence, and never two number-lines back to back; give each number a beat to land
     (a short pause, a reaction, or an everyday comparison: the car-sized cave worked, Bidhan loved it).
   - Briefly explain a term the first time in plain words ("magma, melted rock").
   - Slower, relaxed pace for explaining lines (voice speed ~1.0, not 1.1+); quick pace only for reactions.
   - Every fact must connect to the story (why it matters), not be listed.

## Make it sound NATURAL (Bidhan 2026-11-21, applies from video 004)
Script like two friends talking, not presenters reading:
- Contractions and everyday words ("it's", "gonna", "basically"); short uneven turns (2–12 words for reactions);
  small fillers sparingly ("okay so", "hang on", "right?", "huh"); the asker sometimes guesses wrong and is corrected;
  one light joke or tease per video; the explainer says "I know, right?" when the other is amazed.
- Interruptions: a reaction may start ~0.15 s before the previous line ends (overlap), e.g. "— wait, a CAVE?".
- Avoid list-like sentences and written-style clauses ("which", "however", "in addition").
Mix like one room: varied gaps between turns (0.05–0.45 s, shorter for reactions, longer before a reveal), a soft
breath before longer lines, light shared room reverb + low room tone under both voices, voices panned very slightly
apart (M −8 %, F +8 %). Read the whole script aloud in your head as a conversation before generating.
Voice engine: kokoro stays the default (free, fast). If a more natural open model (e.g. Chatterbox / Dia /
Orpheus — no paid services) can be installed and renders the full script on CPU in under ~10 min, test it on 2
lines first and use it only if clearly more natural; otherwise fall back to kokoro. Bidhan's own recorded voice
always wins if he provides it.

## Making it NOT boring (quality bar — every video must beat the last)
1. **Hook in the first 1.5 s**: a bold on-screen claim + matching first spoken line (e.g. "This bridge grows 18 cm every summer"). First frame must already show the subject and hook text (it is the thumbnail).
2. **Visual change every 2–3 s**: cuts, camera push-ins/pans (animate scale/translate), reveals, x-ray cross-sections, before/after splits, counters ticking up, map zooms.
3. **Rich colour and depth**: gradients, glow, parallax layers (foreground/mid/background moving at different speeds), particles (dust, rain, sparks, water), soft shadows. Avoid flat empty frames.
4. **Kinetic captions**: 1–3 words at a time, pop-in scale, key word highlighted gold.
5. **Sound design**: low boom on big reveals, subtle ticks on counters, soft pops (synthesise with numpy — no copyrighted SFX). **No harsh noise (Bidhan 2026-11-21: the "cshhhh cshhhh" was irritating):** noise-based SFX (whoosh, hiss, splash, crack) are rare, quiet and low-passed — audio2.py enforces max one whoosh per 2.5 s and one hiss per 8 s; never put a whoosh on every cut. After mixing, check the >4 kHz energy share of mix.wav stays under ~0.03 (video 003 was 0.07).
6. **Open loops**: tease the payoff early ("…and the last part is the craziest"), deliver it near the end.
7. **Numbers people repeat**: heights, ages, weights, comparisons to familiar things ("taller than 3 Harbour Bridges stacked").
8. **Loop-friendly ending**: final line connects back to the hook so replays feel seamless; then a 2–3 s end card.
9. Draw test stills at the busiest moments and LOOK at them before the full render. Check every glyph renders (no tofu boxes).

## Topic strategy
- Alternate natural wonders and mega-builds. Favour things people have heard of but can't explain.
- Mix: ~30% Australia/NZ (home audience), ~70% global icons — US icons first (US audience pays most). (Revised 2026-11-20 strategy review; was 40/60.)
- Series hooks that build bingeing: "Australia's wonders", "Impossible builds", "Earth's weirdest places".
- Before choosing, check `LOG.md` — never repeat a topic. Check `LEARNINGS.md` and lean into what performed best.
- Facts: verify each claim with at least one reputable source (government, university, encyclopaedia, major museum). Note sources in LOG.md.

## Respect & policy
- Indigenous sacred sites (e.g. Uluṟu, Kata Tjuṯa): distant silhouettes only, no close-up rock features of sensitive sites, acknowledge Traditional Owners.
- No copyrighted footage, characters, logos, music. No real people's likeness. No photos of public figures.
- AI-content labels OFF (Bidhan's decision 2026-11-20: educational videos, no one impersonated): tiktok isAigc=false, instagram isAiGenerated=false, youtube isAiGeneratedContent=false. YouTube madeForKids = false. Never depict real people or make realistic fake events/footage; if a video ever does, ask Bidhan before posting.
- Family-friendly, no gore, no disaster-exploitation.

## Posting
- Schedule through Metricool `createScheduledPost` with all four providers in one post: facebook type REEL (+ title), instagram type REEL, tiktok (title, PUBLIC_TO_EVERYONE), youtube type short (title with #shorts, category EDUCATION or SCIENCE_TECHNOLOGY, tags).
- **Post time: 10:00 am Australia/Sydney, every day (Bidhan's choice 2026-11-20).** = 6 pm US Eastern / 3 pm US Pacific (prime time in the highest-paying market) and the top hour for TikTok, Instagram and Facebook in Metricool's best-time data; UK/Europe catch it next morning; India (low pay per view) is asleep — accepted trade-off. Re-check weekly with `getBestTimeToPostByNetwork` and the account's own analytics; if the data clearly favours another slot, propose the change to Bidhan in the run message rather than switching silently.
- Caption: open with a QUESTION or 'guess' line (Instagram comments were the best signal on video 001) + 1 emoji + the key number + 5–6 hashtags (2 broad, 3 specific, always #howonearth). Titles use the searchable phrase people type ("How was Hoover Dam built"), not just a teaser.
- firstCommentText (Instagram/Facebook): one engagement question, e.g. "Which mega-build should we explain next? 👇" — comment topics feed LOG/topic ideas.
- **Stories every video (Bidhan 2026-11-22, standing rule):** after scheduling the main post, also schedule the same video to **Instagram + Facebook Stories** (one Metricool post, providers instagram + facebook, instagramData.type STORY, facebookData.type STORY, no text, isAiGenerated false). Stories are capped at 60 s, so split the video at a line boundary near the middle — ideally right after a question/cliffhanger line — into `videos/NNN-story-part1.mp4` and `videos/NNN-story-part2.mp4` (ffmpeg re-encode, -b:v 5200k, 60 ms audio fade at the cut; each part ≤ 59 s). Schedule part 1 at 10:01 and part 2 at 10:02 (Sydney), right after the 10:00 reel. Check both raw URLs return 200 first. Metricool has no TikTok/YouTube story option — skip those. Log both story post ids in LOG.md.

## Money plan (US$500/month target)
1. **Facebook Content Monetization** (Australia eligible, invite-only) — usually the first real payout for this niche.
2. **YouTube Partner Program** — Shorts views + weekly **long-form compilations** (combine 8–10 shorts into a 10+ min video) to earn watch hours. Note thresholds rise for new applicants from 1 Feb 2027.
3. **Affiliate**: travel/tour links (Bidhan must sign up himself; add link-in-bio once approved).
4. **Sponsors** from ~5–10k followers: learning apps, STEM kits, travel, tools. Max 1 sponsored per 4 videos, always labelled as paid partnership.
5. TikTok Creator Rewards availability in Australia is uncertain — check TikTok Studio once at 10k followers.

## Comment replies (Windsor.ai)
- Instagram: Windsor connector `instagram`, account `17841461164290075`. Read comments with get_data fields comment_id, comment_text, comment_username, comment_timestamp, comment_parent_id, media_permalink (date_preset last_7dT). Reply with execute_action `reply_to_comment` {comment_id, message}.
- YouTube: Windsor connector `youtube`, account `105358`. Comment fields: comment_id, comment_text, comment_author, comment_published_at, comment_video_id, comment_reply_count. Reply with `reply_to_comment`. (Needs the optional Windsor reconnect at https://onboard.windsor.ai/app/youtube_review — if comment fields fail, tell Bidhan.)
- Facebook and TikTok: no reply tool — Bidhan replies in the apps. TikTok: Bidhan connected Windsor `tiktok_organic` on 2026-11-25 (account `_000bmaF4kFO9TXFbS0fhyta4iqYt6C9kDzb`, personal, not Business). Account fields (followers, username) work, but video and comment fields fail with TikTok error 40002, most likely because the account is personal. Try the comment fields once per run; if they still fail, skip TikTok comments (Bidhan keeps it personal for Creator Rewards).
- **ONE REPLY PER COMMENT — never more (Bidhan's rule).** Before replying to a comment, skip it if ANY of these is true: its comment_id is already in REPLIED.md; its comment_reply_count (Instagram) / comment_reply_count (YouTube) is greater than 0; it was written by the channel itself (comment_username thehowonearth / the channel's own name); it is itself a reply. Windsor's comment list can be cached and does NOT reliably show the channel's own replies, so REPLIED.md and comment_reply_count are the source of truth. After each successful reply, add a line to REPLIED.md straight away, and commit + push it at the end of the run.
- **24-HOUR RULE (Bidhan's rule, 2026-11-20):** never reply to a comment more than 24 hours old (comment_timestamp / comment_published_at vs now, UTC). Older unanswered comments are skipped, not replied to; still flag business enquiries or fact corrections to Bidhan, and hiding spam is still allowed.
- Rules: reply only to top-level comments from other people. Friendly, short (1–2 sentences), add a real fact or answer, often end with a question to keep the conversation going. Vary wording — never copy-paste the same reply. Never argue, never promise anything, never share personal info about Bidhan. Ignore spam; hide (do not delete) abusive or spam comments. Max ~30 replies per run.
- Log replies count in LEARNINGS.md weekly; note which questions people ask (they are topic ideas).
- **TOPIC REQUESTS (Bidhan 2026-11-24):** every comment run, read ALL comments in the last 7 days (Instagram AND Facebook — Windsor `facebook_organic`, account `1474038465792135`, fields comment_id, comment_text, comment_timestamp, comment_parent_id, comment_reply_count, permalink_url; read-only, no reply tool — including replies to our own pinned questions, which both show via comment_parent_id; the 24-hour rule applies only to replying, not to reading) and add any topic suggestion to TOPIC_REQUESTS.md (skip ones already listed). YouTube reply text is not available in Windsor: if one of our YouTube pinned questions has comment_reply_count > 0 that is not yet logged, add it under "Unread YouTube replies" and mention it in the run summary so Bidhan can tell us what it says. Video runs: when choosing a topic, prefer a viewer request that passes the topic filter, and say in the caption that a viewer asked for it.

## Platform flags to avoid (learned 2026-11-20)
- **Facebook flagged video 001: "Your video has a border — can look like repurposed content, may limit distribution."** Cause: large flat, near-black bands at the top (dark navy sky) and bottom (flat dark ground), plus black fade-in/fade-out frames. Rules from now on:
  - Fill the WHOLE 1080×1920 frame edge to edge with detail and colour in every frame — no flat solid-colour bands along any edge (top 200 px, bottom 300 px, left/right 60 px must contain texture, gradient detail, imagery or motion).
  - Keep the brightest/most colourful part of the scene reaching the edges; avoid near-black (#000–#151515) areas larger than ~10% of the frame near the edges.
  - No fade from/to black at the start or end — start on a full, bright, busy frame; use cross-cuts or colour wipes between scenes.
  - After rendering, check: for the first, middle and last frame, measure the mean brightness and variance of the top 150 px and bottom 150 px strips (e.g. with numpy/PIL); if a strip is near-uniform (std dev < 6) or very dark (mean < 25), fix the scene before posting.
- **Edge haze (2026-11-22):** flat skies, grey water and blurred backgrounds fail the check. Wrap every photo/clip frame with `photo.haze(a, t)` (soft drifting fbm mist strongest at the edges, zero in the centre — see render_004.py `finish` wrapper and `bg()`); give drawn full-height bands texture (seams, rivets, dimples). Also check every special glyph exists in Poppins (e.g. → is missing; ≈ … · are fine).
- Facebook also showed "Low 20-second view rate" on video 001: the first 3 seconds must show the most striking image + a bold claim, with the first visual change within 1.5 s.

## Strategy review 2026-11-20 (first analytics, video 001 at ~18 h)
Data: Instagram 312 views / 260 reach, 3-s view rate 65% (skip 35%), avg watch 23.8 s, 8 likes, 4 comments, 1 save, 0 shares. Facebook 103 views (Metricool), avg watch 15 s, ~58% gone by 3 s (Bidhan's screenshot). TikTok 7 views, 3 likes, 1 comment, 2 shares (new account — almost no distribution yet). YouTube: no analytics yet (Windsor returns no rows for the first 48 h; Metricool's YouTube video metrics are deprecated — use Windsor `youtube`).
What changes (v2, applied from video 002):
1. **Hooks** — the biggest leak (35–58% gone in 3 s). Frame 1 = the subject + a ≤6-word claim in huge type ending in "?!"; voice starts at 0.0 s (leading silence trimmed in tts2.py); first cut/punch-in by 1.3 s; open loop ("the fix is still hidden inside") in the second line.
2. **Length** — keep 61–75 s for monetisation, but aim 65–72 s and ≤ ~200 words at voice speed 1.08; tight 0.25 s gaps between lines; end card ≤2.3 s.
3. **Visual style** — new engine (pipeline/engine.py): procedural textures on every surface (sky, rock, water, concrete, terrain), camera push-ins and cuts every 2–3 s, particles (steam, sparks, flow), thermal/x-ray views, counters that tick up, colour-wipe transitions (never black), kinetic captions with gold keywords. Edge-band check is automated (pipeline/check_edges.py) and must PASS.
4. **Sound** — pipeline/audio2.py: driving 100-bpm synth bed ducked under the voice + whoosh/boom/tick/thunk/crack SFX on every cut and counter.
5. **Topics** — every topic must have ONE repeatable shock number for the hook (125 years, 726 ft…). US icons first for pay; alternate natural wonder / mega-build.
6. **Captions & hashtags** — question-led caption, 5–6 hashtags, searchable titles, an engagement question as first comment.
7. **Posting time** — 10:00 Sydney adopted. Compare after 7 posts (2026-11-27) using per-post views at 24 h.
8. **Money plan** — unchanged order; realistic note: no meaningful payout before ~1–3 months. Instagram has no direct payout in Australia → use it for growth and sponsor proof. Start the weekly YouTube long-form compilation once 8 shorts exist (~2026-11-27).
9. **Style test** — CANCELLED 2026-11-20 by Bidhan's feedback on 002: real imagery + globe zoom is now the standard for every video (see section above).

## Anti-"AI slop" rules (2026-11-20) — protects monetisation (YouTube inauthentic-content policy, TikTok originality filter, Meta originality)
- Never let two videos in a row share the same structure. Rotate formats: (a) classic "how it formed/was built" explainer, (b) "3 things you didn't know about X", (c) myth vs fact, (d) timeline "from nothing to now in 60 s", (e) scale comparison ("if Uluru were in Sydney…"), (f) "engineer's take" — one specific engineering/geology insight explained properly (loads, materials, erosion rates, construction method).
- Every video must contain at least one specific, checkable detail that generic AI fact-pages don't have (a number, a method, a named process, a primary source), and show a small on-screen source line.
- Rotate voices, music key/tempo, colour accents and opening shot type; never reuse a sentence or hook phrasing from LOG.md.
- Only 1 video per day maximum. Quality over quantity — skip a day rather than post something weak or unverified.
- Prefer real imagery (public domain / CC) plus our own diagrams over purely synthetic visuals; never generate fake "realistic" footage of real places or events.
- AI-content labels: OFF per Bidhan's 2026-11-20 decision (see Respect & policy) — never depict real people or fake realistic events, so nothing needs a synthetic-media label.
- If Bidhan records his own voiceover for a script, always prefer his voice over TTS.
