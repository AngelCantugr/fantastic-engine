# Parallel/Concurrent Pattern (Simultaneous Execution)

## Overview

The Parallel pattern runs **multiple agents concurrently** on independent tasks, then combines results.

```mermaid
graph TD
    Start[Task] --> A1[Agent 1]
    Start --> A2[Agent 2]
    Start --> A3[Agent 3]

    A1 --> Combine[Combine Results]
    A2 --> Combine
    A3 --> Combine

    Combine --> Final[Final Output]

    style Start fill:#00ff00,stroke:#00ffff
    style Combine fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style Final fill:#00ff00,stroke:#00ffff
```

## When to Use

✅ **Best for:** Independent tasks, health checks, parallel data processing
❌ **Avoid for:** Dependent tasks, sequential requirements

## Key Features

- Fastest execution (concurrent)
- Independent agents
- Result aggregation
- Scales to many agents

## Example 1: Multi-Service Health Check

Check multiple services simultaneously → Aggregate status

See: `examples/parallel/health_checker.py`

## Example 2: Concurrent Data Processing

Process multiple data sources → Transform → Merge results

See: `examples/parallel/data_processor.py`
