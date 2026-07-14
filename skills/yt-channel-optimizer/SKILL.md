---
name: yt-channel-optimizer
description: Audit and rewrite a YouTube channel end-to-end for 2026: name and @handle, banner (2560x1440 with the 1235x338 mobile/TV safe area), profile picture, About plus searchable keywords, trailer for non-subscribers vs featured video for subscribers, sections and playlist layout, watermark, links. Triggers on "optimize my YouTube channel", "rewrite my channel about", "fix my banner", "channel audit", "set my trailer". Converts a viewer into a subscriber. Not for writing a video title (use yt-title-optimizer).
---

# YouTube Channel Optimizer

Audit the parts of a YouTube channel page against what actually converts a
one-time video-viewer into a subscriber in 2026, then rewrite each part that
needs it. A viewer clicks through from one video to the channel page in a moment
of interest. That moment decides whether they subscribe or leave. This skill
fixes the page so the answer is subscribe.

## When to use

- User pastes their channel URL or @handle and asks for an audit
- "Rewrite my channel About", "fix my banner", "set my trailer"
- A channel with real videos but a default or empty channel page
- Any of: "optimize my YouTube channel", "channel audit", "what trailer should I set"

Not for writing a single video's title (use `yt-title-optimizer`), the video
description (use `yt-description-writer`), or the thumbnail overlay (use
`yt-thumbnail-brief`).

## Input

- Channel URL / @handle (or a screenshot of the channel home tab, signed out)
- Goal: **more subscribers** / **more views** / **authority** / **sales** - the
  trailer, About CTA, and section order change by goal
- Optional: their best-performing videos, to pick a trailer and featured video
- Note whether the channel already has 3+ playlists to lay out

## Output

1. **Scorecard** (parts, pass / needs-work / fail)
2. **Priority fixes** ranked by impact (trailer, banner, and About first)
3. **Before -> After** rewrites for each failing part
4. **Trailer + featured-video picks** with the reason for each
5. **Section-order recommendation** matched to the goal

## Steps

1. **Intake.** Collect the channel state + goal. View the channel home tab both
   **signed out** (non-subscriber sees the trailer) and as a subscriber (sees the
   featured video). The two audiences see different things; audit both.
2. **Score the parts** against the scorecard below.
3. **Fix the channel name + @handle.** Name is a real name or brand plus a
   searchable topic ("Sam Rivera - AI Tools"). The @handle is short, memorable,
   no numbers if avoidable. The name field is searchable; set it with intent.
4. **Rewrite the About + keywords.** First 2 lines carry the value prop (they show
   in the sidebar preview). Structure: who the channel is for, what they get, how
   often, one proof. Weave the real search phrases people type into natural
   sentences; do not keyword-stuff. Add business email and links.
5. **Set the channel trailer (non-subscribers).** A 30-to-90-second pitch: who you
   are, what the channel delivers, why subscribe now. This is the single highest-
   leverage slot for subscriber conversion. Not a random recent upload.
6. **Set the featured video (subscribers).** Returning subscribers see this
   instead. Use your best recent video or the one you want watched next, matched
   to the goal (a launch, a flagship, a series opener).
7. **Lay out featured sections + playlists.** Group videos into 3+ named playlists
   by topic or series, then arrange them as sections. Playlists lift session
   watch time (autoplay into the next video) and tell a new visitor what the
   channel is about at a glance. Order sections by the goal: lead with the series
   that converts, not "Uploads" by default.
8. **Order the sections.** Trailer/featured first, then the strongest playlist,
   then popular uploads. Bury generic "Recent uploads" below the curated rows.
9. **Banner check (2560x1440).** Design inside the **1235x338 centered safe area**
   so it reads on mobile and TV where the edges crop. One line of value prop +
   upload cadence ("New AI builds every Tuesday"), high contrast, not a busy
   collage. It reinforces the About, it does not repeat it.
10. **Profile picture check.** Clear face or clean logo, high contrast, recognizable
    at the small circle size it renders at across watch pages and search.
11. **Watermark + links.** Set a branded watermark (a subscribe-prompt or logo)
    that shows on every video for one-click subscribe. Add the goal-matched links
    (site / newsletter / offer) to the banner link row; one primary link wins.
12. **Deliver the before/after diff** + the one-visit test: a stranger who clicks
    through from a single video should, from the trailer + banner + About alone,
    know what they get by subscribing and want to.

## Channel scorecard

| # | Part | Pass criteria (2026) |
|---|------|----------------------|
| 1 | **Channel name + @handle** | Real name or brand + a searchable topic; @handle short and memorable, no stray numbers |
| 2 | **Banner (2560x1440)** | Value prop + cadence inside the 1235x338 mobile/TV safe area, high contrast, readable small |
| 3 | **Profile picture** | Clear face or clean logo, high contrast, recognizable at small circle size |
| 4 | **About + keywords** | First 2 lines carry the value prop; who/what/cadence/proof; real search phrases in natural sentences, no stuffing |
| 5 | **Channel trailer** | Present, 30 to 90s, a made-for-non-subscribers pitch matched to the goal, not a random upload |
| 6 | **Featured video** | Present, the best or most goal-relevant video for returning subscribers |
| 7 | **Sections + playlists** | 3+ named playlists laid out as sections, curated rows above generic uploads |
| 8 | **Section order** | Trailer/featured first, converting playlist next, "Recent uploads" buried below |
| 9 | **Watermark** | Branded subscribe-prompt watermark set on every video |
| 10 | **Links** | One goal-matched primary link in the banner row; extras only if they earn the slot |

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- Audit the channel page as **both** a non-subscriber (trailer) and a subscriber
  (featured video). They are two different first impressions.
- The banner must be designed inside the **1235x338 safe area** centered in the
  2560x1440 canvas. Anything outside it is cropped on mobile and TV. Never put the
  value prop near the edges.
- The trailer is the highest-leverage slot for subscriber conversion. A channel
  with no trailer leaves that slot empty; always recommend setting one.
- First 2 lines of the About carry the whole value prop (they show in the preview
  before "more"). Lead with the viewer's benefit, not a mission statement.
- Real search phrases in natural sentences. Never a comma-separated keyword dump.
- One primary link. A wall of links dilutes the click.
- No em dashes. No "leverage", "fundamentally", "unlock".

## Related skills

- `yt-title-optimizer` - title the videos the optimized channel will host
- `yt-thumbnail-brief` - design the thumbnails the channel grid shows
- `yt-description-writer` - the per-video SEO description and chapters
- `yt-content-planner` - plan the upload cadence the banner promises
