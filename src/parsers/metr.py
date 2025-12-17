import re
from typing import List
from bs4 import BeautifulSoup

from src.parse_utils import parse_duration_to_minutes, safe_snippet


POINT_PATTERNS = [
    r"{label}[^\d]{0,60}(?P<dur>\d+\s*(?:h|hr|hrs|hour|hours)?\s*\d*\s*(?:m|min|mins|minutes)?)",
    r"(?P<dur>\d+\s*(?:h|hr|hrs|hour|hours)?\s*\d*\s*(?:m|min|mins|minutes)?)\s*(?:time horizon|horizon)[^\d]{0,40}{label}",
]

CI_PATTERNS = [
    r"{label}[^\d]{0,120}?(?:95% CI|CI 95%)[^\d]{0,20}(?P<low>\d+[^-–]{0,15}?)(?:-|–|to)\s*(?P<high>\d+[^)\s]{0,15})",
    r"(?:95% CI|CI 95%)\s*\(?(?P<low>\d+[^-–]{0,15}?)(?:-|–|to)\s*(?P<high>\d+[^)\s]{0,15})\)?[^\d]{0,60}{label}",
]


def _extract_entity(soup: BeautifulSoup, fallback: str) -> str:
    title = soup.title.string if soup.title else None
    if title:
        return title.strip()
    return fallback


def _parse_point(text: str, label: str) -> List[dict]:
    metrics = []
    for pattern in POINT_PATTERNS:
        regex = re.compile(pattern.format(label=label), re.IGNORECASE)
        for m in regex.finditer(text):
            dur = m.group("dur")
            minutes = parse_duration_to_minutes(dur)
            if minutes is None:
                continue
            metrics.append({
                "value": minutes,
                "evidence": safe_snippet(text, m.start()),
            })
            return metrics
    return metrics


def _parse_ci(text: str, label: str) -> List[dict]:
    for pattern in CI_PATTERNS:
        regex = re.compile(pattern.format(label=label), re.IGNORECASE)
        match = regex.search(text)
        if match:
            low = parse_duration_to_minutes(match.group("low"))
            high = parse_duration_to_minutes(match.group("high"))
            if low is None or high is None:
                continue
            return [{
                "low": low,
                "high": high,
                "evidence": safe_snippet(text, match.start()),
            }]
    return []


def parse(html: str, url: str, name: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    entity = _extract_entity(soup, name)

    results: List[dict] = []

    for label, key_base in [("50%", "p50"), ("80%", "p80")]:
        point_metrics = _parse_point(text, label)
        for pm in point_metrics:
            results.append({
                "metric_key": f"metr_time_horizon_{key_base}_minutes",
                "value": pm["value"],
                "unit": "minutes",
                "entity": entity,
                "evidence": pm["evidence"],
            })
        ci_metrics = _parse_ci(text, label)
        for ci in ci_metrics:
            results.append({
                "metric_key": f"metr_time_horizon_{key_base}_ci_low_minutes",
                "value": ci["low"],
                "unit": "minutes",
                "entity": entity,
                "evidence": ci["evidence"],
            })
            results.append({
                "metric_key": f"metr_time_horizon_{key_base}_ci_high_minutes",
                "value": ci["high"],
                "unit": "minutes",
                "entity": entity,
                "evidence": ci["evidence"],
            })

    return results
