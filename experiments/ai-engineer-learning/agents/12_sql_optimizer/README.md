# Agent 12: SQL Query Optimizer ⭐⭐

**Complexity:** Intermediate | **Framework:** `sqlparse` + `sqlglot` | **Estimated Time:** 3-4 hours

## 🎯 Learning Objectives

- ✅ Analyze SQL query performance
- ✅ Suggest index optimizations
- ✅ Rewrite queries for better performance
- ✅ Understand database execution plans
- ✅ Detect N+1 query problems

## 🚀 Usage

```bash
# Optimize a single query
python agent.py --query "SELECT * FROM users WHERE name LIKE '%john%'"

# Analyze queries from a file
python agent.py --file slow_queries.sql

# With database context
python agent.py --query "..." --schema schema.sql
```

**Next:** [Agent 13: Dependency Analyzer](../13_dependency_analyzer/README.md) →
