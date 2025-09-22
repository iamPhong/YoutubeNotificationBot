import os
import sqlite3
from typing import List, Optional, Dict

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "channels.db")

def _conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as cx:
        cx.execute(
            """
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY,
                custom_name TEXT
            )
            """
        )

def get_channels() -> List[Dict]:
    with _conn() as cx:
        cx.row_factory = sqlite3.Row
        rows = cx.execute("SELECT id, custom_name FROM channels").fetchall()
        return [dict(r) for r in rows]

def get_channel(channel_id: str) -> Optional[Dict]:
    with _conn() as cx:
        cx.row_factory = sqlite3.Row
        row = cx.execute(
            "SELECT id, custom_name FROM channels WHERE id = ?", (channel_id,)
        ).fetchone()
        return dict(row) if row else None

def add_channel(channel_id: str, custom_name: Optional[str]):
    with _conn() as cx:
        cx.execute(
            "INSERT OR IGNORE INTO channels (id, custom_name) VALUES (?, ?)",
            (channel_id, custom_name),
        )

def remove_channel(channel_id: str) -> bool:
    with _conn() as cx:
        cur = cx.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
        return cur.rowcount > 0

def set_custom_name(channel_id: str, custom_name: str) -> bool:
    with _conn() as cx:
        cur = cx.execute(
            "UPDATE channels SET custom_name = ? WHERE id = ?", (custom_name, channel_id)
        )
        return cur.rowcount > 0

def clear_custom_name(channel_id: str) -> bool:
    with _conn() as cx:
        cur = cx.execute(
            "UPDATE channels SET custom_name = NULL WHERE id = ?", (channel_id,)
        )
        return cur.rowcount > 0

def import_env_channels_if_empty(env_raw: str):
    if not env_raw:
        return
    if get_channels():
        return
    for cid in env_raw.split():
        add_channel(cid, None)

def get_all_channel_ids():
    return [c["id"] for c in get_channels()]
