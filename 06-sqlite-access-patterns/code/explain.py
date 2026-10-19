"""
uv run code/explain.py
"""

from pathlib import Path
import sqlite3
from contextlib import closing

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "cloudchat.db"

QUERIES = {
    "List conversations by recency": """
        SELECT conversation_id, last_message, last_activity_at
        FROM conversation_inbox
        WHERE user_id = ?
        ORDER BY last_activity_at DESC, conversation_id DESC
    """,
    "Get conversation messages": """
        SELECT message_id, sender_id, body, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY message_id ASC
    """,
}

PARAMETERS = ("alice", "CONV#alice#bob")


def explain_query_plan(db, name, sql, parameter):
    print(f"\n{name}")

    rows = db.execute(
        f"EXPLAIN QUERY PLAN {sql}",
        (parameter,),
    ).fetchall()

    for row in rows:
        print(f"  {row[3]}")


def main():
    with closing(sqlite3.connect(DB_PATH)) as db:
        for (name, sql), parameter in zip(QUERIES.items(), PARAMETERS):
            explain_query_plan(db, name, sql, parameter)


if __name__ == "__main__":
    main()
