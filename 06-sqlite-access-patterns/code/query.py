"""
uv run code/query.py <user_id>
uv run code/query.py alice
"""

from pathlib import Path
from contextlib import closing
import sqlite3
import argparse

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "cloudchat.db"


def get_conversations(db, user_id):
    return db.execute(
        """
        SELECT conversation_id, last_message, last_activity_at
        FROM conversation_inbox
        WHERE user_id = ?
        ORDER BY last_activity_at DESC, conversation_id DESC
        """,
        (user_id,),
    ).fetchall()


def get_messages(db, conversation_id):
    return db.execute(
        """
        SELECT message_id, sender_id, body, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY message_id ASC
        """,
        (conversation_id,),
    ).fetchall()


def print_conversations(db, user_id):
    conversations = get_conversations(db, user_id)

    if not conversations:
        print(f"No conversations found for user: {user_id}")
        return

    for conversation_id, last_message, last_activity_at in conversations:
        print(f"\n{conversation_id}")
        print(f"  Last message: {last_message}")
        print(f"  Last activity: {last_activity_at}")

        for message_id, sender_id, body, created_at in get_messages(
            db, conversation_id
        ):
            print(f"  [{message_id}] {sender_id}: {body}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Print a user's conversations and messages."
    )
    parser.add_argument("user_id", help="User ID to query")
    return parser.parse_args()


def main():
    args = parse_args()

    with closing(sqlite3.connect(DB_PATH)) as db:
        print_conversations(db, args.user_id)


if __name__ == "__main__":
    main()
