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
          Delivered    Schedule Retry
                            │
                            ▼
                   Remain Eligible for Delivery
```

> Messages are always persisted locally first.
