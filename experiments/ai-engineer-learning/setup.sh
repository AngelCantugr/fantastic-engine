#!/bin/bash

# 🤖 AI Engineer Learning Path - Setup Script
# This script sets up your environment for building AI agents with Ollama

set -e  # Exit on error

echo "🚀 Setting up AI Engineer Learning Environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Ollama is installed
echo "📦 Checking prerequisites..."
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama is not installed!${NC}"
    echo "Please install Ollama from: https://ollama.ai"
    exit 1
else
    echo -e "${GREEN}✅ Ollama is installed${NC}"
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama is not running. Starting Ollama...${NC}"
    ollama serve &
    sleep 3
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"

# Create virtual environment
echo ""
echo "🐍 Creating Python virtual environment..."
if command -v uv &> /dev/null; then
    echo "Using uv (faster)..."
    uv venv
else
    echo "Using standard venv..."
    python3 -m venv .venv
fi
echo -e "${GREEN}✅ Virtual environment created${NC}"

# Activate virtual environment
echo ""
echo "📚 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo ""
echo "📦 Installing Python dependencies (this may take a few minutes)..."
pip install -r requirements.txt -q

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Pull recommended Ollama models
echo ""
echo "🤖 Pulling recommended Ollama models..."
echo ""

echo "Pulling qwen2.5-coder:7b (best for coding tasks)..."
ollama pull qwen2.5-coder:7b

echo ""
echo -e "${YELLOW}Optional: Would you like to pull additional models? (y/n)${NC}"
read -r PULL_MORE

if [[ $PULL_MORE =~ ^[Yy]$ ]]; then
    echo "Pulling qwen2.5:3b (faster, smaller model)..."
    ollama pull qwen2.5:3b

    echo "Pulling deepseek-r1:7b (advanced reasoning)..."
    ollama pull deepseek-r1:7b
fi

# Create shared configuration
echo ""
echo "⚙️  Creating shared configuration..."
cat > shared/config.py << 'EOF'
"""Shared configuration for all AI agents."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Global settings for AI agents."""

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "qwen2.5-coder:7b"
    OLLAMA_FAST_MODEL: str = "qwen2.5:3b"
    OLLAMA_REASONING_MODEL: str = "deepseek-r1:7b"

    # Model Parameters
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048
    STREAM_RESPONSES: bool = True

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    CACHE_DIR: Path = PROJECT_ROOT / ".cache"
    VECTOR_DB_DIR: Path = PROJECT_ROOT / ".vectordb"

    # Performance
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Create necessary directories
settings.CACHE_DIR.mkdir(exist_ok=True)
settings.VECTOR_DB_DIR.mkdir(exist_ok=True)
EOF

# Create shared utilities
cat > shared/ollama_client.py << 'EOF'
"""Shared Ollama client utilities."""

import httpx
from typing import Dict, Any, Iterator, Optional
from rich.console import Console
from config import settings

console = Console()

class OllamaClient:
    """Simple Ollama client wrapper."""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_DEFAULT_MODEL
        self.client = httpx.Client(timeout=settings.REQUEST_TIMEOUT)

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = None,
        stream: bool = True
    ) -> Iterator[str] | str:
        """Generate a response from Ollama."""

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature or settings.DEFAULT_TEMPERATURE,
                "num_predict": settings.MAX_TOKENS
            }
        }

        if stream:
            return self._stream_response(payload)
        else:
            return self._sync_response(payload)

    def _stream_response(self, payload: Dict[str, Any]) -> Iterator[str]:
        """Stream response from Ollama."""
        with self.client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload
        ) as response:
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "message" in data:
                        yield data["message"]["content"]

    def _sync_response(self, payload: Dict[str, Any]) -> str:
        """Get synchronous response from Ollama."""
        payload["stream"] = False
        response = self.client.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        return response.json()["message"]["content"]

    def check_health(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

EOF

echo -e "${GREEN}✅ Configuration created${NC}"

# Test installation
echo ""
echo "🧪 Testing installation..."
python3 << 'PYTEST'
import sys
try:
    import ollama
    import langchain
    import llama_index
    from rich.console import Console

    console = Console()
    console.print("[green]✅ All core libraries imported successfully![/green]")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
PYTEST

# Create .env template
echo ""
echo "📝 Creating .env template..."
cat > .env.example << 'EOF'
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen2.5-coder:7b

# Model Parameters
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=2048

# Optional: Add API keys for external services
# GITHUB_TOKEN=your_token_here
# ANTHROPIC_API_KEY=your_key_here
EOF

# Final message
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Setup complete! You're ready to build AI agents!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📚 Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo -e "   ${YELLOW}source .venv/bin/activate${NC}"
echo ""
echo "2. Start with Agent 1:"
echo -e "   ${YELLOW}cd agents/01_simple_chat${NC}"
echo -e "   ${YELLOW}python agent.py${NC}"
echo ""
echo "3. Read the documentation:"
echo -e "   ${YELLOW}cat agents/01_simple_chat/README.md${NC}"
echo ""
echo "4. Check available Ollama models:"
echo -e "   ${YELLOW}ollama list${NC}"
echo ""
echo "Happy learning! 🚀"
echo ""
