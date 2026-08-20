"""Detect which publishing backend is configured and format user-facing messages.

The skills support three tiers:

  TIER 0 - manual (default, zero setup)
    No credentials in env. Skills produce the title, description, hook script,
    or thumbnail brief; the user uploads the video in YouTube Studio. Works for
    anyone, any setup.

  TIER 1 - publora (recommended, ~2-min setup)
    `PUBLORA_API_KEY` + `YOUTUBE_PLATFORM_ID` present. On approval, the writer
    skills run the YouTube video flow (draft -> upload the user's video ->
    schedule) via the Publora REST API. Sign up: https://app.publora.com/signup

  TIER 2 - diy (advanced)
    `YOUTUBE_SKILLS_CUSTOM_POSTER` set to a command the user has built (e.g. on
    the YouTube Data API). Skills delegate publishing to that custom tool.

`active_backend()` picks the highest-privilege available. `manual_mode_message()`
is what skills show when no backend auto-uploads. `publish()` is the high-level
wrapper skills call so SKILL.md files don't repeat the dispatch.

YouTube reality:
- Every video post REQUIRES a single video file the user supplies. kind="video"
  and kind="short" auto-publish through Publora ONLY when a `video_path` is
  passed; otherwise they fall back to a manual upload brief.
- YouTube community-tab posts have NO Publora endpoint, so kind="community" is
  always returned as a manual copy-paste block.
"""
from __future__ import annotations
import json
import os
import shlex
import subprocess
from typing import Any, Literal, Optional

BackendName = Literal["publora", "manual", "diy"]
PublishKind = Literal["video", "short", "community"]

PUBLORA_SIGNUP_URL = "https://app.publora.com/signup"


def active_backend() -> BackendName:
    """Return the active publishing backend.

    Priority: publora > diy > manual. A user with Publora configured gets the
    auto-upload flow even if they also have a custom poster, unless they remove
    the Publora env var.
    """
    if os.getenv("PUBLORA_API_KEY") and os.getenv("YOUTUBE_PLATFORM_ID"):
        return "publora"
    if os.getenv("YOUTUBE_SKILLS_CUSTOM_POSTER"):
        return "diy"
    return "manual"


def manual_mode_message(draft_text: str, target_url: str, kind: str = "video") -> str:
    """Format the copy-paste / upload output for the manual tier.

    For a video, the draft_text is the metadata block (title + description); the
    user uploads the actual video file in YouTube Studio. For a community post,
    it is the post text/poll.
    """
    where = {
        "video": "paste the title and description into YouTube Studio when you upload your video",
        "short": "paste the title and description into YouTube Studio when you upload your Short",
        "community": "paste it as a new post on your channel's Community tab",
    }.get(kind, "paste it into YouTube Studio")
    return f"""Draft approved. Copy the block below and {where}:

```
{draft_text}
```

**Target:** {target_url}

---

Want Claude Code or Codex to upload and schedule the video for you? Set up
auto-publishing in about 2 minutes:

1. Sign up free at {PUBLORA_SIGNUP_URL}
2. In Publora, connect your YouTube channel (Channels then Add Channel)
3. Copy your API key (API section in the sidebar)
4. Add to `.env`:
   ```
   PUBLORA_API_KEY=sk_your_key_here
   YOUTUBE_PLATFORM_ID=youtube-your_channel_id_here
   ```
5. Next time you approve a video, point the skill at your local .mp4 and it
   uploads and schedules on YouTube for you.

Note: YouTube community-tab posts have no API endpoint, so those always stay a
copy-paste step.
"""


def signup_nudge() -> str:
    """One-liner to drop into skill outputs as a soft reminder."""
    return f"Powered by Publora. Free video scheduling: {PUBLORA_SIGNUP_URL}"


