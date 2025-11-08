# 🔌 MCP Configuration for Industry News Aggregator

This guide covers detailed setup for MCP (Model Context Protocol) servers across different AI assistants.

## 📋 Required MCP Servers

1. **Brave Search** - Web search capabilities
2. **Perplexity** - AI-powered search and summaries
3. **Memory** - Context persistence for follow-up questions
4. **Knowledge Graph** (Optional) - Relationship tracking between topics

## 🔑 API Keys Setup

### Brave Search API

1. Visit [https://brave.com/search/api/](https://brave.com/search/api/)
2. Sign up for an account
3. Choose the free tier:
   - 2,000 queries per month
   - Rate limit: 1 request per second
4. Copy your API key from the dashboard

### Perplexity API

1. Visit [https://www.perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
2. Sign up or log in
3. Navigate to API settings
4. Generate a new API key
5. Copy the key (shown only once!)

### Environment Variables

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.profile`):

```bash
# Industry News Aggregator - MCP API Keys
export BRAVE_API_KEY="your-brave-api-key-here"
export PERPLEXITY_API_KEY="your-perplexity-api-key-here"
```

Then reload:

```bash
source ~/.bashrc  # or your shell profile
```

Verify they're set:

```bash
echo $BRAVE_API_KEY
echo $PERPLEXITY_API_KEY
```

## 🛠️ Configuration by AI Assistant

### Claude Code

#### Location
`~/.config/claude/config.json`

#### Configuration

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "perplexity": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-perplexity"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "env": {
        "MEMORY_STORAGE_PATH": "/absolute/path/to/fantastic-engine/projects/industry-news-aggregator/data/memory"
      }
    },
    "knowledge-graph": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-knowledge-graph"
      ],
      "env": {
        "KNOWLEDGE_GRAPH_PATH": "/absolute/path/to/fantastic-engine/projects/industry-news-aggregator/data/memory/knowledge-graph.json"
      }
    }
  }
}
```

!!! warning "Path Configuration"
    Replace `/absolute/path/to/` with the actual absolute path to your `fantastic-engine` directory.

    To find it:
    ```bash
    cd /path/to/fantastic-engine
    pwd
    # Use the output in your config
    ```

### Goose Desktop

#### Location
`~/.config/goose/config.yaml` (or Goose's config location)

#### Configuration

```yaml
mcp_servers:
  - name: brave-search
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-brave-search"
    env:
      BRAVE_API_KEY: ${BRAVE_API_KEY}

  - name: perplexity
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-perplexity"
    env:
      PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY}

  - name: memory
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-memory"
    env:
      MEMORY_STORAGE_PATH: /absolute/path/to/fantastic-engine/projects/industry-news-aggregator/data/memory

  - name: knowledge-graph
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-knowledge-graph"
    env:
      KNOWLEDGE_GRAPH_PATH: /absolute/path/to/fantastic-engine/projects/industry-news-aggregator/data/memory/knowledge-graph.json
```

### GitHub Copilot CLI

!!! info "Copilot CLI MCP Support"
    As of now, GitHub Copilot CLI's MCP integration is evolving. Check the official documentation:
    - [GitHub Copilot Documentation](https://docs.github.com/en/copilot)

    You may need to use alternative methods or wait for full MCP support.

### Opencode

#### Configuration

Opencode typically uses a similar configuration format to Claude Code. Check the Opencode documentation for the exact config file location and format.

## 🧪 Testing MCP Servers

### Verify Installation

```bash
# Test Brave Search MCP
npx -y @modelcontextprotocol/server-brave-search --version

# Test Perplexity MCP
npx -y @modelcontextprotocol/server-perplexity --version

# Test Memory MCP
npx -y @modelcontextprotocol/server-memory --version
```

### Test API Connectivity

Create a test script `test-mcp.sh`:

```bash
#!/bin/bash

echo "Testing Brave Search API..."
curl -H "Accept: application/json" \
     -H "Accept-Encoding: gzip" \
     -H "X-Subscription-Token: $BRAVE_API_KEY" \
     "https://api.search.brave.com/res/v1/web/search?q=test&count=1"

echo -e "\n\nBrave API test complete."
```

Run:

```bash
chmod +x test-mcp.sh
./test-mcp.sh
```

## 📊 Storage Configuration

### Memory MCP Storage

```
projects/industry-news-aggregator/data/memory/
├── .gitkeep
├── context-*.json          # Conversation contexts
└── knowledge-graph.json    # Topic relationships
```

**Important**: This directory is git-tracked, so your memory persists across sessions and machines!

### Catalog Storage

```
projects/industry-news-aggregator/data/
├── raw/                    # Raw search results (JSON)
├── summaries/              # Processed summaries (Markdown)
├── outputs/                # Organized outputs
└── catalog.json            # Master index
```

## 🔍 Troubleshooting

### MCP Server Not Found

```bash
# Ensure Node.js is installed
node --version

# Should be 18.x or higher
# If not, install/update Node.js:
nvm install 18
nvm use 18
```

### API Authentication Failed

```bash
# Check API keys are set
echo $BRAVE_API_KEY
echo $PERPLEXITY_API_KEY

# If empty, add to shell profile and source it
```

### Memory Not Persisting

1. **Check path is absolute**:
   ```bash
   # ❌ Wrong
   MEMORY_STORAGE_PATH: "./data/memory"

   # ✅ Correct
   MEMORY_STORAGE_PATH: "/home/user/fantastic-engine/projects/industry-news-aggregator/data/memory"
   ```

2. **Verify directory exists**:
   ```bash
   ls -la /path/to/fantastic-engine/projects/industry-news-aggregator/data/memory/
   ```

3. **Check permissions**:
   ```bash
   chmod 755 /path/to/fantastic-engine/projects/industry-news-aggregator/data/memory/
   ```

### Rate Limiting

**Brave Search Free Tier**: 1 request per second

If you hit rate limits:
- Add delays between searches
- Upgrade to a paid tier
- Use Perplexity more heavily (different rate limits)

## 🔐 Security Best Practices

### API Key Management

!!! danger "Never Commit API Keys"
    - ❌ Don't hardcode keys in config files
    - ❌ Don't commit keys to git
    - ✅ Use environment variables
    - ✅ Use `.env` files (in `.gitignore`)

### Alternative: `.env` File

Create `/path/to/fantastic-engine/projects/industry-news-aggregator/.env`:

```bash
BRAVE_API_KEY=your-brave-key-here
PERPLEXITY_API_KEY=your-perplexity-key-here
```

Add to `.gitignore`:

```
.env
```

Load before using:

```bash
source .env
```

## 📚 MCP Server Documentation

- [Brave Search MCP](https://github.com/modelcontextprotocol/server-brave-search)
- [Perplexity MCP](https://github.com/modelcontextprotocol/server-perplexity)
- [Memory MCP](https://github.com/modelcontextprotocol/server-memory)
- [Knowledge Graph MCP](https://github.com/modelcontextprotocol/server-knowledge-graph)

## 🔄 Updating MCP Servers

MCP servers installed via `npx -y` are automatically updated to the latest version on each run.

To force a specific version:

```json
{
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-brave-search@1.2.3"
  ]
}
```

## ✅ Verification Checklist

Before using the aggregator, verify:

- [ ] API keys set in environment
- [ ] MCP servers install successfully via npx
- [ ] Config file has absolute paths
- [ ] Memory storage directory exists
- [ ] Test API connectivity works
- [ ] Shell profile sourced and reloaded

---

**Next Steps**:

- Return to [Quick Start Guide](industry-news-aggregator-quickstart.md)
- Read the [Full Documentation](industry-news-aggregator.md)
