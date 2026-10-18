# Lab 05 — Message History and Outbox

## 1. Client-Side Architecture

```text
             User Sends Message
                     │
                     ▼
           Persist in Local Database
             (Atomic Transaction)
                     │
              ┌──────┴──────┐
              ▼             ▼
        Message History   Outgoing Queue
        (Source of Truth) (Pending Work)
              │              │
              ▼              ▼
        Conversation     Delivery Worker
            View             │
                             ▼
                        Send to Server
                             │
                      ┌──────┴──────┐
                      ▼             ▼
                   Success        Failure
                      │             │
                      ▼             ▼
                Update History  Schedule Retry
                Remove from     Keep in Queue
                Queue
```

> Every message is persisted in local history before delivery is attempted. The outgoing queue tracks work that remains to be delivered.

## 2. Persistence and Recovery

```text
             App Restarts
                  │
                  ▼
          Load Message History
                  │
                  ▼
        Find Pending Outgoing Work
                  │
                  ▼
          Resume Delivery Attempts
                  │
             ┌────┴────┐
             ▼         ▼
          Success    Failure
             │         │
             ▼         ▼
        Update State  Retry Later
```

## Design Principles

- **Atomic persistence:** Create the history record and outgoing work record in one database transaction.
- **Idempotency:** Repeated delivery attempts must not create duplicate logical messages at the recipient.
