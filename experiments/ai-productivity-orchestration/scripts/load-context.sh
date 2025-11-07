#!/bin/bash
# load-context.sh - Load saved context from Memory MCP
# Part of AI Productivity Orchestration experiment

echo "📥 Context Loader"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check for recent context files
echo "Recent context files:"
echo ""
ls -lt /tmp/work-context-*.txt 2>/dev/null | head -5 | awk '{print NR") " $9 " (" $6 " " $7 " " $8 ")"}'

if [ $? -ne 0 ] || [ $(ls /tmp/work-context-*.txt 2>/dev/null | wc -l) -eq 0 ]; then
  echo "No saved context files found."
  echo ""
  echo "💡 Use save-context.sh to create context files"
  exit 0
fi

echo ""
read -p "Select file number (or press Enter to use Claude Desktop Memory MCP): " file_num

if [ -z "$file_num" ]; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📋 To load from Memory MCP:"
  echo ""
  echo "1. Open Claude Desktop"
  echo "2. Say: 'What was I working on last session?'"
  echo "3. Or: 'Load my context about [topic/tag]'"
  echo ""
  echo "💡 Memory MCP will retrieve your saved context"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
  # Get the selected file
  selected_file=$(ls -lt /tmp/work-context-*.txt 2>/dev/null | head -5 | awk "NR==$file_num {print \$9}")

  if [ -n "$selected_file" ] && [ -f "$selected_file" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cat "$selected_file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 Context loaded from: $selected_file"

    # Copy to clipboard if available
    if command -v pbcopy &> /dev/null; then
      cat "$selected_file" | pbcopy
      echo "✨ Content copied to clipboard!"
    elif command -v xclip &> /dev/null; then
      cat "$selected_file" | xclip -selection clipboard
      echo "✨ Content copied to clipboard!"
    fi
  else
    echo "Invalid selection."
  fi
fi

echo ""
