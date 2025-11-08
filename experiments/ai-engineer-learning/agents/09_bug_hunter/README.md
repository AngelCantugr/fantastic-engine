# Agent 9: Bug Hunter (ReAct) ⭐⭐⭐⭐⭐

**Complexity:** Very Advanced | **Framework:** `langgraph` | **Estimated Time:** 6-8 hours

## 🎯 Learning Objectives

- ✅ ReAct pattern (Reasoning + Acting)
- ✅ LangGraph state machines
- ✅ Agent loops and iterations
- ✅ Tool calling and execution
- ✅ Dynamic problem solving

## 🧠 Key Concepts

### ReAct Pattern

ReAct combines **Reasoning** and **Acting** in a loop:

1. **Thought**: Agent reasons about the problem
2. **Action**: Agent decides what tool to use
3. **Observation**: Agent sees the tool result
4. Repeat until solved

### LangGraph

LangGraph creates stateful agents with explicit control flow:
- Define states
- Define transitions
- Build graphs
- Execute with loops

## 🚀 Usage

```bash
# Hunt bugs in a file
python agent.py --file src/buggy_code.py

# Hunt bugs in a codebase
python agent.py --directory src/

# With specific bug types
python agent.py --file app.py --types "security,performance"
```

**Next:** [Agent 10: AI Pair Programmer](../10_pair_programmer/README.md) →
