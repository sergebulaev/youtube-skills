# Sub-skill: Build / update the Voice & Brand Profile

Builds or refreshes `../../references/voice-profile.md` so every writing skill in
this bundle drafts in the user's real voice. Runs on any agent (Claude Code,
Codex, OpenClaw): the core path needs only the user's own writing pasted in. A
read token is an optional accelerator, never required.

## When this runs

- User says "build my voice profile", "learn my voice", or invokes `yt-community-post-writer --mode profile`.
- Also offer it the first time a writing skill runs and finds `filled: no`.

## Inputs (any one is enough)

1. **Pasted samples (portable default).** Ask for 3-6 of the user's own real
   YouTube community posts, video descriptions, or scripts. Enough on its own.
2. **Read-layer assisted (optional).** If a token is configured, pull recent
   activity via the bundle's read layer as extra samples.
3. **Manual.** The user can state their niche, rules, and links directly.

## Steps

1. Gather 3+ real samples of the user's writing.
2. Extract the voice fingerprint from the samples, not assumptions: rhythm,
   openers, punctuation habits, favored vocabulary, avoided words, emoji use.
3. Infer niche, ICP, and pillars from the sample topics; confirm rather than guess.
4. Capture hard rules and CTA/link style the samples reveal or the user states.
5. Write `../../references/voice-profile.md`: fill sections 1-5, copy the 2-4
   strongest lines verbatim into "Signature examples", set Status to `filled: yes`,
   `source: <pasted|read-layer|manual>`, `updated: <today>`.
6. Show the filled profile for approval; tell the user every writing skill will
   now match it automatically.

## Hard rules

- Build the fingerprint from the user's ACTUAL samples. Never invent a voice.
- Preserve their quirks. Only the generic AI-tell scrub applies to drafts, not
  to the profile itself.
- With only 3 samples, say it is a first pass; suggest re-running after 10+ posts.
- Never put anything the user did not provide into the file.

## Related

- The filled profile is read by this bundle's writing skills before they draft.
- Re-run any time the user's voice or focus shifts.
