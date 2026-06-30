---
name: yt-title-optimizer
description: Write high-CTR YouTube and YouTube Shorts titles under 100 characters using 2026 packaging formulas (curiosity-gap, number, how-I outcome, mistake/loss, transformation, versus). Balances curiosity with a real keyword, front-loads the click-deciding words for the 60-char mobile cutoff, and returns 3 to 5 A/B variants tagged by goal for Test and Compare. Use to title or rework a video. Not for the description (use yt-description-writer) or the thumbnail overlay (use yt-thumbnail-brief).
---

# YouTube Title Optimizer

Titles are half the click. This skill turns a topic, a draft title, or a video
URL into a shortlist of titles that earn the click honestly, then leaves the
final pick (and the A/B test) to you.

## When to use

- User says "give me title ideas for this video"
- User has a flat or clickbait title and wants sharper, honest options
- User wants titles tied to a specific goal (CTR for browse, or search-intent)
- User wants A/B variants to drop into YouTube's Test & Compare

## Formulas this skill uses (packaging shapes, Y1-Y6)

| Code | Formula | Best for |
|---|---|---|
| Y1 | Curiosity-Gap | a surprising result whose mechanism is hidden |
| Y2 | Number / Listicle | a finite, scannable payoff |
| Y3 | How-I Outcome | a first-person result with a number and timeframe |
| Y4 | Mistake / Negativity | a costly thing the viewer is getting wrong |
| Y5 | Transformation | a before/after arc over a timeframe |
| Y6 | Versus / Comparison | two named options in tension (search-friendly) |

Full skeletons in `../../references/hook-formulas.md`.

## Steps

1. **Gather inputs.** The topic or rough title, the real payoff of the video, the
   target viewer, the main search phrase if any, and whether it is long-form or a
   Short. If a URL is given, parse it with `lib/url_parser.py` and ask the user
   to paste the current title and what the video actually delivers.
2. **Decide the job.** Browse-first (lead with curiosity and emotion) or
   search-first (lead with the exact query phrase). Most videos want browse; how-
   to and comparison videos lean search.
3. **Shortlist 2 to 3 formulas** that fit the payoff, then draft.
4. **Write 3 to 5 titles.** Each one:
   - Under 100 chars, ideally 40 to 60, click-deciding words first.
   - One specific number where the claim allows it.
   - Curiosity AND a concrete noun. Never pure mystery, never a dry label.
   - Complements a thumbnail (note what the thumbnail should carry instead).
   - No em dashes, no ALL CAPS, 0 to 1 emoji.
5. **Humanizer pass.** Strip AI vocabulary, rule-of-three, and any em dash.
6. **Tag each variant** with its formula, char count, and primary goal, and flag
   the one to lead the Test & Compare with.
7. **Approval card.** Show the variants with char counts. The user picks or asks
   for another round.
8. **On approval.** Titles ride along when the video is published. If the user is
   also uploading via this bundle, pass the chosen title as the `title` kwarg to
   `lib.publish(kind="video"|"short", ...)`; otherwise hand it over for Studio.

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- 100-char hard cap. Aim 40 to 60 so mobile does not truncate the payoff.
- Front-load: the words that decide the click go before any colon.
- Title and thumbnail never repeat the same words. Note the split every time.
- Curiosity must be honest. The title cannot promise more than the first 30
  seconds delivers (a fast click-away is a ranking penalty).
- Always return at least 3 variants. One title is not a recommendation.

## Anti-patterns (skill will refuse)

- Clickbait the video does not honor ("you won't believe what happened").
- ALL CAPS titles or 3+ emoji for fake intensity.
- Keyword-stuffing the title to chase search.
- Em dashes anywhere.
- Vague mystery with no concrete noun ("This changes everything").
- Repeating the thumbnail's words in the title.

## Resources

- `../../references/hook-formulas.md` - Y1-Y6 title skeletons and the pairing table
- `../../references/algorithm-heuristics.md` - CTR x retention, packaging, the 60-char cutoff
- `references/title-checklist.md` - the per-title scrub and CTR fit list

## Related skills

- `yt-thumbnail-brief` - design the other half of the click
- `yt-hook-scripter` - script the first 30 seconds so the title's promise lands
- `yt-description-writer` - the SEO description and chapters
- `yt-content-planner` - pair titles and thumbnails across a week
