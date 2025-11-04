# Claude Code Configuration

This directory contains custom configurations for Claude Code to optimize the experiment workflow.

## Subagents

Custom subagents specialized for different tasks:

### 🎓 learn-assistant
**Use when:** You want to understand a new technology or concept

**Example:**
```
Help me learn about async/await in Rust
```

Provides:
- Clear, step-by-step explanations
- Visual diagrams
- Hands-on examples
- Learning paths
- ADHD-friendly presentation

### 🧪 experiment-guide
**Use when:** Setting up a new experiment or project

**Example:**
```
I want to experiment with web scraping in Python
```

Provides:
- Environment setup guidance
- Step-by-step implementation
- Time-boxed plans
- Quick wins first approach
- Documentation templates

### 💭 brainstorm-buddy
**Use when:** Exploring ideas and planning features

**Example:**
```
Let's brainstorm features for a personal task manager
```

Provides:
- Structured brainstorming
- Mind mapping
- Idea organization
- Prioritization frameworks
- Action item conversion

### 📝 doc-writer
**Use when:** Creating documentation for your project

**Example:**
```
Help me document this API I built
```

Provides:
- Documentation templates
- Visual diagrams
- Scannable formatting
- ADHD-optimized structure
- Quick reference sections

## How to Use Subagents

In Claude Code, mention the agent in your request:

```
@learn-assistant explain recursion
@experiment-guide set up a Deno project
@brainstorm-buddy help me plan app features
@doc-writer create a README for this project
```

Or just describe what you need, and Claude will choose the appropriate agent.

## Customization

You can edit these agent files to adjust their behavior to your preferences. Each agent file is a markdown document with specific instructions.

---

All agents are optimized for ADHD-friendly workflows with:
- Clear, concise communication
- Visual aids and diagrams
- Step-by-step guidance
- Time-boxing
- Quick wins focus
