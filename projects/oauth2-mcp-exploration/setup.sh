#!/bin/bash
# Setup script for OAuth 2.0 MCP Exploration

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🔐 OAuth 2.0 MCP Exploration - Setup                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Node.js version
echo "📋 Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "   Please install Node.js 20.11 or higher"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "❌ Node.js version must be >= 20.11"
    echo "   Current version: $(node -v)"
    echo "   Please upgrade Node.js"
    exit 1
fi

echo "✓ Node.js version: $(node -v)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# OAuth 2.0 Configuration

# Authorization Server
AUTH_SERVER_URL=http://localhost:4000

# Resource Server
RESOURCE_SERVER_URL=http://localhost:4001

# MCP Client
MCP_CLIENT_ID=mcp-task-manager
MCP_CLIENT_SECRET=mcp-secret-12345

# Agent Client
AGENT_CLIENT_ID=ai-agent-assistant
AGENT_CLIENT_SECRET=agent-secret-67890

# JWT Secret (CHANGE IN PRODUCTION!)
JWT_SECRET=your-super-secret-jwt-key-change-in-production
EOF
    echo "✓ .env file created"
else
    echo "ℹ️  .env file already exists, skipping"
fi
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                      ║"
echo "╟──────────────────────────────────────────────────────────╢"
echo "║  Next steps:                                             ║"
echo "║                                                          ║"
echo "║  1. Start the auth server:                               ║"
echo "║     npm run dev:auth                                     ║"
echo "║                                                          ║"
echo "║  2. Start the resource server (new terminal):            ║"
echo "║     npm run dev:resource                                 ║"
echo "║                                                          ║"
echo "║  3. Run the agent demo (new terminal):                   ║"
echo "║     npm run dev:agent                                    ║"
echo "║                                                          ║"
echo "║  Or start all servers:                                   ║"
echo "║     npm run dev:all                                      ║"
echo "║                                                          ║"
echo "║  📚 Read the docs:                                       ║"
echo "║     - README.md                                          ║"
echo "║     - docs/learning-guide.md                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
