import re
from typing import Callable, List
from bs4 import BeautifulSoup

from src.parse_utils import safe_snippet


MODEL_PATTERN = re.compile(r"(gpt-4o|o4-mini|o3|gpt-5)\s+(?P<value>\d+(?:\.\d+)?)%", re.IGNORECASE)


def _latest_html_url(abs_soup: BeautifulSoup) -> str:
    links = []
    for a in abs_soup.find_all("a", href=True):
        href = a["href"]
        match = re.search(r"/html/2510\.04374v(\d+)", href)
        if match:
            version = int(match.group(1))
            links.append((version, href))
    if links:
        _, best_href = max(links, key=lambda x: x[0])
        return best_href
    return "/html/2510.04374v1"


def parse(abs_html: str, url: str, name: str, fetch_fn: Callable) -> List[dict]:
    abs_soup = BeautifulSoup(abs_html, "html.parser")
    html_path = _latest_html_url(abs_soup)
    if not html_path.startswith("http"):
        base = "https://arxiv.org"
        html_url = base + html_path
    else:
        html_url = html_path

    status, html_text, _ = fetch_fn(html_url, None, None)
    if status != 200:
        print(f"[gdpval] Failed to fetch HTML version for {url}: status {status}")
        return []

    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(" ", strip=True)

    table_match = re.search(r"Table\s*2[^:]*:.*?win rate", text, re.IGNORECASE)
    search_text = text
    if table_match:
        start = max(table_match.start() - 100, 0)
        end = min(table_match.end() + 2000, len(text))
        search_text = text[start:end]

    results: List[dict] = []
    for m in MODEL_PATTERN.finditer(search_text):
        value = float(m.group("value"))
        entity = m.group(1).lower()
        results.append({
            "metric_key": "gdpval_table2_win_rate_percent",
            "value": value,
            "unit": "percent",
            "entity": entity,
            "evidence": safe_snippet(search_text, m.start()),
        })

    return results
