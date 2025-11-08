# 🔌 Agent Communication Protocols

## Introduction

Agent communication protocols are the **"USB-C for AI"** - standardized interfaces that enable AI agents to connect with data sources, tools, and other agents without custom integrations.

## The Protocol Landscape (2025)

```mermaid
graph TB
    subgraph "Agent Protocols Ecosystem"
        A[AI Agent] --> P{Protocol Layer}

        P --> MCP[MCP<br/>Model Context Protocol]
        P --> A2A[A2A<br/>Agent-to-Agent]
        P --> ACP[ACP<br/>Agent Communication]
        P --> ANP[ANP<br/>Agent Network]

        MCP --> D1[Databases]
        MCP --> D2[APIs]
        MCP --> D3[File Systems]

        A2A --> AG1[Agent 1]
        A2A --> AG2[Agent 2]
        A2A --> AG3[Agent N]

        ACP --> T1[Task Queue]
        ACP --> T2[Workflow Engine]

        ANP --> N1[Agent Network]
        ANP --> N2[Discovery Service]
    end

    style MCP fill:#ff00ff,stroke:#00ffff,stroke-width:3px
    style A2A fill:#00ffff,stroke:#ff00ff,stroke-width:3px
    style ACP fill:#ffff00,stroke:#ff00ff,stroke-width:3px
    style ANP fill:#00ff00,stroke:#ff00ff,stroke-width:3px
```

## 1. MCP (Model Context Protocol)

**Creator:** Anthropic
**Released:** November 2024
**Status:** Industry standard (adopted by OpenAI, Google in 2025)

### Overview

MCP standardizes how AI assistants connect to data sources, enabling seamless integration with content repositories, business tools, and development environments.

### Architecture

```mermaid
graph LR
    subgraph "MCP Architecture"
        Client[AI Assistant<br/>Claude/GPT-4] --> MCP_Client[MCP Client]
        MCP_Client <-->|JSON-RPC 2.0| MCP_Server[MCP Server]
        MCP_Server --> Resources[Resources<br/>Files, Data]
        MCP_Server --> Tools[Tools<br/>Functions]
        MCP_Server --> Prompts[Prompts<br/>Templates]
    end

    style MCP_Client fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style MCP_Server fill:#00ffff,stroke:#ff00ff,stroke-width:2px
```

### Key Features

**1. Resources** - Read-only data sources
```json
{
  "resource": {
    "uri": "file:///project/README.md",
    "mimeType": "text/markdown",
    "text": "# Project Documentation..."
  }
}
```

**2. Tools** - Executable functions
```json
{
  "tool": {
    "name": "search_database",
    "description": "Search the product database",
    "inputSchema": {
      "type": "object",
      "properties": {
        "query": {"type": "string"}
      }
    }
  }
}
```

**3. Prompts** - Reusable templates
```json
{
  "prompt": {
    "name": "code_review",
    "description": "Review code for best practices",
    "arguments": ["file_path", "language"]
  }
}
```

### MCP Communication Flow

```mermaid
sequenceDiagram
    participant C as Claude/GPT-4
    participant MC as MCP Client
    participant MS as MCP Server
    participant DB as Database

    C->>MC: Request data
    MC->>MS: list_resources()
    MS->>MC: Available resources
    MC->>C: Show options

    C->>MC: Read resource
    MC->>MS: resources/read
    MS->>DB: Query
    DB->>MS: Data
    MS->>MC: Resource content
    MC->>C: Display data

    Note over MC,MS: JSON-RPC 2.0
```

### Real-World MCP Servers

**Popular MCP Servers (2025):**
- **@modelcontextprotocol/server-filesystem** - File system access
- **@modelcontextprotocol/server-github** - GitHub integration
- **@modelcontextprotocol/server-postgres** - PostgreSQL database
- **@modelcontextprotocol/server-google-drive** - Google Drive
- **@modelcontextprotocol/server-slack** - Slack integration

### MCP Implementation Example

```python
# Simple MCP Server (Python)
from mcp import Server, Resource, Tool

server = Server("my-mcp-server")

@server.resource("config://settings")
async def get_settings():
    return {
        "uri": "config://settings",
        "mimeType": "application/json",
        "text": '{"theme": "dark", "language": "en"}'
    }

@server.tool("calculate")
async def calculate(expression: str):
    """Safely evaluate math expressions"""
    # Implementation here
    return {"result": eval(expression)}

# Run server
server.run()
```

### Security Concerns (2025 Research)

⚠️ **Critical Issues:**
- **No authentication** - Most public MCP servers lack auth
- **Prompt injection** - Malicious prompts can exploit tools
- **Tool permissions** - Combining tools can exfiltrate data
- **Lookalike tools** - Malicious tools can replace trusted ones

