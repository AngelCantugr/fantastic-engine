#!/usr/bin/env python3
"""Agent 23: Design Pattern Teacher - Learn software design patterns."""

import sys
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class DesignPatternTeacher:
    PATTERNS = {
        "Creational": ["Factory", "Abstract Factory", "Builder", "Prototype", "Singleton"],
        "Structural": ["Adapter", "Bridge", "Composite", "Decorator", "Facade", "Flyweight", "Proxy"],
        "Behavioral": ["Chain of Responsibility", "Command", "Iterator", "Mediator", "Memento",
                      "Observer", "State", "Strategy", "Template Method", "Visitor"]
    }

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.2)

    def teach_pattern(self, pattern: str) -> str:
        """Teach a design pattern with examples."""
        prompt = f"""Teach the {pattern} design pattern:

1. Intent: What problem does it solve?
2. Structure: UML-style diagram (ASCII)
3. Python Implementation: Complete working example
4. Real-world use case
5. Pros and cons
6. When to use vs when to avoid
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Design Pattern Teacher")
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--list", action="store_true", help="List all patterns")
    args = parser.parse_args()

    teacher = DesignPatternTeacher()

    if args.list:
        for category, patterns in teacher.PATTERNS.items():
            console.print(f"\n[bold]{category}:[/bold]")
            for p in patterns:
                console.print(f"  • {p}")
    else:
        lesson = teacher.teach_pattern(args.pattern)
        console.print(lesson)

if __name__ == "__main__":
    main()
