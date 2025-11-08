# AI Engineer Learning Path

Welcome to the **AI Engineer Learning Path** - a comprehensive, hands-on curriculum for mastering AI engineering through building 10 progressively complex agents.

## 🎯 Overview

This learning path teaches you how to:

- Connect to local LLMs with Ollama
- Master prompt engineering and structured prompts
- Implement RAG (Retrieval-Augmented Generation)
- Build multi-agent systems
- Create production-ready AI tools for your engineering workflow

## 📚 The 10 Agents

### Beginner Level

1. **[Simple Chat Agent](agents/01_simple_chat.md)** ⭐
   - Basic Ollama API connection
   - Streaming responses
   - Conversation history

2. **[Code Review Assistant](agents/02_code_review.md)** ⭐⭐
   - Structured prompting
   - Few-shot learning
   - Template management

3. **[Git Commit Message Generator](agents/03_commit_message.md)** ⭐⭐
   - Tool integration
   - LangChain basics
   - Git integration

### Intermediate Level

4. **[Documentation Writer](agents/04_doc_writer.md)** ⭐⭐⭐
   - RAG fundamentals
   - LlamaIndex usage
   - Vector embeddings

5. **[Test Generator](agents/05_test_generator.md)** ⭐⭐⭐
   - AST parsing
   - Code analysis
   - Test automation

6. **[PR Analyzer](agents/06_pr_analyzer.md)** ⭐⭐⭐⭐
   - Multi-step reasoning
   - LCEL chains
   - Structured analysis

### Advanced Level

7. **[Refactoring Suggester](agents/07_refactoring_suggester.md)** ⭐⭐⭐⭐
   - Vector embeddings
   - Semantic code search
   - Pattern recognition

8. **[Architecture Advisor](agents/08_architecture_advisor.md)** ⭐⭐⭐⭐⭐
   - Multi-agent systems
   - CrewAI framework
   - Collaborative problem-solving

9. **[Bug Hunter](agents/09_bug_hunter.md)** ⭐⭐⭐⭐⭐
   - ReAct pattern
   - LangGraph
   - Agent loops

10. **[AI Pair Programmer](agents/10_pair_programmer.md)** ⭐⭐⭐⭐⭐⭐
    - Full agentic workflow
    - Planning and execution
    - Complete AI assistant

## 🚀 Quick Start

```bash
# Clone and setup
cd experiments/ai-engineer-learning
./setup.sh

# Start with Agent 1
cd agents/01_simple_chat
python agent.py
```

See the [Quick Start Guide](../QUICKSTART.md) for detailed setup instructions.

## 📖 Learning Resources

- [Main README](../README.md) - Complete curriculum overview
- [Setup Guide](../QUICKSTART.md) - Installation instructions
- Individual agent READMEs - Detailed documentation for each agent

## 🎓 Learning Path

Follow the 3-week curriculum in the main README or go at your own pace. Each agent builds on concepts from previous ones.

## 🛠️ Tech Stack

- **Python 3.11+**
- **Ollama** - Local LLM runtime
- **LangChain** - LLM orchestration
- **LlamaIndex** - RAG and data connectors
- **CrewAI** - Multi-agent framework
- **LangGraph** - Stateful agents
- **ChromaDB** - Vector database

## 📊 Progress Tracking

Track your progress as you complete each agent:

- [ ] Agent 1: Simple Chat
- [ ] Agent 2: Code Review
- [ ] Agent 3: Commit Messages
- [ ] Agent 4: Documentation
- [ ] Agent 5: Test Generation
- [ ] Agent 6: PR Analysis
- [ ] Agent 7: Refactoring
- [ ] Agent 8: Architecture
- [ ] Agent 9: Bug Hunting
- [ ] Agent 10: Pair Programming

## 🤝 Contributing

Found an improvement? Have a suggestion? This is a learning playground - contributions are welcome!

---

**Ready to start your AI engineering journey?** Begin with [Agent 1: Simple Chat](agents/01_simple_chat.md) →
