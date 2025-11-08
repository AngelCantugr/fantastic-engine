#!/usr/bin/env python3
"""
Agent 12: SQL Query Optimizer
==============================

Analyzes and optimizes SQL queries using LLM + SQL parsing libraries.
"""

import sys
from pathlib import Path

try:
    import sqlparse
except ImportError:
    print("Run: pip install sqlparse")
    sys.exit(1)

from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.panel import Panel

console = Console()


class SQLOptimizer:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def analyze_query(self, query: str, schema_context: str = "") -> str:
        """Analyze and optimize SQL query."""

        # Format query
        formatted = sqlparse.format(query, reindent=True, keyword_case='upper')

        prompt = f"""Analyze this SQL query and provide optimizations:

Query:
{formatted}

{f"Schema context: {schema_context}" if schema_context else ""}

Provide:
1. Performance issues identified
2. Suggested indexes
3. Optimized query version
4. Explanation of improvements
"""
        return self.llm.invoke(prompt)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SQL Query Optimizer")
    parser.add_argument("--query", help="SQL query to optimize")
    parser.add_argument("--file", type=Path, help="File containing queries")
    parser.add_argument("--schema", type=Path, help="Schema context file")
    args = parser.parse_args()

    optimizer = SQLOptimizer()

    query = args.query or (args.file.read_text() if args.file else None)
    if not query:
        console.print("[red]Provide --query or --file[/red]")
        sys.exit(1)

    schema = args.schema.read_text() if args.schema else ""

    console.print(Panel.fit("[bold cyan]SQL Query Optimizer[/bold cyan]"))
    console.print("\n[cyan]Analyzing query...[/cyan]\n")

    analysis = optimizer.analyze_query(query, schema)
    console.print(Panel(analysis, title="Optimization Analysis", border_style="green"))


if __name__ == "__main__":
    main()
