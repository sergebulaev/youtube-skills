---
name: youtube-marketing
description: Plan, write, and publish for YouTube and YouTube Shorts. Use when the user wants high-CTR video titles, an SEO description with chapters and links, a first-30-seconds retention script (or a 3-second Shorts hook), a designer-ready thumbnail brief, a community-tab post or poll, or a weekly upload plan. The user supplies the video; the skills produce the title, description, hook, and thumbnail brief, then on approval upload and schedule via the Publora API.
---

# YouTube Marketing Skills

A bundle of 6 focused skills for YouTube content ops in 2026, covering both
long-form and YouTube Shorts. Each skill is single-purpose, follows the draft
then approval then publish pattern, and uses the [Publora API](https://publora.com)
for uploading and scheduling the video you supply.

## When to use this bundle

- **Writing high-CTR titles** (curiosity, number, how-I, comparison) with A/B variants -> use `yt-title-optimizer`
- **Writing the description** (first-150-char hook, chapters, keywords, links) -> use `yt-description-writer`
- **Scripting the first 30 seconds for retention** (or the first 3 seconds of a Short) -> use `yt-hook-scripter`
- **Briefing a thumbnail** (text overlay, face/emotion, contrast) plus the upload flow -> use `yt-thumbnail-brief`
- **Writing a community-tab post or poll** -> use `yt-community-post-writer`
- **Planning a week of uploads** (long-form vs Shorts mix, title/thumbnail pairing) -> use `yt-content-planner`

## Core pattern

Every action-taking skill follows three steps:

1. **Parse the input.** If the user gives a YouTube URL, the skill uses
   `lib/url_parser.py` to extract the video id, Short id, channel, or handle.
2. **Draft the content.** The skill applies 2026 research (title and hook
   formulas, CTR x retention heuristics, thumbnail principles, voice rules) and
   shows the draft to the user.
3. **Wait for approval.** The user replies "publish", "yes", or suggests edits.
   Only after explicit approval does the skill upload and schedule via Publora.

## Why YouTube is video-first (read this once)

YouTube is a **video-only platform**: every published post requires a single
video file, which the user supplies. The skills write the title, description,
hook script, and thumbnail brief; you bring the .mp4. On approval the upload
follows the documented Publora flow:

1. `create-post` with no scheduledTime -> creates a **draft**, returns a `postGroupId`
2. `get-upload-url` -> a pre-signed S3 URL
3. PUT your video to S3
4. `update-post/:postGroupId` -> set the scheduledTime (and any youtube settings)

A custom thumbnail is set **after** the draft exists, via `update-post` (the
thumbnail upload needs the `postGroupId`), never on `create-post`. YouTube
community-tab posts have no Publora endpoint, so `yt-community-post-writer`
always returns a copy-paste block.

## Prerequisites

**Three tiers - pick one.**

### Tier 0 - Draft only (default, no setup)

The skills work out of the box. No API keys, no signup. Every approved draft is
returned as a copy-paste block (title + description, hook script, thumbnail
brief, or community post) for you to use in YouTube Studio. Great for trying the
skills before committing to any backend.

### Tier 1 - Publora auto-upload (recommended, ~2 min)

On approval, the writer skills upload and schedule the video you supply via the
[Publora API](https://publora.com).

1. Sign up free: **https://app.publora.com/signup**
2. Connect your YouTube channel in Publora (Channels then Add Channel, Google OAuth)
3. Copy your API key from Publora's API panel
4. Drop into `.env`:
   ```
   PUBLORA_API_KEY=sk_...
   YOUTUBE_PLATFORM_ID=youtube-UC...
   ```
5. Run `pip install -r requirements.txt`

Why Publora: uploading to YouTube on the native Data API means a Google OAuth
flow, the resumable-upload protocol, and quota tracking. Publora does the draft,
the S3 upload, the schedule, and the metadata in a handful of REST calls. We
built on top of it so we did not have to reimplement the upload chain.

### Tier 2 - Build your own uploader (advanced)

Prefer not to SaaS it? Ask Claude Code or Codex to build a custom uploader on the
YouTube Data API. Set `YOUTUBE_SKILLS_CUSTOM_POSTER=<your command>` and the
skills invoke it on approval. Publora is the 2-minute path.

### Note on community posts

YouTube community-tab posts and polls have no Publora endpoint, and there is no
public API for them. So `yt-community-post-writer` always returns its draft as a
copy-paste block for you to post in the Community tab yourself. Videos and Shorts
upload and schedule through Publora normally.

## Voice rules (baked into every skill)

1. No em dashes (`—`), en dashes, or double dashes. Biggest AI tell.
2. Use `..` as a soft pause in a script line when rhythm calls for it.
3. Capitalize all personal, company, and product names.
4. Specific numbers beat adjectives. "in 28 days" beats "fast".
5. Title is a promise, not a summary. Curiosity plus a concrete payoff.
6. Title and thumbnail are a pair. They never repeat the same words.
7. The first 30 seconds (or 3 on a Short) is the real algorithm. No intro.
8. Title caps at 100 chars (sweet spot 40 to 60). Description caps at 5,000, first 150 visible.
9. Avoid AI vocabulary: `leverage`, `fundamentally`, `streamline`, `harness`, `delve`, `unlock`, `foster`.
10. Do not keyword-stuff. Natural language with the real search phrase once.

(Canonical reference: `references/voice-rules.md`. See also
`references/hook-formulas.md`, `references/algorithm-heuristics.md`, and
`references/thumbnail-principles.md`.)

## How YouTube URLs map

| URL shape | Parsed to |
|---|---|
| `https://www.youtube.com/watch?v=VIDEO_ID` | video_id, type `video` |
| `https://youtu.be/VIDEO_ID` | video_id, type `video` |
| `https://www.youtube.com/shorts/VIDEO_ID` | video_id, `is_short: true`, type `short` |
| `https://www.youtube.com/@handle` | handle, type `channel` |
| `https://www.youtube.com/channel/UC...` | channel_id, type `channel` |

`lib/url_parser.parse_youtube_url(url)` returns `{video_id, handle, channel_id,
is_short, url_type, canonical_url}`.

## Known gotchas

- **A video is required.** A text-only YouTube post is accepted by `create-post`
  but fails at publish with `VIDEO_REQUIRED`. Always use the draft -> upload ->
  schedule flow. The exception is a community post, which is not a video upload
  (and has no endpoint, so it is copy-paste).
- **Title defaults to empty.** If you do not set `platformSettings.youtube.title`,
  YouTube derives one from the first 70 chars of the content. Always set it.
- **Content becomes the description.** The `content` you pass is the video
  description; the `title` is separate in `platformSettings`.
- **Thumbnail needs a postGroupId.** It cannot be set on `create-post`. Create
  the draft, upload the thumbnail (verified channel, JPEG/PNG <= 2 MB), then
  `update-post`. The apply is best-effort: a rejected thumbnail does not block
  the video.
- **Publora caps uploads at 512 MB** even though YouTube natively allows far
  larger. Compress or use the dashboard for bigger files.
- **CTR is only half the product.** A title that over-promises and loses the
  first 30 seconds is punished harder than a modest title. Pair every title with
  a hook that keeps it.

## Resources

- [Publora API docs](https://docs.publora.com) - endpoint reference for the publishing layer
- `lib/publora_client.py` - Python client (create-post, get-upload-url, update-post, connections)
- `lib/url_parser.py` - YouTube video / Short / channel URL parser

## Acknowledgments

Publishing powered by the [Publora REST API](https://publora.com).
