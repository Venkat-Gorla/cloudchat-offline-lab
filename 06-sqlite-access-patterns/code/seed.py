
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema.sql"
DB_PATH = ROOT / "cloudchat.sqlite3"

# Crockford Base32 alphabet used by ULID.
ULID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def encode_base32(value: int, length: int) -> str:
    chars = []
    for _ in range(length):
        value, remainder = divmod(value, 32)
        chars.append(ULID_ALPHABET[remainder])
    return "".join(reversed(chars))


def make_ulid(timestamp: str, sequence: int) -> str:
    """Create a deterministic ULID for reproducible sample data."""
    dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
    timestamp_ms = int(dt.timestamp() * 1000)

    time_part = encode_base32(timestamp_ms, 10)
    random_part = encode_base32(sequence, 16)
    return time_part + random_part


def timestamp_ms(timestamp: str) -> int:
    dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def main() -> None:
    messages = [
        ("alice", "bob", "2026-10-15T09:00:00", "Hi Bob!"),
        ("alice", "bob", "2026-10-16T09:00:00", "How are you?"),
        ("bob", "alice", "2026-10-17T09:00:00", "Doing well, thanks!"),

        ("alice", "carol", "2026-10-16T10:00:00", "Hi Carol!"),
        ("carol", "alice", "2026-10-17T10:00:00", "Hey Alice!"),
        ("alice", "carol", "2026-10-18T10:00:00", "See you soon!"),
    ]

    with sqlite3.connect(DB_PATH) as db:
        db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        latest_by_conversation = {}

        for sequence, (sender, recipient, created, body) in enumerate(
            messages, start=1
        ):
            participants = sorted([sender, recipient])
            conversation_id = f"CONV#{participants[0]}#{participants[1]}"
            message_id = make_ulid(created, sequence)
            created_at = timestamp_ms(created)

            db.execute(
                """
                INSERT INTO messages (
                    message_id, conversation_id, created_at,
                    sender_id, body, delivery_status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_id) DO UPDATE SET
                    conversation_id = excluded.conversation_id,
                    created_at = excluded.created_at,
                    sender_id = excluded.sender_id,
                    body = excluded.body,
                    delivery_status = excluded.delivery_status
                """,
                (
                    message_id, conversation_id, created_at,
                    sender, body, "delivered",
                ),
            )

            current = latest_by_conversation.get(conversation_id)
            if current is None or created_at > current[0]:
                latest_by_conversation[conversation_id] = (
                    created_at, body, participants
                )

        for conversation_id, (activity, body, participants) in (
            latest_by_conversation.items()
        ):
            for user_id in participants:
                db.execute(
                    """
                    INSERT INTO conversation_inbox (
                        user_id, conversation_id,
                        last_message, last_activity_at
                    )
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, conversation_id)
                    DO UPDATE SET
                        last_message = excluded.last_message,
                        last_activity_at = excluded.last_activity_at
                    """,
                    (user_id, conversation_id, body, activity),
                )

    print(f"Database seeded: {DB_PATH}")


if __name__ == "__main__":
    main()
