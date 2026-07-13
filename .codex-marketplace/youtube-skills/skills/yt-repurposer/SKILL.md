---
name: yt-repurposer
description: Repurpose off-platform content into a native YouTube surface. Take a blog, X thread, LinkedIn post, or newsletter and turn it into a community post or poll, or a video brief (title, spoken hook, description with chapters). Leads with the payoff, converts listicles into chapters, strips off-platform artifacts, publishes via Publora on approval. Not for a fresh community post (use yt-community-post-writer), not for a hook script (use yt-hook-scripter).
---

# YouTube Repurposer

Turn something you already made into a YouTube surface that reads like it was
born on YouTube. Repurposing is not copy-paste. A post that killed on LinkedIn
or X will die on the community tab if you paste it: wrong hook, wrong format, and
artifacts ("link in bio", hashtag walls, @-handles) that scream off-platform.

YouTube is video-first, so "content" here is what you feed the machine, not the
video itself. This skill transforms an external piece into a native YouTube
target: a **community post** you can publish, or a **video brief** (title, spoken
hook, description) you hand to the writer skills. It reads your source, keeps the
idea, and rebuilds the delivery for YouTube.

## When to use

- "Turn this blog post / thread / LinkedIn post into a YouTube community post"
- "Repurpose my newsletter into a video: give me a title, hook, and description"
- "This X thread did well, adapt it for my channel"
- "I have a rough idea in another format, make it native for YouTube"

Not for a blank-page community post (use `yt-community-post-writer`), not for a
fresh spoken opening (use `yt-hook-scripter`), and not for titling a video you
already have (use `yt-title-optimizer`).

## How it works

1. **Take the source.** Any format: a blog post, an X thread, a LinkedIn post, a
   newsletter, a caption, a bullet list, a link to read. Ask for the source and
   the goal (bring subscribers back / seed comments / drive a video) if not given.
2. **Extract the spine.** Strip the source platform's shell and pull out the one
   claim, the one story, or the one number worth keeping. Most repurposing fails
   because it keeps the words instead of the point.
3. **Choose the target surface.** A quick update, a tease, or a question that
   fits between uploads -> a **community post** (hand format to
   `yt-community-post-writer`); a poll if the source is a debate or a list of
   options. A teachable idea worth a full video -> a **video brief**: a title
   (hand to `yt-title-optimizer`), a spoken hook script (hand to
   `yt-hook-scripter`), and a description (hand to `yt-description-writer`).
4. **Re-hook for YouTube.** Lead with the payoff, not the intro. "Here's what I
   found" beats "In this video". For a community post the first line carries it
   (the feed truncates). For a video brief the title is a promise and the spoken
   hook confirms it in the first 30 seconds (or 3 on a Short). The source's hook
   almost never survives; rewrite it using `../../references/hook-formulas.md`.
5. **Refit the format.** A listicle or a numbered thread becomes **chapters with
   timestamps** in the description, one item per chapter. A long-read becomes the
   single most quotable claim as the hook, then the supporting beats. A community
   post stays short: one clear ask, a poll or an image teaser where it fits.
6. **Strip off-platform artifacts.** Remove "link in bio", "smash subscribe",
   "read the thread", hashtag walls, X @-handles that only exist elsewhere, and
   any "as I posted on LinkedIn" throat-clearing. A repurposed piece should not
   admit it was repurposed.
7. **Scrub instead of a humanizer pass.** There is no `yt-humanizer`. Lean on the
   receiving writer skill's own scrub: `yt-community-post-writer`,
   `yt-title-optimizer`, `yt-hook-scripter`, and `yt-description-writer` each
   strip AI vocabulary, em dashes, and rule-of-three before they return. Keep the
   source's real numbers and named entities through the hand-off.
8. **Approval card.** Show: source -> YouTube mapping (what became what), the
   target surface (community post / poll, or the title + hook + description
   brief), the hook formula used, and the primary goal.
9. **On approval.** For a **community post**, publish via
   `lib.publish(kind="community", draft_text=<approved post>, target_url=<community tab url>)`;
   Publora has no community endpoint, so this returns a copy-paste block by
   design. For a **video brief**, hand each part to its writer skill; the video
   itself uploads through that skill's own Publora flow once the user supplies the
   .mp4.

## Native-fit rules (source -> YouTube)

- **Blog / newsletter -> video brief:** pick the single most quotable claim as
  the title and spoken hook, then thread the supporting beats as description
  chapters. Do not summarize the whole piece into a wall.
- **X thread -> video brief or community post:** a teach-thread maps to a video
  with the payoff up front; a hot-take single tweet maps to a community text post
  or a poll. Strip the thread numbering and the "1/" scaffolding.
- **LinkedIn post -> community post:** LinkedIn tolerates a warm-up; the community
  feed truncates, so rewrite the hook onto line one and cut the throat-clearing.
- **Listicle / carousel -> chapters:** one item per chapter with a timestamp, each
  with its own micro-hook, not a wall in the description.
- **Instagram / TikTok caption -> community post:** strip emoji density and
  hashtag blocks; YouTube reads them as noise. A visual source favors an
  image-teaser community post.

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- Keep the source's **claim and facts** intact. Repurposing changes the delivery,
  never the meaning or the numbers.
- Lead with the payoff. If the first line or the title needs a wind-up, rewrite it.
- Never paste the source verbatim and trim. Rebuild the hook and format from the spine.
- One specific number where the source offers one. Keep it.
- Title and thumbnail (if briefed) are a pair; they never repeat the same words.
- Do not hard-sell the user's product. One natural mention max.

## Anti-patterns (skill will refuse)

- Copy-pasting the source with light edits (that is not repurposing).
- Keeping the source platform's artifacts ("link in bio", "read the thread",
  hashtag walls, off-platform @-handles).
- Opening a video brief with "In this video I'm going to.." instead of the payoff.
- A community post that is a wall of text where the tab wants one or two lines.
- ALL CAPS for intensity. Carry it with word choice.
- Em dashes anywhere.
- Rule-of-three lists without specifics.
- "leverage", "fundamentally", "streamline", "harness", "delve".
- Engagement bait ("comment 1 for yes").

## Resources

- `../../references/hook-formulas.md` - the 10 YouTube title and hook formulas to re-hook with
- `../../references/algorithm-heuristics.md` - 2026 YouTube ranking (CTR x retention), timing, limits
- `../../references/voice-rules.md` - the canonical voice rules the receiving writer skills inherit

## Related skills

- `yt-community-post-writer` - write a community post or poll from a blank page (repurposer hands the community target here)
- `yt-title-optimizer` - title the video brief the repurposer produces
- `yt-hook-scripter` - script the spoken opening for the video brief
- `yt-description-writer` - write the description and chapters for the video brief
