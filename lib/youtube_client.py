"""YouTube Data API v3 read client for the YouTube Skills project.

The read layer: given a video or channel, pull commenters, top comments,
video/channel stats, and what is trending in a niche. Unlike scraped social
platforms, YouTube exposes this through a free, first-party, stable API, so no
proxies, no cookies, no scraping.

Auth: YOUTUBE_API_KEY env var (or constructor arg). Get one free at
https://console.cloud.google.com -> enable "YouTube Data API v3" -> Create
credentials -> API key. Free quota is 10,000 units/day (a comment or stats call
is 1 unit; search is 100 units), which is ~100,000 comments/day at no cost.

What YouTube does NOT expose (by design): the list of who LIKED a video. Only
aggregate likeCount is public. So the engagement signal here is COMMENTERS, not
likers. That is a platform wall, not a client limitation.

Methods:
  - fetch_video_comments(video, max_results, order) -> top-level comments with
      author, channel URL, text, like count, reply count, timestamp.
  - fetch_video_stats(video) -> title, channel, views/likes/comments.
  - fetch_channel_stats(channel) -> subscribers, video count, total views.
  - fetch_trending(region_code, category_id, max_results) -> most-popular videos
      (1 unit; no search quota cost) for "what is working in my niche".

Caching: in-process LRU (256 entries, 6h TTL). Pass force_refresh=True to
bypass. Retries on transient 429/5xx (3 attempts, exponential backoff + jitter).
"""
from __future__ import annotations
import os
import random
import time
from collections import OrderedDict
from typing import Any, Optional

import requests

API_BASE = "https://www.googleapis.com/youtube/v3"
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
CACHE_MAX_ENTRIES = 256
CACHE_TTL_SECONDS = 6 * 60 * 60
SIGNUP_URL = "https://console.cloud.google.com/apis/library/youtube.googleapis.com"


class YouTubeError(RuntimeError):
    pass


class YouTubeAuthError(YouTubeError):
    """Raised when no API key is configured. Message explains the free path."""


def _retry(attempts: int = 3, base_delay: float = 0.6):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            last: Optional[Exception] = None
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except YouTubeError as e:
                    status = getattr(e, "status", None)
                    if status not in RETRYABLE_STATUSES or i == attempts - 1:
                        raise
                    last = e
                    time.sleep(base_delay * (2 ** i) + random.uniform(0, 0.3))
            if last:
                raise last
        return wrapper
    return decorator


def _extract_video_id(video: str) -> str:
    """Accept a video id, a watch URL, a youtu.be URL, or a shorts URL."""
    v = video.strip()
    if "watch?v=" in v:
        return v.split("watch?v=")[1].split("&")[0]
    if "youtu.be/" in v:
        return v.split("youtu.be/")[1].split("?")[0].split("/")[0]
    if "/shorts/" in v:
        return v.split("/shorts/")[1].split("?")[0].split("/")[0]
    return v  # assume it is already an id


class YouTubeClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 20):
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        self.timeout = timeout
        self._cache: "OrderedDict[str, tuple[float, Any]]" = OrderedDict()

    # ---- internal ----
    def _require_key(self) -> str:
        if not self.api_key:
            raise YouTubeAuthError(
                "No YOUTUBE_API_KEY set. Get one free: enable 'YouTube Data API v3' "
                f"at {SIGNUP_URL}, create an API key, and set YOUTUBE_API_KEY. "
                "Or paste the comments/stats you already have and the skill will "
                "work from that."
            )
        return self.api_key

    def _cache_get(self, key: str):
        hit = self._cache.get(key)
        if hit and (time.time() - hit[0]) < CACHE_TTL_SECONDS:
            self._cache.move_to_end(key)
            return hit[1]
        return None

    def _cache_put(self, key: str, val: Any):
        self._cache[key] = (time.time(), val)
        self._cache.move_to_end(key)
        while len(self._cache) > CACHE_MAX_ENTRIES:
            self._cache.popitem(last=False)

    @_retry()
    def _get(self, endpoint: str, params: dict) -> dict:
        params = {**params, "key": self._require_key()}
        try:
            r = requests.get(f"{API_BASE}/{endpoint}", params=params, timeout=self.timeout)
        except requests.RequestException as e:
            err = YouTubeError(f"network error calling {endpoint}: {e}")
            err.status = 503
            raise err
        if r.status_code == 403 and "quota" in r.text.lower():
            raise YouTubeError("YouTube API daily quota exceeded (resets midnight PT).")
        if r.status_code >= 400:
            err = YouTubeError(f"{endpoint} returned {r.status_code}: {r.text[:200]}")
            err.status = r.status_code
            raise err
        return r.json()

    # ---- public read methods ----
    def fetch_video_comments(self, video: str, max_results: int = 100,
                             order: str = "relevance", force_refresh: bool = False) -> list[dict]:
        """Top-level comments on a video. order: 'relevance' or 'time'.
        Returns author, author_channel_url, text, like_count, reply_count, published_at."""
        vid = _extract_video_id(video)
        ck = f"comments:{vid}:{max_results}:{order}"
        if not force_refresh and (c := self._cache_get(ck)) is not None:
            return c
        out: list[dict] = []
        page_token = None
        while len(out) < max_results:
            data = self._get("commentThreads", {
                "part": "snippet", "videoId": vid,
                "maxResults": min(100, max_results - len(out)),
                "order": order, **({"pageToken": page_token} if page_token else {}),
            })
            for it in data.get("items", []):
                s = it["snippet"]["topLevelComment"]["snippet"]
                out.append({
                    "author": s.get("authorDisplayName"),
                    "author_channel_url": s.get("authorChannelUrl"),
                    "text": s.get("textDisplay"),
                    "like_count": s.get("likeCount", 0),
                    "reply_count": it["snippet"].get("totalReplyCount", 0),
                    "published_at": s.get("publishedAt"),
                })
            page_token = data.get("nextPageToken")
            if not page_token:
                break
        self._cache_put(ck, out)
        return out

    def fetch_video_stats(self, video: str, force_refresh: bool = False) -> dict:
        vid = _extract_video_id(video)
        ck = f"vstats:{vid}"
        if not force_refresh and (c := self._cache_get(ck)) is not None:
            return c
        data = self._get("videos", {"part": "snippet,statistics", "id": vid})
        items = data.get("items", [])
        if not items:
            raise YouTubeError(f"video not found: {vid}")
        it = items[0]
        st = it.get("statistics", {})
        res = {
            "video_id": vid,
            "title": it["snippet"].get("title"),
            "channel_title": it["snippet"].get("channelTitle"),
            "views": int(st.get("viewCount", 0)),
            "likes": int(st.get("likeCount", 0)) if "likeCount" in st else None,
            "comments": int(st.get("commentCount", 0)) if "commentCount" in st else None,
            "published_at": it["snippet"].get("publishedAt"),
        }
        self._cache_put(ck, res)
        return res

    def fetch_channel_stats(self, channel: str, force_refresh: bool = False) -> dict:
        """Accept a channel id (UC...), an @handle, or a handle string."""
        ch = channel.strip()
        ck = f"cstats:{ch}"
        if not force_refresh and (c := self._cache_get(ck)) is not None:
            return c
        params = {"part": "snippet,statistics"}
        if ch.startswith("UC") and len(ch) > 20:
            params["id"] = ch
        else:
            params["forHandle"] = ch.lstrip("@")
        data = self._get("channels", params)
        items = data.get("items", [])
        if not items:
            raise YouTubeError(f"channel not found: {channel}")
        it = items[0]
        st = it.get("statistics", {})
        res = {
            "channel_id": it.get("id"),
            "title": it["snippet"].get("title"),
            "subscribers": int(st.get("subscriberCount", 0)) if not st.get("hiddenSubscriberCount") else None,
            "videos": int(st.get("videoCount", 0)),
            "total_views": int(st.get("viewCount", 0)),
        }
        self._cache_put(ck, res)
        return res

    def fetch_trending(self, region_code: str = "US", category_id: Optional[str] = None,
                       max_results: int = 25, force_refresh: bool = False) -> list[dict]:
        """Most-popular videos (1 unit, no search cost). category_id filters to a niche."""
        ck = f"trending:{region_code}:{category_id}:{max_results}"
        if not force_refresh and (c := self._cache_get(ck)) is not None:
            return c
        params = {"part": "snippet,statistics", "chart": "mostPopular",
                  "regionCode": region_code, "maxResults": min(50, max_results)}
        if category_id:
            params["videoCategoryId"] = str(category_id)
        data = self._get("videos", params)
        out = []
        for it in data.get("items", []):
            st = it.get("statistics", {})
            out.append({
                "video_id": it.get("id"),
                "title": it["snippet"].get("title"),
                "channel_title": it["snippet"].get("channelTitle"),
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)) if "likeCount" in st else None,
                "comments": int(st.get("commentCount", 0)) if "commentCount" in st else None,
            })
        self._cache_put(ck, out)
        return out


if __name__ == "__main__":
    import json as _json
    c = YouTubeClient()
    print(_json.dumps(c.fetch_video_stats("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), indent=2))
