---
name: yt-audience-insights
description: Read your YouTube audience from the comments: pull commenters and top comments on any video, surface recurring questions and themes (content ideas), repeat commenters (superfans), sentiment, and which comments to reply to or pin. Also channel stats and niche trending, via the free official YouTube Data API. Triggers on "who commented on my video", "analyze my comments", "audience insights", "trending on YouTube". Not for writing a community post (use yt-community-post-writer).
---

# YouTube Audience Insights

Turn a video's comment section into a read on your audience: who is showing up, what they keep asking, who your repeat fans are, which comments deserve a reply or a pin, and what is working in your niche right now.

One honest limit up front: YouTube keeps the list of who **liked** a video private (only the aggregate count is public). So the engagement signal here is **commenters**, not likers. On YouTube the comment section is the richer signal anyway: it carries the questions, the objections, and the content ideas.

## When to use

- "Who commented on my video / analyze my comments"
- "What are people asking me / what should my next video be"
- "Who are my repeat viewers"
- "What is trending in [niche] on YouTube right now"

Not for drafting a community post (use `yt-community-post-writer`) or writing a title (use `yt-title-optimizer`).

## Setup (free, optional)

The read layer uses the official **YouTube Data API v3**, which is free: enable it at `https://console.cloud.google.com/apis/library/youtube.googleapis.com`, create an API key, and set `YOUTUBE_API_KEY`. Free quota is 10,000 units/day (a comments or stats call is 1 unit) which covers ~100,000 comments a day.

No key yet? Paste the comments (or a CSV export) and the skill runs the same analysis on what you give it.

## Input

- A video URL (or your channel, for a recent-videos sweep)
- Optional: the goal (content ideas / community management / competitor scan)

## Output

1. **Audience snapshot** - commenter count, top comments by likes, reply-worthy questions
2. **Themes** - the recurring questions and topics, ranked (each is a next-video candidate)
3. **Superfans** - repeat commenters across your recent videos, worth a reply by name
4. **Action list** - which comments to reply to, which to pin, which to turn into a video
5. **Niche pulse** (optional) - what is trending in your category right now

## Steps

1. **Load the comments.** Call `lib.YouTubeClient().fetch_video_comments(video_url, max_results=100, order="relevance")`. Falls back to pasted comments if no key.
2. **Rank the top comments.** Sort by like_count and reply_count. The high-like comments are what the room agrees with; the high-reply ones are where the conversation is.
3. **Extract themes.** Cluster the comments into recurring questions and topics. Each distinct question that shows up 3+ times is a content idea, name it as a potential title.
4. **Find superfans.** Pull comments across the channel's recent videos (`fetch_channel_stats` for the channel, then per-video comments) and flag authors who appear on multiple videos. These get a reply by name.
5. **Read sentiment.** Group into positive / question / critical. Critical-but-specific comments are the most useful; surface them, do not bury them.
6. **Build the action list.** For each: reply now (a real question with traction), pin (best social proof or a correction), or bank as a video idea. Route reply drafts through the relevant writer.
7. **Optional niche pulse.** `fetch_trending(region_code, category_id)` for what is currently most-popular in the category, as a format and topic scan.
8. **Deliver the report** in the Output shape above, with the raw top comments attached.

## What the read layer exposes

| Method | Returns |
|---|---|
| `fetch_video_comments(video, max_results, order)` | top-level comments: author, channel URL, text, likes, reply count, time |
| `fetch_video_stats(video)` | title, channel, views, likes, comments |
| `fetch_channel_stats(channel)` | subscribers, video count, total views (self or competitor) |
| `fetch_trending(region_code, category_id)` | most-popular videos in a niche (1 quota unit, no search cost) |

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific rules:

- Be honest that this reads **commenters, not likers** (likers are private on YouTube). Do not imply a full engager list.
- Never invent a comment, a count, or a theme. If the data is thin, say so.
- A theme is only a content idea if it actually recurs; do not promote a one-off comment to a trend.
- Respect the free quota: prefer `mostPopular` over `search` (search costs 100 units); batch comment pulls.

## Related skills

- `yt-community-post-writer` - answer a recurring question as a community post
- `yt-hook-scripter` - turn a top question into a video hook
- `yt-content-planner` - feed the extracted themes into a content plan
- `yt-channel-optimizer` - fix the channel the new viewers will land on
