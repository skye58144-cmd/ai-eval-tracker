import hashlib
import re
from datetime import datetime, timezone
from typing import Optional


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_duration_to_minutes(text: str) -> Optional[float]:
    pattern = re.compile(
        r"(?:(?P<hours>\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours))?\s*(?P<minutes>\d+(?:\.\d+)?)?\s*(?:m|min|mins|minutes)?",
        re.IGNORECASE,
    )
    match = pattern.search(text.replace(" ", ""))
    if not match:
        # try spaced version
        match = pattern.search(text)
    if not match:
        return None

    hours = match.group("hours")
    minutes = match.group("minutes")

    total_minutes = 0.0
    if hours:
        total_minutes += float(hours) * 60
    if minutes:
        total_minutes += float(minutes)

    return total_minutes if total_minutes > 0 else None


def safe_snippet(text: str, start_idx: int, length: int = 220) -> str:
    start = max(start_idx - length // 2, 0)
    end = min(start_idx + length // 2, len(text))
    snippet = text[start:end]
    snippet = re.sub(r"\s+", " ", snippet).strip()
    return snippet
