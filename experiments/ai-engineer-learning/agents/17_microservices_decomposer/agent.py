#!/usr/bin/env python3
"""Agent 17: Microservices Decomposer - Suggest service boundaries using DDD."""

import sys
import ast
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class MicroservicesDecomposer:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def analyze_codebase(self, directory: Path) -> Dict[str, Set[str]]:
        """Analyze codebase to find module dependencies."""
        dependencies = defaultdict(set)

        for file in directory.rglob("*.py"):
            try:
                tree = ast.parse(file.read_text())
                module = file.stem

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies[module].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies[module].add(node.module)
            except:
                pass

        return dependencies

    def suggest_services(self, dependencies: Dict[str, Set[str]]) -> str:
        """Suggest microservice boundaries using AI."""
        dep_summary = "\n".join([
            f"{module}: {', '.join(deps)}"
            for module, deps in dependencies.items()
        ])

        prompt = f"""Analyze these module dependencies and suggest microservice boundaries:

{dep_summary}

Using Domain-Driven Design principles, provide:
1. Suggested service boundaries
2. Bounded contexts
3. Inter-service communication needs
4. Migration strategy from monolith
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Microservices Decomposer")
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()

    decomposer = MicroservicesDecomposer()
    console.print("[cyan]Analyzing codebase...[/cyan]\n")

    dependencies = decomposer.analyze_codebase(args.directory)
    console.print(f"Found {len(dependencies)} modules\n")

    console.print("[cyan]Suggesting service boundaries...[/cyan]\n")
    suggestions = decomposer.suggest_services(dependencies)
    console.print(suggestions)

if __name__ == "__main__":
    main()
