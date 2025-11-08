#!/usr/bin/env python3
"""Agent 26: System Design Interview Coach."""

from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.prompt import Prompt

console = Console()

DESIGN_PROBLEMS = [
    "Design Twitter/X",
    "Design URL Shortener",
    "Design Netflix",
    "Design Uber",
    "Design WhatsApp",
]

class SystemDesignCoach:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.3)

    def conduct_interview(self, problem: str):
        """Interactive system design interview."""
        console.print(f"\n[bold cyan]System Design Interview[/bold cyan]")
        console.print(f"[yellow]Problem: {problem}[/yellow]\n")

        # Requirements gathering
        console.print("[green]Interviewer:[/green] Let's start with requirements.")
        requirements = Prompt.ask("What are the functional requirements?")

        # Scale discussion
        console.print("\n[green]Interviewer:[/green] Good. What about scale?")
        scale = Prompt.ask("How many users/requests per day?")

        # Design review
        design = Prompt.ask("\nDescribe your high-level design")

        feedback = self._get_feedback(problem, requirements, scale, design)
        console.print(f"\n[cyan]Feedback:[/cyan]\n{feedback}")

    def _get_feedback(self, problem, requirements, scale, design) -> str:
        prompt = f"""Review this system design interview response:

Problem: {problem}
Requirements: {requirements}
Scale: {scale}
Design: {design}

Provide:
1. What was done well
2. What's missing
3. Follow-up questions to ask
4. Architecture improvements
5. Score (1-10) with justification
"""
        return self.llm.invoke(prompt)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="System Design Coach")
    parser.add_argument("--problem", choices=DESIGN_PROBLEMS)
    args = parser.parse_args()

    coach = SystemDesignCoach()
    import random
    problem = args.problem or random.choice(DESIGN_PROBLEMS)
    coach.conduct_interview(problem)

if __name__ == "__main__":
    main()
