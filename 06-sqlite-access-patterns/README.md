# Lab 06 — SQLite Access Patterns

```text
                  SQLite Message Store
                           │
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
        List User's    Get Conversation  Update Message
        Conversations     Messages       Delivery Status
              │            │                │
              ▼            ▼                ▼
         user_id       conversation_id    message_id
              │            │
              ▼            ▼
        Order by Last   Order by ULID
          Activity       Ascending
              │            │
              ▼            ▼
         Recent First   Oldest First
```

> Explore DynamoDB-style access patterns using SQLite tables, primary keys, and indexes.
