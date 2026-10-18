# Lab 03 — Connectivity-Aware Delivery

```text
      Delivery Trigger
   ┌─────────┼──────────┐
   ▼         ▼          ▼
New Message  Reconnect  App Startup
   └─────────┼──────────┘
             ▼
     Check Connectivity
             │
       ┌─────┴─────┐
       ▼           ▼
    Offline       Online
       │           │
       ▼           ▼
 Keep Messages   Fetch All Eligible
    Queued       Pending Messages
                     │
                     ▼
                Process Batch
                     │
              ┌──────┴──────┐
              ▼             ▼
           Success        Failure
              │             │
              ▼             ▼
          Delivered      Schedule Retry
              │             │
              ▼             ▼
        Remain in Queue  Remain in Queue
        (Delivered)      (Pending / Retry Due)
```

> Messages are always persisted locally first. Message status and retry timing determine which messages are eligible for subsequent delivery attempts.
