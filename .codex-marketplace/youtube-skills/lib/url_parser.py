"""YouTube URL parser.

Handles the common shapes for videos, Shorts, channels, and handles:

1. Long-form watch URL:
   https://www.youtube.com/watch?v=VIDEO_ID
   https://youtube.com/watch?v=VIDEO_ID&t=42s
   https://m.youtube.com/watch?v=VIDEO_ID

2. Short link:
   https://youtu.be/VIDEO_ID
   https://youtu.be/VIDEO_ID?si=...

3. Shorts:
   https://www.youtube.com/shorts/VIDEO_ID

4. Embed / live:
   https://www.youtube.com/embed/VIDEO_ID
   https://www.youtube.com/live/VIDEO_ID

5. Channel:
   https://www.youtube.com/@handle
   https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxx
   https://www.youtube.com/c/CustomName
   https://www.youtube.com/user/LegacyName

Returns a normalized dict:
    {
      "video_id": "<11-char id>" | None,
      "handle": "<@-less handle>" | None,
      "channel_id": "UC..." | None,
      "is_short": True | False,
      "url_type": "video" | "short" | "channel" | "unknown",
      "canonical_url": "https://www.youtube.com/..." | None,
    }

Note: a YouTube video id is the canonical 11-char base64url token. Shorts share
the same id space as regular videos; `is_short` records which surface the URL
pointed at (it affects how the hook-scripter and content-planner treat it).
"""
from __future__ import annotations
import re
from typing import Optional, TypedDict


class ParsedYouTubeUrl(TypedDict, total=False):
    video_id: Optional[str]
    handle: Optional[str]
    channel_id: Optional[str]
    is_short: bool
    url_type: str
    canonical_url: Optional[str]


_VIDEO_ID = r"[A-Za-z0-9_-]{11}"

# watch?v=ID
_WATCH_RE = re.compile(
    r"(?:https?://)?(?:[\w.]+\.)?youtube\.com/watch\?(?:[^ ]*&)?v=(?P<id>" + _VIDEO_ID + r")",
    re.IGNORECASE,
)
# youtu.be/ID
_SHORTLINK_RE = re.compile(
    r"(?:https?://)?youtu\.be/(?P<id>" + _VIDEO_ID + r")",
    re.IGNORECASE,
)
# /shorts/ID
_SHORTS_RE = re.compile(
    r"(?:https?://)?(?:[\w.]+\.)?youtube\.com/shorts/(?P<id>" + _VIDEO_ID + r")",
    re.IGNORECASE,
)
# /embed/ID  or  /live/ID  or  /v/ID
_EMBED_RE = re.compile(
    r"(?:https?://)?(?:[\w.]+\.)?youtube\.com/(?:embed|live|v)/(?P<id>" + _VIDEO_ID + r")",
    re.IGNORECASE,
)
# /@handle
_HANDLE_RE = re.compile(
    r"(?:https?://)?(?:[\w.]+\.)?youtube\.com/@(?P<handle>[A-Za-z0-9._-]+)",
    re.IGNORECASE,
)
# /channel/UCxxxx
_CHANNEL_RE = re.compile(
    r"(?:https?://)?(?:[\w.]+\.)?youtube\.com/channel/(?P<cid>UC[A-Za-z0-9_-]{22})",
    re.IGNORECASE,
)
# /c/Name  or  /user/Name
_CUSTOM_RE = re.compile(
    r"(?:https?://)?(?:[\w.]+\.)?youtube\.com/(?:c|user)/(?P<name>[A-Za-z0-9._-]+)",
    re.IGNORECASE,
)


def parse_youtube_url(url: str) -> ParsedYouTubeUrl:
    """Parse any YouTube video, Short, or channel URL into structured fields.

    >>> p = parse_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s")
    >>> p["video_id"]
    'dQw4w9WgXcQ'
    >>> p["url_type"]
    'video'
    >>> parse_youtube_url("https://www.youtube.com/shorts/abc123XYZ_-")["is_short"]
    True
    """
    out: ParsedYouTubeUrl = {
        "video_id": None,
        "handle": None,
        "channel_id": None,
        "is_short": False,
        "url_type": "unknown",
        "canonical_url": None,
    }
    if not url:
        return out
    text = url.strip()

    m = _SHORTS_RE.search(text)
    if m:
        vid = m.group("id")
        out["video_id"] = vid
        out["is_short"] = True
        out["url_type"] = "short"
        out["canonical_url"] = f"https://www.youtube.com/shorts/{vid}"
        return out

    for rx in (_WATCH_RE, _SHORTLINK_RE, _EMBED_RE):
        m = rx.search(text)
        if m:
            vid = m.group("id")
            out["video_id"] = vid
            out["url_type"] = "video"
            out["canonical_url"] = f"https://www.youtube.com/watch?v={vid}"
            return out

    m = _CHANNEL_RE.search(text)
    if m:
        cid = m.group("cid")
        out["channel_id"] = cid
        out["url_type"] = "channel"
        out["canonical_url"] = f"https://www.youtube.com/channel/{cid}"
        return out

    m = _HANDLE_RE.search(text)
    if m:
        handle = m.group("handle")
        out["handle"] = handle
        out["url_type"] = "channel"
        out["canonical_url"] = f"https://www.youtube.com/@{handle}"
        return out

    m = _CUSTOM_RE.search(text)
    if m:
        out["handle"] = m.group("name")
        out["url_type"] = "channel"
        out["canonical_url"] = out["canonical_url"] or f"https://www.youtube.com/c/{m.group('name')}"
        return out

    # Bare 11-char video id with no host.
    if re.fullmatch(_VIDEO_ID, text):
        out["video_id"] = text
        out["url_type"] = "video"
        out["canonical_url"] = f"https://www.youtube.com/watch?v={text}"
        return out

    return out


def build_watch_url(video_id: str) -> str:
    """Format a canonical watch URL from a video id."""
    return f"https://www.youtube.com/watch?v={video_id}"


def build_shorts_url(video_id: str) -> str:
    """Format a canonical Shorts URL from a video id."""
    return f"https://www.youtube.com/shorts/{video_id}"


if __name__ == "__main__":
    import json
    import sys

    examples = sys.argv[1:] or [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
        "https://youtu.be/dQw4w9WgXcQ?si=abc",
        "https://www.youtube.com/shorts/abc123XYZ_-",
        "https://www.youtube.com/@mkbhd",
        "https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ",
    ]
    for u in examples:
        print(u)
        print(json.dumps(parse_youtube_url(u), indent=2))
        print()
