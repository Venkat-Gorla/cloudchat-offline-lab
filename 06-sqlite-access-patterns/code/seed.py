"""
uv run code/seed.py
"""

from pathlib import Path
from datetime import datetime, timedelta, timezone
import sqlite3
import ulid

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema.sql"
DB_PATH = ROOT / "cloudchat.db"

TEST_CONVERSATIONS = [
    ("alice", "bob"),
    ("alice", "carol"),
]


def insert_messages(db, messages, conversation_id, conversation_time):
    for msg_index, (sender, body) in enumerate(messages):
        message_time = conversation_time + timedelta(minutes=10 * msg_index)
        timestamp_ms = int(message_time.timestamp() * 1000)
        message_id = f"MSG#{ulid.from_timestamp(timestamp_ms / 1000)}"

        db.execute(
            """
            INSERT INTO messages (
                message_id, conversation_id, created_at,
                sender_id, body, delivery_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                conversation_id,
                timestamp_ms,
                sender,
                body,
                "delivered",
            ),
        )


def insert_conversations(
    db,
    participants,
    conversation_id,
    last_message,
    last_timestamp
) -> None:
    for user_id in participants:
        db.execute(
            """
            INSERT INTO conversation_inbox (
                user_id, conversation_id,
                last_message, last_activity_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                conversation_id,
                last_message,
                last_timestamp,
            ),
        )


def inject_test_data(db):
    base_time = datetime.now(timezone.utc) - timedelta(
        days=len(TEST_CONVERSATIONS)
    )

    for index, (u1, u2) in enumerate(TEST_CONVERSATIONS):
        conversation_id = f"CONV#{u1}#{u2}"
        participants = [u1, u2]

        # Each conversation separated by one day.
        conversation_time = base_time + timedelta(days=index)

        messages = [
            (u1, f"Message 1 from {u1} to {u2}"),
            (u2, f"Reply 1 from {u2} to {u1}"),
            (u1, f"Message 2 from {u1} to {u2}"),
        ]

        insert_messages(db, messages, conversation_id, conversation_time)

        last_message = messages[-1][1]
        last_timestamp = int(
            (
                conversation_time +
                timedelta(minutes=10 * (len(messages) - 1))
            ).timestamp() * 1000
        )

        insert_conversations(
            db,
            participants,
            conversation_id,
            last_message,
            last_timestamp
        )


if __name__ == "__main__":
    print("Starting SQLite test data injection...")

    with sqlite3.connect(DB_PATH) as db:
        db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        inject_test_data(db)

    print(f"Test data successfully written to {DB_PATH}")
