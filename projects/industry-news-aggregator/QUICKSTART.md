# ⚡ Quick Start Guide

Get up and running with the Industry News Aggregator in 5 minutes.

## 🎯 Prerequisites

- Node.js 18+ (for MCP servers via npx)
- Python 3.11+ (for catalog scripts - optional)
- One of these AI assistants:
  - Claude Code (recommended)
  - GitHub Copilot CLI
  - Goose Desktop
  - Opencode

## 📝 Step 1: Get API Keys (5 minutes)

### Brave Search API (Required)

1. Go to https://brave.com/search/api/
2. Sign up for free tier (2000 queries/month)
3. Copy your API key

### Perplexity API (Required)

1. Go to https://www.perplexity.ai/settings/api
2. Sign up and get API key
3. Copy your API key

### Add to Environment

```bash
# Add to ~/.bashrc or ~/.zshrc
export BRAVE_API_KEY="your-brave-api-key-here"
export PERPLEXITY_API_KEY="your-perplexity-api-key-here"

# Reload your shell
source ~/.bashrc  # or source ~/.zshrc
```

## ⚙️ Step 2: Configure MCP Servers (2 minutes)

### For Claude Code

Edit `~/.config/claude/config.json` and add:

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-perplexity"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_STORAGE_PATH": "/absolute/path/to/fantastic-engine/projects/industry-news-aggregator/data/memory"
      }
    }
  }
}
```

**IMPORTANT**: Replace `/absolute/path/to/` with your actual path!

### For Goose Desktop

See [.mcp/README.md](.mcp/README.md) for Goose configuration.

## ✏️ Step 3: Customize Your Preferences (1 minute)

Edit `user-preferences.json`:

```json
{
  "interests": {
    "primary_topics": [
      "YOUR TOPICS HERE",
      "e.g., artificial intelligence",
      "web development"
    ]
  }
}
```

## 🚀 Step 4: Try It Out!

### Using Claude Code

```bash
cd /path/to/fantastic-engine/projects/industry-news-aggregator

# Start Claude Code
claude

# In Claude Code prompt:
"Use the industry-news-aggregator skill to catch me up on AI developments from this week"
```

### Using Direct Prompts (Any AI Assistant)

```
I want to catch up on [YOUR TOPIC] from the last week.

Please:
1. Use Brave Search MCP to find recent articles
2. Use Perplexity MCP for curated insights
3. Filter based on my interests in user-preferences.json
4. Create a concise, scannable summary
5. Save everything:
   - Raw results to data/raw/
   - Summary to data/summaries/
   - Update data/catalog.json
6. Store context in Memory MCP for follow-ups

Format the summary with:
- 🔥 Top highlights (must read)
- 📊 Trend analysis
- 🎯 Relevance to my interests
- 🤔 Follow-up questions
- 📚 Source links
```

## ✅ Verify It's Working

After your first search, you should see:

```bash
# Check catalog was updated
cat data/catalog.json

# List summaries
ls data/summaries/

# View your first summary
cat data/summaries/2025-11-08-*.md
```

## 📖 Example Usage

```
User: "Catch me up on Claude AI developments this month"

AI: I'll search for Claude AI developments from the last month.

[Uses Brave MCP and Perplexity MCP]
[Creates summary]
[Saves to files]
[Updates catalog]

Here's your summary:

# Industry News Summary: Claude AI Developments
**Date**: 2025-11-08
**Coverage**: Last 30 days
...
```

## 🔄 Follow-up Questions

Thanks to Memory MCP, you can ask follow-ups:

```
User: "Tell me more about the computer use feature mentioned"

AI: [Retrieves from memory] The computer use feature...
```

## 🛠️ Using Helper Scripts (Optional)

```bash
# Search past summaries
./scripts/catalog_manager.py search --query "Claude"

# View catalog report
./scripts/catalog_manager.py topics

# Get specific entry
./scripts/catalog_manager.py get ENTRY_ID --summary
```

## 🆘 Troubleshooting

### "MCP server not found"

```bash
# Test MCP installation
npx -y @modelcontextprotocol/server-brave-search --help
```

### "API key not set"

```bash
# Verify environment variables
echo $BRAVE_API_KEY
echo $PERPLEXITY_API_KEY
```

### "Memory not persisting"

Check that `MEMORY_STORAGE_PATH` in your config points to the correct absolute path.

## 🎉 You're Ready!

Start exploring:
- Try different topics
- Adjust your preferences
- Search the catalog
- Ask follow-up questions

---

**Next**: Read the full [README.md](README.md) for advanced usage and customization.
