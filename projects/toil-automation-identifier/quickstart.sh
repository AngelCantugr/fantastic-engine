#!/bin/bash
# Quickstart script for Toil Automation Identifier

set -e

echo "🤖 Toil Automation Identifier - Quickstart"
echo "==========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo

# Check if in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    echo "   Run this from within a git repository, or use --repo option"
    exit 1
fi

echo "✓ Git repository detected"
echo

# Offer to create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✓ Dependencies installed"
echo

# Run demo
echo "🎯 Running demo to show example output..."
echo
python3 demo.py

echo
echo "=========================================="
echo "🎉 Setup complete!"
echo
echo "To analyze YOUR repository:"
echo "  1. Activate venv: source .venv/bin/activate"
echo "  2. Run: python main.py"
echo "  3. Or: python main.py --commits 500"
echo "  4. Help: python main.py --help"
echo
echo "To deactivate venv: deactivate"
