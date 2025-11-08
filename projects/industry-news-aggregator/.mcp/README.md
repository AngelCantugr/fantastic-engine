# MCP Configuration for Industry News Aggregator

This directory contains MCP (Model Context Protocol) server configurations for the news aggregator tool.

## Required MCP Servers

1. **Brave Search** - Web search capabilities
2. **Perplexity** - AI-powered search and summaries
3. **Memory** - Context persistence for follow-up questions
4. **Knowledge Graph** - Relationship tracking between topics

## Setup Instructions

### 1. Install Required API Keys

You'll need API keys for:

- **Brave Search API**: Get from https://brave.com/search/api/
- **Perplexity API**: Get from https://www.perplexity.ai/settings/api

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export BRAVE_API_KEY="your-brave-api-key"
export PERPLEXITY_API_KEY="your-perplexity-api-key"
```

### 2. Configure Your AI Tool

#### For Claude Code

Add to your `~/.config/claude/config.json`:

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
        "MEMORY_STORAGE_PATH": "/path/to/fantastic-engine/projects/industry-news-aggregator/data/memory"
      }
    }
  }
}
```

#### For Goose Desktop

Add to your Goose configuration (usually `~/.config/goose/config.yaml`):

```yaml
mcp_servers:
  - name: brave-search
    command: npx
    args: ["-y", "@modelcontextprotocol/server-brave-search"]
    env:
      BRAVE_API_KEY: ${BRAVE_API_KEY}

  - name: perplexity
    command: npx
    args: ["-y", "@modelcontextprotocol/server-perplexity"]
    env:
      PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY}

  - name: memory
    command: npx
    args: ["-y", "@modelcontextprotocol/server-memory"]
    env:
      MEMORY_STORAGE_PATH: /path/to/fantastic-engine/projects/industry-news-aggregator/data/memory
```

#### For GitHub Copilot CLI / Opencode

These tools may have different MCP integration methods. Refer to their documentation for MCP server configuration.

### 3. Verify MCP Servers

After configuration, verify the servers are accessible:

```bash
# Test Brave Search MCP
npx -y @modelcontextprotocol/server-brave-search --help

# Test Perplexity MCP
npx -y @modelcontextprotocol/server-perplexity --help

# Test Memory MCP
npx -y @modelcontextprotocol/server-memory --help
```

## Storage Locations

- **Memory Storage**: `../data/memory/`
- **Knowledge Graph**: `../data/memory/knowledge-graph.json`
- **Outputs**: `../data/outputs/`

All storage is git-trackable for version control and history.

## Troubleshooting

### MCP Server Not Found

```bash
# Install Node.js if needed
nvm install 18
nvm use 18

# npx will auto-install MCP servers on first use
```

### API Key Errors

Verify your environment variables are set:

```bash
echo $BRAVE_API_KEY
echo $PERPLEXITY_API_KEY
```

### Path Issues

Update the `MEMORY_STORAGE_PATH` to match your actual installation path of this repository.
