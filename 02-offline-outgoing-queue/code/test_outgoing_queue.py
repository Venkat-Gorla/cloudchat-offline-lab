"""
uv run pytest code -v
"""

from outgoing_queue import (
    initialize_db,
    enqueue_message,
    get_pending_messages,
    mark_in_flight,
    mark_delivery_failed,
)


def test_enqueue_message(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = enqueue_message(db_path, "alice", "bob", "Hello Bob")
    assert result == {"id": 1, "status": "pending"}


def test_get_pending_messages(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    enqueue_message(db_path, "alice", "bob", "Hello Bob")
    enqueue_message(db_path, "carol", "dave", "Hello Dave")

    messages = get_pending_messages(db_path)

    assert len(messages) == 2
    assert messages[0]["sender"] == "alice"
    assert messages[1]["sender"] == "carol"
    assert messages[0]["recipient"] == "bob"
    assert messages[1]["recipient"] == "dave"
    assert all(message["status"] == "pending" for message in messages)


def test_mark_in_flight(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = enqueue_message(db_path, "alice", "bob", "Hello Bob")
    claimed = mark_in_flight(db_path, result["id"])

    assert claimed is True
    messages = get_pending_messages(db_path)
    assert messages == []


def test_mark_delivery_failed_preserves_message(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = enqueue_message(db_path, "alice", "bob", "Hello Bob")
    message_id = result["id"]

    assert mark_in_flight(db_path, message_id) is True
    assert mark_delivery_failed(db_path, message_id) is True

    messages = get_pending_messages(db_path)

    # The retry is scheduled for the future.
    assert messages == []