**Best Practices:**
```mermaid
graph TD
    S1[Implement Authentication] --> S2[Rate Limiting]
    S2 --> S3[Input Validation]
    S3 --> S4[Principle of Least Privilege]
    S4 --> S5[Audit Logging]
    S5 --> S6[Sandboxed Execution]

    style S1 fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style S6 fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

## 2. A2A (Agent-to-Agent Protocol)

**Creator:** Google
**Released:** April 2025
**Status:** Growing adoption (Microsoft joined working group)

### Overview

A2A defines how autonomous agents interact directly, enabling coordination, task delegation, and outcome tracking.

### Architecture

```mermaid
graph TB
    subgraph "A2A Communication"
        A1[Agent 1<br/>Research] -->|Request| A2A_Layer[A2A Protocol Layer]
        A2A_Layer -->|Task| A2[Agent 2<br/>Analysis]
        A2 -->|Status| A2A_Layer
        A2A_Layer -->|Result| A1

        A2A_Layer --> Msg[Message Format]
        A2A_Layer --> Intent[Intent Sharing]
        A2A_Layer --> Track[Task Tracking]
    end

    style A2A_Layer fill:#00ffff,stroke:#ff00ff,stroke-width:3px
```

### Message Structure

```json
{
  "protocol": "a2a",
  "version": "1.0",
  "from": "research-agent-001",
  "to": "analysis-agent-002",
  "messageType": "task_request",
  "payload": {
    "taskId": "task-123",
    "action": "analyze_data",
    "data": {...},
    "priority": "high",
    "deadline": "2025-11-08T18:00:00Z"
  },
  "tracking": {
    "correlationId": "corr-456",
    "timestamp": "2025-11-08T12:00:00Z"
  }
}
```

### A2A Communication Patterns

```mermaid
sequenceDiagram
    participant A1 as Agent 1<br/>(Coordinator)
    participant A2 as Agent 2<br/>(Worker)
    participant A3 as Agent 3<br/>(Specialist)

    A1->>A2: Task Request
    A2->>A1: Acknowledgment
    A2->>A3: Sub-task Delegation
    A3->>A2: Sub-task Complete
    A2->>A1: Task Complete
    A1->>A2: Feedback

    Note over A1,A3: All via A2A Protocol
```

### Use Cases

1. **Multi-Agent Research**
   - Coordinator agent delegates to research, analysis, and writing agents

2. **Distributed Processing**
   - Load balancing across multiple agent instances

3. **Specialized Collaboration**
   - Agents with different capabilities work together

## 3. ACP (Agent Communication Protocol)

**Creator:** IBM
**Released:** 2024
**Focus:** Enterprise task coordination

### Key Features

- **Workflow Integration** - Connects with enterprise workflow engines
- **Task Queues** - Asynchronous task processing
- **State Management** - Maintains agent and task states
- **Enterprise Security** - Built-in authentication and authorization

## 4. ANP (Agent Network Protocol)

**Status:** Emerging community standard
**Focus:** Agent discovery and networking

### Features

- **Agent Discovery** - Find agents by capabilities
- **Capability Negotiation** - Determine agent abilities
- **Network Topology** - Manage agent networks

## Protocol Comparison

| Feature | MCP | A2A | ACP | ANP |
|---------|-----|-----|-----|-----|
| **Purpose** | Data integration | Agent communication | Task coordination | Agent discovery |
| **Transport** | JSON-RPC 2.0 | Custom | Enterprise bus | Network protocol |
| **Adoption** | Very High | Growing | Enterprise | Emerging |
| **Complexity** | Low | Medium | High | Medium |
| **Best For** | Connecting to data | Multi-agent systems | Enterprise workflows | Large agent networks |

## When to Use Which Protocol

```mermaid
graph TD
    Start{What's your need?} --> Data{Connecting to<br/>data sources?}
    Start --> Agents{Multiple agents<br/>collaborating?}
    Start --> Enterprise{Enterprise<br/>workflows?}
    Start --> Discovery{Agent<br/>discovery?}

    Data --> MCP_Use[Use MCP]
    Agents --> A2A_Use[Use A2A]
    Enterprise --> ACP_Use[Use ACP]
    Discovery --> ANP_Use[Use ANP]

    style MCP_Use fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style A2A_Use fill:#00ffff,stroke:#ff00ff,stroke-width:2px
    style ACP_Use fill:#ffff00,stroke:#ff00ff,stroke-width:2px
    style ANP_Use fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

## Combining Protocols

Most production systems use multiple protocols:

```mermaid
graph TB
    subgraph "Production Agent System"
        User[User] --> Agent1[Coordinator Agent]

        Agent1 -->|A2A| Agent2[Research Agent]
        Agent1 -->|A2A| Agent3[Analysis Agent]

        Agent2 -->|MCP| DB1[(Database)]
        Agent2 -->|MCP| API1[External API]

        Agent3 -->|MCP| Files[File System]

        Agent1 -->|ACP| Workflow[Enterprise Workflow]
    end

    style Agent1 fill:#ff00ff,stroke:#00ffff,stroke-width:3px
```

## Future Trends

1. **Protocol Convergence** - Standards bodies working on unified approach
2. **Enhanced Security** - Better authentication and authorization
3. **Performance Optimization** - Faster message passing
4. **Cross-Platform** - Better interoperability between vendors

## Practical Next Steps

1. **Start with MCP** - Easiest to learn and widely supported
2. **Add A2A** - When you need multi-agent coordination
3. **Consider ACP** - For enterprise integrations
4. **Explore ANP** - For large-scale agent networks

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [A2A GitHub](https://github.com/google/agent-to-agent)
- [MCP Python SDK](https://github.com/anthropics/python-sdk)
- [MCP TypeScript SDK](https://github.com/anthropics/typescript-sdk)

---

**Previous:** [← Overview](01-overview.md) | **Next:** [RAG Systems →](03-rag-systems.md)
