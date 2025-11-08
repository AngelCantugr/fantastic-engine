#!/usr/bin/env python3
"""Agent 24: Tech Stack Explorer - Research and compare technologies."""

import sys
from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.table import Table

console = Console()

class TechStackExplorer:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.3)

    def compare_technologies(self, techs: list[str]) -> str:
        """Compare multiple technologies."""
        prompt = f"""Compare these technologies: {', '.join(techs)}

Create a comprehensive comparison:

1. Overview of each
2. Comparison table:
   - Performance
   - Learning curve
   - Community size
   - Ecosystem/libraries
   - Use cases
   - Pros/cons

3. Decision matrix scoring (1-10 for each criterion)
4. Recommendation based on common use cases
5. Migration considerations
"""
        return self.llm.invoke(prompt)

    def explore_trend(self, topic: str) -> str:
        """Explore a technology trend."""
        prompt = f"""Research current trends in: {topic}

Provide:
1. Current state of the technology
2. Key players and solutions
3. Adoption trends
4. Future predictions
5. Getting started guide
6. Resources for learning
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tech Stack Explorer")
    parser.add_argument("--compare", nargs='+', help="Technologies to compare")
    parser.add_argument("--explore", type=str, help="Technology trend to explore")
    args = parser.parse_args()

    explorer = TechStackExplorer()

    if args.compare:
        console.print(f"[cyan]Comparing: {', '.join(args.compare)}[/cyan]\n")
        comparison = explorer.compare_technologies(args.compare)
        console.print(comparison)
    elif args.explore:
        console.print(f"[cyan]Exploring: {args.explore}[/cyan]\n")
        analysis = explorer.explore_trend(args.explore)
        console.print(analysis)

if __name__ == "__main__":
    main()
