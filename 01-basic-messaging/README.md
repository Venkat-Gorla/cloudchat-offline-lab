# Lab 01 — Basic Messaging

```text
Alice CLI                  Bob CLI
    │                          ▲
    ▼                          │
HTTP Request ──► HTTP Server ──┘
                      │
                      ▼
                  SQLite DB
                      │
                      ▼
              Persisted Message
```

> Basic messaging prototype — send and persist messages over HTTP.
