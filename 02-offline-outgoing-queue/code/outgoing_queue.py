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
                recipient TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                attempt_count INTEGER NOT NULL DEFAULT 0
            )
        """)


def enqueue_message(db_path: Path, recipient: str, body: str):
    with connect_db(db_path) as db:
        cursor = db.execute(
            """
            INSERT INTO outgoing_messages (recipient, body)
            VALUES (?, ?)
            """,
            (recipient, body),
        )
        message_id = cursor.lastrowid

    return {"id": message_id, "status": "pending"}
