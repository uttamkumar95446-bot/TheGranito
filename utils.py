# utils.py
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

DATA_DIR = "data"
VISITOR_FILE = os.path.join(DATA_DIR, "visitors.json")


def _load_json(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _save_json(path: str, data: List[Dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_visitor(ip: str = "127.0.0.1", user_agent: str = "Unknown") -> None:
    visitors = _load_json(VISITOR_FILE)

    visitors.append({
        "timestamp": datetime.utcnow().isoformat(),
        "ip": ip,
        "user_agent": user_agent
    })

    visitors = visitors[-1000:]  # keep last 1000
    _save_json(VISITOR_FILE, visitors)


def get_visitor_count() -> int:
    return len(_load_json(VISITOR_FILE))


def get_today_visitors() -> int:
    visitors = _load_json(VISITOR_FILE)
    today = datetime.utcnow().date()

    return sum(
        1 for v in visitors
        if datetime.fromisoformat(v["timestamp"]).date() == today
    )


def clean_old_data(days: int = 30) -> int:
    visitors = _load_json(VISITOR_FILE)
    cutoff = datetime.utcnow() - timedelta(days=days)

    filtered = [
        v for v in visitors
        if datetime.fromisoformat(v["timestamp"]) > cutoff
    ]

    _save_json(VISITOR_FILE, filtered)
    return len(visitors) - len(filtered)
