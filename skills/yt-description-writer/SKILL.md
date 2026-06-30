---
name: yt-description-writer
description: Write a full YouTube video description under 5,000 characters with a first-150-character hook (the only part visible before Show more, and what shows in search and suggested), timestamped chapters, naturally placed keywords, links, and a clear call to action. Covers long-form and YouTube Shorts. Becomes the create-post content that publishes with the video. Use to write or rework a description. Not for the title (use yt-title-optimizer) or the spoken opening (use yt-hook-scripter).
---

# YouTube Description Writer

The description does three jobs: it hooks the reader in its first 150 characters,
it feeds YouTube and Google search, and it organizes the video with chapters and
links. This skill writes all three layers.

## When to use

- User says "write the description for this video"
- User has a video and wants chapters, keywords, and links structured
- User wants the first 150 chars optimized for the search/suggested snippet
- User is about to upload and needs the `content` that ships with the video

## The three layers of a description

| Layer | Chars | Job |
|---|---|---|
| **Hook** | first ~150 | the only text visible before "Show more"; also the search/suggested snippet. Lead with the payoff or the question and the search phrase. |
| **Body** | ~150 to 1,000 | expand the value, restate the promise, place the main keywords naturally, link the key resource. |
| **Furniture** | rest, up to 5,000 | chapters, links, social, credits, hashtags. Skimmable, labeled. |

## Steps

1. **Gather inputs.** The title (so the description complements it), the video's
   payoff, the main search phrase plus 3 to 5 secondary keywords, the chapter
   beats with timestamps, any links (lead magnet, gear, socials), and whether it
   is long-form or a Short. If a URL is given, parse it with `lib/url_parser.py`.
2. **Write the first 150 chars as a second hook.** Lead with the payoff or the
   question, work the primary keyword in naturally, and make it read well as a
   standalone snippet. This is not "welcome back to the channel".
3. **Write the body.** 2 to 4 short paragraphs that restate the promise and place
   the keywords without stuffing. Put the single most important link here.
4. **Add chapters.** Timestamps starting at `0:00`, each label short and
   descriptive. YouTube needs at least 3 chapters and a `0:00` start to enable
   the chapter UI. For a Short, skip chapters.
5. **Add the furniture.** Links section, socials, a one-line CTA (subscribe for
   the specific reason, not "smash like"), and 3 to 5 relevant hashtags at the
   very end (the first 3 surface above the title).
6. **Humanizer pass and length check.** Strip AI vocabulary and em dashes; keep
   the whole thing under 5,000 chars. Confirm the first 150 read well truncated.
7. **Approval card.** Show the description with a marked 150-char cutoff and the
   total char count.
8. **On approval.** This description is the `content` passed to
   `lib.publish(kind="video"|"short", draft_text=<description>, title=<title>,
   ...)`. The title travels separately in `platformSettings.youtube.title`.

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- 5,000-char hard cap. The first 150 chars carry the hook and the search phrase.
- The first line is never boilerplate ("Hi everyone, welcome back").
- Chapters: at least 3, first one at `0:00`, short labels. Long-form only.
- Keywords appear in natural sentences, never as a comma-separated dump.
- Hashtags: 3 to 5 max, at the end. More than 15 makes YouTube ignore all of them.
- Every link is labeled so the reader knows what it is before clicking.

## Anti-patterns (skill will refuse)

- A boilerplate greeting in the first 150 chars.
- A keyword dump or a tag wall pretending to be a description.
- 15+ hashtags (YouTube strips them all).
- Em dashes anywhere.
- "Smash that like button and subscribe" dead phrasing.
- Chapters that do not start at `0:00` (the UI will not render them).
- Raw unlabeled links.

## Resources

- `../../references/algorithm-heuristics.md` - the 150-char snippet, chapters, search signals
- `../../references/voice-rules.md` - the canonical voice rules
- `references/description-template.md` - the full skeleton with chapters, links, hashtags

## Related skills

- `yt-title-optimizer` - the title the description complements
- `yt-hook-scripter` - the spoken first 30 seconds (different from the written hook)
- `yt-content-planner` - keyword and link strategy across a series
