# 🔧 Shared Utilities

**Status:** 🚧 In Progress
**Purpose:** Common utilities and helpers for ADHD productivity and learning tools

## Contents

- **ai_helpers.py** - OpenAI and Ollama integration helpers
- **config.py** - Configuration management
- **cli_helpers.py** - Rich CLI utilities
- **obsidian_helpers.py** - Obsidian markdown file operations
- **ticktick_helpers.py** - TickTick MCP integration
- **logging_helpers.py** - Structured logging

## Usage

```python
from shared_utils.ai_helpers import get_openai_client, get_ollama_client
from shared_utils.cli_helpers import create_panel, create_progress
from shared_utils.obsidian_helpers import read_vault, parse_tasks
```

## Tech Stack

- Python 3.11+
- OpenAI SDK
- Ollama Python SDK
- Rich (Terminal UI)
- Typer (CLI framework)
