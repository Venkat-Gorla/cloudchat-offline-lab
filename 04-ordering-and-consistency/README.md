# Lab 04 — Ordering and Consistency

## 1. Message Ordering

```text
     Messages Created
       A → B → C
            │
            ▼
      Persist in Order
            │
            ▼
     Fetch Eligible Messages
            │
            ▼
       Process Queue
            │
       ┌────┴────┐
       ▼         ▼
   A Succeeds  A Fails
       │         │
       ▼         ▼
   Process B   Retry A Later
       │         │
       ▼         ▼
   Process C   B and C May Pass A
```

> Queue order does not automatically guarantee delivery order. Strict ordering requires later messages to wait when an earlier message fails, trading throughput for consistency.

## 2. Duplicate Suppression

```text
      Submit Message
       ID: msg-123
            │
            ▼
      Check Message ID
            │
       ┌────┴────┐
       ▼         ▼
      New      Already Exists
       │         │
       ▼         ▼
    Persist    Return Existing
    Message    Result
```

> Local duplicate suppression does not guarantee exactly-once delivery to a remote recipient.

## 3. Concurrent Workers

```text
       Pending Message
              │
        ┌─────┴─────┐
        ▼           ▼
      Worker A    Worker B
        │           │
        └─────┬─────┘
              ▼
         Atomic Claim
              │
        ┌─────┴─────┐
        ▼           ▼
      Success      Rejected
        │           │
        ▼           ▼
   Process Once   Do Not Process
```

> Fetching and claiming a message as separate operations can allow multiple workers to select the same message. Atomic claiming ensures only one worker successfully acquires it.
