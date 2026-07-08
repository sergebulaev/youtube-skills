---
name: yt-community-post-writer
description: Write YouTube community-tab posts: text updates, polls, image-caption posts, and questions that drive comments and bring subscribers back between video uploads. Tuned to the community tab's role as a low-friction touchpoint that keeps a channel warm and feeds session signals. Returns a copy-paste block (community posts have no publishing API, so this is always manual by design). Use to write a community post or poll. Not for video titles or descriptions (use yt-title-optimizer and yt-description-writer).
---

# YouTube Community Post Writer

The community tab is the channel's between-uploads touchpoint. A good post keeps
subscribers engaged, seeds comments, and warms the audience for the next video.
This skill writes those posts and polls.

## When to use

- User says "write a community post" or "make a poll for my channel"
- User wants to tease, build hype for, or follow up on a video
- User wants to keep the channel active between uploads
- User wants a poll to source ideas or settle a debate with the audience

## Why this is always copy-paste

YouTube community posts and polls have **no Publora endpoint and no public
publishing API**. So this skill always returns a finished post as a copy-paste
block for you to publish in the Community tab yourself. That is by design, not a
limitation of the draft tier. (Videos and Shorts do auto-upload through Publora.)

## Post types this skill writes

| Type | Best for |
|---|---|
| **Text update** | a quick thought, a tease, a behind-the-scenes note |
| **Poll** | sourcing ideas, settling a debate, low-effort engagement |
| **Image + caption** | a teaser frame, a before/after, a result screenshot |
| **Question prompt** | a direct ask that fills the comments |

## Steps

1. **Gather inputs, goal first.** Ask (or infer) what the post should earn
   before picking a format, then map goal to format: tease a video -> image or
   text teaser with a curiosity gap; source ideas / decide content -> poll;
   follow up on a video -> text post replying to top comments; keep warm
   between uploads -> behind-the-scenes image or quiz. Then gather the topic,
   the channel's voice, and confirm the post type fits the goal. If the post relates
   to a specific video, take the URL and parse it with `lib/url_parser.py`.
2. **Pick the type.** A poll for input or low-effort engagement; a text update
   for a tease or note; an image caption for a visual teaser; a question to drive
   comments.
3. **Write the post.**
   - Lead with the hook; the first line carries it (the community feed truncates).
   - One clear ask: vote, comment a specific thing, or watch the linked video.
   - For a poll: a clear question plus 2 to 4 tight options. No false dilemmas.
   - Keep it short. The community tab rewards low-friction, not essays.
4. **Humanizer pass.** Strip AI vocabulary, em dashes, and rule-of-three. Sound
   like the creator, not a brand account.
5. **Approval card.** Show the post (and poll options) and the target Community
   tab URL.
6. **On approval.** Call `lib.publish(kind="community", draft_text=<post>,
   target_url=<community tab url>)`. The wrapper returns the copy-paste block;
   the user posts it in the Community tab.

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- The first line carries the hook (the community feed truncates long posts).
- One clear ask per post. Two asks split the response.
- Polls: 2 to 4 options, mutually exclusive, no loaded framing.
- Keep it short. A community post is a touchpoint, not a blog.
- No engagement bait ("comment 1 for yes"); ask a real question.

## Anti-patterns (skill will refuse)

- A wall of text where the community tab wants one or two lines.
- Two competing asks in one post.
- A poll with a false dilemma or 6+ options.
- Engagement bait ("like if you agree, comment if you don't").
- Em dashes anywhere.
- "Don't forget to smash subscribe" dead phrasing.

## Resources

- `../../references/voice-rules.md` - the canonical voice rules
- `../../references/algorithm-heuristics.md` - comments and session signals
- `references/post-types.md` - templates for each community post type

## Related skills

- `yt-content-planner` - schedule community posts between uploads
- `yt-title-optimizer` - when the post is teasing a specific video
