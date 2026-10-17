"""
uv run pytest code/test_messaging.py -v
uv run pytest code -s
uv run pytest code -v
"""

from server import initialize_db, save_message, list_messages


def test_save_message(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = save_message(db_path, "alice", "bob", "Hello Bob")
    assert result == {"id": 1, "status": "accepted"}


def test_list_messages_for_recipient(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    save_message(db_path, "alice", "bob", "Hello Bob")
    save_message(db_path, "carol", "dave", "Hello Dave")

    messages = list_messages(db_path, "bob")

    assert len(messages) == 1
    assert messages[0]["sender"] == "alice"
    assert messages[0]["recipient"] == "bob"
    assert messages[0]["body"] == "Hello Bob"
