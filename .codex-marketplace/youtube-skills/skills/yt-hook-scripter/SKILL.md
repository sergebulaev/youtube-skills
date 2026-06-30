---
name: yt-hook-scripter
description: Script the spoken opening that decides retention: the first 30 seconds of a long-form YouTube video or the first 3 seconds of a YouTube Short. Uses 2026 patterns (restate-and-raise, cold-open payoff tease, question-and-contract, and the 3-second frame-one Shorts hook with a designed loop) to confirm the title's promise, open a loop, and earn the next 30 seconds with no intro. Use to write or fix a video opening. Not for the title (use yt-title-optimizer) or description (use yt-description-writer).
---

# YouTube Hook Scripter

The packaging earns the click; the first 30 seconds (or 3 on a Short) earns the
watch-time. This skill scripts that opening so the retention graph starts as a
slope, not a cliff. It writes the words you say on camera, not the metadata.

## When to use

- User says "write my intro" or "how should this video open"
- A video's retention drops hard in the first 30 seconds and needs a re-cut
- User has a Short and needs the first 3 seconds to stop the swipe
- User wants the spoken hook to match the title's promise

## Formulas this skill uses (opening-hook shapes)

| Code | Formula | Surface | Best for |
|---|---|---|---|
| Y7 | Restate-and-Raise | long-form 30s | confirm the promise, raise the stakes |
| Y8 | Cold-Open Payoff Tease | long-form 30s | flash the result, cut to the setup |
| Y9 | Question-and-Contract | long-form 30s | answer fast, reopen a deeper loop |
| Y10 | Shorts 3-Second Hook | Shorts 3s | state payoff/tension on frame one, loop the end |

Full skeletons in `../../references/hook-formulas.md`.

## Steps

1. **Gather inputs.** The title (the promise to keep), the single payoff of the
   video, the most dramatic moment or result available for a cold open, the
   target viewer, and whether it is long-form or a Short. If a URL is given,
   parse it with `lib/url_parser.py`; `is_short` decides the surface.
2. **Pick the surface.**
   - Long-form: write the first 30 seconds, beat by beat, with rough timestamps.
   - Short: write the first 3 seconds (frame one), then the line that makes the
     ending loop back to the start.
3. **Pick the formula.** Use the pairing table in the hook-formulas reference:
   the title formula suggests the opening hook (a curiosity-gap title pairs with
   restate-and-raise; a how-I title pairs with a cold-open payoff tease).
4. **Write the script.** Spoken voice, one person to one person. For long-form:
   - Line 1 lands the title's promise in your own words (no greeting).
   - Line 2 raises the stakes or names the obstacle (opens the loop).
   - Line 3 makes the watch-contract ("by the end you will..").
   - Note where B-roll, a cold-open clip, or on-screen text goes.
   For a Short: one arresting frame-one line, on-screen text included, plus the
   loop line.
5. **Strip the intro.** Cut any "welcome back", logo sting, or channel-trailer
   reflex. The hook is the first thing the viewer hears.
6. **Humanizer pass.** Remove AI vocabulary, em dashes, and rule-of-three; use
   `..` for a spoken pause instead of a dash.
7. **Approval card.** Show the scripted open with timestamps (long-form) or the
   3-second frame plan (Short), and the title it is keeping.
8. **On approval.** This is a script the user performs; it is not published by
   itself. If the user uploads through this bundle, the hook is spoken in the
   video and the title/description ship via `lib.publish(...)`.

## Hard rules

Global voice rules: see root `SKILL.md` Voice rules. Additional skill-specific
rules:

- No greeting, no intro animation, no logo sting before the hook. Ever.
- Long-form: the promise from the title is restated in the first 1 to 2 spoken
  lines, then a loop is opened. Earn the next 30 seconds by the 30-second mark.
- Short: the payoff or tension lands on frame one (second 0 to 1), with on-screen
  text so it works muted. Design the ending to loop back to the start.
- The opening can never promise more than the video delivers. Honor the click.
- Use `..` for a spoken pause, never an em dash (it leaks into a teleprompter).

## Anti-patterns (skill will refuse)

- "Hey guys, welcome back to the channel" or any greeting in the open.
- A 15-second intro animation before the first word of value.
- A cold open that teases a moment not actually in the video.
- "Make sure to like and subscribe" inside the first 30 seconds.
- Em dashes in a line meant to be read aloud.
- A Short that opens with a slow zoom or a logo instead of the payoff.

## Resources

- `../../references/hook-formulas.md` - Y7-Y10 opening-hook skeletons and the title pairing
- `../../references/algorithm-heuristics.md` - the first-30-seconds and 3-second retention rules
- `references/retention-beats.md` - the beat-by-beat opening structure for long-form and Shorts

## Related skills

- `yt-title-optimizer` - the promise the hook keeps
- `yt-thumbnail-brief` - the emotion the open should match
- `yt-description-writer` - the written hook (different surface from the spoken one)
