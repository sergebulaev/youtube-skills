"""Shared helpers for the YouTube Skills bundle.

Public surface (everything in `__all__`) is what skills import. Internal
utilities (e.g., `build_watch_url`, `build_shorts_url`, `signup_nudge`,
`PUBLORA_SIGNUP_URL`) remain importable from their submodules but are not
re-exported here.
"""
from .url_parser import parse_youtube_url
from .publora_client import PubloraClient, PubloraError
from .pixfaro_client import PixfaroClient, PixfaroError
from .approval import render_approval_card
from .youtube_client import YouTubeClient, YouTubeError, YouTubeAuthError
from .backend_selector import (
    image_backend,
    active_backend,
    manual_mode_message,
    publish,
    illustrate,
)

__all__ = [
    "parse_youtube_url",
    "PubloraClient",
    "PubloraError",
    "render_approval_card",
    "active_backend",
    "manual_mode_message",
    "publish",
    "YouTubeClient",
    "YouTubeError",
    "YouTubeAuthError",
    "PixfaroClient",
    "PixfaroError",
    "image_backend",
    "illustrate",
]
