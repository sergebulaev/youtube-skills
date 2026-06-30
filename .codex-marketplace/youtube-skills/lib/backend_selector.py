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
