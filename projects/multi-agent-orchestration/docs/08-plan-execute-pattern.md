# Plan-Execute Pattern (Strategic Planning)

## Overview

The Plan-Execute pattern uses a **planner agent to create dynamic task lists** that executor agents carry out, with replanning based on results.

```mermaid
graph TD
    P[Planner] --> T1[Task 1]
    P --> T2[Task 2]
    P --> T3[Task 3]

    T1 --> E1[Executor]
    T2 --> E2[Executor]
    T3 --> E3[Executor]

    E1 --> R[Review Results]
    E2 --> R
    E3 --> R

    R --> C{Complete?}
    C -->|No| P
    C -->|Yes| Done

    style P fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style Done fill:#00ff00,stroke:#00ffff
```

## When to Use

✅ **Best for:** Complex multi-step tasks, ambiguous requirements, need for adaptation
❌ **Avoid for:** Simple well-defined tasks, need for speed

## Key Features

- Dynamic planning
- Adaptive execution
- Handles ambiguity
- Can replan mid-execution

## Example 1: Feature Implementation Planner

Break down feature request → Create tasks → Execute → Verify → Iterate

See: `examples/plan-execute/feature_planner.py`

## Example 2: System Migration Orchestrator

Analyze current state → Plan migration steps → Execute with validation → Handle issues

See: `examples/plan-execute/migration_orchestrator.py`
