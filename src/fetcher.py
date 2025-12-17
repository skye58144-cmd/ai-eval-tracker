import httpx
from typing import Dict, Optional, Tuple

USER_AGENT = "ai-eval-tracker/1.0 (https://github.com/)"


def fetch(url: str, etag: Optional[str] = None, last_modified: Optional[str] = None) -> Tuple[int, str, Dict[str, str]]:
    headers = {"User-Agent": USER_AGENT}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified

    timeout = httpx.Timeout(30.0)
    retries = 2
    last_exc = None

    for attempt in range(retries + 1):
        try:
            response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
            return response.status_code, response.text, dict(response.headers)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt == retries:
                print(f"[fetch] failed after {retries + 1} attempts for {url}: {exc}")
                break
    return 0, "", {}
