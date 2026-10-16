"""
uv run pytest code/test_messaging.py -v
uv run pytest code -v
"""

from server import initialize_db, save_message


def test_save_message(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(db_path)

    result = save_message(db_path, "alice", "bob", "Hello Bob")
    assert result == {"id": 1, "status": "accepted"}
