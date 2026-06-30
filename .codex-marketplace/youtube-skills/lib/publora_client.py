"""Thin Publora REST client for the YouTube Skills project.

Wraps the Publora API endpoints this bundle uses. As of 2026-06 Publora exposes:
- POST /create-post              (create a draft or scheduled post)
- POST /get-upload-url           (pre-signed S3 URL for media)
- PUT  /update-post/:postGroupId (set scheduledTime, status, platformSettings)
- GET  /platform-connections     (list connected accounts + token health)

YouTube is a video-only platform: every published post REQUIRES a single video.
A text-only YouTube post is accepted by create-post but fails at publish time
(VIDEO_REQUIRED). So the correct flow is:

    1. POST /create-post            -> create a DRAFT (omit scheduledTime)
    2. POST /get-upload-url         -> pre-signed S3 URL for the video
    3. PUT  {uploadUrl}             -> upload the .mp4 to S3
    4. PUT  /update-post/:id        -> set scheduledTime (and any youtube settings)

The custom thumbnail cannot be set on create-post (the thumbnail upload itself
requires a postGroupId). This client provides the thumbnail ATTACH step only:
update-post with platformSettings.youtube.thumbnail = {mediaId, url} (see
`set_thumbnail`). It does NOT upload the thumbnail image. Publora requires the
thumbnail to be a tracked media asset from its dedicated YouTube thumbnail
endpoint, and that upload route is out of band here (do it in the Publora
dashboard, or via the dedicated endpoint once available) — the generic
get-upload-url media flow is not accepted for thumbnails. So in practice this
bundle outputs the thumbnail brief plus attach instructions rather than a
one-call thumbnail upload. YouTube community-tab posts have no Publora endpoint
at all, so those are draft-only (copy-paste) in this bundle.

Base URL: https://api.publora.com/api/v1
Auth header: x-publora-key: sk_...  (NOT Bearer)
Content-Type: application/json. Server-to-server only (custom headers are not in
the CORS allowlist, so browser calls fail preflight).

Design note: this client is deliberately minimal. Skills call exactly one method
per action, after the user has approved a draft rendered via `lib/approval.py`.
Write methods retry on transient 408/429/5xx via the shared retry decorator.
"""
from __future__ import annotations
import os
import time
import random
from datetime import datetime, timezone
from typing import Any, Optional

import requests


class PubloraError(RuntimeError):
    pass


