# 🚀 Quick Start Guide

Get started with the AI Engineer Learning Path in under 10 minutes!

## Prerequisites

1. **M4 Mac** (or any Mac with Apple Silicon)
2. **Ollama installed** - [Download from ollama.ai](https://ollama.ai)
3. **Python 3.11+**

## Step 1: Setup (5 minutes)

```bash
# Navigate to the project
cd experiments/ai-engineer-learning

# Run the setup script
./setup.sh

# This will:
# - Create a virtual environment
# - Install all Python dependencies
# - Pull recommended Ollama models
# - Create configuration files
```

## Step 2: Verify Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Check Ollama is running
ollama list

# You should see qwen2.5-coder:7b and other models
```

## Step 3: Run Your First Agent (2 minutes)

```bash
# Try the Simple Chat Agent
cd agents/01_simple_chat
python agent.py

# Start chatting! Ask it:
# "Explain Python decorators"
# "What's the difference between a list and a tuple?"
```

## Step 4: Explore More Agents

```bash
# Code Review Assistant
cd ../02_code_review
echo 'def add(x,y):return x+y' | python agent.py --review-type style

# Git Commit Message Generator
cd ../03_commit_message
python agent.py  # (requires staged git changes)

# Test Generator
cd ../05_test_generator
python agent.py --file ../../shared/config.py

# And 6 more agents to explore!
```

## Common Commands

```bash
# Activate environment
source .venv/bin/activate

# List all agents
ls agents/

# Run any agent
cd agents/XX_agent_name
python agent.py --help

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Troubleshooting

### Ollama not responding

```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
killall ollama
ollama serve &

# Pull missing models
ollama pull qwen2.5-coder:7b
```

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify virtual environment
which python  # Should show .venv/bin/python
```

### Model too slow on M4 Mac

```bash
# Use smaller model
ollama pull qwen2.5:3b

# Then specify when running agents
python agent.py --model qwen2.5:3b
```

## Learning Path

1. **Week 1**: Agents 1-3 (Foundations)
2. **Week 2**: Agents 4-6 (Intermediate)
3. **Week 3**: Agents 7-10 (Advanced)

Read the main [README.md](./README.md) for the complete curriculum.

## Next Steps

- [ ] Complete Agent 1 and read its documentation
- [ ] Run the example usage scripts
- [ ] Try modifying prompts to customize behavior
- [ ] Build your own agent combining concepts learned
- [ ] Share your learnings!

## Getting Help

- Check individual agent README.md files
- Review the main README.md
- Open an issue if you find bugs
- Read the troubleshooting section above

**Happy learning! 🚀**
