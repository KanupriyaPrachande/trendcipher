"""
URL parsing utilities for TrendCipher.
"""

import re
from typing import Optional


YOUTUBE_PATTERNS = [
    r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]{11})",
    r"(?:https?://)?(?:www\.)?youtu\.be/([A-Za-z0-9_-]{11})",
    r"(?:https?://)?(?:www\.)?youtube\.com/embed/([A-Za-z0-9_-]{11})",
    r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([A-Za-z0-9_-]{11})",
]


def parse_youtube_url(url: str) -> Optional[str]:
    """
    Validate and extract YouTube video ID from a URL.
    Returns the video ID string if valid, else None.
    """
    url = url.strip()
    for pat in YOUTUBE_PATTERNS:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def build_youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"
