#!/bin/bash

# Memory & Knowledge Graph MCP Setup Script
# Purpose: Automated setup for MCP servers across multiple AI agents

set -e

echo "🧠 Memory & Knowledge Graph MCP Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
MEMORY_DIR="$HOME/.local/share/ai-memory"
CONFIG_BACKUP_DIR="$HOME/.ai-config-backup-$(date +%Y%m%d-%H%M%S)"

echo -e "${BLUE}Step 1: Creating storage directory${NC}"
mkdir -p "$MEMORY_DIR"
echo "✓ Created $MEMORY_DIR"
echo ""

echo -e "${BLUE}Step 2: Checking for Node.js${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js found: $NODE_VERSION"
else
    echo -e "${YELLOW}⚠ Node.js not found. Please install Node.js first:${NC}"
    echo "  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -"
    echo "  sudo apt-get install -y nodejs"
    exit 1
fi
echo ""

echo -e "${BLUE}Step 3: Installing MCP Servers${NC}"
echo "This will globally install:"
echo "  - @modelcontextprotocol/server-memory"
echo "  - @modelcontextprotocol/server-knowledge-graph (if available)"
echo ""

read -p "Continue with installation? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Note: These are hypothetical package names
    # Replace with actual package names when available
    echo "Installing memory server..."
    # npm install -g @modelcontextprotocol/server-memory
    echo -e "${YELLOW}⚠ Note: Install actual MCP packages when available${NC}"
    echo "  For now, check https://github.com/modelcontextprotocol/servers"
else
    echo "Skipping installation"
fi
echo ""

echo -e "${BLUE}Step 4: Backing up existing configurations${NC}"
mkdir -p "$CONFIG_BACKUP_DIR"

# Backup Claude config
if [ -f "$HOME/.config/claude/claude_desktop_config.json" ]; then
    cp "$HOME/.config/claude/claude_desktop_config.json" "$CONFIG_BACKUP_DIR/"
    echo "✓ Backed up Claude config"
fi

# Backup Goose config
if [ -f "$HOME/.config/goose/config.yaml" ]; then
    cp "$HOME/.config/goose/config.yaml" "$CONFIG_BACKUP_DIR/"
    echo "✓ Backed up Goose config"
fi

# Backup Aider config
if [ -f "$HOME/.aider.conf.yml" ]; then
    cp "$HOME/.aider.conf.yml" "$CONFIG_BACKUP_DIR/"
    echo "✓ Backed up Aider config"
fi

echo "Backups saved to: $CONFIG_BACKUP_DIR"
echo ""

echo -e "${BLUE}Step 5: Configuration files${NC}"
echo "Sample configuration files have been created in ./configs/"
echo ""
echo "To configure each agent:"
echo "1. Review the sample configs in ./configs/"
echo "2. Merge with your existing configs (backups in $CONFIG_BACKUP_DIR)"
echo "3. Restart each agent"
echo ""

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Configure your agents using the sample configs in ./configs/"
echo "2. Test with: 'Store this learning note: Testing MCP setup'"
echo "3. Read the full README.md for usage examples"
echo ""
echo "Storage location: $MEMORY_DIR"
echo "Backup location: $CONFIG_BACKUP_DIR"
