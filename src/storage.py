import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple


def append_snapshot(path_jsonl: Path, snapshot_obj: Dict) -> None:
    path_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with path_jsonl.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot_obj, ensure_ascii=False) + "\n")


def rebuild_latest(jsonl_path: Path, latest_path: Path) -> None:
    latest: Dict[Tuple[str, str], Dict] = {}
    if jsonl_path.exists():
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    snapshot = json.loads(line)
                except json.JSONDecodeError:
                    continue
                fetched_at = snapshot.get("fetched_at")
                try:
                    fetched_dt = datetime.fromisoformat(fetched_at) if fetched_at else None
                except ValueError:
                    fetched_dt = None
                for metric in snapshot.get("metrics", []):
                    key = (metric.get("metric_key"), metric.get("entity"))
                    if None in key:
                        continue
                    current = latest.get(key)
                    if current is None:
                        latest[key] = {
                            "metric_key": metric.get("metric_key"),
                            "entity": metric.get("entity"),
                            "value": metric.get("value"),
                            "unit": metric.get("unit"),
                            "evidence": metric.get("evidence"),
                            "timestamp": fetched_at,
                            "source": snapshot.get("source"),
                            "url": snapshot.get("url"),
                        }
                    else:
                        current_dt = datetime.fromisoformat(current["timestamp"]) if current.get("timestamp") else None
                        if fetched_dt and (current_dt is None or fetched_dt > current_dt):
                            latest[key] = {
                                "metric_key": metric.get("metric_key"),
                                "entity": metric.get("entity"),
                                "value": metric.get("value"),
                                "unit": metric.get("unit"),
                                "evidence": metric.get("evidence"),
                                "timestamp": fetched_at,
                                "source": snapshot.get("source"),
                                "url": snapshot.get("url"),
                            }

    latest_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {f"{k[0]}::{k[1]}": v for k, v in latest.items()}
    with latest_path.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
