# 🔧 AI Productivity Helper Scripts

These scripts help you work efficiently with multiple AI agents and MCP servers.

## 📋 Available Scripts

### 1. task-router.sh
**Purpose:** Helps you choose the right AI tool for your task

**Usage:**
```bash
./scripts/task-router.sh
```

**What it does:**
- Presents a menu of common tasks
- Recommends the best AI tool(s) for each task
- Provides step-by-step guidance

**When to use:**
- Unsure which AI tool to use
- Want to optimize tool selection
- Learning the orchestration system

---

### 2. save-context.sh
**Purpose:** Save your current work context to paste into Memory MCP

**Usage:**
```bash
./scripts/save-context.sh
```

**What it does:**
- Prompts for task, progress, next steps, and tags
- Formats context for Memory MCP
- Saves to `/tmp/work-context-[timestamp].txt`
- Copies to clipboard (if pbcopy/xclip available)

**When to use:**
- End of work session
- Before context switching
- Before taking a break
- End of day

**Example:**
```
Task: Implementing JWT authentication
Progress: Completed token generation, working on refresh logic
Next: Test token rotation, add error handling
Tags: auth, jwt, security
```

---

### 3. load-context.sh
**Purpose:** Load previously saved work context

**Usage:**
```bash
./scripts/load-context.sh
```

**What it does:**
- Lists recent context files
- Displays selected context
- Provides instructions for using with Claude Desktop
- Copies to clipboard (if available)

**When to use:**
- Starting work session
- Returning to paused task
- Context switching back to previous work

---

### 4. add-to-knowledge-graph.sh
**Purpose:** Format entries for Knowledge Graph MCP

**Usage:**
```bash
./scripts/add-to-knowledge-graph.sh
```

**What it does:**
- Prompts for concept details
- Formats entry for Knowledge Graph MCP
- Saves to `/tmp/kg-entry-[timestamp].txt`
- Copies to clipboard (if available)

**When to use:**
- After learning something new
- After solving a problem
- Discovered a useful pattern
- Want to remember a technique

**Example:**
```
Concept: Two Pointer Technique
Description: Algorithm pattern using two pointers to traverse array
Category: Design Pattern
Related: Arrays, Strings, Sliding Window
Insight: Reduces O(n²) to O(n) for many problems
```

---

## 🚀 Quick Start

### Make scripts executable (if not already):
```bash
chmod +x scripts/*.sh
```

### Try the task router:
```bash
./scripts/task-router.sh
```

### Save your first context:
```bash
./scripts/save-context.sh
```

### Add to knowledge graph:
```bash
./scripts/add-to-knowledge-graph.sh
```

---

## 🔄 Daily Workflow

### Morning Routine:
```bash
# 1. Load yesterday's context
./scripts/load-context.sh

# 2. Open Claude Desktop and paste context
# Say: "Load this context: [paste]"

# 3. Check what you need to do
./scripts/task-router.sh
```

### During Work:
- Use task router when unsure of tool selection
- Add insights to knowledge graph as you learn

### End of Day:
```bash
# Save context for tomorrow
./scripts/save-context.sh

# Open Claude Desktop and paste
# This persists in Memory MCP
```

---

## 💡 Pro Tips

### Context Saving
- **Be specific** with tags - easier to search later
- **Save often** - especially before breaks
- **Include blockers** - remember what you were stuck on

### Knowledge Graph
- **Build daily** - 5 minutes per day compounds
- **Link concepts** - relationships are key to retention
- **Add insights** - your unique learnings matter

### Task Routing
- **Use liberally** - builds good habits
- **Learn patterns** - you'll internalize over time
- **Customize** - edit scripts for your workflow

---

## 🛠️ Customization

These scripts are templates. Feel free to modify them for your needs:

```bash
# Copy and customize
cp scripts/save-context.sh scripts/save-context-custom.sh
# Edit to match your workflow
```

### Ideas for customization:
- Add project-specific tags
- Integrate with your task tracker
- Add git branch info to context
- Auto-commit context files to git
- Send context to external note-taking app

---

## 📝 Script Maintenance

### Context Files
Location: `/tmp/work-context-*.txt`

Clean up old files periodically:
```bash
# Remove context files older than 30 days
find /tmp -name "work-context-*.txt" -mtime +30 -delete
```

### Knowledge Graph Entries
Location: `/tmp/kg-entry-*.txt`

These are temporary - the real data is in Claude Desktop's Knowledge Graph MCP.

---

## 🐛 Troubleshooting

### Clipboard not working
If clipboard copy doesn't work:
- macOS: Install `brew install pbcopy` (usually pre-installed)
- Linux: Install `sudo apt-get install xclip`
- Manually copy from the output

### Scripts not executable
```bash
chmod +x scripts/*.sh
```

### Scripts not found
```bash
# Run from project root
cd /path/to/ai-productivity-orchestration
./scripts/task-router.sh
```

---

## 🔗 Related Documentation

- [ai-tool-integration-solution.md](../ai-tool-integration-solution.md) - Full integration guide
- [practical-use-cases.md](../practical-use-cases.md) - Real-world scenarios
- [ai-agent-testing-checklist.md](../ai-agent-testing-checklist.md) - Testing guide

---

## 🤝 Contributing

Have ideas for new scripts? Create them and share!

Useful script ideas:
- Daily metrics tracker
- Tool usage statistics
- Context search across history
- Knowledge graph query helper
- Multi-project context manager

---

**Remember:** These scripts are helpers, not required. Use what's useful, ignore the rest! 🚀
