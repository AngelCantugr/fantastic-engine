#!/usr/bin/env python3
"""
Agent 21: Coding Kata Coach
============================

Daily coding practice with AI-powered feedback and progressive challenges.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import random

from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass
class UserProfile:
    """Track user's progress and stats."""
    username: str
    katas_completed: int = 0
    current_streak: int = 0
    best_streak: int = 0
    last_practice_date: Optional[str] = None
    skill_level: int = 1  # 1-10
    patterns_mastered: List[str] = None

    def __post_init__(self):
        if self.patterns_mastered is None:
            self.patterns_mastered = []


KATA_DATABASE = {
    "easy": [
        {
            "name": "Two Sum",
            "description": "Find two numbers that add up to a target",
            "pattern": "hash-map",
            "tests": [
                {"input": ([2, 7, 11, 15], 9), "output": [0, 1]},
                {"input": ([3, 2, 4], 6), "output": [1, 2]},
            ]
        },
        {
            "name": "Palindrome Check",
            "description": "Check if a string is a palindrome",
            "pattern": "two-pointers",
            "tests": [
                {"input": "racecar", "output": True},
                {"input": "hello", "output": False},
            ]
        },
    ],
    "medium": [
        {
            "name": "Longest Substring Without Repeating",
            "description": "Find length of longest substring without repeating chars",
            "pattern": "sliding-window",
            "tests": [
                {"input": "abcabcbb", "output": 3},
                {"input": "bbbbb", "output": 1},
            ]
        },
    ],
    "hard": [
        {
            "name": "Median of Two Sorted Arrays",
            "description": "Find median of two sorted arrays",
            "pattern": "binary-search",
            "tests": [
                {"input": ([1, 3], [2]), "output": 2.0},
                {"input": ([1, 2], [3, 4]), "output": 2.5},
            ]
        },
    ]
}