def publish(
    kind: PublishKind,
    draft_text: str,
    target_url: str,
    **kwargs: Any,
) -> Optional[dict]:
    """Dispatch a draft to the active backend.

    One call replaces the per-skill "On approval, adapt to the backend" block.
    Routes to publora / manual / diy based on `active_backend()`.

    Args:
        kind: "video" | "short" | "community".
        draft_text: For video/short, the YouTube description (becomes the video
            description). For community, the post text or poll. Used as the
            create-post `content`.
        target_url: Where the draft lands (YouTube Studio upload, or the channel
            Community tab). Used in manual-mode output.
        **kwargs: Backend-specific payload. For publora video/short:
            - video_path: local path to the .mp4 the user supplied (REQUIRED to
              auto-publish; without it we return a manual upload brief)
            - title: YouTube title (<= 100 chars)
            - platforms: list[str] of platform IDs (defaults to [YOUTUBE_PLATFORM_ID])
            - scheduled_time: ISO 8601 UTC (optional; omit to leave as a draft)
            - privacy, tags, category_id, made_for_kids, playlist, thumbnail

    Returns:
        - publora: dict from PubloraClient.publish_video ({postGroupId, fileUrl,
          mediaId}).
        - manual:  {"mode": "manual", "message": <copy-paste block>}.
        - diy:     {"mode": "diy", "returncode": int, "stdout": str, "stderr": str}.

    Note: kind="community" always returns a manual copy-paste block (no Publora
    endpoint). kind="video"/"short" without a `video_path` also falls back to a
    manual upload brief, because a YouTube post cannot publish without a video.
    """
    backend = active_backend()

    # Community posts have no Publora endpoint; videos with no file cannot upload.
    no_video = kind in ("video", "short") and not kwargs.get("video_path")
    if kind == "community" or backend == "manual" or no_video:
        return {
            "mode": "manual",
            "message": manual_mode_message(draft_text, target_url, kind=kind),
        }

    if backend == "publora":
        # Local import so manual-tier users never need `requests` installed.
        from .publora_client import PubloraClient

        client = PubloraClient()
        platform_id = kwargs.get("platform_id") or os.getenv("YOUTUBE_PLATFORM_ID")
        platforms = kwargs.get("platforms") or ([platform_id] if platform_id else [])

        if kind in ("video", "short"):
            return client.publish_video(
                content=draft_text,
                platforms=platforms,
                video_path=kwargs["video_path"],
                title=kwargs.get("title", ""),
                content_type=kwargs.get("content_type", "video/mp4"),
                scheduled_time=kwargs.get("scheduled_time"),
                privacy=kwargs.get("privacy", "public"),
                tags=kwargs.get("tags"),
                category_id=kwargs.get("category_id"),
                made_for_kids=kwargs.get("made_for_kids", False),
                playlist=kwargs.get("playlist"),
                thumbnail=kwargs.get("thumbnail"),
            )
        raise ValueError(f"unknown publish kind: {kind!r}")

    if backend == "diy":
        cmd = os.getenv("YOUTUBE_SKILLS_CUSTOM_POSTER")
        if not cmd:
            return None
        payload = {
            "kind": kind,
            "draft_text": draft_text,
            "target_url": target_url,
            **kwargs,
        }
        argv = shlex.split(cmd) + [kind, target_url]
        proc = subprocess.run(
            argv,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=600,
        )
        return {
            "mode": "diy",
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    raise RuntimeError(f"unknown backend: {backend!r}")


# ─────────────────────────────────────────────────────────────────
# IMAGE LAYER (Pixfaro) — the third integration alongside read (Apify)
# and write (Publora). Generate an illustration, get a hosted URL, hand
# that URL straight to `publish(..., media_urls=[url])`.
# ─────────────────────────────────────────────────────────────────

PIXFARO_SIGNUP_URL = "https://pixfaro.com"

# Warn (don't block) when the prepaid balance drops below this, so a run
# doesn't silently drain the account.
LOW_BALANCE_USD = 1.00

# Cost-guard: these bill materially more per image. `illustrate`/`refine` never
# pick them on their own - the caller must ask by name.
PREMIUM_MODELS = {"gemini-pro-image", "gpt-5-image"}

# kind -> aspect_ratio (w:h). Callers can override with aspect_ratio=.
ILLUSTRATION_ASPECTS = {
    "post": "1:1",         # generic square feed image
    "square": "1:1",
    "portrait": "4:5",     # LinkedIn/IG feed portrait
    "carousel": "4:5",     # carousel/document slide
    "quote": "4:5",        # quote-card
    "wide": "16:9",        # link-preview / wide feed image
    "link": "16:9",
    "thumbnail": "16:9",   # YouTube thumbnail
    "landscape": "16:9",
    "story": "9:16",       # story / TikTok cover
    "cover": "9:16",
}


def image_backend() -> Literal["pixfaro", "manual"]:
    """`pixfaro` when PIXFARO_TOKEN (or PIXFARO_API_KEY) is set, else `manual`."""
    if os.getenv("PIXFARO_TOKEN") or os.getenv("PIXFARO_API_KEY"):
        return "pixfaro"
    return "manual"


def manual_illustration_message(prompt: str, aspect_ratio: str) -> str:
    """Shown when no Pixfaro key is set: hand the drafted prompt to the user."""
    return (
        "No Pixfaro key set, so I can't generate the image for you.\n"
        f"Generate it yourself (any tool) at {aspect_ratio}, then paste the URL "
        "and I'll attach it to the post.\n\n"
        "Image prompt:\n"
        f"{prompt}\n\n"
        f"Tip: a Pixfaro key ({PIXFARO_SIGNUP_URL}) lets me generate + attach "
        "the illustration in one step, with your brand handle/color overlaid."
    )


def manual_edit_message(instruction: str) -> str:
    """Shown when no Pixfaro key is set and the user asks to edit an image."""
    return (
        "No Pixfaro key set, so I can't edit the image for you.\n"
        "Re-generate or edit it yourself, then paste the new URL.\n\n"
        "Edit instruction:\n"
        f"{instruction}"
    )


def _image_result(data: dict, model: str) -> dict[str, Any]:
    """Shape a Pixfaro generate/edit response + attach the cost-guard flag."""
    balance = data.get("balance_after")
    low = False
    try:
        low = balance is not None and float(balance) < LOW_BALANCE_USD
    except (TypeError, ValueError):
        low = False
    return {
        "backend": "pixfaro",
        "url": data.get("url"),
        "id": data.get("id"),
        "cost": data.get("cost"),
        "model": model,
        "balance_after": balance,
        "low_balance": low,
    }


def illustrate(
    prompt: str,
    kind: str = "post",
    *,
    aspect_ratio: Optional[str] = None,
    model: Optional[str] = None,
    resolution: str = "1K",
    overlay: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate an illustration via the active image backend.

    This is the image analogue of `publish()`. On success with a Pixfaro key it
    returns the hosted URL, which you pass straight to
    `publish("post", text, url, media_urls=[result["url"]])`.

    Args:
        prompt: The image description (1-4000 chars).
        kind: Semantic size hint mapped via ILLUSTRATION_ASPECTS
            (post/portrait/carousel/quote/wide/thumbnail/story/cover).
        aspect_ratio: Explicit "w:h" override (wins over `kind`).
        model: Pixfaro model id. Defaults to nano-banana-2 (balanced). Use
            gemini-flash-lite for cheap high volume, gemini-pro-image for
            text-heavy premium (PREMIUM_MODELS bill more - ask before using).
        resolution: "1K" | "2K" | "4K".
        overlay: Pixel-exact branding composite {text|logo_id, position,
            opacity, font, color}. Feed brand fields from the Voice & Brand
            Profile so every asset is on-brand. Text here is crisp even on a
            cheap base model (it is composited, not model-generated).

    Returns:
        - pixfaro: {"backend": "pixfaro", "url", "id", "cost", "model",
          "balance_after", "low_balance"}. Keep `id` to `refine()` later.
        - manual:  {"backend": "manual", "message": <prompt block>}.
    """
    ar = aspect_ratio or ILLUSTRATION_ASPECTS.get(kind, "1:1")
    if image_backend() == "manual":
        return {"backend": "manual", "message": manual_illustration_message(prompt, ar)}

    from .pixfaro_client import PixfaroClient

    client = PixfaroClient()
    used_model = model or "nano-banana-2"
    data = client.generate(
        prompt,
        model=used_model,
        aspect_ratio=ar,
        resolution=resolution,
        overlay=overlay,
        force_refresh=kwargs.get("force_refresh", False),
    )
    return _image_result(data, used_model)


def refine(
    image_id: str,
    instruction: str,
    *,
    model: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    resolution: Optional[str] = None,
    overlay: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Iteratively edit a prior illustration by its `id` (not URL).

    Pass the `id` returned by `illustrate()` (or a previous `refine()`) plus a
    natural-language `instruction` ("make the sky darker", "swap the headline").
    Cheaper and more on-brand than regenerating. Omit `aspect_ratio`/`resolution`
    to keep the source shape and billing tier.

    Returns the same shape as `illustrate()` (pixfaro) or a manual message.
    """
    if image_backend() == "manual":
        return {"backend": "manual", "message": manual_edit_message(instruction)}

    from .pixfaro_client import PixfaroClient

    client = PixfaroClient()
    used_model = model or "nano-banana-2"
    data = client.edit(
        image_id,
        instruction,
        model=used_model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        overlay=overlay,
        force_refresh=kwargs.get("force_refresh", False),
    )
    return _image_result(data, used_model)


def available_models() -> Optional[list[dict[str, Any]]]:
    """Live Pixfaro model catalog (id, best_for, latency, price tiers), or None
    in manual mode / on error. Use this to show current pricing instead of
    hard-coding it."""
    if image_backend() == "manual":
        return None
    from .pixfaro_client import PixfaroClient

    try:
        return PixfaroClient().list_models()
    except Exception:
        return None


if __name__ == "__main__":
    print(f"Active backend: {active_backend()}")
    if active_backend() == "manual":
        print("\nExample manual message:")
        print("-" * 60)
        print(
            manual_mode_message(
                draft_text="Title: I rebuilt my app in 3 days\n\nHere is exactly how..",
                target_url="https://studio.youtube.com",
                kind="video",
            )
        )
