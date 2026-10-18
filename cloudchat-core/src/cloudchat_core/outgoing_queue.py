from pathlib import Path
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone

DB_PATH = Path("outgoing.db")


def connect_db(db_path: Path = DB_PATH):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(connect_db(db_path)) as db:
        with db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS outgoing_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    next_attempt_at TEXT
                )
            """)


def enqueue_message(
    db_path: Path,
    sender: str,
    recipient: str,
    body: str,
):
    with closing(connect_db(db_path)) as db:
        with db:
            cursor = db.execute(
                """
                INSERT INTO outgoing_messages (sender, recipient, body)
                VALUES (?, ?, ?)
                """,
                (sender, recipient, body),
            )
            message_id = cursor.lastrowid

    return {"id": message_id, "status": "pending"}


def get_message(db_path: Path, message_id: int):
    with closing(connect_db(db_path)) as db:
        row = db.execute(
            """
            SELECT id, sender, recipient, body, status,
                   attempt_count, next_attempt_at
            FROM outgoing_messages
            WHERE id = ?
            """,
            (message_id,),
        ).fetchone()

    return dict(row) if row else None


def get_pending_messages(db_path: Path):
    now = datetime.now(timezone.utc).isoformat()

    with closing(connect_db(db_path)) as db:
        rows = db.execute(
            """
            SELECT id, sender, recipient, body, status,
                   attempt_count, next_attempt_at
            FROM outgoing_messages
            WHERE status = 'pending'
              AND (
                  next_attempt_at IS NULL
                  OR next_attempt_at <= ?
              )
            ORDER BY id
            """,
            (now,),
        ).fetchall()

    return [dict(row) for row in rows]


def mark_in_flight(db_path: Path, message_id: int):
    with closing(connect_db(db_path)) as db:
        with db:
            cursor = db.execute(
                """
                UPDATE outgoing_messages
                SET status = 'in_flight',
                    attempt_count = attempt_count + 1
                WHERE id = ? AND status = 'pending'
                """,
                (message_id,),
            )
            updated = cursor.rowcount == 1

    return updated


def mark_delivery_failed(
    db_path: Path,
    message_id: int,
    retry_delay_seconds: int = 30,
):
    if retry_delay_seconds < 0:
        raise ValueError("retry_delay_seconds must be non-negative")

    next_attempt_at = (
        datetime.now(timezone.utc) + timedelta(seconds=retry_delay_seconds)
    ).isoformat()

    with closing(connect_db(db_path)) as db:
        with db:
            cursor = db.execute(
                """
                UPDATE outgoing_messages
                SET status = 'pending',
                    next_attempt_at = ?
                WHERE id = ? AND status = 'in_flight'
                """,
                (next_attempt_at, message_id),
            )
            updated = cursor.rowcount == 1

    return updated


def mark_delivered(db_path: Path, message_id: int):
    with closing(connect_db(db_path)) as db:
        with db:
            cursor = db.execute(
                """
                UPDATE outgoing_messages
                SET status = 'delivered',
                    next_attempt_at = NULL
                WHERE id = ? AND status = 'in_flight'
                """,
                (message_id,),
            )
            updated = cursor.rowcount == 1

    return updated
