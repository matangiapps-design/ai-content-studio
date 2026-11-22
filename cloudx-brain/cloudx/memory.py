import json
import sqlite3
from pathlib import Path
from typing import Any

class EventMemory:
    """Durable local event history; never stores credentials."""
    def __init__(self, path: str = "cloudx-brain/data/cloudx.db"):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, created_at TEXT, event_type TEXT, payload TEXT)")

    def record(self, created_at: str, event_type: str, payload: dict[str, Any]) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO events(created_at,event_type,payload) VALUES(?,?,?)",
                       (created_at, event_type, json.dumps(payload)))

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT id,created_at,event_type,payload FROM events ORDER BY id DESC LIMIT ?",
                              (max(1, min(limit, 200)),)).fetchall()
        return [{"id": r[0], "created_at": r[1], "event_type": r[2], "payload": json.loads(r[3])} for r in rows]
