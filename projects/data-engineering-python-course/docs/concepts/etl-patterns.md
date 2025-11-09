# ETL Patterns

## Overview

ETL (Extract, Transform, Load) patterns define how data moves from source to destination. Modern data engineering uses various patterns depending on latency, volume, and freshness requirements.

## Common Patterns

### 1. Full Refresh

```mermaid
graph LR
    A[Source] -->|Extract All| B[Transform]
    B -->|Truncate & Load| C[Target]

    style A fill:#ff69b4,stroke:#00ffff
    style C fill:#00ff00,stroke:#00ffff
```

**When to use:**
- Small datasets (< 1GB)
- No historical tracking needed
- Simple refresh logic

**Pros:** Simple, consistent state
**Cons:** Inefficient, longer processing time

---

### 2. Incremental Load

```mermaid
graph LR
    A[Source] -->|Extract New/Changed| B[Transform]
    B -->|Append/Upsert| C[Target]
    D[Watermark Store] --> A
    B --> D

    style A fill:#ff69b4,stroke:#00ffff
    style C fill:#00ff00,stroke:#00ffff
    style D fill:#ffff00,stroke:#00ffff
```

**When to use:**
- Large datasets
- Frequent updates
- Timestamp or sequence ID available

**Pros:** Efficient, faster
**Cons:** Complex change detection

---

### 3. Change Data Capture (CDC)

```mermaid
graph LR
    A[Database Transaction Log] -->|Stream Changes| B[CDC Tool]
    B -->|INSERT/UPDATE/DELETE Events| C[Kafka]
    C -->|Consume| D[Data Warehouse]

    style A fill:#ff69b4,stroke:#00ffff
    style C fill:#ffff00,stroke:#00ffff
    style D fill:#00ff00,stroke:#00ffff
```

**When to use:**
- Near real-time sync needed
- All changes must be captured
- Source database supports CDC

**Pros:** Low latency, complete change history
**Cons:** Complex setup, database dependency

---

### 4. Streaming ETL

```mermaid
graph LR
    A[Event Stream] -->|Real-time| B[Stream Processor]
    B -->|Transform| C[Sink]

    style A fill:#ff69b4,stroke:#00ffff
    style B fill:#ffff00,stroke:#00ffff
    style C fill:#00ff00,stroke:#00ffff
```

**When to use:**
- Sub-second latency required
- Event-driven architecture
- Continuous processing

**Pros:** Real-time insights
**Cons:** Complex state management

## Pattern Decision Tree

```mermaid
graph TD
    A{Data Volume?} -->|Small| B[Full Refresh]
    A -->|Large| C{Latency Requirement?}
    C -->|Batch| D{Change Detection Available?}
    C -->|Real-time| E[Streaming ETL]
    D -->|Yes| F[Incremental Load]
    D -->|No, but DB supports CDC| G[CDC]
    D -->|No| B

    style B fill:#ff69b4,stroke:#00ffff
    style E fill:#00ff00,stroke:#00ffff
    style F fill:#ffff00,stroke:#00ffff
    style G fill:#9370db,stroke:#00ffff
```

## Related Projects

- **Project 03:** Incremental ETL Pattern
- **Project 13:** Kafka Streaming Consumer
- **Project 16:** CDC with Debezium
