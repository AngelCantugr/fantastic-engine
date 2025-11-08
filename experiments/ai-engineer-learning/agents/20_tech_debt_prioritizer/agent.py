#!/usr/bin/env python3
"""Agent 20: Tech Debt Prioritizer - Analyze and prioritize technical debt."""

import sys
import ast
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.table import Table

console = Console()

@dataclass
class DebtItem:
    location: str
    type: str
    severity: int  # 1-10
    effort: int    # hours
    impact: int    # 1-10

class TechDebtPrioritizer:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)
        self.debt_items: List[DebtItem] = []

    def analyze_directory(self, directory: Path) -> List[DebtItem]:
        """Scan codebase for technical debt indicators."""
        debt = []

        for file in directory.rglob("*.py"):
            try:
                content = file.read_text()
                tree = ast.parse(content)

                # Simple heuristics
                if "TODO" in content or "FIXME" in content:
                    debt.append(DebtItem(str(file), "TODO comment", 3, 2, 5))

                # Check for code smells
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Long functions
                        if len(node.body) > 50:
                            debt.append(DebtItem(
                                f"{file}:{node.lineno}",
                                "Long function",
                                6, 4, 7
                            ))

                        # Many parameters
                        if len(node.args.args) > 5:
                            debt.append(DebtItem(
                                f"{file}:{node.lineno}",
                                "Too many parameters",
                                5, 3, 6
                            ))
            except:
                pass

        return debt

    def prioritize(self, debt_items: List[DebtItem]) -> List[DebtItem]:
        """Calculate ROI and prioritize debt items."""
        # ROI = Impact / Effort
        return sorted(debt_items, key=lambda d: d.impact / d.effort, reverse=True)

    def generate_report(self, debt_items: List[DebtItem]) -> str:
        """Generate AI-enhanced debt report."""
        debt_summary = "\n".join([
            f"- {d.location}: {d.type} (Severity: {d.severity}, Effort: {d.effort}h, Impact: {d.impact})"
            for d in debt_items[:20]
        ])

        prompt = f"""Analyze this technical debt inventory:

{debt_summary}

Provide:
1. Top 5 priorities to address
2. Estimated total cost of delay
3. Recommended refactoring strategy
4. Quick wins (low effort, high impact)
5. Long-term improvement plan
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tech Debt Prioritizer")
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()

    prioritizer = TechDebtPrioritizer()

    console.print("[cyan]Scanning for technical debt...[/cyan]\n")
    debt_items = prioritizer.analyze_directory(args.directory)
    console.print(f"[yellow]Found {len(debt_items)} debt items[/yellow]\n")

    # Prioritize
    prioritized = prioritizer.prioritize(debt_items)

    # Display table
    table = Table(title="Technical Debt Priority")
    table.add_column("Location", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("ROI", style="green")

    for item in prioritized[:10]:
        roi = f"{item.impact / item.effort:.2f}"
        table.add_row(item.location, item.type, roi)

    console.print(table)

    # Generate AI report
    console.print("\n[cyan]Generating detailed analysis...[/cyan]\n")
    report = prioritizer.generate_report(prioritized)
    console.print(report)

if __name__ == "__main__":
    main()