def _utc_now_iso() -> str:
    """Current UTC time as an ISO 8601 string with millisecond precision and a
    trailing Z (e.g. '2026-06-30T16:00:00.000Z'), matching the client's
    scheduledTime style. Used for publish-now: Publora treats a past/current
    scheduledTime as 'send now'."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


RETRYABLE_STATUSES = {408, 429, 500, 502, 503, 504}


def _retry(attempts: int = 3, base_delay: float = 0.6):
    """Retry decorator for HTTP methods. Triggers on 408/429/5xx and on
    transient network errors. Exponential backoff with jitter."""

    def decorator(fn):
        def wrapper(*args, **kwargs):
            last_exc: Optional[Exception] = None
            for attempt in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except PubloraError as e:
                    msg = str(e)
                    retryable = any(f"HTTP {s}" in msg for s in RETRYABLE_STATUSES)
                    if not retryable or attempt == attempts - 1:
                        raise
                    last_exc = e
                except (requests.ConnectionError, requests.Timeout) as e:
                    if attempt == attempts - 1:
                        raise
                    last_exc = e
                time.sleep(base_delay * (2**attempt) + random.uniform(0, 0.25))
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


# Platform IDs must match Publora's regex: /^[a-z]+-[a-zA-Z0-9_-]+$/
# For YouTube the prefix is `youtube-` followed by the channel id
# (e.g. "youtube-UCxxxxxxxxxxxxxxxxxxxxxx").
PLATFORM_ID_PREFIX = "youtube-"

# YouTube text limits (the API itself allows YouTube's native 5,000 description
# chars; Publora's dashboard validates at 1,000, but the API does not).
TITLE_MAX = 100
DESCRIPTION_MAX = 5000
DESCRIPTION_VISIBLE = 150  # chars shown before "Show more"


class PubloraClient:
    BASE_URL = "https://api.publora.com/api/v1"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 60.0):
        self.api_key = api_key or os.getenv("PUBLORA_API_KEY")
        if not self.api_key:
            raise PubloraError(
                "PUBLORA_API_KEY not set. Export it or pass api_key= explicitly."
            )
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "x-publora-key": self.api_key,
                "Content-Type": "application/json",
            }
        )

    # ---- Create / schedule ------------------------------------------------

    def create_post(
        self,
        *,
        content: str,
        platforms: list[str],
        scheduled_time: Optional[str] = None,
        platform_settings: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a YouTube post group.

        For a real video upload, call this with NO scheduled_time so it lands as
        a draft, then upload the video and schedule via `update_post`. Use the
        `publish_video` helper to run all four steps in order.

        Args:
            content: The video description. The first ~150 chars are visible
                before "Show more". Max 5,000 chars on YouTube. If you do not
                pass a title in platform_settings, YouTube derives one from the
                first 70 chars of this content, so always set the title.
            platforms: List of platform connection IDs, e.g. ["youtube-UC..."].
                Each must match /^[a-z]+-[a-zA-Z0-9_-]+$/.
            scheduled_time: ISO 8601 UTC datetime. Omit for a draft. A past time
                is silently set to now. For video uploads, leave this OFF here
                and set it in update_post AFTER the video finishes uploading.
            platform_settings: Per-platform object. YouTube keys: title, privacy
                ("public"|"unlisted"|"private"), tags (list or comma string),
                categoryId, madeForKids (bool), playlist ({id, platformId}).
                The thumbnail CANNOT be set here (needs a postGroupId first).

        Returns:
            { "success": true, "postGroupId": "..." } on HTTP 200.
        """
        if not content or not content.strip():
            raise PubloraError("content is required (cannot be empty or whitespace)")
        if not platforms:
            raise PubloraError("at least one platform ID is required")
        payload: dict[str, Any] = {"content": content, "platforms": platforms}
        if scheduled_time:
            payload["scheduledTime"] = scheduled_time
        if platform_settings:
            payload["platformSettings"] = platform_settings
        return self._post("/create-post", payload)

    def update_post(
        self,
        post_group_id: str,
        *,
        status: Optional[str] = None,
        scheduled_time: Optional[str] = None,
        platform_settings: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Update a draft: schedule it, or attach YouTube settings / thumbnail.

        Used after the video upload completes. Pass scheduled_time (and
        status="scheduled") to publish at a time, or platform_settings to set
        the youtube.thumbnail / playlist / privacy after the fact.

        Note: you cannot change the playlist or thumbnail while the post is
        already `processing` (Publora returns 409). Set them on a draft.
        """
        payload: dict[str, Any] = {}
        if status:
            payload["status"] = status
        if scheduled_time:
            payload["scheduledTime"] = scheduled_time
        if platform_settings:
            payload["platformSettings"] = platform_settings
        if not payload:
            raise PubloraError("update_post needs at least one field to change")
        return self._put(f"/update-post/{post_group_id}", payload)

    # ---- Media ------------------------------------------------------------

    def get_upload_url(
        self,
        *,
        file_name: str,
        content_type: str,
        post_group_id: str,
        media_type: str = "video",
    ) -> dict[str, Any]:
        """Request a pre-signed S3 URL to upload a video (or image) file.

        Args:
            file_name: e.g. "episode-12.mp4". Sanitized server-side.
            content_type: MIME type, e.g. "video/mp4".
            post_group_id: The draft post group to attach the media to.
            media_type: "video" or "image". Always required; omitting it makes
                the S3 PutObjectCommand fail. Defaults to "video" for YouTube.

        Returns:
            { success, uploadUrl, fileUrl, mediaId }. `uploadUrl` expires in 1h.
        """
        payload = {
            "fileName": file_name,
            "contentType": content_type,
            "postGroupId": post_group_id,
            "type": media_type,
        }
        return self._post("/get-upload-url", payload)

    def upload_to_s3(self, upload_url: str, file_path: str, content_type: str) -> None:
        """PUT a local file to the pre-signed S3 URL from `get_upload_url`."""
        with open(file_path, "rb") as f:
            r = requests.put(
                upload_url,
                data=f,
                headers={"Content-Type": content_type},
                timeout=self.timeout,
            )
        if r.status_code >= 400:
            raise PubloraError(f"S3 upload failed: HTTP {r.status_code}: {r.text[:300]}")

    # ---- High-level YouTube video flow ------------------------------------

    def publish_video(
        self,
        *,
        content: str,
        platforms: list[str],
        video_path: str,
        title: str,
        content_type: str = "video/mp4",
        scheduled_time: Optional[str] = None,
        privacy: str = "public",
        tags: Optional[list[str]] = None,
        category_id: Optional[str] = None,
        made_for_kids: bool = False,
        playlist: Optional[dict[str, str]] = None,
        thumbnail: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Run the full media-required YouTube flow in order.

        draft (create-post) -> get-upload-url -> PUT to S3 ->
        update-post (schedule + youtube settings).

        The video file is supplied by the user. Returns the postGroupId plus the
        uploaded media's fileUrl and mediaId.

        scheduled_time: ISO 8601 UTC. If omitted (the publish-now / default
            case), the final update-post carries the current UTC time as
            scheduledTime, which Publora treats as "send now". The final
            update-post always carries a scheduledTime so it never hits the
            "needs at least one field" guard and strand the uploaded video.

        thumbnail: optional {mediaId, url} for a custom thumbnail, set in the
            final update-post. The image must already be a Publora-tracked asset
            (mediaId + url) from Publora's dedicated YouTube thumbnail upload;
            this client does NOT upload the image (that step is out of band — do
            it in the Publora dashboard). Without that asset, leave thumbnail
            unset and set it later in YouTube Studio.
        """
        yt: dict[str, Any] = {"title": title[:TITLE_MAX], "privacy": privacy}
        if tags:
            yt["tags"] = tags
        if category_id:
            yt["categoryId"] = category_id
        yt["madeForKids"] = made_for_kids
        if playlist:
            yt["playlist"] = playlist

        # 1. draft
        draft = self.create_post(
            content=content,
            platforms=platforms,
            platform_settings={"youtube": yt},
        )
        post_group_id = draft["postGroupId"]

        # 2. pre-signed URL
        file_name = os.path.basename(video_path)
        up = self.get_upload_url(
            file_name=file_name,
            content_type=content_type,
            post_group_id=post_group_id,
            media_type="video",
        )

        # 3. upload to S3
        self.upload_to_s3(up["uploadUrl"], video_path, content_type)

        # 4. schedule (and optionally set thumbnail now that media exists).
        # Always carry a scheduledTime: with no explicit time this is a
        # publish-now (current UTC, which Publora sends immediately). This keeps
        # the final update-post from ever being an all-empty payload, which would
        # raise after the video already uploaded to S3.
        effective_time = scheduled_time or _utc_now_iso()
        update_settings: Optional[dict[str, Any]] = None
        if thumbnail:
            update_settings = {"youtube": {"thumbnail": thumbnail}}
        self.update_post(
            post_group_id,
            status="scheduled",
            scheduled_time=effective_time,
            platform_settings=update_settings,
        )
        return {
            "postGroupId": post_group_id,
            "fileUrl": up.get("fileUrl"),
            "mediaId": up.get("mediaId"),
        }

    def set_thumbnail(
        self, post_group_id: str, *, media_id: str, url: str
    ) -> dict[str, Any]:
        """Attach a custom YouTube thumbnail to an existing draft post group.

        This is the ATTACH step only (update-post with platformSettings.youtube
        .thumbnail). It does NOT upload the image. The `mediaId` and `url` must
        already exist: they come from Publora's dedicated YouTube thumbnail
        upload (which itself requires this postGroupId), and that upload is out
        of band for this client — do it in the Publora dashboard, or via the
        dedicated endpoint once available. The generic get-upload-url media flow
        is not accepted for thumbnails, and arbitrary URLs are rejected by
        YouTube. Best-effort: if YouTube rejects the image, the video still
        publishes and only the thumbnail is skipped. Requires a verified channel.
        """
        return self.update_post(
            post_group_id,
            platform_settings={"youtube": {"thumbnail": {"mediaId": media_id, "url": url}}},
        )

    # ---- Connections (read) -----------------------------------------------

    def list_connections(self) -> list[dict[str, Any]]:
        """List connected social accounts with token health.

        Returns the `connections` array from GET /platform-connections. Each
        entry has platformId, username, displayName, tokenStatus, etc. Use it to
        confirm a YouTube channel is connected and which `youtube-<id>` to pass.
        """
        r = self._session.get(
            self.BASE_URL + "/platform-connections", timeout=self.timeout
        )
        data = self._handle(r)
        return data.get("connections", [])

    def youtube_connections(self) -> list[dict[str, Any]]:
        """Convenience filter: only the connected YouTube channels."""
        return [
            c
            for c in self.list_connections()
            if str(c.get("platformId", "")).startswith(PLATFORM_ID_PREFIX)
        ]

    # ---- Internals --------------------------------------------------------

    @_retry()
    def _post(self, path: str, json_body: dict[str, Any]) -> dict[str, Any]:
        r = self._session.post(
            self.BASE_URL + path, json=json_body, timeout=self.timeout
        )
        return self._handle(r)

    @_retry()
    def _put(self, path: str, json_body: dict[str, Any]) -> dict[str, Any]:
        r = self._session.put(
            self.BASE_URL + path, json=json_body, timeout=self.timeout
        )
        return self._handle(r)

    @staticmethod
    def _handle(r: requests.Response) -> dict[str, Any]:
        if r.status_code >= 400:
            try:
                body = r.json()
            except Exception:
                body = {"error": r.text[:500]}
            raise PubloraError(f"HTTP {r.status_code}: {body}")
        return r.json()
