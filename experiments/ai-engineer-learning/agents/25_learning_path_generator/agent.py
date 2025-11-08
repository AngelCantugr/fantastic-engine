#!/usr/bin/env python3
"""Agent 25: Learning Path Generator - Personalized learning roadmaps."""

import sys
from langchain_ollama import OllamaLLM
from rich.console import Console

console = Console()

class LearningPathGenerator:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.3)

    def generate_path(self, current_level: str, goal: str) -> str:
        """Generate personalized learning path."""
        prompt = f"""Create a personalized learning path:

Current Level: {current_level}
Goal: {goal}

Provide:
1. Skill gap analysis
2. 6-month learning roadmap (weekly breakdown)
3. Recommended resources (books, courses, projects)
4. Milestones and checkpoints
5. Practice projects for each phase
6. Interview prep timeline (if applicable)
7. Networking and visibility strategies
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Learning Path Generator")
    parser.add_argument("--goal", required=True, help="Learning goal")
    parser.add_argument("--current", required=True, help="Current level")
    args = parser.parse_args()

    generator = LearningPathGenerator()
    console.print(f"[cyan]Generating path: {args.current} → {args.goal}[/cyan]\n")
    path = generator.generate_path(args.current, args.goal)
    console.print(path)

if __name__ == "__main__":
    main()
