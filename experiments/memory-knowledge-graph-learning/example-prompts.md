# Example Prompts for Memory & Knowledge Graph MCP

**Purpose:** Copy-paste prompts to effectively use Memory and Knowledge Graph MCPs across different agents.

## Memory MCP Prompts

### Storing Learning Notes

```
Store this learning note: [Your learning here]
Tags: [comma, separated, tags]

Example:
Store this learning note: In Rust, async functions return Future types that must be awaited. Use tokio::main macro for async main function.
Tags: rust, async, tokio, fundamentals
```

### Retrieving Context

```
What have I learned about [topic]?

Examples:
- What have I learned about Rust async programming?
- Show me my notes on kubernetes deployments
- What solutions did I find for database connection pooling?
```

### Storing Code Solutions

```
Remember this code solution:
Problem: [description]
Language: [language]
Solution: [code]
Tags: [tags]

Example:
Remember this code solution:
Problem: Creating a basic async HTTP server in Rust
Language: Rust
Solution:
```rust
use axum::{routing::get, Router};

#[tokio::main]
async fn main() {
    let app = Router::new().route("/", get(|| async { "Hello!" }));
    axum::Server::bind(&"0.0.0.0:3000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}
```
Tags: rust, axum, http-server, async
```

### Session Context Handoff

```
Summarize what I've been working on today for the next agent

OR

Load my most recent work session and continue where I left off
```

### Goal Tracking

```
Set learning goal: [Your goal]

Example:
Set learning goal: Master Rust web development with Axum framework by building 3 production-ready APIs

---

Check my progress on: [goal]

Example:
Check my progress on: Rust web development
```

## Knowledge Graph Prompts

### Creating Concept Nodes

```
Add concept to knowledge graph:
Name: [concept name]
Type: [technology|pattern|tool|language|framework]
Description: [brief description]
Difficulty: [beginner|intermediate|advanced]

Example:
Add concept to knowledge graph:
Name: Tokio
Type: framework
Description: Async runtime for Rust, enables concurrent I/O operations
Difficulty: intermediate
```

### Creating Relationships

```
Link concepts in knowledge graph:
From: [concept A]
To: [concept B]
Relationship: [prerequisite|enables|implements|uses|related-to]

Example:
Link concepts in knowledge graph:
From: Rust Basics
To: Ownership Model
Relationship: prerequisite

Link concepts in knowledge graph:
From: Async/Await
To: Tokio
Relationship: implements
```

### Querying the Graph

```
Show me the learning path for [topic]

Example:
Show me the learning path for Rust async programming

---

What concepts are related to [topic]?

Example:
What concepts are related to error handling in Rust?

---

What do I need to learn before [advanced topic]?

Example:
What do I need to learn before building production Rust APIs?
```

### Finding Knowledge Gaps

```
Analyze my knowledge graph for [domain] and show gaps

Example:
Analyze my knowledge graph for web development and show what I'm missing
```

## Multi-Agent Workflow Prompts

### Starting a Learning Session (Claude Code)

```
I want to learn [topic].
- Store this as my current learning goal
- Create initial concepts in the knowledge graph
- Map out what I should learn first

Example:
I want to learn microservices architecture with Rust.
- Store this as my current learning goal
- Create initial concepts in the knowledge graph
- Map out what I should learn first
```

### Switching to Experimentation (Goose)

```
Load my current learning context and help me build a hands-on example

OR

I'm learning [topic]. Check my knowledge graph and memory, then suggest a practical project to build
```

### Code Implementation (Aider)

```
I need to implement [feature].
- Check my memory for related patterns I've used before
- Check knowledge graph for dependencies
- Implement using established patterns

Example:
I need to implement JWT authentication in my Rust API.
- Check my memory for related patterns I've used before
- Check knowledge graph for dependencies
- Implement using established patterns
```

### Review Session (Claude Code)

```
Review my [topic] learning progress:
- What have I learned?
- What have I built?
- What should I learn next?
- Update my knowledge graph

Example:
Review my Rust learning progress:
- What have I learned?
- What have I built?
- What should I learn next?
- Update my knowledge graph
```

### Debugging with Context (Any Agent)

```
I'm getting [error/issue].
- Check my memory for similar issues
- Query knowledge graph for related concepts
- Suggest solutions based on what I already know

Example:
I'm getting "cannot borrow as mutable" error in Rust.
- Check my memory for similar issues
- Query knowledge graph for related concepts
- Suggest solutions based on what I already know
```

## Daily Workflow Templates

### Morning Kickoff

```
Good morning!
- What was I working on yesterday?
- What's my current learning goal?
- What should I focus on today?
```

### End of Day Wrap-up

```
End of day summary:
- Store what I learned today
- Update knowledge graph with new connections
- Set priorities for tomorrow
- Save any unsolved problems for next session
```

### Weekly Review

```
Weekly learning review:
- What did I learn this week?
- How has my knowledge graph grown?
- What patterns/solutions did I discover?
- What should I focus on next week?
- Export knowledge graph snapshot
```

## Advanced Patterns

### Creating a Learning Pathway

```
Create a learning pathway in the knowledge graph:
Topic: [main topic]
Current level: [beginner|intermediate|advanced]
Goal: [what you want to achieve]

Then map out:
1. Fundamentals (prerequisites)
2. Core concepts
3. Advanced topics
4. Practical applications
5. Mastery indicators

Store each step with resources and practice projects
```

### Cross-Domain Learning

```
I'm learning [topic A] and [topic B].
- Find connections between these domains in my knowledge graph
- Suggest how learning one helps with the other
- Create cross-links in the graph

Example:
I'm learning Rust systems programming and Kubernetes.
- Find connections between these domains
- Suggest how learning one helps with the other
- Create cross-links (e.g., "Rust can build K8s controllers")
```

### Pattern Recognition

```
Analyze my stored code solutions for common patterns.
What patterns do I use frequently?
Store these as reusable templates.

Example:
Analyze my stored API implementations.
What patterns do I use for error handling?
Create a template for future APIs.
```

## Prompt Modifiers for Better Results

### For Memory Storage

- Be specific with tags (improves retrieval)
- Include context (why this matters, when to use)
- Rate importance (critical, useful, reference)
- Link to related memories

### For Knowledge Graph

- Use consistent naming conventions
- Specify relationship types clearly
- Include difficulty levels
- Mark practical vs theoretical concepts
- Tag with domains (web, systems, data, etc.)

### For Cross-Agent Handoffs

- Explicitly request context transfer
- Specify what type of work to continue
- Mention which agent last worked on it
- Request relevant memory/graph queries

## Example: Complete Learning Session

```markdown
=== SESSION START (Claude Code) ===

Prompt: "I want to learn Rust error handling. Store this as today's learning goal and create initial knowledge graph nodes."

Claude Code:
- Stores goal in Memory
- Creates nodes: Rust, Error Handling, Result Type, Option Type
- Provides initial explanation
- Stores explanation in Memory

=== SWITCH TO EXPERIMENTATION (Goose) ===

Prompt: "Load my current learning goal. Help me build examples of error handling patterns."

Goose:
- Retrieves goal from Memory
- Queries Knowledge Graph for Error Handling
- Builds practical examples
- Stores examples in Memory
- Updates graph with new learnings

=== SWITCH TO IMPLEMENTATION (Aider) ===

Prompt: "I need to add error handling to my API. Check my memory for Rust error patterns and implement them."

Aider:
- Retrieves error handling patterns from Memory
- Implements in codebase
- Stores implementation notes

=== REVIEW (Claude Code) ===

Prompt: "Review my Rust error handling learning. Update knowledge graph and suggest next steps."

Claude Code:
- Reviews all memories from session
- Updates knowledge graph completeness
- Identifies: Result Type ✅, Option Type ✅, Custom Errors ⏭️ (next)
- Stores review notes

=== SESSION END ===
```

---

**Pro Tips:**

1. **Be explicit:** Always mention "store in memory" or "update knowledge graph" when you want persistence
2. **Use tags liberally:** Makes retrieval much easier later
3. **Create relationships:** Don't just store facts, connect them
4. **Review regularly:** Weekly reviews strengthen the knowledge graph
5. **Cross-reference:** Link new learnings to existing nodes in the graph
