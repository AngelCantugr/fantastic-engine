#!/bin/bash
# add-to-knowledge-graph.sh - Quick knowledge graph entry formatter
# Part of AI Productivity Orchestration experiment

echo "🧠 Knowledge Graph Entry Helper"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get concept details
read -p "📚 Concept/Topic name: " concept
echo ""
read -p "📝 Brief description: " description
echo ""
read -p "🔗 Related concepts (comma-separated): " related
echo ""

# Category selection
echo "🏷️  Select category:"
echo "1) Programming Language"
echo "2) Framework/Library"
echo "3) Design Pattern"
echo "4) Tool/Service"
echo "5) Concept/Theory"
echo "6) Best Practice"
echo "7) Debugging Technique"
echo "8) Other"
echo ""
read -p "Choose (1-8): " cat_choice

case $cat_choice in
  1) category="Programming Language" ;;
  2) category="Framework/Library" ;;
  3) category="Design Pattern" ;;
  4) category="Tool/Service" ;;
  5) category="Concept/Theory" ;;
  6) category="Best Practice" ;;
  7) category="Debugging Technique" ;;
  8)
    read -p "Enter custom category: " category
    ;;
  *) category="Uncategorized" ;;
esac

echo ""
read -p "💡 Key insight or learning: " insight
echo ""
read -p "🔍 Where did you learn this? (optional): " source
echo ""

# Generate entry
timestamp=$(date +"%Y-%m-%d")
entry_file="/tmp/kg-entry-$(date +%Y%m%d-%H%M).txt"

cat > "$entry_file" << EOF
Add this to my knowledge graph:

CONCEPT: $concept

DESCRIPTION:
$description

CATEGORY: $category

RELATED TO: $related

KEY INSIGHT:
$insight
EOF

if [ -n "$source" ]; then
  cat >> "$entry_file" << EOF

SOURCE: $source
EOF
fi

cat >> "$entry_file" << EOF

DATE LEARNED: $timestamp

---
Please create a node for "$concept" and link it to related concepts.
EOF

echo "✅ Knowledge graph entry created!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps:"
echo ""
echo "1. Open Claude Desktop"
echo "2. Paste the content below:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$entry_file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Tip: Build your knowledge graph consistently for better retention"
echo "📁 Entry saved at: $entry_file"
echo ""

# Optionally copy to clipboard
if command -v pbcopy &> /dev/null; then
  cat "$entry_file" | pbcopy
  echo "✨ Content copied to clipboard!"
elif command -v xclip &> /dev/null; then
  cat "$entry_file" | xclip -selection clipboard
  echo "✨ Content copied to clipboard!"
fi
