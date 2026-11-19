# How On Earth — Channel Playbook

Faceless short-video channel: **natural wonders and mega-builds, and how they came to be.**
Owner: Bidhan. Goal: **US$500/month combined** across TikTok, Instagram, Facebook, YouTube.

## Accounts
- Metricool brand: blogId `8221611`, timezone Australia/Sydney. Connected: facebook (How On Earth Page), instagram (@howonearth2026), tiktok (How On Earth 🌍, personal account — keep personal for Creator Rewards), youtube.
- Video hosting: this repo. Public raw URL pattern:
  `https://raw.githubusercontent.com/beedangsb123/how-on-earth-videos/main/videos/<file>.mp4`
- Log of every video: `LOG.md`. Lessons from analytics: `LEARNINGS.md`.

## Video spec
- 1080×1920, 30 fps, H.264 CRF 18, AAC. **61–75 s** (must exceed 60 s for TikTok Creator Rewards / Facebook).
- Voiceover: kokoro-onnx (models from github.com/thewh1teagle/kokoro-onnx releases `model-files-v1.0`), voice `am_michael`. Spell tricky names phonetically for TTS, correct spelling in captions.
- Background music: original synth (pipeline/music.py), ducked under voice. Never use copyrighted music.
- Burnt-in captions in the safe zone: y≈1300–1500, max width 860 px. Keep anything important out of: top 180 px, bottom 400 px, right 160 px (platform UI).
- Brand: night-to-dawn palette — navy #0B1026, #1B2B5C, blue #3E5C9A, orange #F28C38, gold #FFC857. Poppins Bold (Montserrat for ṉ ṟ ṯ). Small "HOW ON EARTH?" badge top. End card with logo + "FOLLOW".

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
- Mix: ~40% Australia/NZ (home audience), ~60% global icons (US/UK/EU audiences pay more).
- Series hooks that build bingeing: "Australia's wonders", "Impossible builds", "Earth's weirdest places".
- Before choosing, check `LOG.md` — never repeat a topic. Check `LEARNINGS.md` and lean into what performed best.
- Facts: verify each claim with at least one reputable source (government, university, encyclopaedia, major museum). Note sources in LOG.md.

## Respect & policy
- Indigenous sacred sites (e.g. Uluṟu, Kata Tjuṯa): distant silhouettes only, no close-up rock features of sensitive sites, acknowledge Traditional Owners.
- No copyrighted footage, characters, logos, music. No real people's likeness. No photos of public figures.
- Always set AI-content labels (tiktok isAigc, instagram isAiGenerated, youtube isAiGeneratedContent). YouTube madeForKids = false.
- Family-friendly, no gore, no disaster-exploitation.

## Posting
- Schedule through Metricool `createScheduledPost` with all four providers in one post: facebook type REEL (+ title), instagram type REEL, tiktok (title, PUBLIC_TO_EVERYONE), youtube type short (title with #shorts, category EDUCATION or SCIENCE_TECHNOLOGY, tags).
- Use `getBestTimeToPostByNetwork` when choosing times; default evening 6–8 pm Sydney.
- Caption: curiosity line + 1 emoji + 5–8 hashtags (mix broad and specific, always #howonearth).

## Money plan (US$500/month target)
1. **Facebook Content Monetization** (Australia eligible, invite-only) — usually the first real payout for this niche.
2. **YouTube Partner Program** — Shorts views + weekly **long-form compilations** (combine 8–10 shorts into a 10+ min video) to earn watch hours. Note thresholds rise for new applicants from 1 Feb 2027.
3. **Affiliate**: travel/tour links (Bidhan must sign up himself; add link-in-bio once approved).
4. **Sponsors** from ~5–10k followers: learning apps, STEM kits, travel, tools. Max 1 sponsored per 4 videos, always labelled as paid partnership.
5. TikTok Creator Rewards availability in Australia is uncertain — check TikTok Studio once at 10k followers.
