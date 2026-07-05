# Thumbnail Principles - 2026

The thumbnail is half of the click. It is read in under a second, at roughly
120 pixels wide on a phone, next to a dozen competitors. This reference is the
shared design language the `yt-thumbnail-brief` skill turns into a brief a
designer (or an image tool) can execute. It is principles, not a Photoshop
manual.

## Contents

- The one job
- The five non-negotiables
- Title and thumbnail are a pair
- Composition cues
- Text rules
- Faces
- Shorts thumbnails
- Consistency vs novelty
- A/B testing
- The brief the skill produces
- The update-post thumbnail flow (when auto-publishing)

## The one job

A thumbnail's only job is to make the right viewer stop and click, then have the
video honor that click. It is not decoration and it is not a summary. It is a
visual promise that complements the title.

## The five non-negotiables

1. **One focal point.** A single subject the eye lands on instantly. Two competing
   subjects halve the impact. If there is a face, it is usually the focal point.
2. **A legible emotion.** A human face with a clear, real expression (surprise,
   focus, dismay, delight) out-clicks a neutral or a logo. The emotion should
   match the video's actual feeling, not a fake open mouth.
3. **High contrast and separation.** The subject must pop off the background.
   Use a rim light, a blurred or darkened background, or a bold color the
   competitors are not using. It has to survive being shrunk to a sidebar.
4. **At most 3 to 4 words of text**, and words the title does NOT also say. Big,
   legible, high-contrast type. The text adds the angle the image cannot show.
5. **Reads at 120 pixels.** Before approving anything, shrink it to thumbnail
   size on a phone. If you cannot tell what it is, it fails, no matter how good
   it looks at full size.

## Title and thumbnail are a pair

The single biggest waste is a thumbnail that repeats the title in words. They are
seen together. Split the load:

| The title says | The thumbnail shows |
|---|---|
| the context, the number, the search phrase | the face, the emotion, the result |
| "How I edited this in 3 days" | the exhausted face + the finished frame |
| "7 tricks that doubled retention" | the retention graph spiking + a shocked face |

If the title already has the words, the thumbnail does not need them. Use the
thumbnail's 3 to 4 words for the angle the title left out.

## Composition cues

- **Rule of thirds.** Put the face or focal subject off-center, text on the
  opposite side. A centered face with text underneath reads as a template.
- **Direction of gaze.** A subject looking at the text or the object pulls the
  viewer's eye there too.
- **Foreground / background depth.** A sharp subject on a softened background
  creates the separation that survives shrinking.
- **Color contrast over color matching.** Pick a dominant color that contrasts
  with both the subject and what is trending in your niche's feed. Reds, yellows,
  and cyans pop; muted earth tones disappear in the feed.
- **Negative space is allowed.** A clean thumbnail with one subject and breathing
  room often beats a busy collage. Clutter reads as noise at 120 px.

## Text rules

- 3 to 4 words maximum. One idea.
- Heavy weight, large size, high contrast, with an outline or drop shadow so it
  survives any background.
- Never the same words as the title.
- No full sentences, no paragraphs, no tiny captions the eye cannot read at
  thumbnail size.
- One emphasized word in a contrasting color is a strong pattern.

## Faces

- A real human face with a genuine, specific emotion is the highest-performing
  thumbnail element for most channels.
- The expression must match the video. A shocked face on a calm tutorial is a
  broken promise the retention graph will punish.
- Close crop: eyes and mouth are the signal. A tiny face in a wide shot loses at
  120 px.
- Faceless channels lean harder on the result, the object, or a bold text-and-
  contrast design.

## Shorts thumbnails

- Shorts are mostly consumed in the vertical feed where the thumbnail barely
  shows, so the **first video frame doubles as the thumbnail**. Make frame one
  arresting on its own.
- On the channel's Shorts shelf and search, a vertical thumbnail does show, so a
  bold vertical-safe focal point still helps. Keep text clear of the bottom UI
  overlay.

## Consistency vs novelty

- A recognizable thumbnail style (consistent color, framing, or face treatment)
  trains your audience to spot and click you on the home feed.
- But novelty inside that style wins each individual click. The frame is
  consistent; the subject and emotion are fresh every time.

## A/B testing

- Always produce **2 to 3 thumbnail concepts**, not one. YouTube's native
  "Test & Compare" rotates up to three and reports the winner by watch-time
  share, not raw CTR, which is the right metric.
- Vary one big thing between concepts (face vs object, text vs no text, color),
  not five small things, so the test tells you something.

## The brief the skill produces

For each video the `yt-thumbnail-brief` skill outputs a brief a human designer or
an image tool can execute:

- **Concept name and the angle** it sells (and how it complements the title).
- **Focal subject** (face + which emotion, or the object / result).
- **Text overlay**: the exact 3 to 4 words, and where they sit.
- **Background and contrast** direction (color, lighting, separation).
- **Composition** (rule-of-thirds placement, gaze direction, crop).
- **The 120-pixel test note**: what must still read when shrunk.
- **2 to 3 variants** for Test & Compare, each varying one big element.

## The update-post thumbnail flow (when auto-publishing)

A custom thumbnail is applied to a Publora-tracked media asset, and it cannot be
attached on `create-post` because the upload needs a `postGroupId` first. The
order is:

1. Create the video post as a **draft** (`create-post`, no scheduledTime).
2. Upload the thumbnail image (JPEG or PNG, max 2 MB, 1280x720 recommended)
   through Publora's dedicated YouTube thumbnail upload, which requires the
   `postGroupId` and returns a `mediaId` and `url`.
3. Call `update-post` with `platformSettings.youtube.thumbnail = {mediaId, url}`.
4. Schedule the post.

Constraints to know: the channel must be **verified**, the apply step is
best-effort (if YouTube rejects the image the video still publishes without the
custom thumbnail), and you cannot change the thumbnail while the post is already
`processing`. In draft-only mode, the skill hands you the brief and you upload
the thumbnail in YouTube Studio yourself.
