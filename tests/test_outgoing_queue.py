"""
uv run pytest -v
"""

from datetime import datetime, timedelta, timezone
from cloudchat_core.outgoing_queue import (
    connect_db,
    initialize_db,
    enqueue_message,
    get_message,
    get_pending_messages,
    mark_in_flight,
    mark_delivery_failed,
    mark_delivered,
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


def test_get_message_by_id(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = enqueue_message(db_path, "alice", "bob", "Hello Bob")
    message = get_message(db_path, result["id"])

    assert message["id"] == result["id"]
    assert message["sender"] == "alice"
    assert message["recipient"] == "bob"
    assert message["body"] == "Hello Bob"
    assert message["status"] == "pending"
    assert message["attempt_count"] == 0
    assert message["next_attempt_at"] is None


def test_failed_message_is_not_ready_before_retry_time(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = enqueue_message(db_path, "alice", "bob", "Hello Bob")
    message_id = result["id"]

    assert mark_in_flight(db_path, message_id) is True
    assert mark_delivery_failed(db_path, message_id) is True

    message = get_message(db_path, message_id)
    assert message["id"] == message_id
    assert message["status"] == "pending"
    assert message["attempt_count"] == 1
    assert message["next_attempt_at"] is not None

    messages = get_pending_messages(db_path)
    assert all(message["id"] != message_id for message in messages)


def test_failed_message_is_ready_after_retry_time(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = enqueue_message(db_path, "alice", "bob", "Hello Bob")
    message_id = result["id"]

    assert mark_in_flight(db_path, message_id) is True
    assert mark_delivery_failed(db_path, message_id) is True

    # Set the retry time to the past to avoid waiting.
    past_time = (
        datetime.now(timezone.utc) - timedelta(seconds=1)
    ).isoformat()

    with connect_db(db_path) as db:
        db.execute(
            """
            UPDATE outgoing_messages
            SET next_attempt_at = ?
            WHERE id = ?
            """,
            (past_time, message_id),
        )

    messages = get_pending_messages(db_path)

    assert len(messages) == 1
    assert messages[0]["id"] == message_id
    assert messages[0]["attempt_count"] == 1


def test_mark_delivered(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = enqueue_message(db_path, "alice", "bob", "Hello Bob")
    message_id = result["id"]

    assert mark_in_flight(db_path, message_id) is True
    assert mark_delivered(db_path, message_id) is True

    message = get_message(db_path, message_id)

    assert message["status"] == "delivered"
    assert message["attempt_count"] == 1
    assert get_pending_messages(db_path) == []
