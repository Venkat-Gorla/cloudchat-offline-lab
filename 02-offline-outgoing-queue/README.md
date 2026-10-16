# Lab 02 — Offline Outgoing Queue

```text
Alice CLI
    │
    ▼
Compose Message
    │
    ▼
SQLite Outgoing Queue
    │
    ▼
Network Available?
    │
    ├── No ──► Keep Pending
    │              │
    │           Reconnect
    │              │
    └── Yes ◄──────┘
           │
           ▼
      HTTP Server
           │
           ▼
   Persisted Message
           │
           ▼
   Mark Queue Item Sent
```

> Offline messaging prototype — persist outgoing messages locally until the server accepts them.
