#!/usr/bin/env python3
"""Agent 22: Algorithm Visualizer - Visual algorithm learning."""

import sys
from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.table import Table

console = Console()

class AlgorithmVisualizer:
    ALGORITHMS = {
        "quicksort": "Divide and conquer sorting algorithm",
        "mergesort": "Stable divide and conquer sort",
        "bfs": "Breadth-first search graph traversal",
        "dfs": "Depth-first search graph traversal",
        "dijkstra": "Shortest path algorithm",
    }

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def explain_algorithm(self, algorithm: str) -> str:
        """Generate step-by-step explanation with ASCII visualization."""
        prompt = f"""Explain the {algorithm} algorithm step-by-step with ASCII art visualization.

Include:
1. How it works conceptually
2. Step-by-step execution on example: [5, 2, 8, 1, 9]
3. ASCII visualization of each step
4. Time complexity: O(?)
5. Space complexity: O(?)
6. When to use it
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Algorithm Visualizer")
    parser.add_argument("--algorithm", required=True, choices=AlgorithmVisualizer.ALGORITHMS.keys())
    args = parser.parse_args()

    viz = AlgorithmVisualizer()
    console.print(f"[cyan]Visualizing: {args.algorithm}[/cyan]\n")
    explanation = viz.explain_algorithm(args.algorithm)
    console.print(explanation)

if __name__ == "__main__":
    main()
