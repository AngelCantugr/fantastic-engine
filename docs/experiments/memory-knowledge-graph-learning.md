# 🧠 Memory & Knowledge Graph MCP Learning Accelerator

!!! info "Experiment Status"
    **Status:** 🧪 Experimental
    **Created:** 2025-11-05
    **Location:** `experiments/memory-knowledge-graph-learning/`

## Overview

An experiment to use Memory and Knowledge Graph MCP servers to create persistent context and knowledge connections across multiple AI agents (Claude Code, Goose, Aider, Copilot CLI, Opencode, Codex).

## The Problem

When using multiple AI agents, each conversation starts fresh. Context from previous sessions is lost, making it harder to:

- Build on previous learnings
- Connect related concepts
- Track learning progress
- Share knowledge between agents

## The Solution

```mermaid
graph TB
    subgraph "AI Agents"
        A1[Claude Code]
        A2[Goose]
        A3[Aider]
        A4[Copilot CLI]
    end

    subgraph "Shared MCP Layer"
        M[Memory MCP<br/>Session History & Notes]
        K[Knowledge Graph<br/>Concept Relations]
    end

    A1 <--> M
    A2 <--> M
    A3 <--> M
    A4 <--> M

    A1 <--> K
    A2 <--> K
    A3 <--> K
    A4 <--> K

    style M fill:#ff00ff,stroke:#00ffff,stroke-width:3px
    style K fill:#00ffff,stroke:#ff00ff,stroke-width:3px
```

Use MCP (Model Context Protocol) servers to create a shared memory and knowledge layer that all agents can read from and write to.

## Key Features

### Memory MCP Server

- ✅ Persistent session memory
- ✅ Searchable notes and code snippets
- ✅ Learning goal tracking
- ✅ Cross-agent context sharing

### Knowledge Graph MCP Server

- ✅ Concept relationship mapping
- ✅ Learning dependency tracking
- ✅ Knowledge gap identification
- ✅ Visual knowledge exploration

## Architecture

```mermaid
sequenceDiagram
    participant You
    participant Agent1 as Claude Code
    participant Memory as Memory MCP
    participant Graph as Knowledge Graph
    participant Agent2 as Goose

    You->>Agent1: Learn topic X
    Agent1->>Memory: Store explanation
    Agent1->>Graph: Create concept nodes
    Agent1-->>You: Teaching complete

    Note over You: Switch to Goose

    You->>Agent2: Build example of X
    Agent2->>Memory: Retrieve context
    Agent2->>Graph: Query dependencies
    Agent2->>Memory: Store solution
    Agent2-->>You: Example built
```

## Quick Start

```bash
# Navigate to experiment
cd experiments/memory-knowledge-graph-learning

# Run setup
./setup.sh

# Configure your agent (see QUICKSTART.md)
cp configs/claude-desktop-config.json ~/.config/claude/

# Test it
# In your agent: "Store this learning note: Testing MCP"
```

## Documentation

The experiment includes comprehensive documentation:

| Document | Purpose |
|----------|---------|
| [README.md](https://github.com/AngelCantugr/fantastic-engine/tree/main/experiments/memory-knowledge-graph-learning) | Full architecture and concepts |
| [QUICKSTART.md](https://github.com/AngelCantugr/fantastic-engine/blob/main/experiments/memory-knowledge-graph-learning/QUICKSTART.md) | Step-by-step setup guide |
| [example-prompts.md](https://github.com/AngelCantugr/fantastic-engine/blob/main/experiments/memory-knowledge-graph-learning/example-prompts.md) | Copy-paste prompts for effective use |
| `configs/` | Sample configurations for each agent |

## Example Use Cases

### 1. Technology Deep Dive

Learn a new technology across multiple sessions and agents:

```mermaid
flowchart LR
    A[Research with Claude] --> B[Store concepts]
    B --> C[Practice with Goose]
    C --> D[Store solutions]
    D --> E[Review & connect]
    E --> F[Mastery]

    style A fill:#ff00ff,stroke:#00ffff
    style F fill:#00ff00,stroke:#00ffff
```

### 2. Multi-Agent Debugging

Continue debugging across different agents with full context:

- Agent 1 identifies the bug → Stores in Memory
- Agent 2 tries fix A → Stores result (didn't work)
- Agent 3 retrieves both → Tries fix B → Success!

### 3. Learning Path Construction

Build a structured learning path with dependencies:

```mermaid
graph TB
    A[Rust Basics] --> B[Ownership]
    B --> C[Borrowing]
    C --> D[Async/Await]
    D --> E[Tokio]

    style A fill:#00ff00,stroke:#00ffff
    style E fill:#ff00ff,stroke:#00ffff
```

The Knowledge Graph tracks what you know and what's next.

## Tech Stack

- **MCP Servers:** Memory, Knowledge Graph
- **Storage:** SQLite (memory), JSON (graph)
- **Agents:** Claude Code, Goose, Aider, Copilot CLI, etc.
- **Protocol:** Model Context Protocol (MCP)

## Current Status

!!! warning "Experimental Stage"
    - ✅ Documentation complete
    - ✅ Architecture designed
    - ✅ Configuration examples created
    - 🚧 Testing with real agents (in progress)
    - ⏳ Real-world usage patterns (pending)

## Next Steps

1. Install and configure MCP servers
2. Test with primary agent (Claude Code)
3. Add secondary agent (Goose)
4. Complete first multi-agent learning session
5. Document learnings and iterate

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Experiment Directory](https://github.com/AngelCantugr/fantastic-engine/tree/main/experiments/memory-knowledge-graph-learning)
- [Setup Guide](https://github.com/AngelCantugr/fantastic-engine/blob/main/experiments/memory-knowledge-graph-learning/QUICKSTART.md)

## Graduation Criteria

This experiment will graduate to its own repository when:

- [ ] Successfully used across 3+ agents
- [ ] Completed 5+ multi-agent learning sessions
- [ ] Built knowledge graph with 50+ concepts
- [ ] Documented 10+ real-world use cases
- [ ] Created backup/export tooling
- [ ] Proven learning acceleration

---

**Try it yourself!** This experiment is ready for testing. Follow the [QUICKSTART.md](https://github.com/AngelCantugr/fantastic-engine/blob/main/experiments/memory-knowledge-graph-learning/QUICKSTART.md) to get started. 🚀
