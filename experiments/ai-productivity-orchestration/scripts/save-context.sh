#!/bin/bash
# save-context.sh - Save current work context to paste into Memory MCP
# Part of AI Productivity Orchestration experiment

echo "💾 Context Saver for Memory MCP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This script helps you format context to save in Memory MCP"
echo ""

# Get session info
read -p "📌 What are you working on? " task
echo ""
read -p "📝 Current progress summary: " progress
echo ""
read -p "🎯 What's next? " next
echo ""
read -p "🏷️  Tags (comma-separated, e.g., rust,authentication,learning): " tags
echo ""

# Optional blockers
read -p "🚧 Any blockers or questions? (press Enter to skip): " blockers
echo ""

# Generate timestamp
timestamp=$(date +"%Y-%m-%d %H:%M")

# Format for Memory MCP
context_file="/tmp/work-context-$(date +%Y%m%d-%H%M).txt"

cat > "$context_file" << EOF
=== WORK CONTEXT ===
Date: $timestamp
Task: $task
Tags: $tags

PROGRESS:
$progress

NEXT STEPS:
$next
EOF

if [ -n "$blockers" ]; then
  cat >> "$context_file" << EOF

BLOCKERS/QUESTIONS:
$blockers
EOF
fi

cat >> "$context_file" << EOF

---
Use this context to resume work in next session.
EOF

echo "✅ Context saved to: $context_file"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps:"
echo ""
echo "1. Open Claude Desktop"
echo "2. Say: 'Remember this context:'"
echo "3. Paste the content below:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$context_file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Tip: Claude Desktop will use Memory MCP to persist this"
echo "📁 File also saved at: $context_file"
echo ""

# Optionally copy to clipboard if pbcopy (macOS) or xclip (Linux) is available
if command -v pbcopy &> /dev/null; then
  cat "$context_file" | pbcopy
  echo "✨ Content copied to clipboard!"
elif command -v xclip &> /dev/null; then
  cat "$context_file" | xclip -selection clipboard
  echo "✨ Content copied to clipboard!"
fi
