from pathlib import Path
import sqlite3

DB_PATH = Path("outgoing.db")


def connect_db(db_path: Path = DB_PATH):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with connect_db(db_path) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS outgoing_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                attempt_count INTEGER NOT NULL DEFAULT 0
            )
        """)


def enqueue_message(
    db_path: Path,
    sender: str,
    recipient: str,
    body: str,
):
    with connect_db(db_path) as db:
        cursor = db.execute(
            """
            INSERT INTO outgoing_messages (sender, recipient, body)
            VALUES (?, ?, ?)
            """,
            (sender, recipient, body),
        )
        message_id = cursor.lastrowid

    return {"id": message_id, "status": "pending"}


def get_pending_messages(db_path: Path):
    with connect_db(db_path) as db:
        rows = db.execute(
            """
            SELECT id, sender, recipient, body, status, attempt_count
            FROM outgoing_messages
            WHERE status = 'pending'
            ORDER BY id
            """
        ).fetchall()

    return [dict(row) for row in rows]