class KataCoach:
    """Interactive coding kata coach."""

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.3)
        self.profile_path = Path.home() / ".kata_coach_profile.json"
        self.profile = self._load_profile()

    def _load_profile(self) -> UserProfile:
        """Load user profile or create new one."""
        if self.profile_path.exists():
            data = json.loads(self.profile_path.read_text())
            return UserProfile(**data)
        else:
            username = Prompt.ask("[cyan]Welcome! What's your name?[/cyan]")
            return UserProfile(username=username)

    def _save_profile(self):
        """Save user profile."""
        self.profile_path.write_text(json.dumps(asdict(self.profile), indent=2))

    def _update_streak(self):
        """Update practice streak."""
        today = datetime.now().date().isoformat()

        if self.profile.last_practice_date:
            last_date = datetime.fromisoformat(self.profile.last_practice_date).date()
            days_diff = (datetime.now().date() - last_date).days

            if days_diff == 0:
                return  # Already practiced today
            elif days_diff == 1:
                self.profile.current_streak += 1
            else:
                self.profile.current_streak = 1  # Streak broken
        else:
            self.profile.current_streak = 1

        self.profile.last_practice_date = today
        self.profile.best_streak = max(self.profile.best_streak, self.profile.current_streak)

    def display_dashboard(self):
        """Show user's stats dashboard."""
        console.print(Panel.fit(
            f"[bold cyan]Coding Kata Coach[/bold cyan]\n\n"
            f"Welcome back, {self.profile.username}!\n\n"
            f"📊 Stats:\n"
            f"  • Katas Completed: [green]{self.profile.katas_completed}[/green]\n"
            f"  • Current Streak: [yellow]{'🔥 ' * min(self.profile.current_streak, 10)}{self.profile.current_streak} days[/yellow]\n"
            f"  • Best Streak: [yellow]{self.profile.best_streak} days[/yellow]\n"
            f"  • Skill Level: [cyan]{'⭐' * self.profile.skill_level}[/cyan]\n"
            f"  • Patterns Mastered: [green]{len(self.profile.patterns_mastered)}[/green]",
            border_style="cyan"
        ))

    def get_daily_kata(self, difficulty: str = None) -> Dict:
        """Get today's kata challenge."""
        if difficulty is None:
            # Auto-select based on skill level
            if self.profile.skill_level < 3:
                difficulty = "easy"
            elif self.profile.skill_level < 7:
                difficulty = "medium"
            else:
                difficulty = "hard"

        katas = KATA_DATABASE.get(difficulty, KATA_DATABASE["easy"])
        return random.choice(katas)

    def present_challenge(self, kata: Dict):
        """Present kata challenge to user."""
        console.print(f"\n[bold yellow]Today's Challenge: {kata['name']}[/bold yellow]")
        console.print(f"[dim]Pattern: {kata['pattern']}[/dim]\n")
        console.print(kata['description'])
        console.print(f"\n[cyan]Example test case:[/cyan]")
        test = kata['tests'][0]
        console.print(f"  Input: {test['input']}")
        console.print(f"  Expected Output: {test['output']}\n")

    def review_solution(self, solution: str, kata: Dict) -> str:
        """Get AI review of solution."""
        prompt = f"""Review this coding solution:

Problem: {kata['name']}
Description: {kata['description']}
Pattern: {kata['pattern']}

Solution:
```python
{solution}
```

Provide:
1. Correctness assessment
2. Time/space complexity
3. Code quality feedback
4. Optimization suggestions
5. Alternative approaches
"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Analyzing your solution..."),
            transient=True
        ) as progress:
            progress.add_task("review", total=None)
            review = self.llm.invoke(prompt)

        return review

    def interactive_session(self, difficulty: str = None):
        """Run interactive kata session."""
        self.display_dashboard()

        kata = self.get_daily_kata(difficulty)
        self.present_challenge(kata)

        console.print("[green]Write your solution:[/green]")
        console.print("[dim](Type 'hint' for a hint, 'skip' to skip, or paste your code)[/dim]\n")

        solution = Prompt.ask("Solution")

        if solution.lower() == "skip":
            console.print("[yellow]Skipped. Try again tomorrow![/yellow]")
            return

        if solution.lower() == "hint":
            hint = self._get_hint(kata)
            console.print(f"\n💡 [yellow]Hint:[/yellow] {hint}\n")
            solution = Prompt.ask("Solution")

        # Review solution
        review = self.review_solution(solution, kata)
        console.print(Panel(review, title="[green]Solution Review[/green]", border_style="green"))

        # Update progress
        if Confirm.ask("\n[cyan]Did you solve it successfully?[/cyan]"):
            self.profile.katas_completed += 1
            self._update_streak()

            if kata['pattern'] not in self.profile.patterns_mastered:
                if self.profile.katas_completed % 5 == 0:  # Master after 5 katas
                    self.profile.patterns_mastered.append(kata['pattern'])
                    console.print(f"\n🏆 [yellow]Pattern Mastered: {kata['pattern']}![/yellow]")

            # Level up
            new_level = min(10, 1 + self.profile.katas_completed // 10)
            if new_level > self.profile.skill_level:
                self.profile.skill_level = new_level
                console.print(f"\n⬆️  [green]Level Up! Now level {new_level}[/green]")

            self._save_profile()
            console.print("\n✅ [green]Great job! See you tomorrow![/green]")

    def _get_hint(self, kata: Dict) -> str:
        """Get progressive hint for kata."""
        prompt = f"""Provide a helpful hint for this problem (don't give away the solution):

Problem: {kata['name']}
Description: {kata['description']}
Pattern: {kata['pattern']}

Give a gentle hint that guides toward the solution without revealing it."""

        return self.llm.invoke(prompt)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Coding Kata Coach")
    parser.add_argument("--daily", action="store_true", help="Get daily challenge")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"])
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--stats", action="store_true", help="Show stats only")
    args = parser.parse_args()

    coach = KataCoach()

    if args.stats:
        coach.display_dashboard()
    elif args.interactive or args.daily:
        coach.interactive_session(args.difficulty)
    else:
        coach.display_dashboard()
        if Confirm.ask("\n[cyan]Ready for today's challenge?[/cyan]"):
            coach.interactive_session(args.difficulty)


if __name__ == "__main__":
    main()
