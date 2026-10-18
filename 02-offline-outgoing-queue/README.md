# Lab 02 — Offline Outgoing Queue

```text
    Enqueue Message
          │
          ▼
  SQLite Outgoing Queue
          │
          ▼
       Pending
          │
          ▼
      In Flight
          │
     ┌────┴────┐
     ▼         ▼
  Failure    Success
     │         │
     ▼         ▼
  Pending   Delivered
     │
     ▼
 Retry When Due
     │
     └────────────► In Flight
```

> Reusable SQLite queue for persistent outgoing messages, delivery state tracking, and retry scheduling.
