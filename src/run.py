import json
from pathlib import Path
from typing import Dict

from src import sources
from src.fetcher import fetch
from src.parse_utils import now_utc_iso, sha256_text
from src.parsers import arcagi2, gdpval, metr
from src.storage import append_snapshot, rebuild_latest

CACHE_PATH = Path("state/cache.json")
DATA_JSONL = Path("docs/data/metrics.jsonl")
LATEST_JSON = Path("docs/data/latest.json")


PARSER_MAP = {
    "metr": metr.parse,
    "gdpval": gdpval.parse,
    "arcagi2": arcagi2.parse,
}


def load_cache() -> Dict:
    if CACHE_PATH.exists():
        try:
            with CACHE_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[run] cache file invalid, starting fresh")
    return {}


def save_cache(cache: Dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def main() -> None:
    cache = load_cache()

    for source in sources.SOURCES:
        name = source["name"]
        url = source["url"]
        parser_key = source["parser"]
        parser_fn = PARSER_MAP.get(parser_key)
        if not parser_fn:
            print(f"[run] No parser found for {name} ({parser_key})")
            continue

        entry = cache.get(url, {})
        status, text, headers = fetch(url, entry.get("etag"), entry.get("last_modified"))
        if status == 304:
            print(f"[run] Not modified: {name}")
            entry["last_fetched"] = now_utc_iso()
            cache[url] = entry
            continue
        if status != 200:
            print(f"[run] Failed fetch {name}: status {status}")
            continue

        content_hash = sha256_text(text)
        if entry.get("content_hash") == content_hash:
            print(f"[run] Content hash unchanged for {name}, skipping parse")
            entry.update({
                "etag": headers.get("ETag") or headers.get("etag"),
                "last_modified": headers.get("Last-Modified") or headers.get("last-modified"),
                "content_hash": content_hash,
                "last_fetched": now_utc_iso(),
            })
            cache[url] = entry
            continue

        try:
            if parser_key == "gdpval":
                metrics = parser_fn(text, url, name, fetch)
            else:
                metrics = parser_fn(text, url, name)
        except Exception as exc:  # noqa: BLE001
            print(f"[run] Parser error for {name}: {exc}")
            continue

        snapshot = {
            "fetched_at": now_utc_iso(),
            "source": name,
            "url": url,
            "content_hash": content_hash,
            "metrics": metrics,
        }

        append_snapshot(DATA_JSONL, snapshot)
        print(f"[run] Recorded snapshot for {name} with {len(metrics)} metrics")

        entry.update({
            "etag": headers.get("ETag") or headers.get("etag"),
            "last_modified": headers.get("Last-Modified") or headers.get("last-modified"),
            "content_hash": content_hash,
            "last_fetched": snapshot["fetched_at"],
        })
        cache[url] = entry

    save_cache(cache)
    rebuild_latest(DATA_JSONL, LATEST_JSON)
    print("[run] Rebuilt latest.json")


if __name__ == "__main__":
    main()
