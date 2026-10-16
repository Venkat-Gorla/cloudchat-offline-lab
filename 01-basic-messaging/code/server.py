"""
uv run uvicorn server:app --app-dir code --reload
"""

from pathlib import Path
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header
from pydantic import BaseModel, Field

DB_PATH = Path("messages.db")


def connect_db(db_path: Path = DB_PATH):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with connect_db(db_path) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                body TEXT NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db()
    yield


app = FastAPI(title="Basic Messaging Lab", lifespan=lifespan)


class MessageRequest(BaseModel):
    recipient: str = Field(min_length=1)
    body: str = Field(min_length=1)


def save_message(
    db_path: Path,
    sender: str,
    recipient: str,
    body: str,
):
    with connect_db(db_path) as db:
        cursor = db.execute(
            """INSERT INTO messages (sender, recipient, body)
               VALUES (?, ?, ?)""",
            (sender, recipient, body),
        )
        message_id = cursor.lastrowid

    return {"id": message_id, "status": "accepted"}


@app.post("/messages", status_code=201)
def send_message(
    request: MessageRequest,
    x_user_id: str = Header(min_length=1),
):
    return save_message(
        DB_PATH,
        x_user_id,
        request.recipient,
        request.body,
    )


@app.get("/messages")
def get_messages(x_user_id: str = Header(min_length=1)):
    with connect_db() as db:
        rows = db.execute(
            """
            SELECT id, sender, recipient, body
            FROM messages
            WHERE recipient = ?
            ORDER BY id
            """,
            (x_user_id,),
        ).fetchall()

    return {"messages": [dict(row) for row in rows]}
