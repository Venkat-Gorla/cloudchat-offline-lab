"""
uv run pytest code -v
"""

from outgoing_queue import enqueue_message, initialize_db


def test_enqueue_message(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = enqueue_message(db_path, "bob", "Hello Bob")
    assert result == {"id": 1, "status": "pending"}
