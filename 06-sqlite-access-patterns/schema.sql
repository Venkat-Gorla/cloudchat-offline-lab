-- SQLite schema for CloudChat access-pattern experiments

CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    sender_id TEXT NOT NULL,
    body TEXT NOT NULL,
    delivery_status TEXT NOT NULL
);

-- Fetch messages for a conversation in ULID order.
CREATE INDEX idx_messages_conversation
ON messages (conversation_id, message_id ASC);


CREATE TABLE conversation_inbox (
    user_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    last_message TEXT,
    last_activity_at INTEGER NOT NULL,
    PRIMARY KEY (user_id, conversation_id)
);

-- Fetch a user's conversations, most recently active first.
CREATE INDEX idx_inbox_recency
ON conversation_inbox (
    user_id,
    last_activity_at DESC,
    conversation_id DESC
);
