---
name: yt-thumbnail-brief
description: Turn a YouTube video idea into a designer-ready thumbnail brief: focal subject, face and emotion, a text overlay of 4 words or fewer that the title does not repeat, contrast and composition, and 2 to 3 A/B concepts for Test and Compare. Built on 2026 principles (one focal point, legible at 120 pixels, complements the title). Outputs the brief plus the Publora attach step (the image upload itself is out of band). Use to plan a thumbnail. Not for title words (use yt-title-optimizer).
---

# YouTube Thumbnail Brief

This skill does not generate an image. It writes the brief a human designer (or
an image tool) executes, grounded in what actually drives the click in 2026, and
documents how a custom thumbnail gets attached when you auto-publish.

## When to use

- User says "what should the thumbnail be for this video"
- User wants a brief to hand to a designer or paste into an image generator
- User wants 2 to 3 thumbnail concepts to A/B test
- User is auto-publishing and needs the thumbnail upload steps

## What the brief contains

For each concept the skill outputs:

- **Concept name and the angle** it sells (and how it complements the title).
- **Focal subject:** a face plus the specific emotion, or the object/result.
- **Text overlay:** the exact words (4 or fewer), and where they sit. Never the
  same words as the title.
- **Background and contrast:** color, lighting, and how the subject separates.
- **Composition:** rule-of-thirds placement, gaze direction, crop.
- **120-pixel test note:** what must still read when shrunk to mobile size.

## Steps

1. **Gather inputs.** The title (so the thumbnail complements, never repeats it),
   the video's payoff and emotional tone, whether there is a face available, the
   single most visual moment or result, and long-form vs Short. If a URL is
   given, parse it with `lib/url_parser.py`.
2. **Split the load with the title.** Decide what the title already says and make
   the thumbnail carry the rest (the face/emotion, the result, the object). List
   the split explicitly.
3. **Write 2 to 3 concepts.** Vary one big element between them (face vs object,
   text vs no text, color), not five small things, so the A/B test is readable.
   Each concept fills the six fields above.
4. **Apply the non-negotiables.** One focal point, a legible real emotion, high
   contrast, 4 words or fewer of text, and it must read at 120 px. Flag any
   concept that risks failing the shrink test.
5. **Recommend the lead concept** for YouTube's Test & Compare and say why.
6. **Hand off the brief.** The user gives it to a designer or an image tool. This
   skill writes words, not pixels.
7. **If auto-publishing, give the upload flow** (see below). Otherwise the user
   sets the thumbnail in YouTube Studio.

## The thumbnail flow (auto-publish)

A custom thumbnail cannot be set on `create-post` because the thumbnail upload
needs a `postGroupId` first. The order is:

1. Create the video post as a **draft** (`create-post`, no scheduledTime) ->
   returns the `postGroupId`.
2. **Upload the thumbnail image out of band.** Publora requires the thumbnail to
   be a tracked media asset from its dedicated YouTube thumbnail endpoint (JPEG
   or PNG, max 2 MB, 1280x720 recommended). That upload is **not wired into this
   bundle**: do it in the Publora dashboard (or via the dedicated endpoint once
   available). The generic `get-upload-url` media flow is not accepted for
   thumbnails. The upload returns a `mediaId` and `url`.
3. Attach it: call `update-post` with
   `platformSettings.youtube.thumbnail = {mediaId, url}` (the
   `lib.PubloraClient.set_thumbnail(post_group_id, media_id=, url=)` helper wraps
   this attach step). This is the part the bundle automates.
4. Schedule the post.

So this skill outputs the thumbnail **brief plus the attach instructions**, not a
one-call thumbnail upload. If you do not have a tracked `{mediaId, url}` yet, ship
the video without the custom thumbnail and set it in YouTube Studio.

Constraints: the channel must be **verified**; the apply is **best-effort** (a
rejected thumbnail does not block the video, it just ships without the custom
one); and you cannot change the thumbnail while the post is `processing`.

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- Text overlay is 4 words or fewer, and never repeats the title's words.
- One focal point per concept. Two competing subjects halve the click.
- The emotion on a face must match the video. A shocked face on a calm tutorial
  is a broken promise the retention graph punishes.
- Every concept must pass the 120-pixel mobile read test.
- Always produce 2 to 3 concepts, each varying one big element.

## Anti-patterns (skill will refuse)

- Repeating the full title as the thumbnail text.
- A face with a fake exaggerated expression that the video does not earn.
- A busy collage with no single focal point.
- Tiny text or full sentences that vanish at 120 px.
- A thumbnail showing a moment that is not in the video.
- Em dashes in any overlay text.

## Resources

- `../../references/thumbnail-principles.md` - the full design language and the upload flow
- `../../references/algorithm-heuristics.md` - packaging, CTR, Test & Compare
- `references/brief-template.md` - the fill-in brief a designer or image tool can execute

## Related skills

- `yt-title-optimizer` - the other half of the click; build them as a pair
- `yt-hook-scripter` - the spoken open should match the thumbnail's emotion
- `yt-content-planner` - pair titles and thumbnails across a week
