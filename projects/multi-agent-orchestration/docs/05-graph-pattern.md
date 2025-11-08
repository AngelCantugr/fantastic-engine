# Graph/Workflow Pattern (State Machine)

## Overview

The Graph pattern uses **state machines with defined transitions** for complex workflows with conditional logic and branching paths.

```mermaid
graph LR
    Start --> Build[Build Agent]
    Build --> Test{Test Agent}
    Test -->|Pass| Security[Security Scan]
    Test -->|Fail| Fix[Fix Agent]
    Fix --> Build
    Security -->|Pass| Deploy[Deploy Agent]
    Security -->|Fail| Alert[Alert Agent]
    Deploy --> Done
    Alert --> Done

    style Build fill:#00ffff,stroke:#ff00ff
    style Test fill:#ffff00,stroke:#ff00ff
    style Security fill:#ffff00,stroke:#ff00ff
    style Done fill:#00ff00,stroke:#00ffff
```

## When to Use

✅ **Best for:** CI/CD pipelines, approval workflows, complex conditional logic
❌ **Avoid for:** Simple linear flows, unclear state transitions

## Key Features

- Explicit state transitions
- Conditional branching
- Loop handling
- Precise flow control

## Example 1: CI/CD Pipeline

Build → Test → Security → Deploy with conditional paths based on results.

See: `examples/graph/cicd_pipeline.py`

## Example 2: Complex Approval Workflow

Multi-level approval with parallel reviews and conditional escalation.

See: `examples/graph/approval_workflow.py`
