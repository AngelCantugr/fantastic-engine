#!/bin/bash
# task-router.sh - Helps you pick the right AI tool for your task
# Part of AI Productivity Orchestration experiment

echo "🤖 AI Tool Router"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "What do you need help with?"
echo ""
echo "1) Complex code refactoring (multi-file)"
echo "2) Quick code snippet or function"
echo "3) Research current information"
echo "4) Learn new technology/framework"
echo "5) Plan a feature or project"
echo "6) Debug an issue"
echo "7) Write or update documentation"
echo "8) Quick question"
echo "9) Generate tests"
echo "10) Git/CLI operations"
echo ""
read -p "Enter number (1-10): " choice
echo ""

case $choice in
  1)
    echo "✨ Best Tool: Claude Code with Sequential Thinking MCP"
    echo ""
    echo "📋 Steps:"
    echo "   1. Open Claude Code in your project"
    echo "   2. Describe the refactoring goal"
    echo "   3. Ask to break it down with Sequential Thinking"
    echo "   4. Review each step before proceeding"
    echo ""
    echo "💡 Tip: Use GitHub Copilot for boilerplate during refactor"
    ;;
  2)
    echo "⚡ Best Tool: ChatGPT Desktop or GitHub Copilot"
    echo ""
    echo "📋 Steps:"
    echo "   • ChatGPT Desktop: Use voice mode for fastest results"
    echo "   • GitHub Copilot: If already in IDE, use inline suggestions"
    echo "   • Opencode: For quick prototyping without IDE"
    echo ""
    echo "💡 Tip: For quality, copy result to Claude Code for review"
    ;;
  3)
    echo "🔍 Best Tool: Perplexity or Comet Browser"
    echo ""
    echo "📋 Steps:"
    echo "   1. Use Perplexity Pro Search for complex queries"
    echo "   2. Check citations and sources"
    echo "   3. Use Focus mode (Academic, Writing, etc.)"
    echo "   4. Copy research to Claude Desktop for deep analysis"
    echo ""
    echo "💡 Tip: Perplexity excels at current/recent information"
    ;;
  4)
    echo "📚 Best Approach: Multi-tool Learning Workflow"
    echo ""
    echo "📋 Steps:"
    echo "   1. Research with Perplexity (find best resources)"
    echo "   2. Plan with Claude Desktop + Sequential Thinking MCP"
    echo "   3. Quick Q&A with ChatGPT Desktop"
    echo "   4. Hands-on practice with Opencode + GitHub Copilot"
    echo "   5. Deep dive with Claude Code"
    echo "   6. Add to Knowledge Graph in Claude Desktop"
    echo ""
    echo "💡 Tip: Build knowledge graph as you learn for retention"
    ;;
  5)
    echo "🎯 Best Tool: Claude Desktop with Sequential Thinking MCP"
    echo ""
    echo "📋 Steps:"
    echo "   1. Describe the feature/project goal"
    echo "   2. Use Sequential Thinking to break it down"
    echo "   3. Optionally visualize in ChatGPT Atlas"
    echo "   4. Save plan to Memory MCP"
    echo "   5. Implement in Claude Code"
    echo ""
    echo "💡 Tip: Save the plan to Memory MCP for context continuity"
    ;;
  6)
    echo "🐛 Best Tool: Claude Code"
    echo ""
    echo "📋 Steps:"
    echo "   1. Document bug symptoms in Memory MCP (via Claude Desktop)"
    echo "   2. Research similar issues in Perplexity"
    echo "   3. Analyze code in Claude Code"
    echo "   4. Use Sequential Thinking to debug systematically"
    echo "   5. Test fix thoroughly"
    echo "   6. Add solution to Knowledge Graph"
    echo ""
    echo "💡 Tip: Sequential Thinking prevents missing edge cases"
    ;;
  7)
    echo "📝 Best Tool: Goose for generation, Claude Code for review"
    echo ""
    echo "📋 Steps:"
    echo "   1. Use Goose to generate initial documentation"
    echo "   2. Review in Claude Code for accuracy"
    echo "   3. Refine technical details with Claude"
    echo "   4. Let Goose handle formatting and structure"
    echo ""
    echo "💡 Tip: Goose excels at documentation patterns"
    ;;
  8)
    echo "❓ Best Tool: ChatGPT Desktop (fastest)"
    echo ""
    echo "📋 Alternatives:"
    echo "   • ChatGPT Desktop: General questions (use voice mode)"
    echo "   • GitHub Copilot CLI: Terminal/CLI questions"
    echo "   • Perplexity: If you need current information"
    echo ""
    echo "💡 Tip: Don't overthink simple queries - speed matters here"
    ;;
  9)
    echo "🧪 Best Tool: GitHub Copilot or Claude Code"
    echo ""
    echo "📋 Steps:"
    echo "   • GitHub Copilot: For unit tests (quick generation)"
    echo "   • Claude Code: For integration tests (more complex)"
    echo "   • Both: Review test coverage and edge cases"
    echo ""
    echo "💡 Tip: Let Copilot generate, Claude Code review"
    ;;
  10)
    echo "⌨️  Best Tool: GitHub Copilot CLI"
    echo ""
    echo "📋 Commands:"
    echo "   gh copilot suggest \"your question\""
    echo "   gh copilot explain \"command to explain\""
    echo ""
    echo "💡 Tip: Use Claude Code for complex git workflows"
    ;;
  *)
    echo "❌ Invalid choice. Please run again and enter 1-10."
    exit 1
    ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Track your tool usage in agent-testing-log.md"
echo ""
