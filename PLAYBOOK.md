# How On Earth — Channel Playbook

Faceless short-video channel: **natural wonders and mega-builds, and how they came to be.**
Owner: Bidhan. Goal: **US$500/month combined** across TikTok, Instagram, Facebook, YouTube.

## Channel mission (Bidhan's own words, 2026-11-20)
Bidhan is a civil engineer who has always been fascinated by how things work — big designs, big buildings — and equally by geography and geology: how natural landscapes came about. He believes people are more interested in the **HOW** than the what/why. The channel should become a platform for like-minded, curious people. "Nothing fancy" — daily, educational, accurate. Every video must answer a clear "how did this come about / how does this work" question, about either a natural landscape or a great human-made structure. Entertainment hooks serve the education, never replace it.
**Topic filter (Bidhan, 2026-11-20): a topic is used ONLY if it passes all three:**
1. **Viral-friendly** — a famous or visually stunning subject most people recognise, with a surprising "wait, what?" fact that works as a 1.5 s hook and makes people share or comment.
2. **Good for monetisation** — appeals to high-value audiences (US/UK/AU/CA adults), fits the 61–75 s format, and links naturally to sponsors/affiliates (travel and tours, learning apps, STEM kits, tools, documentaries).
3. **Ad-friendly** — brand-safe: no disasters with deaths as the focus, no war, politics, religion disputes, tragedy, gore or controversy; family-friendly wording.
If a topic fails any one of these, pick another. Note in LOG.md for each video one line on why it passed.

## Accounts
- Metricool brand: blogId `8221611`, timezone Australia/Sydney. Connected: facebook (How On Earth Page), instagram (@howonearth2026), tiktok (@how.on.earth7, display name How On Earth 🌍, personal account — keep personal for Creator Rewards), youtube.
- Public profile links: TikTok https://www.tiktok.com/@how.on.earth7 · Instagram https://www.instagram.com/howonearth2026/ · Facebook https://www.facebook.com/1474038465792135 · YouTube https://www.youtube.com/@thehowonearth (handle @thehowonearth)
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
6. **Send Bidhan the finished video file every run** (SendUserFile, his request 2026-11-21) with the summary. It is for his viewing, not approval: still schedule without waiting.
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

## Making it NOT boring (quality bar — every video must beat the last)
1. **Hook in the first 1.5 s**: a bold on-screen claim + matching first spoken line (e.g. "This bridge grows 18 cm every summer"). First frame must already show the subject and hook text (it is the thumbnail).
2. **Visual change every 2–3 s**: cuts, camera push-ins/pans (animate scale/translate), reveals, x-ray cross-sections, before/after splits, counters ticking up, map zooms.
3. **Rich colour and depth**: gradients, glow, parallax layers (foreground/mid/background moving at different speeds), particles (dust, rain, sparks, water), soft shadows. Avoid flat empty frames.
4. **Kinetic captions**: 1–3 words at a time, pop-in scale, key word highlighted gold.
5. **Sound design**: whoosh on transitions, low boom on big reveals, subtle ticks on counters (synthesise with numpy — no copyrighted SFX).
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

## Money plan (US$500/month target)
1. **Facebook Content Monetization** (Australia eligible, invite-only) — usually the first real payout for this niche.
2. **YouTube Partner Program** — Shorts views + weekly **long-form compilations** (combine 8–10 shorts into a 10+ min video) to earn watch hours. Note thresholds rise for new applicants from 1 Feb 2027.
3. **Affiliate**: travel/tour links (Bidhan must sign up himself; add link-in-bio once approved).
4. **Sponsors** from ~5–10k followers: learning apps, STEM kits, travel, tools. Max 1 sponsored per 4 videos, always labelled as paid partnership.
5. TikTok Creator Rewards availability in Australia is uncertain — check TikTok Studio once at 10k followers.

## Comment replies (Windsor.ai)
- Instagram: Windsor connector `instagram`, account `17841461164290075`. Read comments with get_data fields comment_id, comment_text, comment_username, comment_timestamp, comment_parent_id, media_permalink (date_preset last_7dT). Reply with execute_action `reply_to_comment` {comment_id, message}.
- YouTube: Windsor connector `youtube`, account `105358`. Comment fields: comment_id, comment_text, comment_author, comment_published_at, comment_video_id, comment_reply_count. Reply with `reply_to_comment`. (Needs the optional Windsor reconnect at https://onboard.windsor.ai/app/youtube_review — if comment fields fail, tell Bidhan.)
- Facebook and TikTok: no reply tool — Bidhan replies in the apps.
- **ONE REPLY PER COMMENT — never more (Bidhan's rule).** Before replying to a comment, skip it if ANY of these is true: its comment_id is already in REPLIED.md; its comment_reply_count (Instagram) / comment_reply_count (YouTube) is greater than 0; it was written by the channel itself (comment_username howonearth2026 / the channel's own name); it is itself a reply. Windsor's comment list can be cached and does NOT reliably show the channel's own replies, so REPLIED.md and comment_reply_count are the source of truth. After each successful reply, add a line to REPLIED.md straight away, and commit + push it at the end of the run.
- **24-HOUR RULE (Bidhan's rule, 2026-11-20):** never reply to a comment more than 24 hours old (comment_timestamp / comment_published_at vs now, UTC). Older unanswered comments are skipped, not replied to; still flag business enquiries or fact corrections to Bidhan, and hiding spam is still allowed.
- Rules: reply only to top-level comments from other people. Friendly, short (1–2 sentences), add a real fact or answer, often end with a question to keep the conversation going. Vary wording — never copy-paste the same reply. Never argue, never promise anything, never share personal info about Bidhan. Ignore spam; hide (do not delete) abusive or spam comments. Max ~30 replies per run.
- Log replies count in LEARNINGS.md weekly; note which questions people ask (they are topic ideas).

## Platform flags to avoid (learned 2026-11-20)
- **Facebook flagged video 001: "Your video has a border — can look like repurposed content, may limit distribution."** Cause: large flat, near-black bands at the top (dark navy sky) and bottom (flat dark ground), plus black fade-in/fade-out frames. Rules from now on:
  - Fill the WHOLE 1080×1920 frame edge to edge with detail and colour in every frame — no flat solid-colour bands along any edge (top 200 px, bottom 300 px, left/right 60 px must contain texture, gradient detail, imagery or motion).
  - Keep the brightest/most colourful part of the scene reaching the edges; avoid near-black (#000–#151515) areas larger than ~10% of the frame near the edges.
  - No fade from/to black at the start or end — start on a full, bright, busy frame; use cross-cuts or colour wipes between scenes.
  - After rendering, check: for the first, middle and last frame, measure the mean brightness and variance of the top 150 px and bottom 150 px strips (e.g. with numpy/PIL); if a strip is near-uniform (std dev < 6) or very dark (mean < 25), fix the scene before posting.
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
