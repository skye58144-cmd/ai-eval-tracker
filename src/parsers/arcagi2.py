import re
from typing import List
from bs4 import BeautifulSoup

from src.parse_utils import safe_snippet


PERCENT_PATTERN = re.compile(r"ARC-AGI-2\s+private\s+dataset[^\d]{0,50}?(?P<value>\d+(?:\.\d+)?)%", re.IGNORECASE)
COST_PATTERN = re.compile(r"\$\s*(?P<value>\d+(?:\.\d+)?)\s*/\s*task", re.IGNORECASE)


def parse(html: str, url: str, name: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    results: List[dict] = []

    percent_match = PERCENT_PATTERN.search(text)
    if percent_match:
        value = float(percent_match.group("value"))
        results.append({
            "metric_key": "arc_agi_2_private_sota_percent",
            "value": value,
            "unit": "percent",
            "entity": "ARC-AGI-2",
            "evidence": safe_snippet(text, percent_match.start()),
        })

    cost_match = COST_PATTERN.search(text)
    if cost_match:
        value = float(cost_match.group("value"))
        results.append({
            "metric_key": "arc_agi_2_private_sota_cost_per_task_usd",
            "value": value,
            "unit": "usd_per_task",
            "entity": "ARC-AGI-2",
            "evidence": safe_snippet(text, cost_match.start()),
        })

    return results
