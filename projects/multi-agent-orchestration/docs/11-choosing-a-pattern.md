# Choosing the Right Pattern

## Quick Decision Tree

```mermaid
graph TD
    Start{What's your<br/>primary need?}

    Start -->|Route requests| Router[Router Pattern]
    Start -->|Linear transform| Sequential[Sequential Pattern]
    Start -->|Quality critical| Reflection[Reflection Pattern]
    Start -->|Speed critical| Speed{Independent<br/>tasks?}
    Start -->|Complex workflow| Complex{Conditional<br/>logic?}
    Start -->|Collaboration| Collab{Clear<br/>hierarchy?}
    Start -->|Uncertain tasks| Plan[Plan-Execute]

    Speed -->|Yes| Parallel[Parallel Pattern]
    Speed -->|No| Router

    Complex -->|Yes| Graph[Graph Pattern]
    Complex -->|No| Sequential

    Collab -->|Yes| Supervisor[Supervisor Pattern]
    Collab -->|No| Swarm[Swarm Pattern]

    style Router fill:#00ff00,stroke:#00ffff
    style Sequential fill:#00ff00,stroke:#00ffff
    style Reflection fill:#ffff00,stroke:#ff00ff
    style Parallel fill:#00ff00,stroke:#00ffff
    style Graph fill:#ffff00,stroke:#ff00ff
    style Supervisor fill:#ffff00,stroke:#ff00ff
    style Swarm fill:#ff0000,stroke:#00ffff
    style Plan fill:#ffff00,stroke:#ff00ff
```

## Pattern Selection Matrix

| Your Requirement | Best Pattern | Alternative |
|-----------------|--------------|-------------|
| Simple classification | Router | Supervisor |
| Linear data pipeline | Sequential | Graph |
| Parallel independent tasks | Parallel | Supervisor |
| Complex conditional flow | Graph | Supervisor |
| Quality over speed | Reflection | Swarm |
| Clear hierarchy | Supervisor | Graph |
| Peer collaboration | Swarm | Supervisor |
| Dynamic planning | Plan-Execute | Supervisor |

## Complexity vs Capability

```mermaid
graph LR
    A[Simple] --> B[Medium] --> C[Complex]

    A -.->|Router| A1[2-3 LLM calls]
    A -.->|Sequential| A2[4-5 calls]

    B -.->|Parallel| B1[4-6 calls]
    B -.->|Supervisor| B2[5-6 calls]

    C -.->|Reflection| C1[8-20 calls]
    C -.->|Graph| C2[6-15 calls]
    C -.->|Swarm| C3[5-10 calls]
    C -.->|Plan-Execute| C4[8-20 calls]

    style A fill:#00ff00,stroke:#00ffff
    style B fill:#ffff00,stroke:#ff00ff
    style C fill:#ff0000,stroke:#00ffff
```

## Real-World Use Cases

### Software Engineering Tasks

| Task | Pattern | Why |
|------|---------|-----|
| Code review | Swarm or Reflection | Collaborative or iterative quality |
| API design | Supervisor | Clear sequential steps |
| Bug triage | Router | Classification task |
| Test suite | Parallel | Independent test runs |
| Refactoring | Plan-Execute | Complex planning needed |
| CI/CD | Graph | Conditional workflow |

### Operations Tasks

| Task | Pattern | Why |
|------|---------|-----|
| Incident response | Supervisor | Command structure |
| Health monitoring | Parallel | Check services concurrently |
| Deployment | Graph | Conditional rollout |
| Log analysis | Sequential | Linear pipeline |

### Analysis Tasks

| Task | Pattern | Why |
|------|---------|-----|
| Research review | Reflection | Multiple perspectives |
| Data processing | Sequential or Parallel | Depends on dependencies |
| Classification | Router | Simple routing |

## Cost vs Quality Trade-offs

| Pattern | Cost | Quality | Speed | Use When |
|---------|------|---------|-------|----------|
| Router | 💰 | ⭐⭐ | ⚡⚡⚡ | Budget tight |
| Sequential | 💰💰 | ⭐⭐⭐ | ⚡⚡ | Simple pipeline |
| Parallel | 💰💰 | ⭐⭐⭐ | ⚡⚡⚡ | Speed critical |
| Supervisor | 💰💰💰 | ⭐⭐⭐⭐ | ⚡⚡ | Need control |
| Swarm | 💰💰💰 | ⭐⭐⭐⭐ | ⚡⚡ | Collaboration |
| Graph | 💰💰💰 | ⭐⭐⭐⭐ | ⚡⚡ | Complex flow |
| Reflection | 💰💰💰💰 | ⭐⭐⭐⭐⭐ | ⚡ | Quality critical |
| Plan-Execute | 💰💰💰💰 | ⭐⭐⭐⭐ | ⚡ | Uncertain tasks |

## Hybrid Patterns

Often the best solution combines patterns:

### Router + Swarm
Route to appropriate swarm team.

### Supervisor + Parallel
Supervisor coordinates parallel workers.

### Plan-Execute + Sequential
Planner creates sequential task pipeline.

### Graph + Reflection
Each graph node includes reflection for quality.

## Getting Started

1. **Start simple**: Use Router or Sequential for first implementation
2. **Measure**: Track latency, cost, quality
3. **Iterate**: Upgrade to more complex patterns if needed
4. **Combine**: Hybrid patterns for production systems

## Next Steps

Choose a pattern and try the examples:
- [Swarm Examples](../examples/swarm/)
- [Supervisor Examples](../examples/supervisor/)
- [Reflection Examples](../examples/reflection/)
- [All Other Patterns](../examples/)
