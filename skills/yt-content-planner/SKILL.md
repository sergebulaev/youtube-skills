---
name: yt-content-planner
description: Build a weekly YouTube upload plan: long-form vs YouTube Shorts mix, posting cadence, per-slot title and thumbnail pairing, hook angle, community-tab posts between uploads, and a goal balance across CTR, retention, and subscribes. Maps Shorts as top-of-funnel that points at long-form, and long-form as the loyalty and watch-time engine. Use to plan a week or a content calendar instead of shipping ad hoc. Not for writing a single title, description, or hook (use the dedicated yt skills).
---

# YouTube Content Planner

Turns a channel theme, an audience, and content pillars into a structured week:
what to upload, when, in which format, and how the title and thumbnail pair on
each slot. It plans; the dedicated skills write each piece.

## When to use

- User says "plan my week of YouTube content" or "build me a content calendar"
- User wants a long-form vs Shorts mix and a cadence they can hold
- User wants each slot pre-paired (format, title angle, thumbnail angle, hook)
- User wants the community-tab posts scheduled between uploads

## What it produces

- A **weekly grid**: each slot has a format (long-form or Short), a working title
  angle, a thumbnail angle, the hook formula, the pillar, and a posting window.
- A **long-form vs Shorts ratio** sized to the channel's stage and capacity.
- **Community posts** placed on the non-upload days to keep the channel warm.
- A **goal balance check**: across the week, are you spread across CTR-first,
  retention-first, and subscribe-first pieces, not all one note.

## Steps

1. **Gather inputs.** The channel theme/niche, the audience, 3 to 5 content
   pillars, the target audience timezone, how many videos per week the user can
   realistically make, and the current stage (new channel vs established). If a
   channel URL is given, parse it with `lib/url_parser.py` and ask the user to
   paste their recent titles and rough view counts.
2. **Set the mix.** Size the long-form vs Shorts ratio to capacity and stage. A
   common growing-channel rhythm is 1 long-form per week plus 3 to 5 Shorts, but
   consistency over 12 weeks beats volume. Confirm a cadence the user can hold.
3. **Assign pillars to slots** so the week is varied, not five takes on one
   topic.
4. **Pair each slot.** For every upload, set:
   - format (long-form or Short)
   - working title angle (which Y1-Y6 formula)
   - thumbnail angle (what it carries that the title does not)
   - opening hook formula (Y7-Y10), matched via the pairing table
   - primary goal (CTR / retention / subscribes)
   - posting window in the audience timezone
5. **Place community posts** on the non-upload days (a poll, a tease, a question).
6. **Run the goal balance check.** If every slot is CTR-bait or every slot is a
   deep tutorial, rebalance. Shorts skew top-of-funnel reach; long-form skews
   watch-time and loyalty. Make sure both jobs are covered.
7. **Hand each slot to the right skill.** The planner does not write the final
   title, description, hook, or thumbnail; it routes each slot to
   `yt-title-optimizer`, `yt-description-writer`, `yt-hook-scripter`, and
   `yt-thumbnail-brief`.
8. **Optional approval + schedule.** If the user has videos ready, each one
   publishes through its own skill via `lib.publish(...)`; the planner only sets
   the calendar.

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- Cadence must be one the user can hold for at least 12 weeks. Sustainable beats
  ambitious.
- Every upload slot is pre-paired: format, title angle, thumbnail angle, hook,
  goal, and time. No naked "post a video" slots.
- Shorts and long-form must have a through-line (Shorts point at the library),
  not two disconnected audiences.
- Spread the week across CTR, retention, and subscribe goals. Not all one note.
- Measure long-form watch-time and returning viewers separately from Shorts
  views. Do not let Shorts reach inflate the read on growth.

## Anti-patterns (skill will refuse)

- An over-ambitious cadence the user cannot sustain (daily long-form for a solo
  creator).
- Five slots that are all the same pillar and the same goal.
- Shorts with no connection to the long-form library.
- "Post more" as a plan, with no per-slot pairing.
- Em dashes anywhere in the plan.

## Resources

- `../../references/algorithm-heuristics.md` - long-form vs Shorts strategy, timing, signals
- `../../references/hook-formulas.md` - title and hook formulas to assign per slot
- `references/pillars-framework.md` - turning a niche into pillars and a balanced mix
- `references/example-week.md` - a fully worked weekly grid

## Related skills

- `yt-title-optimizer` - write the title for each planned slot
- `yt-thumbnail-brief` - brief the thumbnail for each planned slot
- `yt-hook-scripter` - script the opening for each planned slot
- `yt-description-writer` - write the description for each planned slot
- `yt-community-post-writer` - the between-uploads community posts
