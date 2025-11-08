# Router Pattern (Classification & Delegation)

## Overview

The Router pattern uses an **initial classifier to route requests** to the appropriate specialist agent in a single handoff.

```mermaid
graph LR
    I[User Request] --> R{Router Agent}
    R -->|Bug Report| Bug[Bug Handler]
    R -->|Feature Request| Feature[Feature Handler]
    R -->|Question| Support[Support Agent]

    style R fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style Bug fill:#00ffff,stroke:#ff00ff
    style Feature fill:#00ffff,stroke:#ff00ff
    style Support fill:#00ffff,stroke:#ff00ff
```

## When to Use

✅ **Best for:** Ticket routing, query classification, simple delegation
❌ **Avoid for:** Multi-step collaboration, complex workflows

## Key Features

- Fastest pattern (lowest latency)
- Simple classification
- Clear specialist boundaries
- One-time handoff

## Example 1: Support Ticket Router

Classify ticket type → Route to appropriate team → Handle

See: `examples/router/ticket_router.py`

## Example 2: Multi-Intent Query Handler

Detect query intent → Route to specialist → Combine results if needed

See: `examples/router/query_classifier.py`
